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
    # my_position = user.position
    stock_code = buy_stock['code']
    current = get_price_day_tx(stock_code.replace('.', ''), count=1)
    buy_price = current['close'][1] * 1.015
    amount = round(my_balance['可用金额']/buy_price, -2)
    user.buy(stock_code, buy_price, amount)
    # 交易完成后 设置缓存
    redis_client.set('filter_stock_info', json.dumps(buy_stock))


def sell_position_all():
    my_position = user.position
    print(my_position)
    cached_result = get_cache('filter_stock_info')
    if cached_result:
        xcode = cached_result['xcode']
        stock_code = cached_result['code']
        for position in my_position:
            if position['证券代码'] == xcode:
                # 获取可用余额和当前市价
                available_balance = position['可用余额']
                current_price = position['市价']
                lower_price = current_price * 0.985  # 比市价低2%的价格
                user.sell(stock_code, lower_price, available_balance)
                redis_client.delete('filter_stock_info')


def is_position_stock():
    # return True
    my_position = user.position
    cached_result = get_cache('filter_stock_info')
    if cached_result:
        # 判断my_position 列表中证券代码，是否包含 max_lower_shadow_stock中的code 并返回
        for position in my_position:
            if position['证券代码'] in cached_result['xcode']:
                return True
    else:
        return False


def is_stop_loss(position, current):
    if current['low'][1] < position['low']:
        # 破位止损
        print("满足破位信号")
        return True


def is_up_shadow_sell(position, current):
    cur_high = current['high'][1]
    cur_low = current['low'][1]
    cur_open = current['open'][1]
    cur_close = current['close'][1]
    # 计算上影线
    upper_shadow = cur_high - max(cur_open, cur_close)
    # 计算下影线
    lower_shadow = min(cur_open, cur_close) - cur_low
    if lower_shadow > 0 and upper_shadow > 0 and upper_shadow > lower_shadow * 2:
        print("满足上影线卖出信号")
        # 卖出信号
        return True



def is_stop_profit(position, current):
    # todo 暂不设置
    print("默认不设置止盈")
    return False

# balance = user.balance
# user.position
# res = user.sell('sz.002513', price=3.53, amount=100)
# print(res)
# print(is_position_stock())