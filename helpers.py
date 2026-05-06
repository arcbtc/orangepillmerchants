from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import urljoin


def round_money(value: float | int | str) -> float:
    amount = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return float(amount)


def build_absolute_url(base_url: str, path: str) -> str:
    return urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
