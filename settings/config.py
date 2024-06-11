import logging
from pathlib import Path

import dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
TINKOFF_DIR = BASE_DIR / 'tinkoff_app'
COMMAND_DIR = TINKOFF_DIR / 'commands'

DATABASE_DIR = BASE_DIR / "test.db"

class Settings(BaseSettings):
    DEBUG: bool = False
    USE_LOCAL_DB: bool = True

    TG_TOKEN: str
    TINKOFF_TOKEN: str = ''
    INVEST_ACCOUNT_ID: int = 123

    BD_HOST: str = ''
    BD_PORT: str = ''
    BD_USER: str = ''
    BD_PASS: str = ''

    MONGO_HOST: str
    MONGO_PORT: str
    MONGO_USER: str
    MONGO_PASS: str
    MONGO_DB: str = 'tinkoff'

    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_NOTIFICATION_CHANNEL: str = 'tinkoff.notification.app'

    BD_NAME: str = "tinkoff"

    PRICE_UPDATE_TIME: int = 10  # интервал обновления цены акций в секундах

    def get_db_uri(self) -> str:
        if self.USE_LOCAL_DB:
            return f"sqlite+aiosqlite:///{str(DATABASE_DIR)}"
        return f'mysql+pymysql://{self.BD_USER}:{self.BD_PASS}@{self.BD_HOST}:{self.BD_PORT}/{self.BD_NAME}'

    def get_mongo_uri(self) -> str:
        return f'mongodb://{self.MONGO_USER}:{self.MONGO_PASS}@{self.MONGO_HOST}:{self.MONGO_PORT}/'

    def get_log_lvl(self):
        if self.DEBUG:
            return logging.WARNING
        return logging.DEBUG

    class Config:
        env_file = Path(BASE_DIR, 'settings', '.env')
        dotenv.load_dotenv(env_file)


settings = Settings()  # type: ignore

