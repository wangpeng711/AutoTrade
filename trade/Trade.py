import easytrader
import schedule
import time
from Strategy import *
from RedisClient import *


# 替换为你的账户号和通用同花顺客户端路径
# 使用 EasyTrader 的 use 函数进行初始化
user = easytrader.use('universal_client')
# 准备登录信息并自动登录
user.prepare(r'D:\IdeaProject\AutoTrade\trade\config.json')

def all_in_one(buy_stock):
    my_balance = user.balance
    my_position = user.position
    cached_result = redis_client.get('filter_stock_info')
    if cached_result:
        max_lower_shadow_stock = json.loads(cached_result.decode('utf-8'))
        # todo all in one
    print(my_balance)
    print(my_position)

    # 交易完成后 设置缓存
    redis_client.set('filter_stock_info', json.dumps(buy_stock))

def sell_all():
    # todo sell all
    pass
def is_position_stock():
    # return True
    my_position = user.position
    cached_result = redis_client.get('filter_stock_info')
    if cached_result:
        max_lower_shadow_stock = json.loads(cached_result.decode('utf-8'))
        # 判断my_position 列表中证券代码，是否包含 max_lower_shadow_stock中的code 并返回
        for position in my_position:
            if position['证券代码'] in max_lower_shadow_stock['xcode']:
                return True
    else:
        return False



# trade(123)