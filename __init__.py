import asyncio

from fastapi import APIRouter
from lnbits.tasks import create_permanent_unique_task
from loguru import logger

from .crud import db
from .tasks import wait_for_paid_invoices
from .views import orangepillmerchants_generic_router
from .views_api import orangepillmerchants_api_router

orangepillmerchants_ext: APIRouter = APIRouter(
    prefix="/orangepillmerchants", tags=["orangepillmerchants"]
)
orangepillmerchants_ext.include_router(orangepillmerchants_generic_router)
orangepillmerchants_ext.include_router(orangepillmerchants_api_router)


orangepillmerchants_static_files = [
    {
        "path": "/orangepillmerchants/static",
        "name": "orangepillmerchants_static",
    }
]

scheduled_tasks: list[asyncio.Task] = []


def orangepillmerchants_stop():
    for task in scheduled_tasks:
        try:
            task.cancel()
        except Exception as ex:
            logger.warning(ex)


def orangepillmerchants_start():
    task = create_permanent_unique_task("ext_orangepillmerchant", wait_for_paid_invoices)
    scheduled_tasks.append(task)


__all__ = [
    "db",
    "orangepillmerchants_ext",
    "orangepillmerchants_start",
    "orangepillmerchants_static_files",
    "orangepillmerchants_stop",
]
