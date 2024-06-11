from typing import Optional

from aiogram.filters.callback_data import CallbackData


class ActionListCallback(CallbackData, prefix="ActKey", sep="__"):
    keyboard_uuid: str
    action: str
    number: Optional[int] = None
