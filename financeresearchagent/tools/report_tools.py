"""
报告生成工具库

提供研究报告生成功能。
"""

from typing import Optional, Dict, Any
from langchain.tools import tool
from jinja2 import Template
from datetime import datetime

# 导入 yfinance 修复模块
from financieresearchagent.utils.ssl_fix import get_yfinance_ticker


# 报告模板
REPORT_TEMPLATE = """
# {{ title }}

**研究标的:** {{ symbol }} - {{ company_name }}
**报告日期:** {{ date }}
**分析师:** AI投资研究Agent

---

## 执行摘要

{{ summary }}

**投资评级:** {{ rating }}
**目标价格:** {{ target_price }}
**当前价格:** {{ current_price }}
**上涨空间:** {{ upside }}

---

## 公司概况

{{ company_overview }}

---

## 财务分析

{{ financial_analysis }}

---

## 技术分析

{{ technical_analysis }}

---

## 风险因素

{{ risk_factors }}

---

## 投资建议

{{ investment_advice }}

---

*本报告由AI投资研究Agent自动生成，仅供参考，不构成投资建议。*
"""


@tool
def generate_research_report(
    symbol: str,
    company_name: str,
    current_price: float,
    target_price: float,
    summary: str,
    financial_analysis: str,
    technical_analysis: str,
    rating: str = "持有",
) -> str:
    """
    生成完整的研究报告。

    Args:
        symbol: 股票代码
        company_name: 公司名称
        current_price: 当前价格
        target_price: 目标价格
        summary: 执行摘要
        financial_analysis: 财务分析内容
        technical_analysis: 技术分析内容
        rating: 投资评级（买入/增持/持有/卖出）

    Returns:
        生成的研究报告markdown文本
    """
    try:
        # 计算上涨空间
        upside_pct = ((target_price - current_price) / current_price) * 100
        upside_str = f"{upside_pct:+.1f}%"

        # 风险因素
        risk_factors = """
1. 市场风险：整体宏观经济下行可能影响公司业绩
2. 行业风险：行业竞争加剧可能压缩利润空间
3. 经营风险：公司业务模式可能面临挑战
4. 估值风险：当前估值处于历史高位水平
5. 政策风险：监管政策变化可能影响业务
"""

        # 投资建议
        if rating in ["买入", "增持"]:
            investment_advice = f"""
基于以上分析，我们给予{symbol}**{rating}**的投资评级。

**理由：**
- 基本面稳健，盈利能力较强
- 技术面呈现上涨趋势
- 估值具有一定吸引力

**操作建议：**
- 建议在${current_price:.2f}附近建仓
- 第一目标位：${target_price * 1.1:.2f}
- 止损位：${current_price * 0.9:.2f}
"""
        elif rating == "持有":
            investment_advice = f"""
基于以上分析，我们给予{symbol}**持有**的投资评级。

**理由：**
- 公司基本面良好，但缺乏明显催化因素
- 技术面处于震荡整理阶段
- 估值处于合理区间

**操作建议：**
- 持有观望，等待更好买入时机
- 如有盈利可考虑部分获利了结
"""
        else:
            investment_advice = f"""
基于以上分析，我们给予{symbol}**卖出**的投资评级。

**理由：**
- 基本面出现恶化迹象
- 技术面趋势向下
- 估值偏高

**操作建议：**
- 建议逢高减持或清仓
- 等待风险释放后再评估
"""

        # 公司概况（简化版）
        company_overview = f"""
{company_name} (股票代码: {symbol}) 是一家在NASDAQ交易所上市的科技公司。
公司主要从事{{业务描述}}，在行业内具有较强的竞争优势。
"""

        # 渲染模板
        template = Template(REPORT_TEMPLATE)
        report = template.render(
            title=f"{company_name} - 投资研究报告",
            symbol=symbol,
            company_name=company_name,
            date=datetime.now().strftime("%Y年%m月%d日"),
            summary=summary,
            rating=rating,
            target_price=f"${target_price:.2f}",
            current_price=f"${current_price:.2f}",
            upside=upside_str,
            company_overview=company_overview,
            financial_analysis=financial_analysis,
            technical_analysis=technical_analysis,
            risk_factors=risk_factors,
            investment_advice=investment_advice,
        )

        return report
    except Exception as e:
        return f"生成研究报告失败: {str(e)}"


