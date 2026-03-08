"""
数据服务层

提供统一的数据获取接口。
"""

from typing import Optional, Dict, Any
import urllib3
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 禁用 SSL 警告和证书验证
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 创建全局共享的 session（禁用 SSL 验证）
_requests_session = None

def get_requests_session():
    """获取全局共享的 requests session"""
    global _requests_session
    if _requests_session is None:
        from requests import Session
        _requests_session = Session()
        _requests_session.verify = False
    return _requests_session


class DataService:
    """数据服务类"""

    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 缓存5分钟

    def get_stock_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """获取股票历史数据"""
        cache_key = f"{symbol}_{period}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # 使用 ssl_fix 中禁用SSL验证的 session
        from ssl_fix import get_yfinance_ticker
        stock = get_yfinance_ticker(symbol)
        data = stock.history(period=period)
        self.cache[cache_key] = data
        return data

    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """获取股票基本信息"""
        cache_key = f"{symbol}_info"
        if cache_key in self.cache:
            return self.cache[cache_key]

        stock = yf.Ticker(symbol)
        info = stock.info or {}
        self.cache[cache_key] = info
        return info

    def get_financials(self, symbol: str, statement: str = "income") -> Optional[pd.DataFrame]:
        """获取财务报表数据"""
        stock = yf.Ticker(symbol)

        if statement == "income":
            return stock.financials
        elif statement == "balance":
            return stock.balance_sheet
        elif statement == "cashflow":
            return stock.cashflow
        elif statement == "earnings":
            return stock.earnings

        return None

    def get_dividends(self, symbol: str) -> Optional[pd.Series]:
        """获取分红历史"""
        stock = yf.Ticker(symbol)
        return stock.dividends

    def get_splits(self, symbol: str) -> Optional[pd.Series]:
        """获取拆股历史"""
        stock = yf.Ticker(symbol)
        return stock.splits

    def get_earnings_dates(self, symbol: str) -> Optional[pd.DataFrame]:
        """获取财报发布日期"""
        stock = yf.Ticker(symbol)
        return stock.earnings_dates

    def get_news(self, symbol: str) -> list:
        """获取股票新闻"""
        stock = yf.Ticker(symbol)
        return stock.news or []

    def get_market_indices(self) -> Dict[str, Dict[str, float]]:
        """获取市场指数数据"""
        indices = {
            '^GSPC': 'S&P 500',
            '^DJI': '道琼斯',
            '^IXIC': '纳斯达克',
        }

        result = {}
        for symbol, name in indices.items():
            try:
                from ssl_fix import get_yfinance_ticker
                index = get_yfinance_ticker(symbol)
                hist = index.history(period="2d")
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
                    change = ((current - prev) / prev) * 100
                    result[name] = {
                        "price": current,
                        "change": change
                    }
            except:
                continue

        return result

    def get_multiple_stocks(self, symbols: list) -> Dict[str, Dict[str, Any]]:
        """获取多只股票数据"""
        result = {}
        for symbol in symbols:
            try:
                info = self.get_stock_info(symbol)
                hist = self.get_stock_data(symbol, period="5d")

                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    change = ((current - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100

                    result[symbol] = {
                        "name": info.get("shortName", symbol),
                        "price": current,
                        "change_5d": change,
                        "market_cap": info.get("marketCap"),
                        "pe_ratio": info.get("peRatio"),
                    }
            except:
                continue

        return result

    def clear_cache(self):
        """清除缓存"""
        self.cache.clear()


# 全局实例
_data_service: Optional[DataService] = None


def get_data_service() -> DataService:
    """获取数据服务单例"""
    global _data_service
    if _data_service is None:
        _data_service = DataService()
    return _data_service