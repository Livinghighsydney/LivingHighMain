"""Extract content + SEO metadata from a WordPress mysqldump (.sql.gz).

This does NOT migrate the raw MySQL schema (see CLAUDE.md). It streams the dump,
parses only the tables we care about, and emits clean structured JSON that the
new Next.js + FastAPI stack renders. The JSON is the migration source of truth.

Usage:
    python scripts/wp_extract.py --dump ../old_db/livinghighcom1_wp_q2vy9.sql.gz \
        --out ../../docs/wp-export --survey

Outputs (in --out):
    posts.json          published pages/posts/listings (content + slug + parent)
    yoast.json          per-URL SEO (title/description/canonical/OG) keyed by permalink
    taxonomy.json       terms + taxonomy + post->term relationships
    summary.json        counts + distributions (also printed)
"""
from __future__ import annotations

import argparse
import gzip
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

PREFIX = "mwnBE0_"


def parse_values(s: str):
    """Yield rows (lists of str|None) from a mysqldump ``VALUES (...),(...);`` payload.

    Handles single-quoted strings with backslash escapes, NULL, and bare numbers.
    """
    i, n = 0, len(s)
    while i < n:
        if s[i] != "(":
            i += 1
            continue
        i += 1  # consume '('
        row: list[str | None] = []
        while i < n:
            while i < n and s[i] in " \t\r\n":
                i += 1
            if i >= n:
                break
            if s[i] == "'":
                i += 1
                buf = []
                while i < n:
                    c = s[i]
                    if c == "\\":
                        # MySQL backslash escape: keep the next char literally.
                        nxt = s[i + 1]
                        buf.append({"n": "\n", "t": "\t", "r": "\r", "0": "\0"}.get(nxt, nxt))
                        i += 2
                        continue
                    if c == "'":
                        i += 1
                        break
                    buf.append(c)
                    i += 1
                row.append("".join(buf))
            else:
                j = i
                while i < n and s[i] not in ",)":
                    i += 1
                tok = s[j:i].strip()
                row.append(None if tok == "NULL" else tok)
            if i < n and s[i] == ",":
                i += 1
                continue
            if i < n and s[i] == ")":
                i += 1
                break
        yield row
        while i < n and s[i] != "(":
            i += 1


def _stmt_complete(buf: str) -> bool:
    """True if ``buf`` ends a SQL statement — an unquoted ``;`` as its last token.

    Quote-aware (respects backslash escapes) because values contain literal
    ``;`` and newlines. Cheap enough to call per appended line since phpMyAdmin
    chunks extended inserts to ~1 MB.
    """
    in_q = False
    i, n = 0, len(buf)
    last = ""
    while i < n:
        c = buf[i]
        if in_q:
            if c == "\\":
                i += 2
                continue
            if c == "'":
                in_q = False
        else:
            if c == "'":
                in_q = True
            elif not c.isspace():
                last = c
        i += 1
    return (not in_q) and last == ";"


def iter_table_rows(dump_path: Path, table: str):
    """Stream all INSERTed rows for one table, assembling multi-line statements.

    This dump is phpMyAdmin-style: ``INSERT INTO `t` (`a`,`b`) VALUES`` on one
    line, then ``(...),`` tuples on following lines, and a single tuple may span
    several physical lines (``post_content`` holds literal newlines). Yields
    ``(colnames_or_None, row)`` mapping by the INSERT's own column list.
    """
    full = f"{PREFIX}{table}"
    start = f"INSERT INTO `{full}` "
    with gzip.open(dump_path, "rt", encoding="utf-8", errors="replace") as f:
        buf = None
        cols = None
        for line in f:
            if buf is None:
                if not line.startswith(start):
                    continue
                rest = line[len(start):]
                if rest.startswith("("):
                    close = rest.index(") VALUES")
                    cols = [c.strip(" `") for c in rest[1:close].split(",")]
                    rest = rest[close + len(") VALUES"):]
                elif rest.startswith("VALUES"):
                    cols = None
                    rest = rest[len("VALUES"):]
                else:
                    continue
                buf = rest
            else:
                buf += line
            if _stmt_complete(buf):
                payload = buf.rstrip().rstrip(";")
                for row in parse_values(payload):
                    yield cols, row
                buf = None


