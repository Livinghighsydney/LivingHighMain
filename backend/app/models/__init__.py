"""Tortoise models package.

Referenced as "app.models" in TORTOISE_ORM (app/db.py); every model must be
imported here so Aerich and Tortoise discover them.
"""

from app.models.base import PublishStatus
from app.models.content import (
    Category,
    Listing,
    Locale,
    MediaAsset,
    Page,
    Post,
    Suburb,
)
from app.models.leads import Lead, LeadType
from app.models.system import AdminUser, Redirect

__all__ = [
    "PublishStatus",
    "Locale",
    "Suburb",
    "Category",
    "MediaAsset",
    "Listing",
    "Page",
    "Post",
    "Lead",
    "LeadType",
    "AdminUser",
    "Redirect",
]
