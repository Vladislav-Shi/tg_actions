import enum
from datetime import datetime
from typing import TypeVar, Optional, Union
from uuid import UUID, uuid4

from beanie import Document, Indexed
from pydantic import Field

T = TypeVar("T", bound=Document)


class InstrumentTypeEnum(enum.StrEnum):
    SHARES = 'shares'
    BONDS = 'bonds'
    ETFS = 'etfs'
    CURRENCIES = 'currencies'
    FUTURES = 'futures'

class AlertConditionEnum(enum.StrEnum):
    GREATER_THAN = 'gte'
    LESS_THAN = 'lte'


class KeyboardCollection(Document):
    id: UUID = Field(default_factory=uuid4)
    keyboard_name: str
    position: int = 0
    btn_ids: list[Union[str, int]]
    query: dict = {}
    create_at: datetime = Field(default_factory=datetime.now)
    message_id: Optional[int] = None
    chat_id: Optional[int] = None

    class Settings:
        name = 'keyboards'
        keep_nulls = True


class InstrumentCollection(Document):
    figi: Indexed(str, unique=True)
    ticker: str
    class_code: str
    isin: str
    currency: str
    name: str
    type: InstrumentTypeEnum = InstrumentTypeEnum.SHARES

    class Settings:
        name = 'instruments'
        keep_nulls = True


class InstrumentAlertCollection(Document):
    id: UUID = Field(default_factory=uuid4)
    user_id: int
    figi: str
    value: float
    currency: str = 'rub'
    create_at: datetime = Field(default_factory=datetime.now)
    active: bool = True
    condition: AlertConditionEnum
    message: Optional[str] = None
    action_name: str = ''

    class Settings:
        name = 'instrument_alert'
        keep_nulls = True
