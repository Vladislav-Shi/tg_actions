import asyncio
from argparse import ArgumentParser

from tinkoff.invest import AsyncClient

from database.mongo.base import init_mongo_db
from database.mongo.crud import bulk_update_or_create_instruments, get_all_instruments
from settings.config import settings
from tinkoff_app.core.command import BaseCommand
from tinkoff_app.operations.instruments import aget_all_instruments


class FindInstruments(BaseCommand):
    command = 'find-instrument'

    async def handle(self, *args, **kwargs):
        await init_mongo_db()

        print('\nStart find instruments')
        tinkoff_client = AsyncClient(settings.TINKOFF_TOKEN)
        objs = await get_all_instruments()
        print('objs len', len(objs))
        instruments = await aget_all_instruments(client=tinkoff_client)
        await bulk_update_or_create_instruments(invests_data=instruments)

        # await asyncio.sleep(2)
        objs = await get_all_instruments()
        print('objs len', len(objs))

    def add_arguments(self, parser: ArgumentParser) -> None:
        pass
