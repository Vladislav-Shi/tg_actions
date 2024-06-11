from typing import List, Type, Tuple, Optional

from beanie import BulkWriter
from beanie.odm.operators.find.evaluation import RegEx
from beanie.odm.operators.update.general import Set

from database.mongo.models import InstrumentCollection, T, KeyboardCollection, InstrumentAlertCollection, \
    AlertConditionEnum


async def bulk_update_or_create_instruments(invests_data: List[dict]) -> List[InstrumentCollection]:
    """Обновляет или вставляет записи в коллекцию InstrumentCollection"""
    objs = []
    for invest_data in invests_data:
        objs.append(InstrumentCollection(
            figi=invest_data['figi'],
            ticker=invest_data['ticker'],
            class_code=invest_data['class_code'],
            isin='0',
            currency=invest_data['currency'],
            name=invest_data['name'],
            type=invest_data['type'],
        ))
    async with (BulkWriter() as bulk_writer):
        for obj in objs:
            await InstrumentCollection.find_one(
                {InstrumentCollection.figi: obj.figi}
            ).upsert(Set(obj.dict(exclude={'figi'})),
                     on_insert=obj
                     )
        await bulk_writer.commit()


async def get_all_instruments() -> List[InstrumentCollection]:
    return await InstrumentCollection.find_all().to_list()


async def get_like_name_instruments(name: str) -> List[InstrumentCollection]:
    regex_pattern = f".*{name}.*"
    users = await InstrumentCollection.find(
        RegEx(InstrumentCollection.name, regex_pattern)
    ).to_list()
    return users


async def get_keyboard_by_uuid(keyboard_uuid: str) -> Optional[KeyboardCollection]:
    obj = await KeyboardCollection.get(keyboard_uuid)
    return obj


async def get_or_create(document_class: Type[T], kwargs: dict, defaults=None) -> Tuple[T, bool]:
    document = await document_class.find_one(kwargs)
    if document is None:
        document_data = kwargs.copy()
        document_data.update(defaults or {})
        document = document_class(**document_data)
        await document.insert()
        return document, True
    return document, False


async def create_alert(
        user_id: int,
        figi: str,
        value: float,
        message: str,
        condition: AlertConditionEnum,
        action_name: str
) -> InstrumentAlertCollection:
    doc = InstrumentAlertCollection(
        user_id=user_id,
        figi=figi,
        value=value,
        condition=condition,
        message=message,
        action_name=action_name
    )
    await doc.insert()
    return doc


async def get_active_subscribes() -> List[InstrumentAlertCollection]:
    objs = await InstrumentAlertCollection.find({'active': True}).to_list()
    return objs
