import redis
import json

# 连接到本地 Redis 服务
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0,password='123qwe!@#')

def redis_test():
    redis_client.set('buy_stock', json.dumps('王鹏 wangpeng 1123123'))
    cached_result = redis_client.get('buy_stock')
    max_lower_shadow_stock = json.loads(cached_result.decode('utf-8'))
    print(max_lower_shadow_stock)
redis_test()