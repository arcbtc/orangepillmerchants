from datetime import datetime, timezone
from uuid import uuid4

from loguru import logger

from lnbits.core.models import Account
from lnbits.core.models.users import UserExtra, UserNotifications
from lnbits.core.services import create_invoice, create_user_account_no_ckeck, pay_invoice
from lnbits.core.services.notifications import send_email_notification
from lnbits.extensions.tpos.crud import create_tpos
from lnbits.extensions.tpos.models import CreateTposData

from .crud import (
    create_merchant,
    create_merchant_payment,
    get_merchant,
    get_merchant_by_tpos_id,
    get_merchant_payment_by_hash,
    update_merchant,
)
from .helpers import build_absolute_url, round_money
from .models import CreateMerchant, Merchant


def _merchant_extra(name: str, email: str) -> UserExtra:
    return UserExtra(
        first_name=name,
        display_name=name,
        email_verified=True,
        notifications=UserNotifications(email_address=email),
    )


def _tpos_link(base_url: str, tpos_id: str) -> str:
    return build_absolute_url(base_url, f"/tpos/{tpos_id}")


def _wallet_link(base_url: str, merchant_user_id: str) -> str:
    return build_absolute_url(base_url, f"/wallet?usr={merchant_user_id}")


def _compose_initial_email(merchant: Merchant) -> str:
    return "\n".join(
        [
            f"Hello {merchant.name},",
            "",
            "Your LNbits point of sale is ready.",
            f"Open your public TPoS page here: {_tpos_link(merchant.base_url, merchant.tpos_id)}",
            "",
            "Use this page to start taking payments.",
        ]
    )


def _compose_login_email(merchant: Merchant) -> str:
    return "\n".join(
        [
            f"Hello {merchant.name},",
            "",
            "Your onboarding balance has now been fully repaid through your TPoS sales.",
            f"Login to your LNbits account here: {_wallet_link(merchant.base_url, merchant.merchant_user_id)}",
            f"Your user ID is: {merchant.merchant_user_id}",
            "",
            "After you log in, please open your account settings and set a password.",
            f"Your TPoS public page remains available here: {_tpos_link(merchant.base_url, merchant.tpos_id)}",
        ]
    )


async def send_initial_tpos_email(merchant: Merchant) -> None:
    response = await send_email_notification(
        [merchant.email],
        _compose_initial_email(merchant),
        subject="Your LNbits TPoS link",
    )
    if response.get("status") != "ok":
        raise ValueError(response.get("message") or "Could not send initial email.")


async def send_login_email(merchant: Merchant) -> None:
    response = await send_email_notification(
        [merchant.email],
        _compose_login_email(merchant),
        subject="Your LNbits account is ready",
    )
    if response.get("status") != "ok":
        raise ValueError(response.get("message") or "Could not send login email.")


async def create_onboarding_merchant(owner_id: str, data: CreateMerchant, base_url: str) -> Merchant:
    merchant_account = Account(
        id=uuid4().hex,
        email=data.email,
        extra=_merchant_extra(data.name, data.email),
    )
    merchant_user = await create_user_account_no_ckeck(
        merchant_account,
        wallet_name=data.name,
        default_exts=["tpos"],
    )
    merchant_wallet = merchant_user.wallets[0]

    tpos = await create_tpos(
        CreateTposData(
            wallet=merchant_wallet.id,
            name=data.name,
            currency=data.currency,
            business_name=data.name,
            business_address=None,
            business_vat_id=None,
            tax_inclusive=True,
            tax_default=0.0,
            tip_options="[]",
            tip_wallet="",
            withdraw_time=0,
            withdraw_between=10,
            lnaddress=False,
            enable_receipt_print=False,
            enable_remote=False,
            only_show_sats_on_bitcoin=False,
            allow_cash_settlement=False,
            onchain_enabled=False,
        )
    )

    merchant = await create_merchant(
        owner_id,
        data,
        merchant_user_id=merchant_user.id,
        merchant_wallet_id=merchant_wallet.id,
        tpos_id=tpos.id,
        base_url=str(base_url),
    )

    try:
        await send_initial_tpos_email(merchant)
        merchant.initial_email_sent_at = datetime.now(timezone.utc)
        await update_merchant(merchant)
    except Exception as exc:
        logger.warning(f"orangepillmerchants: initial email failed for {merchant.id}: {exc}")

    return merchant


async def resend_merchant_email(merchant_id: str) -> Merchant:
    merchant = await get_merchant(merchant_id)
    if not merchant:
        raise ValueError("Merchant not found.")

    if merchant.onboarding_completed:
        await send_login_email(merchant)
        merchant.login_email_sent_at = datetime.now(timezone.utc)
    else:
        await send_initial_tpos_email(merchant)
        merchant.initial_email_sent_at = datetime.now(timezone.utc)

    return await update_merchant(merchant)


def sale_amount_from_payment(payment) -> float:
    if not payment.extra:
        return 0.0
    amount = float(payment.extra.get("amount") or 0)
    tip_amount = float(payment.extra.get("tip_amount") or 0)
    return round_money(amount + tip_amount)


async def process_tpos_payment(payment) -> None:
    if not payment.extra:
        return
    if payment.extra.get("tag") != "tpos" or payment.extra.get("tipSplitted"):
        return

    tpos_id = payment.extra.get("tpos_id")
    if not tpos_id:
        return

    merchant = await get_merchant_by_tpos_id(str(tpos_id))
    if not merchant:
        return

    if await get_merchant_payment_by_hash(payment.payment_hash):
        return

    sale_amount = sale_amount_from_payment(payment)
    payout_payment_hash = None

    if not merchant.onboarding_completed:
        payout_invoice = await create_invoice(
            wallet_id=merchant.source_wallet_id,
            amount=payment.sat,
            memo=f"Orange Pill Merchant repayment from {merchant.name}",
            internal=True,
        )
        payout_payment = await pay_invoice(
            wallet_id=merchant.merchant_wallet_id,
            payment_request=payout_invoice.bolt11,
            extra={
                "tag": "orangepillmerchants",
                "merchant_id": merchant.id,
                "source_payment_hash": payment.payment_hash,
            },
        )
        payout_payment_hash = payout_payment.payment_hash

    try:
        await create_merchant_payment(
            merchant_id=merchant.id,
            payment_hash=payment.payment_hash,
            sale_amount=sale_amount,
            payout_amount_sat=payment.sat if not merchant.onboarding_completed else 0,
            payout_payment_hash=payout_payment_hash,
        )
    except Exception:
        logger.debug(f"orangepillmerchants: payment {payment.payment_hash} already processed.")
        return

    if merchant.onboarding_completed:
        return

    merchant.repaid_amount = round_money(merchant.repaid_amount + sale_amount)
    if merchant.repaid_amount >= merchant.onboarding_amount:
        merchant.onboarding_completed = True
        merchant.completed_at = datetime.now(timezone.utc)
        try:
            await send_login_email(merchant)
            merchant.login_email_sent_at = datetime.now(timezone.utc)
        except Exception as exc:
            logger.warning(f"orangepillmerchants: login email failed for {merchant.id}: {exc}")

    await update_merchant(merchant)
