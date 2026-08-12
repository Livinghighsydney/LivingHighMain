from tortoise import fields
from tortoise.models import Model

from app.models.base import ContentBase, TimestampedModel


class Locale(Model):
    """Supported languages. Reproduces the trilingual URL sets (en / es / zh)."""

    code = fields.CharField(pk=True, max_length=5)  # 'en', 'es', 'zh'
    name = fields.CharField(max_length=50)
    path_prefix = fields.CharField(max_length=10, default="")  # '', '/es', '/zh'

    class Meta:
        table = "locales"


class Suburb(Model):
    slug = fields.CharField(max_length=120, unique=True)
    name = fields.CharField(max_length=120)
    region = fields.CharField(max_length=120, null=True)

    class Meta:
        table = "suburbs"


class Category(Model):
    slug = fields.CharField(max_length=160, unique=True)
    name = fields.CharField(max_length=160)

    class Meta:
        table = "categories"


class MediaAsset(TimestampedModel):
    """Old WordPress upload URL -> Cloudinary URL map.

    Drives image-reference rewriting during content migration (CLAUDE.md).
    """

    original_wp_url = fields.CharField(max_length=512, unique=True)
    cloudinary_public_id = fields.CharField(max_length=255, null=True)
    cloudinary_url = fields.CharField(max_length=512, null=True)
    alt = fields.CharField(max_length=255, null=True)
    width = fields.IntField(null=True)
    height = fields.IntField(null=True)
    mime_type = fields.CharField(max_length=100, null=True)

    class Meta:
        table = "media_assets"


class Listing(ContentBase):
    """A co-living / room listing (was a hierarchical Elementor WP page under
    /studio-apartment-sydney/...). Shape aligns with the KB's Building model."""

    locale = fields.ForeignKeyField("models.Locale", related_name="listings")
    suburb = fields.ForeignKeyField(
        "models.Suburb", related_name="listings", null=True
    )
    subtitle = fields.CharField(max_length=255, null=True)
    room_type = fields.CharField(max_length=120, null=True)
    price_amount = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    price_period = fields.CharField(max_length=20, null=True)  # 'week' | 'month'
    bedrooms = fields.IntField(null=True)
    bathrooms = fields.IntField(null=True)
    address = fields.CharField(max_length=255, null=True)
    latitude = fields.FloatField(null=True)
    longitude = fields.FloatField(null=True)
    whatsapp_url = fields.CharField(max_length=512, null=True)

    class Meta:
        table = "listings"


class Page(ContentBase):
    """A static / marketing page (home, contact, property-management, etc.)."""

    locale = fields.ForeignKeyField("models.Locale", related_name="pages")

    class Meta:
        table = "pages"


class Post(ContentBase):
    """A blog post (82 in the legacy site — organic SEO traffic)."""

    locale = fields.ForeignKeyField("models.Locale", related_name="posts")
    category = fields.ForeignKeyField(
        "models.Category", related_name="posts", null=True
    )
    excerpt = fields.TextField(null=True)
    published_at = fields.DatetimeField(null=True)

    class Meta:
        table = "posts"
