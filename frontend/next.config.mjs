/** @type {import('next').NextConfig} */

// Security headers — applied to every route. See CLAUDE.md "Security requirements".
// CSP is intentionally conservative here; extend the allowlists as GTM/Meta Pixel,
// Cloudinary, and any analytics domains are wired in (don't loosen to unsafe-* blindly).
const securityHeaders = [
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload',
  },
  { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
];

const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,

  images: {
    // Listing images migrate to Cloudinary (see CLAUDE.md migration approach).
    remotePatterns: [
      { protocol: 'https', hostname: 'res.cloudinary.com' },
    ],
  },

  async headers() {
    return [{ source: '/:path*', headers: securityHeaders }];
  },

  // URL preservation is critical for SEO/Ads (CLAUDE.md non-negotiables).
  // Add legacy → new path redirects here for anything that can't keep its exact
  // old path. Prefer matching old URLs over redirecting.
  async redirects() {
    return [];
  },
};

export default nextConfig;
