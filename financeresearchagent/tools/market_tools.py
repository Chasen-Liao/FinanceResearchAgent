"""
市场分析工具库

提供市场新闻、指数、板块分析等功能。
"""

from typing import Optional, List
from langchain.tools import tool

# 导入 yfinance 修复模块
from financieresearchagent.utils.ssl_fix import get_yfinance_ticker


@tool
def get_market_news(topic: Optional[str] = None, max_results: int = 10) -> str:
    """
    获取市场新闻。

    Args:
        topic: 可选，搜索特定话题/股票
        max_results: 最大返回数量

    Returns:
        市场新闻的字符串表示
    """
    try:
        from datetime import datetime, timedelta

        # 创建大市值的股票列表用于获取新闻
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM"]

        all_news = []

        # 尝试从多个股票获取新闻
        for symbol in symbols[:5]:
            try:
                stock = get_yfinance_ticker(symbol)
                news = stock.news
                if news:
                    for item in news[:2]:
                        item['symbol'] = symbol
                    all_news.extend(news[:2])
            except:
                continue

        if not all_news:
            return "无法获取市场新闻"

        # 按发布时间排序
        all_news = sorted(all_news, key=lambda x: x.get('published', ''), reverse=True)

        result = f"市场最新新闻 (共{len(all_news[:max_results])}条):\n"
        for i, item in enumerate(all_news[:max_results], 1):
            title = item.get('title', 'N/A')
            publisher = item.get('publisher', 'N/A')
            symbol = item.get('symbol', '')
            link = item.get('link', 'N/A')

            result += f"\n{i}. {title}\n"
            result += f"   来源: {publisher}"
            if symbol:
                result += f" | 股票: {symbol}"
            result += "\n"

        return result
    except Exception as e:
        return f"获取市场新闻失败: {str(e)}"


@tool
def get_market_indices() -> str:
    """
    获取主要市场指数的实时数据。

    Returns:
        市场指数数据的字符串表示
    """
    try:
        indices = {
            '^GSPC': ('S&P 500', '美国'),
            '^DJI': ('道琼斯工业指数', '美国'),
            '^IXIC': ('纳斯达克综合指数', '美国'),
            '^RUT': ('罗素2000指数', '美国'),
            '^VIX': ('VIX恐慌指数', '美国'),
            '000001.SS': ('上证指数', '中国'),
            'SZ399001.SZ': ('深证成指', '中国'),
            '^N225': ('日经225指数', '日本'),
            '^FTSE': ('富时100指数', '英国'),
            '^GDAXI': ('DAX指数', '德国'),
        }

        result = "全球主要市场指数:\n\n"

        for symbol, (name, country) in indices.items():
            try:
                index = get_yfinance_ticker(symbol)
                hist = index.history(period="2d")

                if not hist.empty and len(hist) >= 2:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2]
                    change = ((current - prev) / prev) * 100
                    change_str = f"+{change:.2f}%" if change >= 0 else f"{change:.2f}%"

                    result += f"{name} ({country}):\n"
                    result += f"  当前: {current:,.2f} ({change_str})\n\n"
            except:
                continue

        return result
    except Exception as e:
        return f"获取市场指数失败: {str(e)}"


@tool
def get_sector_performance() -> str:
    """
    获取各行业板块的表现。

    Returns:
        板块表现的字符串表示
    """
    try:
        # 使用ETF代表各行业板块
        sectors = {
            'XLK': ('科技板块', 'Technology'),
            'XLF': ('金融板块', 'Financials'),
            'XLE': ('能源板块', 'Energy'),
            'XLV': ('医疗保健', 'Healthcare'),
            'XLP': ('消费必需品', 'Consumer Staples'),
            'XLY': ('非必需消费', 'Consumer Discretionary'),
            'XLI': ('工业板块', 'Industrials'),
            'XLB': ('原材料', 'Materials'),
            'XLRE': ('房地产', 'Real Estate'),
            'XLC': ('通信服务', 'Communication Services'),
            'XLU': ('公用事业', 'Utilities'),
        }

        result = "S&P 500各板块表现 (近一个月):\n\n"

        for symbol, (cn_name, en_name) in sectors.items():
            try:
                etf = get_yfinance_ticker(symbol)
                hist = etf.history(period="1mo")

                if not hist.empty and len(hist) >= 2:
                    current = hist['Close'].iloc[-1]
                    month_start = hist['Close'].iloc[0]
                    change = ((current - month_start) / month_start) * 100
                    change_str = f"+{change:.2f}%" if change >= 0 else f"{change:.2f}%"

                    # 添加涨跌emoji
                    emoji = "↑" if change >= 0 else "↓"

                    result += f"{emoji} {cn_name} ({en_name}): {change_str}\n"
            except:
                continue

        return result
    except Exception as e:
        return f"获取板块表现失败: {str(e)}"


@tool
def compare_stocks(symbols: List[str]) -> str:
    """
    比较多个股票的统计数据。

    Args:
        symbols: 股票代码列表

    Returns:
        股票比较结果的字符串表示
    """
    try:
        if not symbols:
            return "请提供股票代码列表"

        result = "股票对比分析:\n\n"

        for symbol in symbols:
            try:
                stock = get_yfinance_ticker(symbol)
                info = stock.info
                hist = stock.history(period="5d")

                if hist.empty or not info:
                    continue

                # 基本信息
                name = info.get('shortName', symbol)
                current = hist['Close'].iloc[-1]

                # 涨跌幅
                if len(hist) > 1:
                    change = ((current - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]) * 100 if len(hist) >= 5 else 0
                else:
                    change = 0

                # 52周数据
                high_52w = info.get('52WeekHigh', 0)
                low_52w = info.get('52WeekLow', 0)

                # 估值
                pe = info.get('peRatio', 0)

                result += f"【{name} ({symbol})】\n"
                result += f"  当前价格: ${current:.2f}\n"
                result += f"  5日涨跌: {change:+.2f}%\n"
                result += f"  52周范围: ${low_52w:.2f} - ${high_52w:.2f}\n"
                if pe:
                    result += f"  市盈率 (P/E): {pe:.2f}\n"
                result += "\n"

        return result if result != "股票对比分析:\n\n" else "无法获取股票数据"
    except Exception as e:
        return f"对比股票失败: {str(e)}"