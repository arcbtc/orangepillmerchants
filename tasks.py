import asyncio

from lnbits.core.models import Payment
from lnbits.tasks import register_invoice_listener
from loguru import logger

from .services import process_tpos_payment


async def wait_for_paid_invoices():
    invoice_queue = asyncio.Queue()
    register_invoice_listener(invoice_queue, "ext_orangepillmerchant")

    while True:
        payment = await invoice_queue.get()
        await on_invoice_paid(payment)


async def on_invoice_paid(payment: Payment) -> None:
    try:
        await process_tpos_payment(payment)
    except Exception as exc:
        logger.error(f"orangepillmerchants: payment processing failed: {exc}")
