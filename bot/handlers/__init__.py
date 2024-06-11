from aiogram import Dispatcher

from .common.handlers import router as common_router


def register_routes(dp: Dispatcher):
    dp.include_router(common_router)
