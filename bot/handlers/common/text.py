from aiogram.utils.formatting import Text, Bold, Italic, BotCommand


def get_action_info_text(instrument: dict) -> Text:
    my_price = instrument["price_in_portfolio"]
    if my_price is None:
        my_price = '0'
    return Text(f'Выбрана акция: ', Italic(instrument["name"]),
                '\nЦена: ', Italic(instrument["price"]), ' руб.',
                '\nВы купили: ', Italic(my_price), ' руб.',
                '\nВведите формулу для оповещения\nВведите ', BotCommand("/valhelp"), ' для помощи')


def get_valhelp_text() -> Text:
    return Text(
        "Помощь по формированию запросов:\n",
        "Общий шаблон выглядит так:\n",
        Italic('<|> condition\ncomment\n\n'),
        Bold('<|>'), " - > - цена акции будет выше, < будет ниже\n",
        Bold('cur'), " - Текущий курс валюты\n",
        Bold('my'), " - Курс по которому валюта покупалась\n\n",
        "Пример использования:\n",
        Italic('>my115%'), " - Уведомить, когда цена будет на 15% выше, чем когда покупалась\n",
        Italic('<500+200'), " - Уведомить, когда цена будет ниже 700\n",
    )


def get_subscribe_success_text(price: float, comment: str, condition: str, action_name: str) -> Text:
    condition_text = 'будет ниже '
    if condition == 'gte':
        condition_text = 'будет выше '
    return Text(
        "Отлично!\n",
        "Уведомление на акцию ", Bold(action_name), f" будет отправлено если цена на акцию {condition_text}",
        Bold(str(price)), ' Руб.\n',
        "Сообщение будет с текстом:\n\n",
        Italic(comment)
    )


WRONG_INPUT_TEXT = '''Для того чтобы вызвать меню бота напиши /menu'''
