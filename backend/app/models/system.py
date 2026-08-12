from tortoise import fields
from tortoise.models import Model

from app.models.base import TimestampedModel


class Redirect(Model):
    """Legacy URL -> new URL map for paths that can't keep their exact old path.

    Feeds the Next.js redirects() config. Prefer preserving the original path
    over adding a redirect (CLAUDE.md).
    """

    source_path = fields.CharField(max_length=512, unique=True)
    target_path = fields.CharField(max_length=512)
    status_code = fields.IntField(default=301)
    note = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "redirects"


class AdminUser(TimestampedModel):
    """Staff/admin login for the new backend. 2FA via TOTP (CLAUDE.md)."""

    email = fields.CharField(max_length=255, unique=True)
    password_hash = fields.CharField(max_length=255)
    full_name = fields.CharField(max_length=160, null=True)
    role = fields.CharField(max_length=40, default="staff")
    totp_secret = fields.CharField(max_length=64, null=True)
    is_active = fields.BooleanField(default=True)
    last_login_at = fields.DatetimeField(null=True)

    class Meta:
        table = "admin_users"
