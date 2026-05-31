import redis
from core.config import REDIS_URL


def get_redis_connection():
    """
    Get a Redis connection.
    Returns a redis.Redis client instance with TCP keepalive and socket timeouts
    designed for blocking operations on Docker Swarm networks.
    """
    return redis.from_url(
        REDIS_URL,
        decode_responses=True,
        socket_timeout=15,
        socket_connect_timeout=5,
        socket_keepalive=True,
    )
