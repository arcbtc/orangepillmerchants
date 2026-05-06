from datetime import datetime, timezone

from lnbits.db import Database, Filters, Page
from lnbits.helpers import urlsafe_short_hash

from .models import CreateMerchant, Merchant, MerchantFilters, MerchantPayment

db = Database("ext_orangepillmerchant")


async def create_merchant(owner_id: str, data: CreateMerchant, **kwargs) -> Merchant:
    merchant = Merchant(
        id=urlsafe_short_hash(),
        owner_id=owner_id,
        name=data.name,
        email=data.email,
        currency=data.currency,
        onboarding_amount=data.onboarding_amount,
        source_wallet_id=data.source_wallet_id,
        **kwargs,
    )
    await db.insert("orangepillmerchant.merchants", merchant)
    return merchant


async def get_merchant(merchant_id: str) -> Merchant | None:
    return await db.fetchone(
        "SELECT * FROM orangepillmerchant.merchants WHERE id = :id",
        {"id": merchant_id},
        Merchant,
    )


async def get_merchant_by_tpos_id(tpos_id: str) -> Merchant | None:
    return await db.fetchone(
        "SELECT * FROM orangepillmerchant.merchants WHERE tpos_id = :tpos_id",
        {"tpos_id": tpos_id},
        Merchant,
    )


async def get_merchants_paginated(
    owner_id: str | None = None,
    filters: Filters[MerchantFilters] | None = None,
) -> Page[Merchant]:
    where = []
    values = {}
    if owner_id:
        where.append("owner_id = :owner_id")
        values["owner_id"] = owner_id

    return await db.fetch_page(
        "SELECT * FROM orangepillmerchant.merchants",
        where=where,
        values=values,
        filters=filters,
        model=Merchant,
    )


async def update_merchant(merchant: Merchant) -> Merchant:
    merchant.updated_at = datetime.now(timezone.utc)
    await db.update("orangepillmerchant.merchants", merchant)
    return merchant


async def delete_merchant(merchant_id: str) -> None:
    await db.execute(
        "DELETE FROM orangepillmerchant.merchant_payments WHERE merchant_id = :merchant_id",
        {"merchant_id": merchant_id},
    )
    await db.execute(
        "DELETE FROM orangepillmerchant.merchants WHERE id = :id",
        {"id": merchant_id},
    )


async def create_merchant_payment(
    merchant_id: str,
    payment_hash: str,
    sale_amount: float,
    payout_amount_sat: int,
    payout_payment_hash: str | None = None,
) -> MerchantPayment:
    merchant_payment = MerchantPayment(
        id=urlsafe_short_hash(),
        merchant_id=merchant_id,
        payment_hash=payment_hash,
        sale_amount=sale_amount,
        payout_amount_sat=payout_amount_sat,
        payout_payment_hash=payout_payment_hash,
    )
    await db.insert("orangepillmerchant.merchant_payments", merchant_payment)
    return merchant_payment


async def get_merchant_payment_by_hash(payment_hash: str) -> MerchantPayment | None:
    return await db.fetchone(
        """
        SELECT * FROM orangepillmerchant.merchant_payments
        WHERE payment_hash = :payment_hash
        """,
        {"payment_hash": payment_hash},
        MerchantPayment,
    )
