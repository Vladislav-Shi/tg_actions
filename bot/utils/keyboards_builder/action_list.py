from typing import Tuple, List, Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from bot.utils.keyboards_builder.callback_data import ActionListCallback
from database.mongo.crud import get_like_name_instruments
from database.mongo.models import KeyboardCollection, InstrumentCollection


class ActionListKeyboardBuilder:
    keyboard_name: str = 'ActKey'
    pagination: int = 5

    _callback: ActionListCallback
    _keyboard: KeyboardCollection
    _page: int
    _instrument_name: str
    _message: Message
    _objects: List[InstrumentCollection]
    _all_objects_len: int
    _all_pages: int
    _is_new_position: bool = False
    _cur_objects: List[InstrumentCollection]

    def __init__(self, message: Message, callback: ActionListCallback, *args, name: Optional[str] = None, **kwargs):
        self._callback = callback
        self._message = message
        self._instrument_name = name

    async def init(self):
        """Выполняет все действия над обьектами. После вызова этого метода должно быть доступо построение новой клавы"""
        await self._get_db_keyboard()
        await self._get_objects()
        await self._navigate()
        await self._get_cur_objects()

    async def _get_db_keyboard(self) -> KeyboardCollection:
        """Получает обьект текущей KeyboardCollection из монги"""
        self._keyboard = await KeyboardCollection.get(self._callback.keyboard_uuid)
        self._page = self._keyboard.position
        if self._instrument_name is None:
            self._instrument_name = self._keyboard.query['name']
        return self._keyboard

    async def _navigate(self):
        """метод отслеживает, менять ли страницу и отрисовывать новую клаву"""
        page = self._page
        if self._callback.action == 'pre':
            self._page = self._page - 1 if self._page > 0 else 0
        elif self._callback.action == 'next':
            self._page = self._page + 1 if self._page + 1 < self._all_pages else self._all_pages - 1
        elif self._callback.action == 'init':
            self._page = 0
        if page != self._page or self._callback.action == 'init':
            self._is_new_position = True
            self._keyboard.position = self._page

    async def _get_objects(self) -> List[InstrumentCollection]:
        objs = await get_like_name_instruments(self._instrument_name)
        self._all_objects_len = len(objs)
        self._all_pages = self._all_objects_len // self.pagination + 1
        self._objects = objs
        return self._objects

    async def _get_cur_objects(self) -> List[InstrumentCollection]:
        """Берет из всей выборки нужные для построения"""
        self._cur_objects = self._objects[self.pagination * self._page: self.pagination * (self._page + 1)]
        self._keyboard.btn_ids = [obj.figi for obj in self._cur_objects]
        await self._keyboard.save()
        return self._cur_objects

    def _get_obj_btns(self, obj: InstrumentCollection, position: int) -> List[InlineKeyboardButton]:
        """Создвет кнопки для текущей акции"""
        subscribe_callback = ActionListCallback(
            keyboard_uuid=self._callback.keyboard_uuid,
            action='subscribe',
            number=position
        )
        return [
            InlineKeyboardButton(text=f'{obj.name}: {obj.figi}', callback_data=subscribe_callback.pack()),
            InlineKeyboardButton(text='Следить', callback_data=subscribe_callback.pack()),
        ]

    def _get_action_btns(self) -> List[List[InlineKeyboardButton]]:
        """Создает кнопки взаимодействия с акциями"""
        return [
            self._get_obj_btns(obj=obj, position=num)
            for num, obj in enumerate(self._cur_objects)
        ]

    async def _get_keyboard(self) -> InlineKeyboardMarkup:
        next_btn = ActionListCallback(
            keyboard_uuid=self._callback.keyboard_uuid,
            action='next'
        )
        pre_btn = ActionListCallback(
            keyboard_uuid=self._callback.keyboard_uuid,
            action='pre'
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                *self._get_action_btns(),
                [
                    InlineKeyboardButton(text='⬅️', callback_data=pre_btn.pack()),
                    InlineKeyboardButton(text=f'{self._page + 1}/{self._all_pages}', callback_data='1'),
                    InlineKeyboardButton(text='➡️', callback_data=next_btn.pack()),
                ],
            ]
        )
        return keyboard

    async def get_message(self) -> Tuple[str, InlineKeyboardMarkup]:
        message = f'''Вот все найденные акции по запросу `{self._instrument_name}`\n\nВсего {self._all_objects_len}'''
        keyboard = await self._get_keyboard()
        return message, keyboard

    async def send_message(self, *args, **kwargs):
        """Создает и отправляет клавиатуру"""
        text, keyboard = await self.get_message()
        if self._is_new_position:
            await self._message.edit_text(text=text, reply_markup=keyboard)

    @classmethod
    async def create_keyboard(cls, name: str, message: Message, *args, **kwargs):
        """ Создает новую клавиатуру в бд и добавляет ее в выбранное сообщение"""
        obj = KeyboardCollection(
            btn_ids=[],
            keyboard_name=cls.keyboard_name,
            position=0,
            query={'name': name}
        )
        await obj.save()
        callback = ActionListCallback(
            keyboard_uuid=str(obj.id),
            action='init'
        )
        keyboard_factory = cls(
            name=name,
            callback=callback,
            message=message
        )
        await keyboard_factory.init()
        await keyboard_factory.send_message(*args, **kwargs)
