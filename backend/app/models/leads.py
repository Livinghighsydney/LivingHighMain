from enum import Enum

from tortoise import fields

from app.models.base import TimestampedModel


class LeadType(str, Enum):
    ENQUIRY = "enquiry"  # "Enquire Now" popup: name/phone/budget/suburb/move-in/gender
    CONTACT = "contact"  # plain contact form: name/email/subject/message


class Lead(TimestampedModel):
    """Single home for the real conversion flow: listing -> lead -> human.

    Replaces the scattered Elementor / WPForms / Chaty capture on the old site.
    """

    type = fields.CharEnumField(LeadType, max_length=16, default=LeadType.ENQUIRY)
    name = fields.CharField(max_length=160)
    email = fields.CharField(max_length=255, null=True)
    phone = fields.CharField(max_length=40, null=True)
    budget = fields.CharField(max_length=60, null=True)
    suburb = fields.CharField(max_length=120, null=True)
    move_in_date = fields.DateField(null=True)
    gender = fields.CharField(max_length=20, null=True)
    message = fields.TextField(null=True)

    source_listing = fields.ForeignKeyField(
        "models.Listing", related_name="leads", null=True, on_delete=fields.SET_NULL
    )
    source_path = fields.CharField(max_length=512, null=True)
    locale = fields.CharField(max_length=5, default="en")

    ip_address = fields.CharField(max_length=45, null=True)
    user_agent = fields.CharField(max_length=512, null=True)
    status = fields.CharField(max_length=20, default="new")

    class Meta:
        table = "leads"
