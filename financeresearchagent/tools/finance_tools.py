"""
财经数据工具库

提供股票价格、基本面、财务数据等的获取功能。
使用yfinance库作为主要数据源。
"""

from typing import Optional, Dict, Any
from langchain.tools import tool

# 导入 yfinance 修复模块
from financieresearchagent.utils.ssl_fix import get_yfinance_ticker

import pandas as pd
from datetime import datetime, timedelta


@tool
def get_stock_price(symbol: str, period: str = "1y", interval: str = "1d") -> str:
    """
    获取股票历史价格数据。

    Args:
        symbol: 股票代码，如 "AAPL", "MSFT", "GOOGL"
        period: 时间周期，可选值为 "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
        interval: 数据间隔，可选值为 "1m", "2m", "5m", "15m", "30m", "60m", "1d", "1wk", "1mo"

    Returns:
        股票历史价格数据的字符串表示，格式为表格形式
    """
    try:
        stock = get_yfinance_ticker(symbol)
        hist = stock.history(period=period, interval=interval)

        if hist.empty:
            return f"无法获取 {symbol} 的股票价格数据"

        # 格式化输出
        hist_formatted = hist.reset_index()
        hist_formatted['Date'] = hist_formatted['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')

        return f"股票 {symbol} 历史价格数据 (周期: {period}, 间隔: {interval}):\n{hist_formatted.to_string(index=False)}"
    except Exception as e:
        return f"获取股票价格失败: {str(e)}"


@tool
def get_stock_info(symbol: str) -> str:
    """
    获取股票的基本信息。

    Args:
        symbol: 股票代码，如 "AAPL", "MSFT", "GOOGL"

    Returns:
        股票基本信息的字符串表示
    """
    try:
        stock = get_yfinance_ticker(symbol)
        info = stock.info

        if not info:
            return f"无法获取 {symbol} 的股票信息"

        # 提取关键信息
        key_fields = [
            'symbol', 'shortName', 'longName', 'sector', 'industry',
            'marketCap', 'enterpriseValue', 'totalRevenue', 'grossMargins',
            'profitMargins', 'operatingMargins', 'ebitdaMargins',
            'peRatio', 'pegRatio', 'payoutRatio', 'currentRatio', 'quickRatio',
            'debtToEquity', 'returnOnAssets', 'returnOnEquity',
            'beta', '52WeekChange', '52WeekHigh', '52WeekLow',
            'dividendYield', 'dividendRate', 'exDividendDate',
            'targetMeanPrice', 'recommendationKey', 'numberOfAnalystOpinions',
            'earningsGrowth', 'revenueGrowth', 'earningsDate',
            'priceToBook', 'priceToSalesTrailing12Months', 'bookValue',
            'ISIN', 'exchange', 'quoteType', 'currency'
        ]

        result = f"股票 {symbol} 基本信息:\n"
        for field in key_fields:
            if field in info and info[field] is not None:
                value = info[field]
                # 格式化数值
                if field in ['marketCap', 'enterpriseValue', 'totalRevenue', 'bookValue']:
                    value = _format_large_number(value)
                elif isinstance(value, float) and field not in ['beta', '52WeekChange']:
                    value = f"{value:.4f}"
                result += f"  {field}: {value}\n"

        return result
    except Exception as e:
        return f"获取股票信息失败: {str(e)}"


