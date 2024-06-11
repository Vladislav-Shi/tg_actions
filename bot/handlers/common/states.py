from aiogram.fsm.state import StatesGroup, State


class SearchInstrumentState(StatesGroup):
    type_name = State()


class SubscribeInstrumentState(StatesGroup):
    type_value = State()
