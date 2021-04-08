import os
import redis


class RedisClient(object):
    def __init__(self):
        self.client = redis.Redis(
            host=os.getenv('REDIS_HOST'),
            password=os.getenv('REDIS_PASSWORD'),
            port=os.getenv('REDIS_PORT'),
            db=os.getenv('REDIS_DB')
        )

    def get_client(self):
        return self.client
