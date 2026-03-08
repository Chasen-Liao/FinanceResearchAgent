"""
分析工具库

提供技术分析和基本面分析功能。
"""

from typing import Optional, Dict, Any
from langchain.tools import tool

# 导入 yfinance 修复模块
from financieresearchagent.utils.ssl_fix import get_yfinance_ticker

import pandas as pd
import numpy as np


@tool
def calculate_technical_indicators(symbol: str, period: str = "6mo") -> str:
    """
    计算股票的技术分析指标。

    Args:
        symbol: 股票代码，如 "AAPL", "MSFT"
        period: 时间周期，可选值为 "1mo", "3mo", "6mo", "1y", "2y"

    Returns:
        技术指标的字符串表示
    """
    try:
        stock = get_yfinance_ticker(symbol)
        hist = stock.history(period=period)

        if hist.empty:
            return f"无法获取 {symbol} 的历史数据"

        close = hist['Close']

        # 计算技术指标
        result = f"股票 {symbol} 技术分析指标 (周期: {period}):\n\n"

        # 移动平均线
        ma5 = close.rolling(window=5).mean()
        ma10 = close.rolling(window=10).mean()
        ma20 = close.rolling(window=20).mean()
        ma60 = close.rolling(window=60).mean()

        result += "【移动平均线】\n"
        result += f"  MA5:  ${ma5.iloc[-1]:.2f}\n"
        result += f"  MA10: ${ma10.iloc[-1]:.2f}\n"
        result += f"  MA20: ${ma20.iloc[-1]:.2f}\n"
        result += f"  MA60: ${ma60.iloc[-1]:.2f}\n\n"

        # RSI (相对强弱指数)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        result += "【RSI 相对强弱指数】\n"
        result += f"  RSI(14): {rsi.iloc[-1]:.2f}\n"
        if rsi.iloc[-1] > 70:
            result += "  信号: 超买区域，可能面临调整\n"
        elif rsi.iloc[-1] < 30:
            result += "  信号: 超卖区域，可能出现反弹\n"
        else:
            result += "  信号: 中性区域\n"

        # MACD
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        macd_hist = macd_line - signal_line

        result += "\n【MACD 指数平滑异同移动平均线】\n"
        result += f"  DIF (MACD线): {macd_line.iloc[-1]:.4f}\n"
        result += f"  DEA (信号线): {signal_line.iloc[-1]:.4f}\n"
        result += f"  MACD柱: {macd_hist.iloc[-1]:.4f}\n"

        # 布林带
        bb_middle = close.rolling(window=20).mean()
        bb_std = close.rolling(window=20).std()
        bb_upper = bb_middle + (bb_std * 2)
        bb_lower = bb_middle - (bb_std * 2)

        result += "\n【布林带】\n"
        result += f"  上轨: ${bb_upper.iloc[-1]:.2f}\n"
        result += f"  中轨: ${bb_middle.iloc[-1]:.2f}\n"
        result += f"  下轨: ${bb_lower.iloc[-1]:.2f}\n"

        # 成交量分析
        volume = hist['Volume']
        avg_volume = volume.rolling(window=20).mean()

        result += "\n【成交量分析】\n"
        result += f"  当前成交量: {volume.iloc[-1]:,.0f}\n"
        result += f"  20日均量: {avg_volume.iloc[-1]:,.0f}\n"

        return result
    except Exception as e:
        return f"计算技术指标失败: {str(e)}"


@tool
def analyze_fundamentals(symbol: str) -> str:
    """
    分析股票的基本面数据。

    Args:
        symbol: 股票代码，如 "AAPL", "MSFT"

    Returns:
        基本面分析结果的字符串表示
    """
    try:
        stock = get_yfinance_ticker(symbol)
        info = stock.info

        if not info:
            return f"无法获取 {symbol} 的基本面数据"

        result = f"股票 {symbol} 基本面分析:\n\n"

        # 估值指标
        result += "【估值指标】\n"
        if 'peRatio' in info and info['peRatio']:
            result += f"  市盈率 (P/E): {info['peRatio']:.2f}\n"
        if 'pegRatio' in info and info['pegRatio']:
            result += f"  PEG比率: {info['pegRatio']:.2f}\n"
        if 'priceToBook' in info and info['priceToBook']:
            result += f"  市净率 (P/B): {info['priceToBook']:.2f}\n"
        if 'priceToSalesTrailing12Months' in info and info['priceToSalesTrailing12Months']:
            result += f"  市销率 (P/S): {info['priceToSalesTrailing12Months']:.2f}\n"

        # 盈利能力
        result += "\n【盈利能力】\n"
        if 'profitMargins' in info and info['profitMargins']:
            result += f"  净利润率: {info['profitMargins']*100:.2f}%\n"
        if 'grossMargins' in info and info['grossMargins']:
            result += f"  毛利率: {info['grossMargins']*100:.2f}%\n"
        if 'operatingMargins' in info and info['operatingMargins']:
            result += f"  营业利润率: {info['operatingMargins']*100:.2f}%\n"
        if 'returnOnEquity' in info and info['returnOnEquity']:
            result += f"  净资产收益率 (ROE): {info['returnOnEquity']*100:.2f}%\n"
        if 'returnOnAssets' in info and info['returnOnAssets']:
            result += f"  总资产收益率 (ROA): {info['returnOnAssets']*100:.2f}%\n"

        # 成长能力
        result += "\n【成长能力】\n"
        if 'revenueGrowth' in info and info['revenueGrowth']:
            result += f"  营收增长率: {info['revenueGrowth']*100:.2f}%\n"
        if 'earningsGrowth' in info and info['earningsGrowth']:
            result += f"  盈利增长率: {info['earningsGrowth']*100:.2f}%\n"

        # 财务健康
        result += "\n【财务健康】\n"
        if 'currentRatio' in info and info['currentRatio']:
            result += f"  流动比率: {info['currentRatio']:.2f}\n"
        if 'quickRatio' in info and info['quickRatio']:
            result += f"  速动比率: {info['quickRatio']:.2f}\n"
        if 'debtToEquity' in info and info['debtToEquity']:
            result += f"  负债权益比: {info['debtToEquity']:.2f}%\n"

        # 股息
        result += "\n【股息政策】\n"
        if 'dividendYield' in info and info['dividendYield']:
            result += f"  股息率: {info['dividendYield']*100:.2f}%\n"
        if 'dividendRate' in info and info['dividendRate']:
            result += f"  股息: ${info['dividendRate']:.2f}\n"
        if 'payoutRatio' in info and info['payoutRatio']:
            result += f"  派息比率: {info['payoutRatio']*100:.2f}%\n"

        return result
    except Exception as e:
        return f"分析基本面失败: {str(e)}"