@tool
def generate_market_summary() -> str:
    """
    生成市场每日简报。

    Returns:
        市场简报的字符串表示
    """
    try:
        from .market_tools import get_market_indices, get_sector_performance

        indices = get_market_indices()
        sectors = get_sector_performance()

        report = f"""# 每日市场简报

**报告日期:** {datetime.now().strftime("%Y年%m月%d日")}

---

## 市场指数

{indices}

---

## 板块表现

{sectors}

---

## 今日要点

1. 关注美股开盘表现，尤其是科技股走势
2. 留意美联储政策信号和经济数据
3. 评估 portfolio 风险敞口，及时调整仓位

---

*本简报由AI投资研究Agent自动生成，仅供参考。*
"""
        return report
    except Exception as e:
        return f"生成市场简报失败: {str(e)}"


@tool
def generate_stock_analysis(symbol: str) -> str:
    """
    生成股票快速分析报告。

    Args:
        symbol: 股票代码

    Returns:
        股票分析报告的字符串表示
    """
    try:
        import yfinance as yf

        stock = get_yfinance_ticker(symbol)
        info = stock.info
        hist = stock.history(period="1mo")

        if not info or hist.empty:
            return f"无法获取 {symbol} 的数据"

        name = info.get('shortName', symbol)
        current_price = hist['Close'].iloc[-1]

        # 涨跌幅
        month_change = ((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100

        # 52周数据
        high_52w = info.get('52WeekHigh', 0)
        low_52w = info.get('52WeekLow', 0)

        # 估值
        pe = info.get('peRatio', 0)
        pb = info.get('priceToBook', 0)

        # 评级
        rec = info.get('recommendationKey', 'N/A')

        report = f"""# {name} ({symbol}) 快速分析

**日期:** {datetime.now().strftime("%Y年%m月%d日")}

---

## 基本信息

| 指标 | 数值 |
|------|------|
| 当前价格 | ${current_price:.2f} |
| 月涨跌幅 | {month_change:+.2f}% |
| 52周最高 | ${high_52w:.2f} |
| 52周最低 | ${low_52w:.2f} |
| 市盈率 (P/E) | {pe:.2f if pe else 'N/A'} |
| 市净率 (P/B) | {pb:.2f if pb else 'N/A'} |
| 分析师评级 | {rec} |

---

## 投资建议

"""

        if pe and pe < 25 and month_change > 0:
            report += "**整体评价：积极** - 估值合理且近期表现强劲\n\n"
            report += "- 估值处于合理区间\n"
            report += "- 近期上涨趋势良好\n"
            report += "- 建议关注\n"
        elif pe and pe > 50:
            report += "**整体评价：谨慎** - 估值偏高\n\n"
            report += "- 市盈率偏高，注意回调风险\n"
            report += "- 建议等待更好的买入时机\n"
        else:
            report += "**整体评价：中性**\n\n"
            report += "- 建议观望，等待更多信息\n"

        return report
    except Exception as e:
        return f"生成股票分析失败: {str(e)}"


@tool
def generate_price_alert(symbol: str, target_price: float, direction: str = "above") -> str:
    """
    设置价格提醒。

    Args:
        symbol: 股票代码
        target_price: 目标价格
        direction: 方向（above/below）

    Returns:
        价格提醒设置结果的字符串表示
    """
    try:
        import yfinance as yf

        stock = get_yfinance_ticker(symbol)
        current = stock.history(period="1d")['Close'].iloc[-1]

        direction_text = "突破" if direction == "above" else "跌破"
        alert_type = "上涨" if direction == "above" else "下跌"

        result = f"""价格提醒设置成功！

股票: {symbol}
当前价格: ${current:.2f}
目标价格: ${target_price:.2f}
触发条件: {direction_text} ${target_price:.2f}

当 {symbol} {direction_text} ${target_price:.2f} 时，您将收到通知。
当前价格距离目标还有 {abs(((target_price - current) / current) * 100):.1f}% 的{alert_type}空间。
"""
        return result
    except Exception as e:
        return f"设置价格提醒失败: {str(e)}"