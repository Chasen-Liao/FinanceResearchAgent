"""
研究报告数据模型
"""

from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ReportType(str, Enum):
    """报告类型"""
    COMPREHENSIVE = "comprehensive"  # 综合报告
    TECHNICAL = "technical"          # 技术分析报告
    FUNDAMENTAL = "fundamental"      # 基本面分析报告
    QUICK = "quick"                  # 快速分析


class Rating(str, Enum):
    """投资评级"""
    BUY = "buy"          # 买入
    OUTPERFORM = "outperform"  # 增持
    HOLD = "hold"        # 持有
    UNDERPERFORM = "underperform"  # 减持
    SELL = "sell"        # 卖出


class ResearchReport(BaseModel):
    """研究报告"""
    report_id: str = Field(..., description="报告ID")
    symbol: str = Field(..., description="股票代码")
    company_name: str = Field(..., description="公司名称")

    # 报告元数据
    report_type: ReportType = Field(ReportType.COMPREHENSIVE, description="报告类型")
    rating: Rating = Field(Rating.HOLD, description="投资评级")
    report_date: datetime = Field(default_factory=datetime.now, description="报告日期")

    # 价格信息
    current_price: float = Field(..., description="当前价格")
    target_price: float = Field(..., description="目标价格")
    upside_potential: float = Field(..., description="上涨空间")

    # 报告内容
    summary: str = Field(..., description="执行摘要")
    company_overview: str = Field(..., description="公司概况")
    financial_analysis: str = Field(..., description="财务分析")
    technical_analysis: str = Field(..., description="技术分析")
    risk_factors: List[str] = Field(default_factory=list, description="风险因素")
    investment_advice: str = Field(..., description="投资建议")

    # 分析师信息
    analyst: str = Field("AI投资研究Agent", description="分析师")
    generated_by: str = Field("Investment Research Agent", description="生成工具")


class MarketReport(BaseModel):
    """市场报告"""
    report_id: str = Field(..., description="报告ID")
    report_date: datetime = Field(default_factory=datetime.now, description="报告日期")

    # 市场指数
    indices_summary: str = Field(..., description="市场指数摘要")

    # 板块表现
    sector_performance: str = Field(..., description="板块表现")

    # 新闻摘要
    news_summary: str = Field(..., description="新闻摘要")

    # 今日要点
    highlights: List[str] = Field(default_factory=list, description="今日要点")


class PriceAlert(BaseModel):
    """价格提醒"""
    alert_id: str = Field(..., description="提醒ID")
    symbol: str = Field(..., description="股票代码")
    target_price: float = Field(..., description="目标价格")
    direction: str = Field(..., description="方向 (above/below)")

    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    triggered: bool = Field(False, description="是否已触发")
    triggered_at: Optional[datetime] = Field(None, description="触发时间")


class ComparisonReport(BaseModel):
    """股票对比报告"""
    symbols: List[str] = Field(..., description="对比的股票代码")

    # 价格对比
    prices: dict = Field(..., description="价格对比")
    changes: dict = Field(..., description="涨跌幅对比")

    # 估值对比
    pe_ratios: dict = Field(..., description="市盈率对比")
    pb_ratios: dict = Field(..., description="市净率对比")

    # 盈利对比
    margins: dict = Field(..., description="利润率对比")

    # 增长对比
    growth_rates: dict = Field(..., description="增长率对比")