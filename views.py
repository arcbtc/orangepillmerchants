from fastapi import APIRouter, Depends

from lnbits.core.views.generic import index
from lnbits.decorators import check_super_user

orangepillmerchants_generic_router = APIRouter()


orangepillmerchants_generic_router.add_api_route(
    "/",
    methods=["GET"],
    endpoint=index,
    dependencies=[Depends(check_super_user)],
)