# Column indexes (from the CREATE TABLE definitions in the dump).
POSTS_COLS = [
    "ID", "post_author", "post_date", "post_date_gmt", "post_content", "post_title",
    "post_excerpt", "post_status", "comment_status", "ping_status", "post_password",
    "post_name", "to_ping", "pinged", "post_modified", "post_modified_gmt",
    "post_content_filtered", "post_parent", "guid", "menu_order", "post_type",
    "post_mime_type", "comment_count",
]
YOAST_COLS = [
    "id", "permalink", "permalink_hash", "object_id", "object_type", "object_sub_type",
    "author_id", "post_parent", "title", "description", "breadcrumb_title", "post_status",
    "is_public", "is_protected", "has_public_posts", "number_of_pages", "canonical",
    "primary_focus_keyword", "primary_focus_keyword_score", "readability_score",
    "is_cornerstone", "is_robots_noindex", "is_robots_nofollow", "is_robots_noarchive",
    "is_robots_noimageindex", "is_robots_nosnippet", "twitter_title", "twitter_image",
    "twitter_description", "twitter_image_id", "twitter_image_source", "open_graph_title",
    "open_graph_description", "open_graph_image", "open_graph_image_id",
    "open_graph_image_source", "open_graph_image_meta", "link_count", "incoming_link_count",
    "prominent_words_version", "created_at", "updated_at", "blog_id", "language", "region",
    "schema_page_type", "schema_article_type", "has_ancestors",
    "estimated_reading_time_minutes", "version", "object_last_modified",
    "object_published_at", "inclusive_language_score",
]


def rowdict(insert_cols, row, default_cols):
    cols = insert_cols or default_cols
    return {c: (row[i] if i < len(row) else None) for i, c in enumerate(cols)}


LANG_PREFIXES = {"es": "es", "zh": "zh"}


