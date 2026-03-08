"""
工具库模块

导出所有可用的Agent工具：
- finance_tools: 财经数据获取工具
- analysis_tools: 数据分析工具
- report_tools: 报告生成工具
- market_tools: 市场分析工具
"""

from .finance_tools import (
    get_stock_price,
    get_stock_info,
    get_financial_data,
    get_stock_news,
    get_market_summary,
)

from .analysis_tools import (
    calculate_technical_indicators,
    analyze_fundamentals,
    analyze_price_trend,
    calculate_volatility,
)

from .report_tools import (
    generate_research_report,
    generate_market_summary,
    generate_stock_analysis,
)

from .market_tools import (
    get_market_news,
    get_market_indices,
    get_sector_performance,
)

__all__ = [
    # Finance tools
    "get_stock_price",
    "get_stock_info",
    "get_financial_data",
    "get_stock_news",
    "get_market_summary",
    # Analysis tools
    "calculate_technical_indicators",
    "analyze_fundamentals",
    "analyze_price_trend",
    "calculate_volatility",
    # Report tools
    "generate_research_report",
    "generate_market_summary",
    "generate_stock_analysis",
    # Market tools
    "get_market_news",
    "get_market_indices",
    "get_sector_performance",
]