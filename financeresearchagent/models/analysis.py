"""
分析结果数据模型
"""

from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class TrendDirection(str, Enum):
    """趋势方向"""
    UPTREND = "uptrend"        # 上涨趋势
    DOWNTREND = "downtrend"    # 下跌趋势
    SIDEWAYS = "sideways"      # 震荡整理
    UNCERTAIN = "uncertain"    # 不确定


class Signal(str, Enum):
    """交易信号"""
    BUY = "buy"                # 买入
    SELL = "sell"              # 卖出
    STRONG_BUY = "strong_buy"  # 强力买入
    STRONG_SELL = "strong_sell"  # 强力卖出
    HOLD = "hold"              # 持有


class TechnicalAnalysis(BaseModel):
    """技术分析结果"""
    symbol: str = Field(..., description="股票代码")
    analysis_date: datetime = Field(default_factory=datetime.now, description="分析日期")

    # 趋势分析
    trend: TrendDirection = Field(TrendDirection.SIDEWAYS, description="趋势方向")
    trend_strength: float = Field(0.5, description="趋势强度 (0-1)")
    support_level: Optional[float] = Field(None, description="支撑位")
    resistance_level: Optional[float] = Field(None, description="阻力位")

    # 移动平均
    ma_signals: dict = Field(default_factory=dict, description="均线信号")
    ma_cross: Optional[str] = Field(None, description="均线交叉信号")

    # 动量指标
    rsi: float = Field(0, description="RSI值")
    rsi_signal: Signal = Field(Signal.HOLD, description="RSI信号")
    macd: float = Field(0, description="MACD")
    macd_signal: Signal = Field(Signal.HOLD, description="MACD信号")

    # 布林带
    bb_position: float = Field(0.5, description="布林带位置 (0-1)")
    bb_signal: Signal = Field(Signal.HOLD, description="布林带信号")

    # 成交量
    volume_ratio: float = Field(1.0, description="量比")
    volume_signal: str = Field("normal", description="成交量信号")

    # 综合信号
    overall_signal: Signal = Field(Signal.HOLD, description="综合信号")
    confidence: float = Field(0.5, description="信号置信度 (0-1)")


class FundamentalAnalysis(BaseModel):
    """基本面分析结果"""
    symbol: str = Field(..., description="股票代码")
    analysis_date: datetime = Field(default_factory=datetime.now, description="分析日期")

    # 估值分析
    pe_ratio: Optional[float] = Field(None, description="市盈率")
    pb_ratio: Optional[float] = Field(None, description="市净率")
    ps_ratio: Optional[float] = Field(None, description="市销率")
    pc_ratio: Optional[float] = Field(None, description="市现率")
    ev_ebitda: Optional[float] = Field(None, description="EV/EBITDA")
    peg_ratio: Optional[float] = Field(None, description="PEG比率")

    # 估值评级
    valuation_rating: str = Field("neutral", description="估值评级 (overvalued/fair/undervalued)")
    pe_percentile: Optional[float] = Field(None, description="市盈率历史分位")

    # 盈利能力
    roe: Optional[float] = Field(None, description="净资产收益率")
    roa: Optional[float] = Field(None, description="总资产收益率")
    gross_margin: Optional[float] = Field(None, description="毛利率")
    net_margin: Optional[float] = Field(None, description="净利润率")
    operating_margin: Optional[float] = Field(None, description="营业利润率")

    # 盈利评级
    profitability_rating: str = Field("neutral", description="盈利能力评级")

    # 成长能力
    revenue_growth: Optional[float] = Field(None, description="营收增长率")
    earnings_growth: Optional[float] = Field(None, description="盈利增长率")
    cagr_5y: Optional[float] = Field(None, description="5年复合增长率")

    # 成长评级
    growth_rating: str = Field("neutral", description="成长能力评级")

    # 财务健康
    debt_to_equity: Optional[float] = Field(None, description="负债权益比")
    current_ratio: Optional[float] = Field(None, description="流动比率")
    quick_ratio: Optional[float] = Field(None, description="速动比率")
    interest_coverage: Optional[float] = Field(None, description="利息保障倍数")

    # 财务评级
    health_rating: str = Field("neutral", description="财务健康评级")

    # 股息
    dividend_yield: Optional[float] = Field(None, description="股息率")
    payout_ratio: Optional[float] = Field(None, description="派息比率")
    dividend_growth: Optional[float] = Field(None, description="股息增长率")

    # 综合评级
    overall_rating: str = Field("neutral", description="综合评级")
    score: float = Field(50, description="综合得分 (0-100)")


class RiskAssessment(BaseModel):
    """风险评估结果"""
    symbol: str = Field(..., description="股票代码")
    analysis_date: datetime = Field(default_factory=datetime.now, description="分析日期")

    # 市场风险
    beta: float = Field(1.0, description="Beta系数")
    volatility: float = Field(0, description="年化波动率")
    var_95: Optional[float] = Field(None, description="95% VaR")

    # 经营风险
    business_risk: str = Field("medium", description="经营风险 (low/medium/high)")
    concentration_risk: Optional[str] = Field(None, description="集中度风险")

    # 财务风险
    financial_risk: str = Field("medium", description="财务风险 (low/medium/high)")
    leverage_level: Optional[float] = Field(None, description="杠杆水平")

    # 行业风险
    industry_risk: str = Field("medium", description="行业风险 (low/medium/high)")
    regulatory_risk: Optional[str] = Field(None, description="监管风险")

    # 综合风险
    overall_risk: str = Field("medium", description="综合风险 (low/medium/high)")
    risk_score: float = Field(50, description="风险评分 (0-100)")
    max_drawdown: Optional[float] = Field(None, description="历史最大回撤")