def build_url_map(posts, yoast):
    """Join posts + Yoast into one entry per live URL — the migration source of truth.

    Each entry carries the full URL path (rebuilt from the parent chain, trailing
    slash), detected language, a ``translation_group`` (the language-stripped
    path, so EN/es/zh variants of a page share a key), and the per-URL SEO fields
    (title/description/canonical/OG) from Yoast keyed on the post ID.
    """
    byid = {p["id"]: p for p in posts}
    # Yoast rows for real posts are keyed by object_id (the WP post ID).
    yoast_by_id = {y["object_id"]: y for y in yoast if y.get("object_type") == "post" and y.get("object_id")}

    def full_path(p):
        parts, cur, seen = [], p, set()
        while cur and cur["id"] not in seen:
            seen.add(cur["id"])
            if cur["slug"]:
                parts.append(cur["slug"])
            cur = byid.get(cur["parent"])
        return "/" + "/".join(reversed(parts)) + "/" if parts else "/"

    entries = []
    for p in posts:
        path = full_path(p)
        segs = path.strip("/").split("/")
        first = segs[0] if segs and segs[0] else ""
        lang = LANG_PREFIXES.get(first, "en")
        # translation_group: strip the language prefix so variants align.
        group = path
        if lang != "en":
            group = "/" + "/".join(segs[1:]) + "/" if len(segs) > 1 else "/"
        y = yoast_by_id.get(p["id"], {})
        entries.append({
            "wp_id": p["id"],
            "type": p["type"],
            "path": path,
            "language": lang,
            "translation_group": group,
            "title": p["title"],
            "seo_title": (y.get("title") or "").strip() or None,
            "seo_description": (y.get("description") or "").strip() or None,
            "canonical": (y.get("canonical") or "").strip() or None,
            "og_image": (y.get("og_image") or "").strip() or None,
            "og_title": (y.get("og_title") or "").strip() or None,
            "is_noindex": y.get("is_noindex"),
            "parent_wp_id": p["parent"] or None,
            "date": p["date"],
            "modified": p["modified"],
        })
    entries.sort(key=lambda e: e["path"])
    return entries


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--survey", action="store_true", help="only print distributions, write nothing")
    # Which post types to keep as real content. WooCommerce/system types excluded.
    ap.add_argument("--types", default="page,post")
    args = ap.parse_args()

    dump = Path(args.dump)
    outdir = Path(args.out)
    keep_types = set(args.types.split(","))

    # ---- survey pass: what post types/statuses exist ----
    type_status = Counter()
    for cols, row in iter_table_rows(dump, "posts"):
        p = rowdict(cols, row, POSTS_COLS)
        type_status[(p["post_type"], p["post_status"])] += 1

    print("== post_type / post_status distribution ==")
    for (t, s), c in sorted(type_status.items(), key=lambda x: -x[1]):
        print(f"{c:6d}  {t or '?':26s} {s}")

    if args.survey:
        return

    outdir.mkdir(parents=True, exist_ok=True)

    # ---- posts ----
    posts = []
    for cols, row in iter_table_rows(dump, "posts"):
        p = rowdict(cols, row, POSTS_COLS)
        if p["post_type"] in keep_types and p["post_status"] == "publish":
            posts.append({
                "id": int(p["ID"]),
                "type": p["post_type"],
                "slug": p["post_name"],
                "title": p["post_title"],
                "content": p["post_content"],
                "excerpt": p["post_excerpt"],
                "parent": int(p["post_parent"]) if p["post_parent"] else 0,
                "menu_order": int(p["menu_order"]) if p["menu_order"] else 0,
                "date": p["post_date"],
                "modified": p["post_modified"],
                "guid": p["guid"],
            })
    (outdir / "posts.json").write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- yoast per-URL SEO ----
    yoast = []
    for cols, row in iter_table_rows(dump, "yoast_indexable"):
        y = rowdict(cols, row, YOAST_COLS)
        if y["object_type"] not in ("post", "post-type-archive", "home-page", "term"):
            continue
        yoast.append({
            "object_id": int(y["object_id"]) if y["object_id"] else None,
            "object_type": y["object_type"],
            "object_sub_type": y["object_sub_type"],
            "permalink": y["permalink"],
            "title": y["title"],
            "description": y["description"],
            "canonical": y["canonical"],
            "breadcrumb_title": y["breadcrumb_title"],
            "og_title": y["open_graph_title"],
            "og_description": y["open_graph_description"],
            "og_image": y["open_graph_image"],
            "twitter_title": y["twitter_title"],
            "twitter_description": y["twitter_description"],
            "twitter_image": y["twitter_image"],
            "focus_keyword": y["primary_focus_keyword"],
            "is_noindex": y["is_robots_noindex"],
            "language": y["language"],
        })
    (outdir / "yoast.json").write_text(json.dumps(yoast, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- taxonomy ----
    terms = {}
    for cols, r in iter_table_rows(dump, "terms"):
        t = rowdict(cols, r, ["term_id", "name", "slug", "term_group"])
        terms[int(t["term_id"])] = {"term_id": int(t["term_id"]), "name": t["name"], "slug": t["slug"]}
    taxonomy = {}
    for cols, r in iter_table_rows(dump, "term_taxonomy"):
        tt = rowdict(cols, r, ["term_taxonomy_id", "term_id", "taxonomy", "description", "parent", "count"])
        taxonomy[int(tt["term_taxonomy_id"])] = {
            "term_taxonomy_id": int(tt["term_taxonomy_id"]),
            "term_id": int(tt["term_id"]),
            "taxonomy": tt["taxonomy"],
            "parent": int(tt["parent"]) if tt["parent"] else 0,
            "count": int(tt["count"]) if tt["count"] else 0,
            "term": terms.get(int(tt["term_id"])),
        }
    relationships = defaultdict(list)
    for cols, r in iter_table_rows(dump, "term_relationships"):
        rr = rowdict(cols, r, ["object_id", "term_taxonomy_id", "term_order"])
        relationships[int(rr["object_id"])].append(int(rr["term_taxonomy_id"]))
    (outdir / "taxonomy.json").write_text(json.dumps({
        "taxonomy": list(taxonomy.values()),
        "post_terms": relationships,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- master URL map: join full path + language + translation group + SEO ----
    url_map = build_url_map(posts, yoast)
    (outdir / "url-map.json").write_text(json.dumps(url_map, ensure_ascii=False, indent=2), encoding="utf-8")
    lang_counts = Counter(e["language"] for e in url_map)

    summary = {
        "post_type_status": {f"{t}/{s}": c for (t, s), c in type_status.items()},
        "posts_extracted": len(posts),
        "yoast_rows": len(yoast),
        "terms": len(terms),
        "taxonomies": len(taxonomy),
        "url_map_entries": len(url_map),
        "url_map_by_language": dict(lang_counts),
        "url_map_with_seo": sum(1 for e in url_map if e["seo_title"] or e["seo_description"]),
    }
    (outdir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n== extracted ==")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
