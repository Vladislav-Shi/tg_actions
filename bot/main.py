from aiogram import Bot, Dispatcher

from bot.handlers import register_routes
from bot.utils.redis_management import get_redis_connection
from database.mongo.base import init_mongo_db
from settings.config import settings

TG_TOKEN = settings.TG_TOKEN

bot = Bot(token=TG_TOKEN)
dp = Dispatcher()
register_routes(dp)


async def run_bot():
    await init_mongo_db()
    dp['redis_client'] = get_redis_connection()
    await dp.start_polling(bot)
