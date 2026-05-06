from datetime import datetime, timezone

from pydantic import BaseModel, Field, validator

from lnbits.db import FilterModel
from lnbits.helpers import is_valid_email_address


class CreateMerchant(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: str
    currency: str = Field(default="GBP", min_length=3, max_length=3)
    onboarding_amount: float = Field(..., gt=0)
    source_wallet_id: str = Field(..., min_length=1)

    @validator("currency")
    def normalize_currency(cls, value: str) -> str:
        return value.upper()

    @validator("email")
    def validate_email(cls, value: str) -> str:
        if not is_valid_email_address(value):
            raise ValueError("Invalid email address.")
        return value


class Merchant(BaseModel):
    id: str
    owner_id: str
    merchant_user_id: str
    merchant_wallet_id: str
    source_wallet_id: str
    tpos_id: str
    base_url: str
    name: str
    email: str
    currency: str
    onboarding_amount: float
    repaid_amount: float = 0.0
    onboarding_completed: bool = False
    initial_email_sent_at: datetime | None = None
    login_email_sent_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MerchantPayment(BaseModel):
    id: str
    merchant_id: str
    payment_hash: str
    sale_amount: float
    payout_amount_sat: int
    payout_payment_hash: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MerchantFilters(FilterModel):
    __search_fields__ = [
        "name",
        "email",
        "currency",
        "merchant_user_id",
        "merchant_wallet_id",
        "source_wallet_id",
        "tpos_id",
    ]

    __sort_fields__ = [
        "name",
        "email",
        "currency",
        "onboarding_amount",
        "repaid_amount",
        "onboarding_completed",
        "created_at",
        "updated_at",
        "completed_at",
    ]

    onboarding_completed: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    completed_at: datetime | None = None
