from http import HTTPStatus

from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException

from lnbits.core.crud import get_wallet, get_wallets
from lnbits.core.models import SimpleStatus
from lnbits.core.models.users import Account
from lnbits.db import Filters, Page
from lnbits.decorators import check_super_user, parse_filters
from lnbits.helpers import generate_filter_params_openapi

from .crud import delete_merchant, get_merchant, get_merchants_paginated
from .models import CreateMerchant, Merchant, MerchantFilters
from .services import create_onboarding_merchant, resend_merchant_email

orangepillmerchants_api_router = APIRouter(
    prefix="/api/v1", tags=["orangepillmerchants"]
)
merchant_filters = parse_filters(MerchantFilters)


@orangepillmerchants_api_router.get("/wallets")
async def api_get_superuser_wallets(account: Account = Depends(check_super_user)) -> list[dict]:
    wallets = await get_wallets(account.id)
    return [{"id": wallet.id, "name": wallet.name} for wallet in wallets]


@orangepillmerchants_api_router.post("/merchants", status_code=HTTPStatus.CREATED)
async def api_create_merchant(
    data: CreateMerchant,
    request: Request,
    account: Account = Depends(check_super_user),
) -> Merchant:
    wallet = await get_wallet(data.source_wallet_id)
    if not wallet or wallet.user != account.id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Selected recoup wallet does not belong to the super user.",
        )
    try:
        return await create_onboarding_merchant(account.id, data, str(request.base_url))
    except ValueError as exc:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(exc)) from exc


@orangepillmerchants_api_router.get(
    "/merchants/paginated",
    response_model=Page[Merchant],
    openapi_extra=generate_filter_params_openapi(MerchantFilters),
)
async def api_get_merchants_paginated(
    filters: Filters = Depends(merchant_filters),
    account: Account = Depends(check_super_user),
) -> Page[Merchant]:
    return await get_merchants_paginated(owner_id=account.id, filters=filters)


@orangepillmerchants_api_router.get(
    "/merchants/{merchant_id}", response_model=Merchant
)
async def api_get_merchant(merchant_id: str, account: Account = Depends(check_super_user)) -> Merchant:
    merchant = await get_merchant(merchant_id)
    if not merchant or merchant.owner_id != account.id:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Merchant not found.")
    return merchant


@orangepillmerchants_api_router.post(
    "/merchants/{merchant_id}/resend", response_model=Merchant
)
async def api_resend_merchant_email(
    merchant_id: str, account: Account = Depends(check_super_user)
) -> Merchant:
    merchant = await get_merchant(merchant_id)
    if not merchant or merchant.owner_id != account.id:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Merchant not found.")
    try:
        return await resend_merchant_email(merchant_id)
    except ValueError as exc:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(exc)) from exc


@orangepillmerchants_api_router.delete(
    "/merchants/{merchant_id}", response_model=SimpleStatus
)
async def api_delete_merchant(merchant_id: str, account: Account = Depends(check_super_user)) -> SimpleStatus:
    merchant = await get_merchant(merchant_id)
    if not merchant or merchant.owner_id != account.id:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Merchant not found.")

    await delete_merchant(merchant_id)
    return SimpleStatus(success=True, message="Merchant deleted.")
