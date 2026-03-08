"""
股票数据模型

定义股票相关的数据结构。
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class StockInfo(BaseModel):
    """股票基本信息"""
    symbol: str = Field(..., description="股票代码")
    short_name: str = Field(..., description="股票简称")
    long_name: Optional[str] = Field(None, description="股票全称")
    sector: Optional[str] = Field(None, description="所属行业")
    industry: Optional[str] = Field(None, description="所属行业细分")
    market_cap: Optional[float] = Field(None, description="市值")
    enterprise_value: Optional[float] = Field(None, description="企业价值")
    pe_ratio: Optional[float] = Field(None, description="市盈率")
    peg_ratio: Optional[float] = Field(None, description="PEG比率")
    price_to_book: Optional[float] = Field(None, description="市净率")
    dividend_yield: Optional[float] = Field(None, description="股息率")
    beta: Optional[float] = Field(None, description="Beta系数")
   52_week_high: Optional[float] = Field(None, description="52周最高价")
   52_week_low: Optional[float] = Field(None, description="52周最低价")


class StockPrice(BaseModel):
    """股票价格数据"""
    symbol: str = Field(..., description="股票代码")
    date: datetime = Field(..., description="日期")
    open: float = Field(..., description="开盘价")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    close: float = Field(..., description="收盘价")
    volume: int = Field(..., description="成交量")
    adjusted_close: Optional[float] = Field(None, description="调整后收盘价")


class FinancialStatement(BaseModel):
    """财务报表数据"""
    symbol: str = Field(..., description="股票代码")
    period: str = Field(..., description="财报期间")
    report_date: datetime = Field(..., description="报告日期")
    total_revenue: Optional[float] = Field(None, description="总营收")
    net_income: Optional[float] = Field(None, description="净利润")
    operating_income: Optional[float] = Field(None, description="营业利润")
    total_assets: Optional[float] = Field(None, description="总资产")
    total_liabilities: Optional[float] = Field(None, description="总负债")
    shareholders_equity: Optional[float] = Field(None, description="股东权益")
    operating_cash_flow: Optional[float] = Field(None, description="经营活动现金流")
    investing_cash_flow: Optional[float] = Field(None, description="投资活动现金流")
    financing_cash_flow: Optional[float] = Field(None, description="筹资活动现金流")


class TechnicalIndicators(BaseModel):
    """技术指标数据"""
    symbol: str = Field(..., description="股票代码")
    date: datetime = Field(..., description="日期")

    # 移动平均线
    ma5: Optional[float] = Field(None, description="5日均线")
    ma10: Optional[float] = Field(None, description="10日均线")
    ma20: Optional[float] = Field(None, description="20日均线")
    ma60: Optional[float] = Field(None, description="60日均线")
    ma120: Optional[float] = Field(None, description="120日均线")
    ma250: Optional[float] = Field(None, description="250日均线")

    # 动量指标
    rsi_14: Optional[float] = Field(None, description="RSI(14)")
    macd: Optional[float] = Field(None, description="MACD")
    macd_signal: Optional[float] = Field(None, description="MACD信号线")
    macd_hist: Optional[float] = Field(None, description="MACD柱")

    # 布林带
    bb_upper: Optional[float] = Field(None, description="布林带上轨")
    bb_middle: Optional[float] = Field(None, description="布林带中轨")
    bb_lower: Optional[float] = Field(None, description="布林带下轨")

    # 成交量
    volume: Optional[int] = Field(None, description="成交量")
    avg_volume_20: Optional[float] = Field(None, description="20日均量")


class StockAnalysis(BaseModel):
    """股票分析结果"""
    symbol: str = Field(..., description="股票代码")
    analysis_date: datetime = Field(default_factory=datetime.now, description="分析日期")

    # 价格信息
    current_price: float = Field(..., description="当前价格")
    price_change_1d: float = Field(0, description="日涨跌幅")
    price_change_1w: float = Field(0, description="周涨跌幅")
    price_change_1m: float = Field(0, description="月涨跌幅")

    # 估值指标
    pe_ratio: Optional[float] = Field(None, description="市盈率")
    pb_ratio: Optional[float] = Field(None, description="市净率")
    ps_ratio: Optional[float] = Field(None, description="市销率")
    peg_ratio: Optional[float] = Field(None, description="PEG比率")

    # 盈利能力
    roe: Optional[float] = Field(None, description="净资产收益率")
    roa: Optional[float] = Field(None, description="总资产收益率")
    gross_margin: Optional[float] = Field(None, description="毛利率")
    net_margin: Optional[float] = Field(None, description="净利润率")

    # 成长能力
    revenue_growth: Optional[float] = Field(None, description="营收增长率")
    earnings_growth: Optional[float] = Field(None, description="盈利增长率")

    # 风险指标
    beta: Optional[float] = Field(None, description="Beta系数")
    volatility: Optional[float] = Field(None, description="波动率")