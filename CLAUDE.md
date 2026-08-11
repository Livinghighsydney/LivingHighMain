# Living High — Website Revamp (React + FastAPI)

## What this is

A full rebuild of the Living High marketing/listings website (livinghigh.com.au),
currently WordPress + Elementor + WooCommerce, hosted on Verpex. Built by Alter
Technologies. This is a **separate effort from the Living High KB** ("Living
High Brain") project, though the two may share infrastructure and eventually
merge listing data — see "Relationship to the KB" below.

Current site is public-facing (leads, SEO traffic, Google Ads). This is not
an internal tool — unlike the KB dashboard, this site is meant for the public.

## Why we're rebuilding

Redesign started as a WordPress theme/staging swap, then scope expanded to a
full platform rebuild, fully off WordPress, onto **React (Next.js) + FastAPI**
— matching the stack already used by the KB project. Reasoning: shared team
stack knowledge, potential to unify listing data with the KB's `Building` page
model, more control than WordPress/Elementor allows long-term.

## Critical finding: there is no payment/booking system to migrate

Checked the live site directly (2026-08). Confirmed:
- "Check Availability" buttons are `wa.me` links (WhatsApp deep links with a
  pre-filled message) — not a booking flow.
- "Enquire Now" opens a lead-capture popup (name, phone, budget, suburb,
  move-in date, gender) — submits an enquiry, not a payment.
- A separate plain contact form exists (name, email, subject, message).
- FAQ on the live site states members pay via bank transfer, off-platform,
  after a human conversation.

**Implication:** no Stripe/PCI/booking-calendar engine needs to be built.
The real conversion flow to preserve is **listing page → lead form or
WhatsApp click → human follow-up**. Confirm with Derek whether WooCommerce
Bookings is doing anything real behind the scenes (e.g. internal inventory)
before assuming it's fully decorative.

## What must carry over exactly (non-negotiable)

- **URL structure** — preserve existing paths (e.g.
  `/studio-apartment-sydney/co-living-space-bondibeach/`) wherever possible.
  This is the single biggest lever for avoiding SEO/Ads damage — prefer
  matching old URLs over building 301 redirects for everything.
- **Meta Pixel** (`id=2502462696653746`) and **GTM container**
  (`GTM-T4NPBPPZ`) — reuse the same IDs, don't create new ones, or
  remarketing audiences and conversion history reset.
- **Google Ads landing page URLs** — check every active campaign's Final
  URL / Sitelink URLs before cutover; never let an ad point to a URL that
  404s.
- **Listing content & images** — all current room types, pricing, location
  pages, and photos.
- **WhatsApp numbers** — `+61478555218` (availability), `+61485936012`
  (general), WeChat `+61488883066`, plus the WhatsApp Channel link for
  room alerts.

## Infrastructure

- **Domain registrar:** GoDaddy — currently on GoDaddy's own default
  nameservers (`ns05`/`ns06.domaincontrol.com`), i.e. GoDaddy manages DNS
  directly. Not delegated to Verpex.
- **Current hosting:** Verpex (cPanel), live server `192.250.233.29`.
- **Existing DNS records of note:** `api` CNAME → Railway (KB backend),
  `kb` CNAME → Vercel (KB frontend). These belong to the separate KB
  project — don't touch during this rebuild.
- **Target hosting (proposed):** Vercel (Next.js frontend) + Railway
  (FastAPI backend), matching the KB stack. This is a real domain
  cutover (not a same-server folder swap), so DNS propagation delay
  applies — plan accordingly.
- **Any new subdomain (e.g. `test.livinghigh.com.au`) needs a manual A/CNAME
  record added in GoDaddy** — creating it in a host's control panel alone is
  not sufficient here, unlike setups where nameservers are delegated.

## Migration approach

- **Do not migrate the raw WordPress MySQL database.** It's structured
  around WordPress's internal model (`wp_posts`, `wp_postmeta`, shortcodes)
  and isn't portable to a FastAPI/Postgres schema.
- **Export content via the WP REST API** (`/wp-json/wp/v2/...`, plus
  `/wp-json/wc/v3/products` for WooCommerce listings — requires WooCommerce
  REST API keys) as structured JSON, then write a one-time migration script
  to load it into the new schema.
- **Images/videos:** download the full `wp-content/uploads` folder, bulk
  upload to Cloudinary (same pattern already used for the KB's Papyrs
  migration), and build an old-URL → new-Cloudinary-URL mapping. Rewrite
  every image reference in migrated content using that mapping.
- **Embedded videos** (YouTube/Vimeo) need no migration — they're just URLs
  in content. Only self-hosted video files go through the Cloudinary step.
- Keep a full cold backup (uploads .zip + DB .sql export) stored off-server,
  independent of the migration itself.

## Staging & rollout plan

1. Build on a staging subdomain (`test.livinghigh.com.au`) while the current
   WordPress site stays live and untouched.
2. Password-protect / IP-restrict the staging subdomain — don't leave it
   open to bots while incomplete.
3. Run penetration testing and load testing against staging only, never
   production.
4. Before cutover: full URL inventory + redirect map for anything that
   can't preserve its exact old path; verify GTM/Pixel events fire
   correctly (GA4 DebugView / Ads Tag Assistant) on staging.
5. Cutover = DNS repoint in GoDaddy (main domain → new hosting), done in a
   low-traffic window.
6. Submit updated sitemap to Search Console immediately after cutover;
   monitor Coverage/crawl errors daily for the first couple weeks.
7. Keep the old WordPress/Verpex hosting running, de-indexed, for a few
   weeks post-cutover as a fallback before fully archiving.

## Security requirements (build in from the start, not after)

- Rate limiting on FastAPI endpoints (especially forms/login) — e.g. slowapi.
- CORS locked to the actual frontend domain, not wildcard.
- HTTPS + HSTS everywhere; standard security headers (CSP, X-Frame-Options,
  X-Content-Type-Options).
- Server-side input validation/sanitization on all form submissions.
- Secrets (API keys, DB credentials) in Railway/Vercel env vars only —
  never committed to the repo.
- 2FA for any staff/admin login the new backend introduces.
- Cloudflare (or similar) in front of the domain for DDoS/WAF/bot filtering.
- Automated daily Postgres backups, separate from manual migration backups.
- Error monitoring (e.g. Sentry).

## Relationship to the KB project

- The KB backend currently treats WordPress as an ongoing, one-way,
  read-only content source (WP REST API sync). Once WordPress is retired,
  that sync job has nothing to pull from.
- Open decision: does the new site's FastAPI backend become a new source
  feeding the KB, and does the KB's `Building` page model merge with this
  site's listing/property model (same address/bedrooms/bathrooms shape)?
  Worth deciding deliberately rather than defaulting into two parallel
  records of the same property data.
- Chat widget integration is explicitly **out of scope until the KB and its
  embeddings are ready** — the redesigned site should be built without
  assuming the widget yet, but shouldn't block adding it later (single
  script tag, no theme dependency).

## Explicitly out of scope for now

- Real payment/checkout system (Stripe or otherwise) — current flow is
  lead-capture → WhatsApp/human → manual bank transfer.
- Booking/availability calendar engine.
- Chat widget embedding (waiting on KB completion).
- Owner-facing portal or access.

## Open questions to resolve, not blocking but don't guess silently

- Is WooCommerce Bookings doing anything functionally real (internal
  inventory tracking, etc.) or is it decorative relative to the actual
  WhatsApp-driven conversion flow?
- Final call on Next.js vs. another SSR approach for the frontend.
- Whether listing/property data lives in the same Postgres instance as the
  KB or a separate database.
- Exact cutover date/window, coordinated with Google Ads campaign activity.
