from typing import List, Optional, Dict

from tinkoff.invest import Client, AsyncClient
from tinkoff.invest.async_services import AsyncServices

from settings.config import settings
from tinkoff_app.core.currensy_calculate import get_float_from_quotation


def get_all_instruments(client: Client) -> List[dict]:
    """запрашивает все ценные бумаги/ валюты и фьючерсы
    Возвращает список со словарем с инфой об инструменте"""

    result: List[dict] = []
    with client as client_session:
        for method in ["shares", "bonds", "etfs", "currencies", "futures"]:
            for item in getattr(client_session.instruments.shares, method)().instruments:
                result.append(
                    {
                        "name": item.name,
                        "ticker": item.ticker,
                        "class_code": item.class_code,
                        "figi": item.figi,
                        "type": method,
                        "currency": item.currency,
                    }
                )
    return result


async def aget_all_instruments(client: AsyncClient) -> List[dict]:
    result: List[dict] = []
    async with client as client_session:
        for method in ["shares", "bonds", "etfs", "currencies", "futures"]:
            for item in (await getattr(client_session.instruments, method)()).instruments:
                result.append(
                    {
                        "name": item.name,
                        "ticker": item.ticker,
                        "class_code": item.class_code,
                        "figi": item.figi,
                        "type": method,
                        "currency": item.currency,
                    }
                )
    return result


async def get_instrument_info(client: AsyncClient, figi: str, account_id: Optional[int] = None) -> dict:
    """Получает информацию об акции
    Её цена, название и тд"""
    async with client as client_session:
        info_response = await client_session.instruments.find_instrument(query=figi)
        price_response = await client_session.market_data.get_last_prices(figi=[figi])
        if account_id is None:
            account_id = settings.INVEST_ACCOUNT_ID
        portfolio_response = await client_session.operations.get_portfolio(account_id=str(account_id))
        price_in_portfolio = next(
            filter(lambda x: x.figi == info_response.instruments[0].figi,
                   portfolio_response.positions),
            None)
        if price_in_portfolio is not None:
            price_in_portfolio = get_float_from_quotation(price_in_portfolio.average_position_price)

        result = {
            "name": info_response.instruments[0].name,
            "figi": info_response.instruments[0].figi,
            "type": info_response.instruments[0].instrument_type,
            "price": get_float_from_quotation(price_response.last_prices[0].price),
            "price_in_portfolio": price_in_portfolio
        }
    return result


async def get_instrument_last_prices(client: AsyncClient, figis: List[str]) -> Dict[str, float]:
    async with client as client_session:
        # client_session.
        price_response = await client_session.market_data.get_last_prices(figi=figis)
    result = {i.figi: get_float_from_quotation(i.price) for i in price_response.last_prices}
    return result
