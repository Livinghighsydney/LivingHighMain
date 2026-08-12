# URL Inventory — livinghigh.com.au (legacy WordPress)

Auto-generated from the public Yoast sitemaps + robots.txt on **2026-08-11**.
This is the SEO backbone: **new site must preserve these exact paths** (CLAUDE.md
non-negotiable). Counts below are from the sitemap; still to be reconciled against
Google Ads Final URLs and Search Console before cutover.

Source of truth: `https://livinghigh.com.au/sitemap_index.xml` (Yoast SEO).
Sub-sitemaps: `page-sitemap.xml`, `post-sitemap.xml`, `category-sitemap.xml`,
`product-sitemap.xml`, `author-sitemap.xml`.

## Key structural findings

1. **The real "listings" are WordPress PAGES, not WooCommerce products.**
   Listing/location pages live at:
   `/studio-apartment-sydney/co-living-space-{suburb}/` (21 suburbs, English).
   The `product-sitemap.xml` contains only **`/all-rooms/`** — so WooCommerce is
   essentially not producing indexed per-listing URLs. This reinforces the
   CLAUDE.md open question: WooCommerce looks close to decorative for SEO/URLs.
   Confirm with Derek before assuming.

2. **The site is MULTILINGUAL** — Spanish (`/es/`) and Chinese (`/zh/`) variants
   mirror the English pages with localized slugs. Note the slug differs by
   language for listings:
   - EN: `/studio-apartment-sydney/co-living-space-{suburb}/`
   - ES/ZH: `/{lang}/studio-apartment-sydney/accommodation-{suburb}/`
   This means the new frontend needs an i18n/routing strategy that reproduces
   all three URL sets exactly. (Likely WPML or Polylang on the WP side —
   confirm which.)

3. **Large blog footprint (82 posts)** — mostly student/lifestyle SEO content.
   These drive organic traffic; every one must keep its path.

4. **WooCommerce/membership functional pages exist** (`/checkout/`, `/my-account/`,
   `/membership-*`, `/room-booking/`). Under the new lead-capture-only model these
   may not be rebuilt as-is — but each needs a decision: rebuild, redirect, or
   retire. Don't silently 404 any that Ads or SEO point to.

---

## Listings — English (21) — `/studio-apartment-sydney/co-living-space-{suburb}/`

bondibeach, bondi-junction, chippendale, darling-harbour, darlinghurst,
darlington, enmore, glebe, haymarket-chinatown, kensington, kingsford,
millers-point, newtown, paddington, petersham, potts-point-kings-cross,
redfern, rosebery, stanmore, surry-hills
(plus the hub page `/studio-apartment-sydney/` and `/all-rooms/`)

## Listings — Spanish `/es/studio-apartment-sydney/accommodation-{suburb}/` and Chinese `/zh/...`

Both languages cover the same suburb set (accommodation-* slug), plus
`/es/` and `/zh/` home, `/es/contact/`, `/zh/contact/`,
`/es|zh/property-management-services/`, `/es/testimonios/`.

## Core / marketing pages (English)

/ , /studio-apartment-sydney/ , /all-rooms/ , /co-living-operators/ ,
/property? , /contact/ , /whatsapp/ , /testimonials/ , /blog/ ,
/privacy-policy/ , /thank-you/ ,
/top-10-suburbs-for-students-and-young-professionals/ ,
/move-in-ready-fully-furnished-room-with-bills-included/ ,
/discover-sydney-like-a-local/ , /stay-connected/ ,
/sydney-room-listings-every-monday/

## WooCommerce / membership functional pages (decide: rebuild / redirect / retire)

/checkout/ , /my-account/ , /room-booking/ ,
/membership-join/ , /membership-join/membership-registration/ ,
/membership-login/ , /membership-login/membership-profile/ ,
/membership-login/password-reset/

## Category / product sitemaps

- category-sitemap.xml → /affordable-living-sydney/
- product-sitemap.xml → /all-rooms/

## Blog posts (82) — post-sitemap.xml

fitness-gyms, grocery-shopping-sydney, american-moving-to-australia,
cheap-eats-sydney, public-transport-sydney, sydney-ocean-pools,
best-music-for-studying, making-friends-in-sydney,
student-visa-expiry-date-australia, australia-pr-process, how-to-write-a-resume,
students-accommodation, shopping-malls-in-sydney,
student-visa-process-in-australia, best-cafes-in-sydney,
no-fee-bank-accounts-australia, shared-accommodation, best-spa-in-sydney,
ferry-trips-in-sydney, australian-healthcare, graduation-opportunities,
restaurants-with-a-view, best-mobile-plans-for-students, best-salon-in-sydney,
best-side-hustles, best-affordable-fashion-brands, dating-apps-australia,
debit-vs-credit-card, best-android-phones, uni-textbooks, prepaid-vs-postpaid,
cost-of-living-for-students-in-australia, best-wine-shop-sydney,
hairstyles-by-face-shape, pr-application, gym-outfits, best-nightclubs-in-sydney,
law-school, best-apps-for-students, student-support, student-housing,
working-in-australia-on-a-student-visa, best-cinemas,
student-discounts-in-australia, weekend-escapes-sydney, best-museums-sydney,
sydney-opera-house, things-to-do-in-sydney, part-time-jobs, asian-food,
best-views-in-sydney, best-chinese-food-insydney,
affordable-universities-in-australia, best-banks-in-ustralia,
best-karaoke-in-sydney, study-tips, best-budget-tech, aussie-foods,
cheapest-gyms-in-sydney, student-jobs-sydney, best-libraries-in-sydney,
romantic-restaurants-sydney, top-5-study-spots-sydney, australian-culture,
language-exchange-sydney, aussie-culture,
top-suburbs-for-international-students-sydney, cheap-sim-cards-australia,
opal-card, australias-healthcare-system, best-haircuts-for-men,
festivals-in-sydney, study-in-sydney,
a-students-guide-to-thriving-and-not-starving-in-sydney-smart-budget-hacks,
best-part-time-jobs-sydney-college-students,
student-moving-checklist-sydney-guide,
guide-for-foreign-students-making-friends-sydney

> Note two apparent typos in live slugs — `best-chinese-food-insydney` and
> `best-banks-in-ustralia`. Preserve them exactly as-is (they're the indexed
> URLs); do not "fix" the spelling or you break the existing SEO/links.

## Approx totals

- Pages: 95 (incl. ES/ZH) · Posts: 82 · Category: 1 · Product: 1
- **~179 indexed URLs** (author-sitemap not yet pulled — low priority, usually
  author archives). Reconcile with Ads Final URLs + Search Console before cutover.