@tool
def analyze_price_trend(symbol: str, period: str = "3mo") -> str:
    """
    分析股票价格趋势。

    Args:
        symbol: 股票代码
        period: 时间周期

    Returns:
        趋势分析结果的字符串表示
    """
    try:
        stock = get_yfinance_ticker(symbol)
        hist = stock.history(period=period)

        if hist.empty:
            return f"无法获取 {symbol} 的数据"

        close = hist['Close']
        current_price = close.iloc[-1]

        # 计算各种均线
        ma5 = close.rolling(5).mean().iloc[-1]
        ma20 = close.rolling(20).mean().iloc[-1]
        ma60 = close.rolling(60).mean().iloc[-1]

        # 计算涨跌幅
        change_1d = ((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100 if len(close) > 1 else 0
        change_1w = ((close.iloc[-1] - close.iloc[-5]) / close.iloc[-5]) * 100 if len(close) > 5 else 0
        change_1m = ((close.iloc[-1] - close.iloc[-22]) / close.iloc[-22]) * 100 if len(close) > 22 else 0

        result = f"股票 {symbol} 趋势分析 (周期: {period}):\n\n"
        result += f"当前价格: ${current_price:.2f}\n\n"

        result += "【涨跌幅】\n"
        result += f"  日涨跌: {change_1d:+.2f}%\n"
        result += f"  周涨跌: {change_1w:+.2f}%\n"
        result += f"  月涨跌: {change_1m:+.2f}%\n\n"

        result += "【均线位置】\n"
        result += f"  当前价格 vs MA5: {'高于' if current_price > ma5 else '低于'} ${abs(current_price - ma5):.2f}\n"
        result += f"  当前价格 vs MA20: {'高于' if current_price > ma20 else '低于'} ${abs(current_price - ma20):.2f}\n"
        result += f"  当前价格 vs MA60: {'高于' if current_price > ma60 else '低于'} ${abs(current_price - ma60):.2f}\n\n"

        # 趋势判断
        result += "【趋势判断】\n"
        if current_price > ma5 > ma20 > ma60:
            result += "  整体趋势: 强势上涨趋势（多头排列）\n"
        elif current_price < ma5 < ma20 < ma60:
            result += "  整体趋势: 弱势下跌趋势（空头排列）\n"
        elif current_price > ma5 and ma5 > ma20:
            result += "  整体趋势: 短期上涨趋势\n"
        elif current_price < ma5 and ma5 < ma20:
            result += "  整体趋势: 短期下跌趋势\n"
        else:
            result += "  整体趋势: 震荡整理\n"

        return result
    except Exception as e:
        return f"分析价格趋势失败: {str(e)}"


@tool
def calculate_volatility(symbol: str, period: str = "1y") -> str:
    """
    计算股票波动率指标。

    Args:
        symbol: 股票代码
        period: 时间周期

    Returns:
        波动率分析结果的字符串表示
    """
    try:
        stock = get_yfinance_ticker(symbol)
        hist = stock.history(period=period)

        if hist.empty:
            return f"无法获取 {symbol} 的数据"

        close = hist['Close']
        returns = close.pct_change().dropna()

        result = f"股票 {symbol} 波动率分析 (周期: {period}):\n\n"

        # 日波动率
        daily_volatility = returns.std()
        result += f"日波动率: {daily_volatility*100:.4f}%\n"

        # 年化波动率
        annualized_volatility = daily_volatility * (252 ** 0.5)
        result += f"年化波动率: {annualized_volatility*100:.2f}%\n"

        # 历史高低价
        high = close.max()
        low = close.min()
        current = close.iloc[-1]
        position = ((current - low) / (high - low)) * 100

        result += f"\n【价格区间】\n"
        result += f"  最高价: ${high:.2f}\n"
        result += f"  最低价: ${low:.2f}\n"
        result += f"  当前价格: ${current:.2f}\n"
        result += f"  当前位置: {position:.1f}% (从低点到当前)\n"

        # Beta值
        if 'beta' in stock.info and stock.info['beta']:
            beta = stock.info['beta']
            result += f"\n【Beta系数】\n"
            result += f"  Beta: {beta:.2f}\n"
            if beta > 1.5:
                result += "  解读: 高于市场波动性\n"
            elif beta < 0.8:
                result += "  解读: 低于市场波动性\n"
            else:
                result += "  解读: 与市场波动性相近\n"

        return result
    except Exception as e:
        return f"计算波动率失败: {str(e)}"