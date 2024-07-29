import redis


# 连接到本地 Redis 服务
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0,password='123qwe!@#')