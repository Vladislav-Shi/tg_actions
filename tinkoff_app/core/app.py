import asyncio
import operator
from typing import Dict, List

import redis.asyncio as redis
from aiogram import Bot
from grpc._cython.cygrpc import UsageError
from tinkoff.invest import AsyncClient

from database.mongo.crud import bulk_update_or_create_instruments, get_active_subscribes
from database.mongo.models import InstrumentAlertCollection
from settings.config import settings
from tinkoff_app.operations.alert import get_alert_list, get_alert_message, send_alert
from tinkoff_app.operations.instruments import aget_all_instruments, get_instrument_last_prices


class TinkoffApp:
    _redis_client: redis.Redis
    _bot: Bot
    _tinkoff_client: AsyncClient
    _commands: dict
    _alerts: Dict[str, List[InstrumentAlertCollection]]
    _operation: dict = {
        'lte': operator.le,
        'gte': operator.ge,
    }

    def __init__(self, tinkoff_client: AsyncClient, redis_client: redis.Redis, bot: Bot):
        self._tinkoff_client = tinkoff_client
        self._redis_client = redis_client
        self._alerts = dict()
        self._bot = bot
        self._commands = {
            'find_instruments': self.find_instruments,
            'update_subscribe': self.update_subscribe
        }

    async def _redis_subscribe(self):
        """Обработка и подписка на редис"""
        print('start _redis_subscribe')
        pubsub = self._redis_client.pubsub()
        await pubsub.subscribe(settings.REDIS_NOTIFICATION_CHANNEL)
        print(f"Subscribed to channel: {settings.REDIS_NOTIFICATION_CHANNEL}")
        async for message in pubsub.listen():
            if message['type'] == 'message':
                await self._commands[message['data'].decode('utf-8')]()

    async def find_instruments(self):
        instruments = await aget_all_instruments(client=self._tinkoff_client)
        await bulk_update_or_create_instruments(invests_data=instruments)

    async def update_subscribe(self):
        """Обновляет список отслеживаемых"""
        objs = await get_active_subscribes()
        self._alerts = get_alert_list(objs)

    async def check_prices(self):
        """проверяет цены и отправляет уведомления"""
        print('price check start')
        last_prices = await get_instrument_last_prices(
            client=self._tinkoff_client,
            figis=list(self._alerts.keys()))
        for figi, value in last_prices.items():
            for alert in self._alerts[figi]:
                if self._operation[alert.condition](alert.value, value) and alert.active:
                    message = get_alert_message(actin_alert=alert)
                    await send_alert(self._bot, alert.user_id, message)
                    alert.active = False
                    await alert.save()
        print('price check end')

    async def _price_check_task(self):
        while True:
            try:
                await self.check_prices()
            except UsageError as e:
                print('UsageError', e)
                self._tinkoff_client = AsyncClient(settings.TINKOFF_TOKEN)
            await asyncio.sleep(settings.PRICE_UPDATE_TIME)

    async def start(self):
        """Запускает инстанс"""
        await self.update_subscribe()
        await asyncio.gather(self._redis_subscribe(), self._price_check_task())
