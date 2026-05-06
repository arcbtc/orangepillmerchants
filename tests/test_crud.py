from uuid import uuid4

import pytest

from orangepillmerchants.crud import (  # type: ignore[import]
    create_merchant,
    create_merchant_payment,
    delete_merchant,
    get_merchant,
    get_merchant_by_tpos_id,
    get_merchant_payment_by_hash,
    get_merchants_paginated,
    update_merchant,
)
from orangepillmerchants.models import CreateMerchant  # type: ignore[import]


@pytest.mark.asyncio
async def test_create_and_get_merchant():
    owner_id = uuid4().hex
    merchant_user_id = uuid4().hex
    merchant_wallet_id = uuid4().hex
    source_wallet_id = uuid4().hex
    tpos_id = uuid4().hex

    merchant = await create_merchant(
        owner_id,
        CreateMerchant(
            name="Corner Shop",
            email="merchant@example.com",
            currency="gbp",
            onboarding_amount=50.0,
            source_wallet_id=source_wallet_id,
        ),
        merchant_user_id=merchant_user_id,
        merchant_wallet_id=merchant_wallet_id,
        tpos_id=tpos_id,
        base_url="https://example.com/",
    )

    stored = await get_merchant(merchant.id)
    assert stored
    assert stored.owner_id == owner_id
    assert stored.currency == "GBP"
    assert stored.tpos_id == tpos_id

    by_tpos = await get_merchant_by_tpos_id(tpos_id)
    assert by_tpos
    assert by_tpos.id == merchant.id

    page = await get_merchants_paginated(owner_id=owner_id)
    assert page.total == 1
    assert page.data[0].id == merchant.id


@pytest.mark.asyncio
async def test_update_merchant_and_record_payment():
    owner_id = uuid4().hex
    merchant = await create_merchant(
        owner_id,
        CreateMerchant(
            name="Bakery",
            email="bakery@example.com",
            currency="EUR",
            onboarding_amount=25.0,
            source_wallet_id=uuid4().hex,
        ),
        merchant_user_id=uuid4().hex,
        merchant_wallet_id=uuid4().hex,
        tpos_id=uuid4().hex,
        base_url="https://example.com/",
    )

    merchant.repaid_amount = 12.5
    await update_merchant(merchant)

    updated = await get_merchant(merchant.id)
    assert updated
    assert updated.repaid_amount == 12.5

    payment = await create_merchant_payment(
        merchant_id=merchant.id,
        payment_hash=uuid4().hex,
        sale_amount=12.5,
        payout_amount_sat=50000,
        payout_payment_hash=uuid4().hex,
    )
    stored_payment = await get_merchant_payment_by_hash(payment.payment_hash)
    assert stored_payment
    assert stored_payment.merchant_id == merchant.id
    assert stored_payment.sale_amount == 12.5

    await delete_merchant(merchant.id)
    assert await get_merchant(merchant.id) is None
