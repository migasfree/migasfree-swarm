import redis
from core.config import REDIS_URL


def get_redis_connection():
    """
    Get a Redis connection.
    Returns a redis.Redis client instance.
    """
    return redis.from_url(REDIS_URL, decode_responses=True)
