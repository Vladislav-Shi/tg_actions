import redis.asyncio as redis
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from tinkoff.invest import AsyncClient

from bot.handlers.common.keyboards import menu_keyboard
from bot.handlers.common.states import SearchInstrumentState, SubscribeInstrumentState
from bot.handlers.common.text import get_action_info_text, get_valhelp_text, get_subscribe_success_text, \
    WRONG_INPUT_TEXT
from bot.utils.alert_calculator import AlertCalculator
from bot.utils.keyboards_builder.action_list import ActionListKeyboardBuilder
from bot.utils.keyboards_builder.callback_data import ActionListCallback
from bot.utils.redis_management import notification_to_new_subscribe
from database.mongo.crud import get_keyboard_by_uuid, create_alert
from settings.config import settings
from tinkoff_app.operations.instruments import get_instrument_info

router = Router()


@router.message(Command('menu'))
async def get_menu_handler(message: Message):
    """Выводит меню для работы"""
    message_text = '''Вот список доступных команд для пользователя'''
    await message.answer(text=message_text, reply_markup=menu_keyboard)


@router.callback_query(F.data == 'search_instrument')
async def search_action_handler(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(SearchInstrumentState.type_name)
    await callback_query.message.answer(text='Введите название акции (можно часть):')


@router.message(SearchInstrumentState.type_name)
async def search_result_handler(message: Message, state: FSMContext):
    search_text = message.text
    await state.clear()
    msg = await message.answer(text='Ожидайте..')
    await ActionListKeyboardBuilder.create_keyboard(name=search_text, message=msg)


@router.callback_query(ActionListCallback.filter(F.action == 'subscribe'))
async def action_subscribe_handler(query: CallbackQuery, callback_data: ActionListCallback, state: FSMContext):
    keyboard = await get_keyboard_by_uuid(keyboard_uuid=callback_data.keyboard_uuid)

    tinkoff_client = AsyncClient(settings.TINKOFF_TOKEN)
    instrument = await get_instrument_info(client=tinkoff_client, figi=keyboard.btn_ids[callback_data.number])
    text = get_action_info_text(instrument=instrument)

    await state.set_state(SubscribeInstrumentState.type_value)
    await state.update_data(instrument=instrument)
    await query.message.answer(**text.as_kwargs())


@router.callback_query(ActionListCallback.filter())
async def action_list_handler(query: CallbackQuery, callback_data: ActionListCallback):
    builder = ActionListKeyboardBuilder(message=query.message, callback=callback_data)
    await builder.init()
    await builder.send_message()


@router.message(SubscribeInstrumentState.type_value)
async def search_result_handler(message: Message, state: FSMContext, redis_client: redis.Redis):
    data = await state.get_data()
    text = message.text
    if text == '/valhelp':
        await message.answer(**get_valhelp_text().as_kwargs())
        await message.answer(**get_action_info_text(data['instrument']).as_kwargs())
        return
    msg = await message.answer(text='Ожидайте..')
    alert_calc = AlertCalculator(message=text, instrument_info=data['instrument'])
    if alert_calc.validate():
        price, comment, condition = alert_calc.calculate()
        await msg.edit_text(**get_subscribe_success_text(
            price=price,
            comment=comment,
            condition=condition,
            action_name=data['instrument']['name']).as_kwargs())

        await create_alert(
            user_id=message.from_user.id,
            figi=data['instrument']['figi'],
            value=price,
            message=comment,
            condition=condition,
            action_name=data['instrument']['name']
        )
        await notification_to_new_subscribe(client=redis_client)
        await state.clear()
    else:
        await msg.edit_text(f'Произошла ошибка. Введите корректную формулу')


@router.message()
async def wrong_input_handler(message: Message):
    """Выводит меню для работы"""
    await message.answer(text=WRONG_INPUT_TEXT)
