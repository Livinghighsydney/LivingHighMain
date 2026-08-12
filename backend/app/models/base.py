from enum import Enum

from tortoise import fields
from tortoise.models import Model


class PublishStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class TimestampedModel(Model):
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True


class ContentBase(TimestampedModel):
    """Shared columns for every URL-addressable content type.

    - ``path`` is the exact legacy URL path and is UNIQUE — this is how we
      guarantee the old WordPress URLs survive (CLAUDE.md's #1 SEO
      non-negotiable), rather than relying on slug/parent mechanics.
    - ``translation_group`` links the en/es/zh versions of the same content
      (the site has no translation plugin — languages are independent page
      trees under /es and /zh path prefixes).
    - SEO fields carry the Yoast title/description/canonical over per URL.
    """

    translation_group = fields.UUIDField(index=True)
    path = fields.CharField(max_length=512, unique=True)
    title = fields.CharField(max_length=255)
    body = fields.TextField(null=True)
    status = fields.CharEnumField(
        PublishStatus, max_length=16, default=PublishStatus.PUBLISHED
    )

    seo_title = fields.CharField(max_length=255, null=True)
    seo_description = fields.TextField(null=True)
    canonical_url = fields.CharField(max_length=512, null=True)
    og_image_url = fields.CharField(max_length=512, null=True)

    class Meta:
        abstract = True
