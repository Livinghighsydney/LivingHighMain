from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "admin_users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password_hash" VARCHAR(255) NOT NULL,
    "full_name" VARCHAR(160),
    "role" VARCHAR(40) NOT NULL  DEFAULT 'staff',
    "totp_secret" VARCHAR(64),
    "is_active" BOOL NOT NULL  DEFAULT True,
    "last_login_at" TIMESTAMPTZ
);
COMMENT ON TABLE "admin_users" IS 'Staff/admin login for the new backend. 2FA via TOTP (CLAUDE.md).';
CREATE TABLE IF NOT EXISTS "categories" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "slug" VARCHAR(160) NOT NULL UNIQUE,
    "name" VARCHAR(160) NOT NULL
);
CREATE TABLE IF NOT EXISTS "locales" (
    "code" VARCHAR(5) NOT NULL  PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL,
    "path_prefix" VARCHAR(10) NOT NULL  DEFAULT ''
);
COMMENT ON TABLE "locales" IS 'Supported languages. Reproduces the trilingual URL sets (en / es / zh).';
CREATE TABLE IF NOT EXISTS "media_assets" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "original_wp_url" VARCHAR(512) NOT NULL UNIQUE,
    "cloudinary_public_id" VARCHAR(255),
    "cloudinary_url" VARCHAR(512),
    "alt" VARCHAR(255),
    "width" INT,
    "height" INT,
    "mime_type" VARCHAR(100)
);
COMMENT ON TABLE "media_assets" IS 'Old WordPress upload URL -> Cloudinary URL map.';
CREATE TABLE IF NOT EXISTS "pages" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "translation_group" UUID NOT NULL,
    "path" VARCHAR(512) NOT NULL UNIQUE,
    "title" VARCHAR(255) NOT NULL,
    "body" TEXT,
    "status" VARCHAR(16) NOT NULL  DEFAULT 'published',
    "seo_title" VARCHAR(255),
    "seo_description" TEXT,
    "canonical_url" VARCHAR(512),
    "og_image_url" VARCHAR(512),
    "locale_id" VARCHAR(5) NOT NULL REFERENCES "locales" ("code") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_pages_transla_2c3db5" ON "pages" ("translation_group");
COMMENT ON COLUMN "pages"."status" IS 'DRAFT: draft\nPUBLISHED: published';
COMMENT ON TABLE "pages" IS 'A static / marketing page (home, contact, property-management, etc.).';
CREATE TABLE IF NOT EXISTS "posts" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "translation_group" UUID NOT NULL,
    "path" VARCHAR(512) NOT NULL UNIQUE,
    "title" VARCHAR(255) NOT NULL,
    "body" TEXT,
    "status" VARCHAR(16) NOT NULL  DEFAULT 'published',
    "seo_title" VARCHAR(255),
    "seo_description" TEXT,
    "canonical_url" VARCHAR(512),
    "og_image_url" VARCHAR(512),
    "excerpt" TEXT,
    "published_at" TIMESTAMPTZ,
    "category_id" INT REFERENCES "categories" ("id") ON DELETE CASCADE,
    "locale_id" VARCHAR(5) NOT NULL REFERENCES "locales" ("code") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_posts_transla_06ed65" ON "posts" ("translation_group");
COMMENT ON COLUMN "posts"."status" IS 'DRAFT: draft\nPUBLISHED: published';
COMMENT ON TABLE "posts" IS 'A blog post (82 in the legacy site — organic SEO traffic).';
CREATE TABLE IF NOT EXISTS "redirects" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "source_path" VARCHAR(512) NOT NULL UNIQUE,
    "target_path" VARCHAR(512) NOT NULL,
    "status_code" INT NOT NULL  DEFAULT 301,
    "note" VARCHAR(255),
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE "redirects" IS 'Legacy URL -> new URL map for paths that can''t keep their exact old path.';
CREATE TABLE IF NOT EXISTS "suburbs" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "slug" VARCHAR(120) NOT NULL UNIQUE,
    "name" VARCHAR(120) NOT NULL,
    "region" VARCHAR(120)
);
CREATE TABLE IF NOT EXISTS "listings" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "translation_group" UUID NOT NULL,
    "path" VARCHAR(512) NOT NULL UNIQUE,
    "title" VARCHAR(255) NOT NULL,
    "body" TEXT,
    "status" VARCHAR(16) NOT NULL  DEFAULT 'published',
    "seo_title" VARCHAR(255),
    "seo_description" TEXT,
    "canonical_url" VARCHAR(512),
    "og_image_url" VARCHAR(512),
    "subtitle" VARCHAR(255),
    "room_type" VARCHAR(120),
    "price_amount" DECIMAL(10,2),
    "price_period" VARCHAR(20),
    "bedrooms" INT,
    "bathrooms" INT,
    "address" VARCHAR(255),
    "latitude" DOUBLE PRECISION,
    "longitude" DOUBLE PRECISION,
    "whatsapp_url" VARCHAR(512),
    "locale_id" VARCHAR(5) NOT NULL REFERENCES "locales" ("code") ON DELETE CASCADE,
    "suburb_id" INT REFERENCES "suburbs" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_listings_transla_74beb1" ON "listings" ("translation_group");
COMMENT ON COLUMN "listings"."status" IS 'DRAFT: draft\nPUBLISHED: published';
COMMENT ON TABLE "listings" IS 'A co-living / room listing (was a hierarchical Elementor WP page under';
CREATE TABLE IF NOT EXISTS "leads" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "type" VARCHAR(16) NOT NULL  DEFAULT 'enquiry',
    "name" VARCHAR(160) NOT NULL,
    "email" VARCHAR(255),
    "phone" VARCHAR(40),
    "budget" VARCHAR(60),
    "suburb" VARCHAR(120),
    "move_in_date" DATE,
    "gender" VARCHAR(20),
    "message" TEXT,
    "source_path" VARCHAR(512),
    "locale" VARCHAR(5) NOT NULL  DEFAULT 'en',
    "ip_address" VARCHAR(45),
    "user_agent" VARCHAR(512),
    "status" VARCHAR(20) NOT NULL  DEFAULT 'new',
    "source_listing_id" INT REFERENCES "listings" ("id") ON DELETE SET NULL
);
COMMENT ON COLUMN "leads"."type" IS 'ENQUIRY: enquiry\nCONTACT: contact';
COMMENT ON TABLE "leads" IS 'Single home for the real conversion flow: listing -> lead -> human.';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
