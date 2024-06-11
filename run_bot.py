import asyncio
import logging

from settings.config import settings

logging.basicConfig(level=settings.get_log_lvl(),
                    format=" %(levelname)s: %(asctime)s -- %(name)s -- %(message)s")
log = logging.getLogger('bot')

from bot.main import run_bot

if __name__ == '__main__':
    log.info('Start bot')
    asyncio.run(run_bot())
