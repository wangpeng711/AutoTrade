import redis
import json


# 连接到本地 Redis 服务
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0,password='123qwe!@#')


def get_cache(key):
    cached_result = redis_client.get(key)
    if cached_result:
        value = json.loads(cached_result.decode('utf-8'))
        return value
