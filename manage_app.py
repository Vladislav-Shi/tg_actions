import argparse
import asyncio
import logging

from settings.config import settings
from tinkoff_app.core.command import CommandControl
from tinkoff_app.main import run_tinkoff_app

logging.basicConfig(level=settings.get_log_lvl(),
                    format="%(levelname)s: %(asctime)s -- %(name)s -- %(message)s")
log = logging.getLogger('tinkoff_app')


def main():
    """Запускает приложение по работе с API"""
    logging.info('start')
    parser = argparse.ArgumentParser(description="Описание команд для API Тинькоффа")
    cmd = CommandControl(parser=parser)
    if not cmd.parse_command():
        # asyncio.run не будет работать, так как grpcio создает свой loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_tinkoff_app())


if __name__ == '__main__':
    main()