@tool
def get_financial_data(symbol: str, frequency: str = "annual") -> str:
    """
    获取财务报表数据。

    Args:
        symbol: 股票代码，如 "AAPL", "MSFT", "GOOGL"
        frequency: 财报频率，可选值为 "annual" (年度), "quarterly" (季度)

    Returns:
        财务报表数据的字符串表示
    """
    try:
        stock = get_yfinance_ticker(symbol)
        result = f"股票 {symbol} 财务报表数据:\n"

        # 获取利润表
        if frequency == "annual":
            financials = stock.financials
            if financials is not None and not financials.empty:
                result += f"\n利润表 (年度):\n{financials.to_string()}"
        else:
            financials = stock.quarterly_financials
            if financials is not None and not financials.empty:
                result += f"\n利润表 (季度):\n{financials.to_string()}"

        # 获取资产负债表
        balance_sheet = stock.balance_sheet
        if balance_sheet is not None and not balance_sheet.empty:
            if frequency == "annual":
                result += f"\n\n资产负债表 (年度):\n{balance_sheet.to_string()}"
            else:
                quarterly_bs = stock.quarterly_balance_sheet
                if quarterly_bs is not None and not quarterly_bs.empty:
                    result += f"\n\n资产负债表 (季度):\n{quarterly_bs.to_string()}"

        # 获取现金流量表
        cashflow = stock.cashflow
        if cashflow is not None and not cashflow.empty:
            if frequency == "annual":
                result += f"\n\n现金流量表 (年度):\n{cashflow.to_string()}"
            else:
                quarterly_cf = stock.quarterly_cashflow
                if quarterly_cf is not None and not quarterly_cf.empty:
                    result += f"\n\n现金流量表 (季度):\n{quarterly_cf.to_string()}"

        return result
    except Exception as e:
        return f"获取财务报表数据失败: {str(e)}"


@tool
def get_stock_news(symbol: str, max_results: int = 10) -> str:
    """
    获取股票的最近新闻。

    Args:
        symbol: 股票代码，如 "AAPL", "MSFT", "GOOGL"
        max_results: 最大返回新闻数量，默认10条

    Returns:
        股票新闻的字符串表示
    """
    try:
        stock = get_yfinance_ticker(symbol)
        news = stock.news

        if not news:
            return f"无法获取 {symbol} 的新闻"

        result = f"股票 {symbol} 最近新闻:\n"
        for i, item in enumerate(news[:max_results], 1):
            title = item.get('title', 'N/A')
            publisher = item.get('publisher', 'N/A')
            link = item.get('link', 'N/A')
            published = item.get('published', 'N/A')

            result += f"\n{i}. {title}\n"
            result += f"   来源: {publisher}\n"
            result += f"   发布时间: {published}\n"
            result += f"   链接: {link}\n"

        return result
    except Exception as e:
        return f"获取股票新闻失败: {str(e)}"


@tool
def get_market_summary(symbols: Optional[list] = None) -> str:
    """
    获取市场概况信息和指定股票的价格汇总。

    Args:
        symbols: 股票代码列表，如果为空则返回主要市场指数

    Returns:
        市场概况的字符串表示
    """
    try:
        result = ""

        if symbols is None or len(symbols) == 0:
            # 返回主要市场指数
            indices = {
                '^GSPC': 'S&P 500',
                '^DJI': '道琼斯工业指数',
                '^IXIC': '纳斯达克综合指数',
                '^RUT': '罗素2000指数',
                '^VIX': 'VIX恐慌指数'
            }

            result += "主要市场指数:\n"
            for symbol, name in indices.items():
                index = get_yfinance_ticker(symbol)
                hist = index.history(period="2d")

                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
                    change = ((current - prev) / prev) * 100
                    change_str = f"+{change:.2f}%" if change >= 0 else f"{change:.2f}%"
                    result += f"  {name} ({symbol}): {current:.2f} ({change_str})\n"
        else:
            # 返回指定股票的价格信息
            result += "股票价格汇总:\n"
            for symbol in symbols:
                stock = get_yfinance_ticker(symbol)
                info = stock.info
                hist = stock.history(period="2d")

                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
                    change = ((current - prev) / prev) * 100

                    short_name = info.get('shortName', symbol) if info else symbol
                    change_str = f"+{change:.2f}%" if change >= 0 else f"{change:.2f}%"
                    result += f"  {short_name} ({symbol}): ${current:.2f} ({change_str})\n"

        return result
    except Exception as e:
        return f"获取市场概况失败: {str(e)}"


