from typing import List, Dict

from aiogram import Bot
from aiogram.utils.formatting import Text, Bold, Italic

from database.mongo.models import InstrumentAlertCollection


def get_alert_list(objs: List[InstrumentAlertCollection]) -> Dict[str, List[InstrumentAlertCollection]]:
    """Преобразует обьекты сообщений из базы в удобный формат"""
    result = dict()
    for obj in objs:
        if obj.figi not in result:
            result[obj.figi] = []
        result[obj.figi].append(obj)
    return result


def get_alert_message(actin_alert: InstrumentAlertCollection) -> Text:
    condition_text = ' стала ниже '
    if actin_alert.condition == 'gte':
        condition_text = ' стала выше '
    return Text('📌Уведомление📌\n',
                'Цена на акцию ', Bold(actin_alert.action_name), condition_text, Bold(actin_alert.value),
                '\nТекст комментария:\n\n',
                Italic(actin_alert.message)
                )


async def send_alert(bot: Bot, user_id: int, message: Text):
    await bot.send_message(user_id, **message.as_kwargs())
