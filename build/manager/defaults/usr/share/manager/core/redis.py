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


def append_task_log(prefix: str, task_id: str, line: str, con=None):
    """
    Append a log line to a task-specific Redis list with a 24-hour TTL.
    """
    try:
        if con is None:
            con = get_redis_connection()
        key = f"{prefix}{task_id}:logs"
        con.rpush(key, line)
        con.expire(key, 86400)
    except Exception:
        # Avoid breaking the build worker if Redis logging fails
        pass

