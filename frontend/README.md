# Frontend — Next.js (App Router)

Public marketing/listings site. Deploys to **Vercel**.

## Setup

```bash
cp .env.example .env.local
npm install
npm run dev        # http://localhost:3000
```

## Notes

- **Security headers** are set in `next.config.mjs`. Extend the (future) CSP
  allowlist as GTM, Meta Pixel, Cloudinary, and analytics domains are added.
- **URL structure must match the legacy WordPress site** wherever possible
  (SEO/Ads). Add unavoidable legacy→new redirects in `next.config.mjs`.
- **GTM/Meta Pixel IDs are reused, not new** — see `.env.example` and CLAUDE.md.
- Listing images are served from Cloudinary (`res.cloudinary.com`), already
  allowlisted in `next.config.mjs`.

## Structure (to be filled in)

```
src/
├─ app/          # App Router routes — mirror legacy URL paths
├─ components/   # shared UI
└─ lib/          # API client, analytics helpers
```
