import asyncio

from aiogram import Bot
from tinkoff.invest import AsyncClient

from bot.utils.redis_management import get_redis_connection
from database.mongo.base import init_mongo_db
from settings.config import settings
from tinkoff_app.core.app import TinkoffApp

tinkoff_client = AsyncClient(settings.TINKOFF_TOKEN)
redis_client = get_redis_connection()
bot = Bot(token=settings.TG_TOKEN)

app = TinkoffApp(
    tinkoff_client=tinkoff_client,
    redis_client=redis_client,
    bot=bot
)


async def run_tinkoff_app():
    # await init_mongo_db(event_loop=asyncio.get_running_loop)
    await init_mongo_db()
    await app.start()
