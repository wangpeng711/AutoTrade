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
        # 如果持仓，判断并全部卖出
        sell_all()
    else:
        # 未持仓
        # 筛选股票
        buy_stock = filter_stocks()
        # 交易股票
        if buy_stock:
            all_in_one(buy_stock)

def schedule_job():
    # 设置每个工作日下午2:43执行任务
    schedule.every().day.at("14:43").do(job)
    # 循环检查是否到达任务执行时间
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每隔一分钟检查一次


job()