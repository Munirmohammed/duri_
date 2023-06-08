from redis import Redis
from src.core.config import settings
from redis_om import get_redis_connection

print(settings.redis_host)

#redis_conn = get_redis_connection(url=f"redis://{settings.redis_host}", decode_responses=True)
redis_conn = Redis(host='redis', port=6379, decode_responses=True)

""" 
Notes:
    - https://redis.readthedocs.io/en/stable/examples/search_json_examples.html#Searching
    - https://redis.readthedocs.io/en/stable/examples.html
    - https://redis.io/commands/hget/
"""
class RedisClient:
    def __init__(self):
        #self.client = Redis(host='redis', port=6379,)
        self.client = redis_conn

    def get_set_keys(self, set_key):
        keys = self.client.zrange(set_key, 0, -1) # withscores=True
        #print(keys)
        return keys
    
    def get_keys(self, key_pattern):
        keys = self.client.keys(key_pattern)
        print(keys)
        return keys
        result = [key.decode() for key in keys]
        print(result)
        return result
    
    def get_hash(self, key_name):
        content = self.client.hget(key_name, 'content')
        metadata = self.client.hget(key_name, 'metadata')
        return {"content": content, "metadata": metadata}
    
    def scan_keys(self, key_pattern):
        cursor = '0'
        keys = []
        while True:
            cursor, partial_keys = self.client.scan(cursor, match=key_pattern)
            keys.extend(partial_keys)
            if cursor == '0':
                break
        return [key.decode() for key in keys]
