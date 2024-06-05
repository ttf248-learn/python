# https://zhuanlan.zhihu.com/p/660010862
# 代码分为两个主要函数：json_to_dfcf 和 generate_stat_data。
# 第一个函数负责通过东方财富 API 获取 K 线数据，而第二个函数负责计算 16 种不同的技术指标。

# 其余的二十多个函数为计算技术指标的函数，不过多的阐述，详情见代码。

# json_to_dfcf 函数： 
# 通过东方财富 API 获取指定股票的 K 线数据，并将其转换为 Pandas DataFrame。 使用 requests 库发送 HTTP 请求，并解析返回的 JSON 数据以获取 K 线数据。

# generate_stat_data 函数： 
# 调用 json_to_dfcf 函数获取数据。 计算多个移动平均线、指数移动平均线、市场宽度指标等技术指标。 使用 Pandas 的 concat 函数将所有指标合并到一个 DataFrame 中。 （可选）将数据导出到 CSV 文件。

import pandas as pd
import requests
import numpy as np
import json
from scipy import stats
from datetime import datetime, timedelta
import sqlite3
import math

# 通过东方财富api获取K线数据
def json_to_dfcf(secid):     # 参数参考我的东方财富api文档
    today = datetime.now().date()   # 获取当前时间
    start_date = (today - timedelta(days=2555)).strftime('%Y%m%d')    # 获取多少年之前的时间
    end_date = today.strftime('%Y%m%d')     # 对今天的时间设置取结束时间，总设定格式 
    url = f'http://push2his.eastmoney.com/api/qt/stock/kline/get?&secid={secid}&fields1=f1,f3&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&beg={start_date}&end={end_date}'
    response = requests.get(url)
    data = response.json()['data']['klines']    # 获取json数据下的'data'，再获取'data'下的'klines'数据
    data = [x.split(',') for x in data]     # 数据以','，将数据循环的放到pandas中
    column_names = ['datetime', 'open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude', 'change_percent', 'change_amount', 'turnover_ratio']
    df = pd.DataFrame(data, columns=column_names, dtype=float)
    return df

# 获取简单移动平均线，参数有2个，一个是数据源，一个是日期
def MA(data, n):
    MA = pd.Series(data['close'].rolling(n).mean(), name='MA_' + str(n))
    return MA.dropna()

# 获取指数移动平均线，参数有2个，一个是数据源，一个是日期
def EMA(data, n):
    EMA = pd.Series(data['close'].ewm(span=n, min_periods=n).mean(), name='EMA_' + str(n))
    return EMA.dropna()

# 获取一目均衡表基准线 (data, conversion_periods, base_periods, lagging_span2_periods, displacement)
# 参数有5个，第一个是数据源，其他4个分别是一目均衡表基准线 (9, 26, 52, 26)，即ichimoku_cloud(data,9, 26, 52, 26)
def ichimoku_cloud(data, conversion_periods, base_periods, lagging_span2_periods, displacement):
    def donchian(length):
        return (data['high'].rolling(length).max() + data['low'].rolling(length).min()) / 2
    
    conversion_line = donchian(conversion_periods)
    base_line = donchian(base_periods)
    lead_line1 = (conversion_line + base_line) / 2
    lead_line2 = donchian(lagging_span2_periods)
    
    lagging_span = data['close'].shift(-displacement + 1).shift(25).ffill()
    leading_span_a = lead_line1.shift(displacement - 1)
    leading_span_b = lead_line2.shift(displacement - 1)
    
    ichimoku_data = pd.concat([conversion_line, base_line, lagging_span, lead_line1, lead_line2, leading_span_a, leading_span_b], axis=1)
    ichimoku_data.columns = ['Conversion Line', 'Base Line', 'Lagging Span', 'lead_line1', 'lead_line2', 'Leading Span A', 'Leading Span B']
    
    return ichimoku_data.dropna()

