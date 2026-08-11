# Docs

Project reference lives in the root [`CLAUDE.md`](../CLAUDE.md) — the source of
truth for the brief, non-negotiables, migration approach, staging/rollout plan,
and security requirements.

Use this folder for working notes as they get produced, e.g.:

- **URL inventory + redirect map** — every legacy WordPress path and its new
  home (or 301 target). Critical before cutover (SEO/Ads).
- **Migration runbook** — WP REST API export → new schema, Cloudinary image
  upload, old→new URL mapping.
- **Cutover checklist** — GTM/Pixel verification, sitemap resubmission, DNS
  repoint in GoDaddy, fallback plan.
