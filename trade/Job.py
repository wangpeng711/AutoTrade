import schedule
import time
from datetime import datetime
from Trade import *
from Strategy import *
from RedisClient import *


def job():
    # 在这里执行你的跑批任务的代码
    print("Running trade job at", datetime.datetime.now())
    if is_position_stock():
        # 如果持仓
        position = get_cache('filter_stock_info')
        print("持仓股票:", position)
        stock_code = position['code']
        current = get_price_day_tx(stock_code.replace('.', ''), count=1)
        # 满足卖出条件: 止损位 or 上影线卖出条件 or 止盈位
        if is_stop_loss(position, current) or is_up_shadow_sell(position, current):
            sell_position_all()
            print("卖出股票:", stock_code)
            time.sleep(3)
            print("卖出成功后重新选择股票")
            # 筛选股票
            buy_stock = filter_stocks()
            print("筛选股票:", buy_stock)
            # 交易股票
            if buy_stock:
                all_in_one(buy_stock)
                print("梭哈股票：", buy_stock)
        print("-----持仓操作完成-----")
    else:
        # 未持仓
        print("当前未策略持仓")
        # 筛选股票
        buy_stock = filter_stocks()
        print("筛选股票:", buy_stock)
        # 交易股票
        if buy_stock:
            all_in_one(buy_stock)
            print("梭哈股票：", buy_stock)
        print("-----未持仓操作完成-----")

def schedule_job():
    # 设置每个工作日下午2:43执行任务
    schedule.every().day.at("14:43").do(job)
    # 循环检查是否到达任务执行时间
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每隔一分钟检查一次

# current = get_price_day_tx('sh.601919'.replace('.', ''), count=1)
# print(current['low'][1])
# look_stocks = []
# look_stocks.append({
#     'code': 'sh.601919',
#     'xcode':'601919',
#     'date': '',
#     'open': 12.91,
#     'close': 13.06,
#     'low': 12.67,
#     'high':13.14,
#     'volume':1212413.00000,
#     'lower_shadow_ratio': 0.001
# })
# position = max(look_stocks, key=lambda x: x['lower_shadow_ratio'])
# redis_client.set('filter_stock_info', json.dumps(position))
# print(is_stop_loss(position,current))
# print(is_up_shadow_sell(position,current))