# 成交量加权移动平均线 VWMA (data, 20)，参数有2个，1个是数据源，另一个是日期，通过为20
def VWMA(data, n):
    VWMA = pd.Series((data['close'] * data['volume']).rolling(n).sum() / data['volume'].rolling(n).sum(), name='VWMA_' + str(n))
    return VWMA.dropna()

# 计算Hull MA船体移动平均线 Hull MA (data,9)，参数有2，一个是数据源，另一个是日期，一般为9
def HullMA(data, n=9):
    def wma(series, period):
        weights = np.arange(1, period + 1)
        return series.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)
    
    source = data['close']
    wma1 = wma(source, n // 2) * 2
    wma2 = wma(source, n)
    hullma = wma(wma1 - wma2, int(math.floor(math.sqrt(n))))
    return hullma.dropna()

# 计算RSI指标，参数有2，一个为数据源，另一个为日期，一般为14，即RSI(data, 14)
def RSI(data, n):
    lc = data['close'].shift(1)
    diff = data['close'] - lc
    up = diff.where(diff > 0, 0)
    down = -diff.where(diff < 0, 0)
    ema_up = up.ewm(alpha=1/n, adjust=False).mean()
    ema_down = down.ewm(alpha=1/n, adjust=False).mean()
    rs = ema_up / ema_down
    rsi = 100 - 100 / (1 + rs)
    return pd.Series(rsi, name='RSI_' + str(n)).dropna()


def STOK(data, n, m, t):
    # 计算过去n天的最高价
    high = data['high'].rolling(n).max()
    # 计算过去n天的最低价
    low = data['low'].rolling(n).min()
    # 计算%K值
    k = 100 * (data['close'] - low) / (high - low)
    # 使用m天的滚动平均计算%D值
    d = k.rolling(m).mean()
    # 使用t天的滚动平均计算%D_signal值
    d_signal = d.rolling(t).mean()
    # 将计算结果保存到data DataFrame中
    data['%K'] = k
    data['%D'] = d
    data['%D_signal'] = d_signal
    # 返回不包含NaN值的结果
    return data[['%K', '%D', '%D_signal']].dropna()


# 计算CCI指标，参数有2，一个是数据源，另一个是日期，一般为20，即CCI(data, 20)
def CCI(data, n):
    TP = (data['high'] + data['low'] + data['close']) / 3
    MA = TP.rolling(n).mean()
    MD = TP.rolling(n).apply(lambda x: np.abs(x - x.mean()).mean())
    CCI = (TP - MA) / (0.015 * MD)
    return pd.Series(CCI, name='CCI_' + str(n)).dropna()

# 平均趋向指数ADX(14)，参数有2，一个是数据源，另一个是日期，一般为14，即ADX(data,14)
def ADX(data, n):
    up = data['high'] - data['high'].shift(1)
    down = data['low'].shift(1) - data['low']
    plusDM = pd.Series(np.where((up > down) & (up > 0), up, 0))
    minusDM = pd.Series(np.where((down > up) & (down > 0), down, 0))
    truerange = np.maximum(data['high'] - data['low'], np.maximum(np.abs(data['high'] - data['close'].shift()), np.abs(data['low'] - data['close'].shift())))
    plus = 100 * plusDM.ewm(alpha=1/n, min_periods=n).mean() / truerange.ewm(alpha=1/n, min_periods=n).mean()
    minus = 100 * minusDM.ewm(alpha=1/n, min_periods=n).mean() / truerange.ewm(alpha=1/n, min_periods=n).mean()
    sum = plus + minus
    adx = 100 * (np.abs(plus - minus) / np.where(sum == 0, 1, sum)).ewm(alpha=1/n, min_periods=n).mean()
    return pd.Series(adx, name='ADX').dropna()

# 计算动量震荡指标(AO)，参数只有一个，即数据源
def AO(data):
    data['AO'] = (data['high'].rolling(5).mean() + data['low'].rolling(5).mean()) / 2 - (data['high'].rolling(34).mean() + data['low'].rolling(34).mean()) / 2
    return data['AO'].dropna()

# 计算动量指标(10)，参数只有一个，即数据源
def MTM(data):
    data['MTM'] = data['close'] - data['close'].shift(10)
    return data['MTM'].dropna()


# 计算MACD Lvel指标，参数有3个，第一个是数据源，其余两个为日期，一般取12和26，即MACD_Level(data, 12,26)
def MACD_Level(data, n_fast, n_slow):
    EMAfast = data['close'].ewm(span=n_fast, min_periods=n_slow).mean()
    EMAslow = data['close'].ewm(span=n_slow, min_periods=n_slow).mean()
    data['MACD'] = EMAfast - EMAslow
    data['MACDsignal'] = data['MACD'].ewm(span=9, min_periods=9).mean()
    data['MACDhist'] = data['MACD'] - data['MACDsignal']
    return data[['MACD', 'MACDsignal', 'MACDhist']].dropna()


# 计算Stoch_RSI(data,3, 3, 14, 14)，有5个参数，第1个为数据源
def Stoch_RSI(data, smoothK, smoothD, lengthRSI, lengthStoch):
    # 计算RSI
    lc = data['close'].shift(1)
    diff = data['close'] - lc
    up = diff.where(diff > 0, 0)
    down = -diff.where(diff < 0, 0)
    ema_up = up.ewm(alpha=1/lengthRSI, adjust=False).mean()
    ema_down = down.ewm(alpha=1/lengthRSI, adjust=False).mean()
    rs = ema_up / ema_down
    rsi = 100 - 100 / (1 + rs)
    # 计算Stochastic
    stoch = (rsi - rsi.rolling(window=lengthStoch).min()) / (rsi.rolling(window=lengthStoch).max() - rsi.rolling(window=lengthStoch).min())
    k = stoch.rolling(window=smoothK).mean()
    d = k.rolling(window=smoothD).mean()
    # 添加到data中
    data['Stoch_RSI_K'] = k * 100
    data['Stoch_RSI_D'] = d * 100
    return data[['Stoch_RSI_K', 'Stoch_RSI_D']].dropna()

# 计算威廉百分比变动，参数有2，第1是数据源，第二是日期，一般为14，即WPR(data, 14)
def WPR(data, n):
    WPR = pd.Series((data['high'].rolling(n).max() - data['close']) / (data['high'].rolling(n).max() - data['low'].rolling(n).min()) * -100, name='WPR_' + str(n))
    return WPR.dropna()

# 计算Bull Bear Power牛熊力量(BBP)，参数有2，一个是数据源，另一个是日期，一般为20，但在tradingview取13，即BBP(data, 13)
def BBP(data, n):
    bullPower = data['high'] - data['close'].ewm(span=n).mean()
    bearPower = data['low'] - data['close'].ewm(span=n).mean()
    BBP = bullPower + bearPower
    data['BBP'] = BBP
    return data['BBP'].dropna()

# 计算Ultimate Oscillator终极震荡指标UO (data,7, 14, 28)，有4个参数，第1个是数据源，其他的是日期
def UO(data, n1, n2, n3):
    min_low_or_close = pd.concat([data['low'], data['close'].shift(1)], axis=1).min(axis=1)
    max_high_or_close = pd.concat([data['high'], data['close'].shift(1)], axis=1).max(axis=1)
    bp = data['close'] - min_low_or_close
    tr_ = max_high_or_close - min_low_or_close
    avg7 = bp.rolling(n1).sum() / tr_.rolling(n1).sum()
    avg14 = bp.rolling(n2).sum() / tr_.rolling(n2).sum()
    avg28 = bp.rolling(n3).sum() / tr_.rolling(n3).sum()
    UO = 100 * ((4 * avg7) + (2 * avg14) + avg28) / 7
    data['UO'] = UO
    return data['UO'].dropna()

def linear_regression_dfcf(data, years_list):    # 参数分别为代码，种类和调取数据年份列表
    df_list = []    
    for many_years in years_list:   # 将调取年份列表放入循环
        percent = round(len(data)/7*many_years)
        y = data.iloc[-percent:]["close"]    # 调取自定义函数中的"close"列
        x = np.arange(len(y))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        expected_value = intercept + slope * len(y)     # 计算期望值
        residuals = y - (intercept + slope * x)     # 残差
        std_residuals = np.std(residuals)   # 残差标准差

        # 构建结果DataFrame
                # 构建结果DataFrame
        columns=[f"expected_value_{many_years}year", f"std_residuals_{many_years}year", f"slope_{many_years}year", f"intercept_{many_years}year", f"r_value_{many_years}year", f"p_value_{many_years}year", f"std_err_{many_years}year"]
        result_data = [expected_value, std_residuals, slope, intercept, r_value, p_value, std_err]
        # 上面数据分别表示线性回归期望值、残差标准差、斜率、截距、相关系数、P值、标准误差
        result_df = pd.DataFrame(data=[result_data], columns=columns)

        df_list.append(result_df)
    result = pd.concat(df_list, axis=1)
    return result

def generate_stat_data(stock_code):
    data = json_to_dfcf(stock_code)

    ma10 = MA(data, 10)
    ma20 = MA(data, 20)
    ma30 = MA(data, 30)
    ma50 = MA(data, 50)
    ma100 = MA(data, 100)
    ma200 = MA(data, 200)

    ema10 = EMA(data, 10)
    ema20 = EMA(data, 20)
    ema30 = EMA(data, 30)
    ema50 = EMA(data, 50)
    ema100 = EMA(data, 100)
    ema200 = EMA(data, 200)

    ic = ichimoku_cloud(data,9, 26, 52, 26)

    vwma = VWMA(data, 20)

    hm = HullMA(data, 9)

    rsi = RSI(data, 14)

    wpr = WPR(data, 14)

    cci = CCI(data, 20)

    adx = ADX(data, 14)

    lr = linear_regression_dfcf(data, [7,3,1])

    stok = STOK(data, 14, 3, 3)

    ao = AO(data)

    mtm = MTM(data)

    madc_level = MACD_Level(data, 12, 26)

    stoch_rsi = Stoch_RSI(data, 3, 3, 14, 14)

    bbp = BBP(data, 13)

    uo = UO(data, 7, 14, 28)

    stat_data = pd.concat([data, ma10, ma20, ma30, ma50, ma100, ma200, ema10, ema20, ema30, ema50, ema100, ema200, ic, vwma, hm, rsi,  cci, adx, wpr, stok, ao, mtm, madc_level, stoch_rsi, bbp, uo], axis=1)[-1:]
    stat_data.reset_index(drop=True, inplace=True)
    stat_data = pd.concat([stat_data.tail(1), lr], axis=1)
    stat_data.insert(0, 'code', stock_code)
    stat_data = stat_data.set_index('code')

    # 导出数据到CSV文件
    csv_filename = f'{stock_code}_stat_data.csv'
    stat_data.to_csv(csv_filename)

    return stat_data
    

def get_sqlite3():  # 保存到数据库
    conn = sqlite3.connect(r'D:\wenjian\python\xuexi\data\my_data.db')  # 连接sqlite3数据库
    cursor = conn.cursor()
    cursor.execute("SELECT 代码 FROM 沪深300严重低估")  # 执行sql语句，选择“代码”列
    codes = [str(row[0]) for row in cursor.fetchall()]  # 将查询结果转换为列表
    cursor.close()
    all_data = pd.DataFrame()
    for code in codes:
        if code.startswith('6'):  # 判断代码是否以6开头
            code = '1.' + code  # 如果是，前面加“1.”
        else:
            code = '0.' + code  # 如果不是，前面加“0.”
        ratios = generate_stat_data(code)  # 假设有一个名为get_valuation_ratios的函数，返回指定股票的估值比率数据。

        all_data = pd.concat([all_data, ratios])
    
    all_data.to_sql('价值线性回归', conn, if_exists='replace', index=True)  # 将all_data数据插入到sqlite3数据库的api线性回归表中
    conn.close()
    return all_data

# print(get_sqlite3())
print(generate_stat_data('0.000001'))