from typing import Any


def get_float_from_quotation(price: Any) -> float:
    """преобразует из их формата в рурбли"""
    return float(f'{price.units}.{price.nano}')