@tool
def get_dividends_and_splits(symbol: str) -> str:
    """
    获取股票的分红和拆股信息。

    Args:
        symbol: 股票代码，如 "AAPL", "MSFT", "GOOGL"

    Returns:
        分红和拆股信息的字符串表示
    """
    try:
        stock = get_yfinance_ticker(symbol)
        result = f"股票 {symbol} 分红和拆股信息:\n"

        # 获取分红历史
        dividends = stock.dividends
        if dividends is not None and not dividends.empty:
            result += f"\n分红历史:\n{dividends.to_string()}"
        else:
            result += "\n分红历史: 无"

        # 获取拆股历史
        splits = stock.splits
        if splits is not None and not splits.empty:
            result += f"\n\n拆股历史:\n{splits.to_string()}"
        else:
            result += "\n拆股历史: 无"

        return result
    except Exception as e:
        return f"获取分红和拆股信息失败: {str(e)}"


@tool
def get_institutional_holders(symbol: str) -> str:
    """
    获取股票的机构持仓信息。

    Args:
        symbol: 股票代码，如 "AAPL", "MSFT", "GOOGL"

    Returns:
        机构持仓信息的字符串表示
    """
    try:
        stock = get_yfinance_ticker(symbol)
        holders = stock.institutional_holders

        if holders is None or holders.empty:
            return f"无法获取 {symbol} 的机构持仓信息"

        # 格式化输出
        result = f"股票 {symbol} 机构持仓信息:\n"
        result += f"总机构持股比例: {holders['pctHeld'].sum():.2f}%\n\n"
        result += holders.to_string(index=False)

        return result
    except Exception as e:
        return f"获取机构持仓信息失败: {str(e)}"


@tool
def get_mutualfund_holders(symbol: str) -> str:
    """
    获取股票的共同基金持仓信息。

    Args:
        symbol: 股票代码，如 "AAPL", "MSFT", "GOOGL"

    Returns:
        共同基金持仓信息的字符串表示
    """
    try:
        stock = get_yfinance_ticker(symbol)
        holders = stock.mutualfund_holders

        if holders is None or holders.empty:
            return f"无法获取 {symbol} 的共同基金持仓信息"

        # 格式化输出
        result = f"股票 {symbol} 共同基金持仓信息:\n"
        result += holders.to_string(index=False)

        return result
    except Exception as e:
        return f"获取共同基金持仓信息失败: {str(e)}"


@tool
def get_earnings_history(symbol: str) -> str:
    """
    获取股票的 earnings 历史记录。

    Args:
        symbol: 股票代码，如 "AAPL", "MSFT", "GOOGL"

    Returns:
        盈利历史信息的字符串表示
    """
    try:
        stock = get_yfinance_ticker(symbol)
        earnings = stock.earnings

        if earnings is None or earnings.empty:
            return f"无法获取 {symbol} 的盈利历史"

        result = f"股票 {symbol} 盈利历史:\n{earnings.to_string()}"
        return result
    except Exception as e:
        return f"获取盈利历史失败: {str(e)}"


@tool
def get_earnings_dates(symbol: str, max_results: int = 10) -> str:
    """
    获取股票的未来和历史财报发布日期。

    Args:
        symbol: 股票代码，如 "AAPL", "MSFT", "GOOGL"
        max_results: 最大返回数量，默认10条

    Returns:
        财报发布日期的字符串表示
    """
    try:
        stock = get_yfinance_ticker(symbol)
        earnings_dates = stock.earnings_dates

        if earnings_dates is None or earnings_dates.empty:
            return f"无法获取 {symbol} 的财报发布日期"

        # 限制结果数量
        if len(earnings_dates) > max_results:
            earnings_dates = earnings_dates.head(max_results)

        result = f"股票 {symbol} 财报发布日期 (未来/历史):\n"
        result += earnings_dates.to_string()

        return result
    except Exception as e:
        return f"获取财报发布日期失败: {str(e)}"


def _format_large_number(value: float) -> str:
    """
    格式化大数字（如市值、营收）使其更易读。

    Args:
        value: 数值

    Returns:
        格式化后的字符串
    """
    if value >= 1e12:
        return f"${value/1e12:.2f}T"
    elif value >= 1e9:
        return f"${value/1e9:.2f}B"
    elif value >= 1e6:
        return f"${value/1e6:.2f}M"
    elif value >= 1e3:
        return f"${value/1e3:.2f}K"
    else:
        return f"${value:.2f}"