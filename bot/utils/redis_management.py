import redis.asyncio as redis

from settings.config import settings


def get_redis_connection() -> redis.Redis:
    client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    return client


async def notification_to_new_subscribe(client: redis.Redis):
    await client.publish(settings.REDIS_NOTIFICATION_CHANNEL, 'update_subscribe')


async def notification_to_parse_instrument(client: redis.Redis):
    await client.publish(settings.REDIS_NOTIFICATION_CHANNEL, 'parse_instruments')
