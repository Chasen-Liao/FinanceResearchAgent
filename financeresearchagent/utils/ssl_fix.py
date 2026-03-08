"""
SSL 修复工具模块

解决 Windows 上 yfinance 的 SSL 证书验证问题。
适用于 yfinance 0.2.x 使用 requests 的情况。
"""

import urllib3
import yfinance as yf
from requests import Session

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 全局共享的 session（用于 requests）
_yfinance_session = None


def get_yfinance_session() -> Session:
    """获取用于 yfinance 的共享 session（禁用 SSL 验证）"""
    global _yfinance_session
    if _yfinance_session is None:
        _yfinance_session = Session()
        _yfinance_session.verify = False
    return _yfinance_session


def get_yfinance_ticker(symbol: str):
    """
    获取 yfinance Ticker 对象（使用禁用 SSL 验证的 session）

    Args:
        symbol: 股票代码，如 "AAPL", "MSFT"

    Returns:
        yfinance Ticker 对象
    """
    ticker = yf.Ticker(symbol)
    # 替换内部使用的 session
    ticker.session = get_yfinance_session()
    return ticker


def download(*args, **kwargs):
    """
    使用 yfinance.download 获取数据（使用禁用 SSL 验证的 session）
    """
    kwargs['session'] = get_yfinance_session()
    return yf.download(*args, **kwargs)