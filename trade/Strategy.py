import time
import redis
import json
from datetime import datetime, timedelta
from RedisClient import *

from Ashare import *
import baostock as bs
import tushare as ts

def query_stock(code, start_date, end_date):
    # 登陆系统
    lg = bs.login()
    #### 获取沪深A股历史K线数据 ####
    # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。“分钟线”不包含指数。
    # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
    # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
    rs = bs.query_history_k_data_plus(code,
                                      "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                      start_date=start_date, end_date=end_date,
                                      frequency="d", adjustflag="3")
    print('query_history_k_data_plus respond error_code:' + rs.error_code)
    print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)
    #### 打印结果集 ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    #### 结果集输出到csv文件 ####
    # result.to_csv("D:\\history_A_stock_k_data.csv", index=False)
    return result


def transform_code(code):
    parts = code.split('.')  # 将代码分割成两部分，使用点号分隔
    if len(parts) == 2:
        exchange = parts[0]  # 交易所部分，例如 "sh"
        number = parts[1]  # 编号部分，例如 "00001"
        return f"{number}.{exchange.upper()}"  # 连接并转换大小写
    else:
        return code  # 如果格式不符合预期，直接返回原始代码


# 打印结果集
def query_hs300():
    # 登陆系统
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    # 获取沪深300成分股
    rs = bs.query_hs300_stocks()
    print('query_hs300 error_code:' + rs.error_code)
    print('query_hs300  error_msg:' + rs.error_msg)

    hs300_stocks = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        hs300_stocks.append(rs.get_row_data())
    result = pd.DataFrame(hs300_stocks, columns=rs.fields)
    # 结果集输出到csv文件
    # result.to_csv("D:/hs300_stocks.csv", encoding="gbk", index=False)
    return result


def filter_stocks():
    start_time = time.time()
    # ts.set_token('59ebf9b48a3e6b93219eb22ff2776bce3157ce53cf9fc7139860b3fb')
    # pro = ts.pro_api()
    look_stocks = []
    hs300_stocks = query_hs300()
    for index, row in hs300_stocks.iterrows():
        code = row['code']
        xcode = code.replace('sh.', '').replace('sz.', '')
        param_code = code.replace('.', '')  # 证券代码编码兼容处理
        if xcode.startswith('60') or xcode.startswith('00'):
            # df10 = get_price(param_code, frequency='1d', count=10)
            # 当前日期
            end_date = datetime.datetime.now().strftime('%Y-%m-%d')
            # 开始日期为当前日期往前15天
            start_date = (datetime.datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d')
            # df10 = pro.query('daily', ts_code=transform_code(code), start_date=start_date, end_date=end_date)
            # df10 = query_stock(code,start_date,end_date)
            df10 = get_price_day_tx(param_code, count=15)
            cur_index = len(df10) - 1
            # cur_index = 0
            cur_date = df10.iloc[cur_index]['time']
            if end_date != cur_date:
                continue
            cur_open = df10.iloc[cur_index]['open']
            cur_close = df10.iloc[cur_index]['close']
            cur_high = df10.iloc[cur_index]['high']
            cur_low = df10.iloc[cur_index]['low']
            # 获取最近五天的收盘价数据
            five_day_closes = df10.iloc[cur_index - 4: cur_index + 1]['close']
            # 计算五日均线价格
            five_day_avg_price = five_day_closes.mean()
            if not (cur_close > five_day_avg_price > cur_open):
                # 非 上穿均线的情况，不考虑
                continue
            # 计算上影线
            upper_shadow = cur_high - max(cur_open, cur_close)
            # 计算下影线
            lower_shadow = min(cur_open, cur_close) - cur_low
            cur_volume = df10.iloc[cur_index]['volume']
            pre_volume = df10.iloc[cur_index - 1]['volume']
            min_low_10days = df10['low'].min()
            if upper_shadow > 0 and lower_shadow > 0 and cur_close > cur_open and cur_low == min_low_10days and lower_shadow > upper_shadow * 2 and cur_volume > pre_volume:
                # Calculate lower shadow ratio
                lower_shadow_ratio = (min(cur_open, cur_close) - cur_low) / min(cur_open, cur_close)
                # Append relevant information to look_stocks
                look_stocks.append({
                    'code': code,
                    'xcode':xcode,
                    'date': cur_date,
                    'open': cur_open,
                    'close': cur_close,
                    'low': cur_low,
                    'high':cur_high,
                    'volume':cur_volume,
                    'lower_shadow_ratio': lower_shadow_ratio
                })
        time.sleep(1)
    if look_stocks:
        max_lower_shadow_stock = max(look_stocks, key=lambda x: x['lower_shadow_ratio'])
        print(f"Stock with maximum lower shadow ratio: {max_lower_shadow_stock}")
        # 将结果存入 Redis，使用 JSON 序列化
        return max_lower_shadow_stock
    else:
        print("No stocks found.")

    end_time = time.time()
    print("filter stock execution time:", end_time - start_time)

# stock = filter_stocks()
# print(stock)
# redis_client.set('filter_stock_info', json.dumps(stock))
# stock_info = get_price_day_tx("sh601618")
# print(stock_info)
# stock = get_cache('filter_stock_info')
# print(stock)
# print(stock['code'])
