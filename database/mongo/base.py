from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from database.mongo.models import KeyboardCollection, InstrumentCollection, InstrumentAlertCollection
from settings.config import settings


async def init_mongo_db(event_loop=None):
    client = AsyncIOMotorClient(settings.get_mongo_uri())
    if event_loop is not None:
        client.get_io_loop = event_loop
    await init_beanie(
        database=client[settings.MONGO_DB],
        document_models=[
            KeyboardCollection,
            InstrumentCollection,
            InstrumentAlertCollection
        ],
    )
