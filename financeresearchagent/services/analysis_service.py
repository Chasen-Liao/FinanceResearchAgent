"""
分析服务层

提供技术分析、基本面分析和风险评估功能。
"""

from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime
import sys
from pathlib import Path

# 兼容处理：支持相对导入和绝对导入
if __name__ != "__main__":
    try:
        from .data_service import get_data_service
    except ImportError:
        # 处理直接运行或作为模块导入时的情况
        current_dir = Path(__file__).parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
        from data_service import get_data_service
else:
    # 直接运行时的备选导入
    from data_service import get_data_service


class AnalysisService:
    """分析服务类"""

    def __init__(self):
        self.data_service = get_data_service()

    def calculate_technical_indicators(self, symbol: str, period: str = "6mo") -> Dict[str, Any]:
        """计算技术指标"""
        hist = self.data_service.get_stock_data(symbol, period)

        if hist.empty:
            return {}

        close = hist['Close']
        result = {}

        # 移动平均线
        for window in [5, 10, 20, 60]:
            result[f'ma{window}'] = close.rolling(window).mean().iloc[-1]

        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        result['rsi'] = 100 - (100 / (1 + rs)).iloc[-1]

        # MACD
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()
        result['macd'] = macd.iloc[-1]
        result['macd_signal'] = signal.iloc[-1]
        result['macd_hist'] = (macd - signal).iloc[-1]

        # 布林带
        ma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        result['bb_upper'] = (ma20 + 2 * std20).iloc[-1]
        result['bb_middle'] = ma20.iloc[-1]
        result['bb_lower'] = (ma20 - 2 * std20).iloc[-1]

        # 成交量分析
        volume = hist['Volume']
        result['volume'] = volume.iloc[-1]
        result['avg_volume'] = volume.rolling(20).mean().iloc[-1]
        result['volume_ratio'] = volume.iloc[-1] / volume.rolling(20).mean().iloc[-1]

        return result

    def analyze_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """分析基本面"""
        info = self.data_service.get_stock_info(symbol)

        if not info:
            return {}

        result = {}

        # 估值指标
        if 'peRatio' in info:
            result['pe_ratio'] = info['peRatio']
        if 'priceToBook' in info:
            result['pb_ratio'] = info['priceToBook']
        if 'priceToSalesTrailing12Months' in info:
            result['ps_ratio'] = info['priceToSalesTrailing12Months']
        if 'pegRatio' in info:
            result['peg_ratio'] = info['pegRatio']
        if 'marketCap' in info:
            result['market_cap'] = info['marketCap']
        if 'enterpriseValue' in info:
            result['enterprise_value'] = info['enterpriseValue']

        # 盈利能力
        if 'returnOnEquity' in info:
            result['roe'] = info['returnOnEquity']
        if 'returnOnAssets' in info:
            result['roa'] = info['returnOnAssets']
        if 'grossMargins' in info:
            result['gross_margin'] = info['grossMargins']
        if 'profitMargins' in info:
            result['net_margin'] = info['profitMargins']
        if 'operatingMargins' in info:
            result['operating_margin'] = info['operatingMargins']

        # 成长能力
        if 'revenueGrowth' in info:
            result['revenue_growth'] = info['revenueGrowth']
        if 'earningsGrowth' in info:
            result['earnings_growth'] = info['earningsGrowth']

        # 财务健康
        if 'currentRatio' in info:
            result['current_ratio'] = info['currentRatio']
        if 'quickRatio' in info:
            result['quick_ratio'] = info['quickRatio']
        if 'debtToEquity' in info:
            result['debt_to_equity'] = info['debtToEquity']

        # 股息
        if 'dividendYield' in info:
            result['dividend_yield'] = info['dividendYield']
        if 'payoutRatio' in info:
            result['payout_ratio'] = info['payoutRatio']

        # 评级
        if 'recommendationKey' in info:
            result['analyst_rating'] = info['recommendationKey']
        if 'targetMeanPrice' in info:
            result['target_price'] = info['targetMeanPrice']

        return result

    def analyze_price_trend(self, symbol: str, period: str = "3mo") -> Dict[str, str]:
        """分析价格趋势"""
        hist = self.data_service.get_stock_data(symbol, period)

        if hist.empty:
            return {"trend": "unknown"}

        close = hist['Close']
        current = close.iloc[-1]

        ma5 = close.rolling(5).mean().iloc[-1]
        ma20 = close.rolling(20).mean().iloc[-1]
        ma60 = close.rolling(60).mean().iloc[-1] if len(close) >= 60 else None

        # 判断趋势
        if current > ma5 > ma20:
            if ma60 and current > ma60:
                trend = "strong_uptrend"
            else:
                trend = "uptrend"
        elif current < ma5 < ma20:
            if ma60 and current < ma60:
                trend = "strong_downtrend"
            else:
                trend = "downtrend"
        else:
            trend = "sideways"

        # 涨跌幅
        change_1d = ((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100) if len(close) > 1 else 0
        change_1w = ((close.iloc[-1] - close.iloc[-5]) / close.iloc[-5] * 100) if len(close) > 5 else 0
        change_1m = ((close.iloc[-1] - close.iloc[-22]) / close.iloc[-22] * 100) if len(close) > 22 else 0

        return {
            "trend": trend,
            "current_price": current,
            "ma5": ma5,
            "ma20": ma20,
            "change_1d": change_1d,
            "change_1w": change_1w,
            "change_1m": change_1m,
        }

    def calculate_volatility(self, symbol: str, period: str = "1y") -> Dict[str, float]:
        """计算波动率"""
        hist = self.data_service.get_stock_data(symbol, period)

        if hist.empty:
            return {}

        close = hist['Close']
        returns = close.pct_change().dropna()

        daily_vol = returns.std()
        annual_vol = daily_vol * (252 ** 0.5)

        return {
            "daily_volatility": daily_vol,
            "annualized_volatility": annual_vol,
            "max_price": close.max(),
            "min_price": close.min(),
            "current_position": (close.iloc[-1] - close.min()) / (close.max() - close.min())
        }

    def generate_technical_signal(self, symbol: str) -> Dict[str, Any]:
        """生成技术分析信号"""
        indicators = self.calculate_technical_indicators(symbol)

        signal = "hold"
        confidence = 0.5
        reasons = []

        # RSI信号
        rsi = indicators.get('rsi', 50)
        if rsi > 70:
            signal = "sell"
            confidence = min((rsi - 70) / 30, 1)
            reasons.append(f"RSI超买({rsi:.1f})")
        elif rsi < 30:
            signal = "buy"
            confidence = min((30 - rsi) / 30, 1)
            reasons.append(f"RSI超卖({rsi:.1f})")

        # MACD信号
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        if macd > macd_signal and macd < 0:
            reasons.append("MACD金叉")
            if signal == "hold":
                signal = "buy"
                confidence = 0.6
        elif macd < macd_signal and macd > 0:
            reasons.append("MACD死叉")
            if signal == "hold":
                signal = "sell"
                confidence = 0.6

        return {
            "signal": signal,
            "confidence": confidence,
            "reasons": reasons,
            "indicators": indicators
        }


# 全局实例
_analysis_service: Optional[AnalysisService] = None


def get_analysis_service() -> AnalysisService:
    """获取分析服务单例"""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service