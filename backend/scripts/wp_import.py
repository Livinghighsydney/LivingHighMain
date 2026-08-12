"""Load the extracted WordPress content into the Postgres tables.

Reads the distilled export (docs/wp-export/url-map.json for path + language +
SEO, posts.json for the bodies) and upserts rows into pages / posts / listings.
Idempotent: keyed on the unique ``path``, so re-running updates in place.

Run from the backend dir with the venv:
    .venv/Scripts/python.exe scripts/wp_import.py

What it sets now: the URL-preservation + SEO core (path, title, body, language,
translation_group, Yoast title/description/canonical/OG) for every live URL.
What it leaves for later: listing specifics (price/bedrooms/bathrooms/suburb)
that are still buried in Elementor markup, and post categories.
"""
from __future__ import annotations

import asyncio
import json
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from tortoise import Tortoise

from app.db import TORTOISE_ORM
from app.models import Listing, Locale, Page, Post
from app.models.base import PublishStatus

EXPORT = Path(__file__).resolve().parents[2] / "docs" / "wp-export"

# Fixed namespace so translation_group UUIDs are stable across runs/machines —
# every en/es/zh variant of a page hashes to the same group id.
TG_NAMESPACE = uuid.UUID("6f9b1e2a-3c4d-5e6f-8a9b-0c1d2e3f4a5b")

LOCALES = [("en", "English", ""), ("es", "Spanish", "/es"), ("zh", "Chinese", "/zh")]


def lang_stripped(entry) -> str:
    """The path with any language prefix removed (the translation-group key)."""
    segs = entry["path"].strip("/").split("/")
    if entry["language"] != "en" and segs:
        segs = segs[1:]
    return "/" + "/".join(segs) + "/" if segs and segs[0] else "/"


def is_listing(entry) -> bool:
    """Accommodation/co-living pages: children under /studio-apartment-sydney/."""
    ls = lang_stripped(entry)
    return entry["type"] == "page" and ls.startswith("/studio-apartment-sydney/") and ls != "/studio-apartment-sydney/"


def translation_group(entry) -> uuid.UUID:
    return uuid.uuid5(TG_NAMESPACE, lang_stripped(entry))


def parse_dt(s):
    if not s or s.startswith("0000"):
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def clip(val, n):
    return val[:n] if val else None


async def run():
    url_map = json.loads((EXPORT / "url-map.json").read_text(encoding="utf-8"))
    bodies = {p["id"]: p for p in json.loads((EXPORT / "posts.json").read_text(encoding="utf-8"))}

    await Tortoise.init(config=TORTOISE_ORM)

    locales = {}
    for code, name, prefix in LOCALES:
        loc, _ = await Locale.get_or_create(code=code, defaults={"name": name, "path_prefix": prefix})
        locales[code] = loc

    counts = Counter()
    for e in url_map:
        b = bodies.get(e["wp_id"], {})
        common = dict(
            translation_group=translation_group(e),
            title=clip(e["title"] or e["path"], 255),
            body=(b.get("content") or None),
            status=PublishStatus.PUBLISHED,
            seo_title=clip(e["seo_title"], 255),
            seo_description=e["seo_description"],
            canonical_url=clip(e["canonical"], 512),
            og_image_url=clip(e["og_image"], 512),
            locale=locales[e["language"]],
        )
        if e["type"] == "post":
            await Post.update_or_create(
                path=e["path"],
                defaults={**common, "excerpt": (b.get("excerpt") or None), "published_at": parse_dt(e["date"])},
            )
            counts["post"] += 1
        elif is_listing(e):
            await Listing.update_or_create(path=e["path"], defaults=common)
            counts["listing"] += 1
        else:
            await Page.update_or_create(path=e["path"], defaults=common)
            counts["page"] += 1

    await Tortoise.close_connections()

    print("== imported ==")
    for k in ("page", "listing", "post"):
        print(f"  {k:8s} {counts[k]}")
    print(f"  {'total':8s} {sum(counts.values())}")


if __name__ == "__main__":
    asyncio.run(run())
