from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Поиск 🔎', callback_data='search_instrument'),
            InlineKeyboardButton(text='Список отслеживаемых 👀', callback_data='watchlist_instruments'),
        ],
        [
            InlineKeyboardButton(text='Мои акции 💼', callback_data='my_instruments'),
        ]
    ]
)
