from redis import Redis
from src.core.config import settings
from redis_om import get_redis_connection

print(settings.redis_host)

#redis_conn = get_redis_connection(url=f"redis://{settings.redis_host}", decode_responses=True)
redis_conn = Redis(host='redis', port=6379, decode_responses=True)

class RedisClient:
    def __init__(self):
        #self.redis_client = Redis(host=host, port=port)
        self.redis_client = redis_conn

    def scan_keys(self, key_pattern):
        cursor = '0'
        keys = []
        while True:
            cursor, partial_keys = self.redis_client.scan(cursor, match=key_pattern)
            keys.extend(partial_keys)
            if cursor == '0':
                break
        return [key.decode() for key in keys]
