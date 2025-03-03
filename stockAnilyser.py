import asyncio
import time
import akshare as ak
import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt
import aiohttp

# 设置股票代码（A股 6 位代码）
STOCK_CODE = "002896"  # 中大力德

# 数据缓存
stock_data_cache = None
# 保留 Figure 和 Axes 对象
fig, axes = None, None

# ================= 计算技术指标 =================
def calculate_ma(df, periods=[5, 10, 20]):
    """计算均线（MA）"""
    for period in periods:
        df[f"MA{period}"] = df["Close"].rolling(window=period).mean()
    return df

def calculate_macd(df):
    """计算 MACD 指标"""
    df["EMA12"] = df["Close"].ewm(span=12, adjust=False).mean()
    df["EMA26"] = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = df["EMA12"] - df["EMA26"]
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    return df

def calculate_rsi(df, period=14):
    """计算 RSI 指标"""
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df

# ================= 获取股票数据 =================
async def get_stock_data_async(stock_code):
    global stock_data_cache
    try:
        async with aiohttp.ClientSession() as session:
            # 这里只是示例，实际 akshare 可能不支持 aiohttp，可根据实际情况修改
            # 简单模拟异步获取数据
            await asyncio.sleep(0.1)
            df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="qfq")
            if len(df.columns) == 12:
                df.columns = ["日期", "开盘", "收盘", "最高", "最低", "成交量", "成交额", "振幅", "涨跌幅", "涨跌额", "换手率", "未知列"]
            else:
                print(f"返回的 DataFrame 列数异常，实际列数: {len(df.columns)}")
                return stock_data_cache

            # 转换日期格式
            df["日期"] = pd.to_datetime(df["日期"])
            df.set_index("日期", inplace=True)

            # 转换为 mplfinance 所需的列名
            df.rename(columns={
                "开盘": "Open",
                "收盘": "Close",
                "最高": "High",
                "最低": "Low",
                "成交量": "Volume"
            }, inplace=True)

            # 转换数据类型为数值类型
            columns_to_convert = ["Open", "High", "Low", "Close", "Volume"]
            for col in columns_to_convert:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # 计算技术指标
            df = calculate_ma(df)
            df = calculate_macd(df)
            df = calculate_rsi(df)

            stock_data_cache = df
            return df
    except Exception as e:
        print(f"数据获取失败: {e}")
        return stock_data_cache

# ================= 绘制股票 K 线图 =================
def plot_stock(df, stock_code):
    global fig, axes
    """绘制股票 K 线图 + 技术指标"""
    if df is not None:
        add_plots = [
            mpf.make_addplot(df["MACD"], panel=1, color='r', secondary_y=False),
            mpf.make_addplot(df["Signal"], panel=1, color='b', secondary_y=False),
            mpf.make_addplot(df["RSI"], panel=2, color='g', secondary_y=False)
        ]

        if fig is None:
            # 如果 Figure 不存在，创建新的 Figure 和 Axes
            fig, axes = mpf.plot(df, type='candle', style='charles', volume=True,
                                 mav=(5, 10, 20), title=f"{stock_code} K线图",
                                 ylabel="价格", ylabel_lower="成交量",
                                 addplot=add_plots, panel_ratios=(3, 1, 1), returnfig=True)
        else:
            # 如果 Figure 已存在，清除 Axes 并重新绘制
            for ax in axes:
                ax.clear()
            mpf.plot(df, type='candle', style='charles',
                     mav=(5, 10, 20), title=f"{stock_code} K线图",
                     ylabel="价格", ylabel_lower="成交量",
                     addplot=add_plots, panel_ratios=(3, 1, 1), ax=axes[0], volume=axes[4])
            fig.canvas.draw_idle()

# ================= 实时监控 =================
async def real_time_monitor(stock_code, refresh_interval=10):
    """实时监控 A 股股票，自动刷新"""
    plt.ion()  # 开启交互模式
    while True:
        df = await get_stock_data_async(stock_code)
        plot_stock(df, stock_code)
        plt.pause(0.001)  # 暂停一小段时间，让图形更新

        print(f"已更新 {stock_code} 数据，等待 {refresh_interval} 秒后刷新...")
        await asyncio.sleep(refresh_interval)

# 运行实时监控
if __name__ == "__main__":
    asyncio.run(real_time_monitor(STOCK_CODE))