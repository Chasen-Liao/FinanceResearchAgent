"""
报告服务层

提供报告生成和管理功能。
"""

from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import sys
from pathlib import Path

# 兼容处理：支持相对导入和绝对导入
if __name__ != "__main__":
    try:
        from .data_service import get_data_service
        from .analysis_service import get_analysis_service
    except ImportError:
        current_dir = Path(__file__).parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
        from data_service import get_data_service
        from analysis_service import get_analysis_service
else:
    from data_service import get_data_service
    from analysis_service import get_analysis_service


class ReportService:
    """报告服务类"""

    def __init__(self):
        self.data_service = get_data_service()
        self.analysis_service = get_analysis_service()

    def generate_stock_analysis(self, symbol: str) -> Dict[str, Any]:
        """生成股票分析报告"""
        # 获取数据
        info = self.data_service.get_stock_info(symbol)
        hist = self.data_service.get_stock_data(symbol, period="1mo")

        if hist.empty or not info:
            return {"error": f"无法获取 {symbol} 的数据"}

        # 当前价格
        current_price = hist['Close'].iloc[-1]
        name = info.get('shortName', symbol)

        # 技术分析
        technical = self.analysis_service.calculate_technical_indicators(symbol)
        trend = self.analysis_service.analyze_price_trend(symbol)

        # 基本面分析
        fundamentals = self.analysis_service.analyze_fundamentals(symbol)

        # 生成信号
        signal = self.analysis_service.generate_technical_signal(symbol)

        return {
            "symbol": symbol,
            "name": name,
            "current_price": current_price,
            "technical": technical,
            "trend": trend,
            "fundamentals": fundamentals,
            "signal": signal,
            "report_date": datetime.now().isoformat()
        }

    def generate_research_report(self, symbol: str, report_type: str = "comprehensive") -> str:
        """生成完整研究报告（Markdown格式）"""
        # 获取分析数据
        analysis = self.generate_stock_analysis(symbol)

        if "error" in analysis:
            return f"生成报告失败: {analysis['error']}"

        # 构建报告
        name = analysis['name']
        price = analysis['current_price']

        # 投资建议
        signal = analysis.get('signal', {})
        signal_text = signal.get('signal', 'hold')
        confidence = signal.get('confidence', 0.5)

        if signal_text == "buy":
            rating = "买入"
            advice = "技术面显示买入信号，建议关注"
        elif signal_text == "sell":
            rating = "卖出"
            advice = "技术面显示风险，建议谨慎"
        else:
            rating = "持有"
            advice = "建议观望，等待更明确信号"

        # 目标价格（简单估算）
        target_price = price * 1.15 if signal_text == "buy" else price * 1.05

        # 基本面评分
        fundamentals = analysis.get('fundamentals', {})
        pe = fundamentals.get('pe_ratio')
        roe = fundamentals.get('roe')

        # 生成报告
        report = f"""# {name} ({symbol}) 投资研究报告

**报告日期:** {datetime.now().strftime("%Y年%m月%d日")}
**分析师:** AI投资研究Agent

---

## 执行摘要

{name}（股票代码：{symbol}）当前交易价格为 ${price:.2f}。

- **投资评级:** {rating}
- **目标价格:** ${target_price:.2f}（上涨空间 {((target_price-price)/price*100):.1f}%）
- **信号置信度:** {confidence*100:.0f}%

**核心观点:** {advice}

---

## 公司概况

| 项目 | 信息 |
|------|------|
| 公司名称 | {name} |
| 股票代码 | {symbol} |
| 市值 | {fundamentals.get('market_cap', 'N/A')} |
| 市盈率 | {pe:.2f if pe else 'N/A'} |
| 分析师评级 | {fundamentals.get('analyst_rating', 'N/A')} |

---

## 技术分析

### 关键指标
"""

        # 技术指标
        technical = analysis.get('technical', {})
        for key, value in technical.items():
            if isinstance(value, (int, float)) and not key.endswith('_ratio'):
                report += f"- **{key.upper()}:** {value:.2f}\n"

        report += f"""
### 价格趋势
- **趋势方向:** {analysis['trend'].get('trend', 'N/A')}
- **当前价格:** ${analysis['trend'].get('current_price', 0):.2f}
- **MA5:** ${analysis['trend'].get('ma5', 0):.2f}
- **MA20:** ${analysis['trend'].get('ma20', 0):.2f}

### 交易信号
- **信号:** {signal_text.upper()}
- **置信度:** {confidence*100:.0f}%

---

## 风险因素

1. 市场波动风险：整体市场可能调整
2. 行业风险：行业竞争加剧
3. 估值风险：当前估值水平
4. 流动性风险：交易量波动

---

## 投资建议

{advice}

**操作建议:**
- {'建议逢低买入' if signal_text == 'buy' else '建议持有观望'}
- 止损位: ${price * 0.9:.2f}
- 目标位: ${target_price:.2f}

---

*本报告由AI投资研究Agent自动生成，仅供参考，不构成投资建议。*
"""
        return report

    def generate_comparison(self, symbols: list) -> str:
        """生成股票对比报告"""
        result = f"# 股票对比分析\n\n**日期:** {datetime.now().strftime('%Y年%m月%d日')}\n\n"
        result += "| 指标 | " + " | ".join(symbols) + " |\n"
        result += "|" + "|".join(["---" for _ in range(len(symbols) + 1)]) + "|\n"

        for symbol in symbols:
            info = self.data_service.get_stock_info(symbol)
            hist = self.data_service.get_stock_data(symbol, period="5d")

            if hist.empty:
                continue

            pe = info.get('peRatio', 'N/A')
            if pe != 'N/A':
                pe = f"{pe:.2f}"

            current = hist['Close'].iloc[-1]
            change = ((current - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100

            result += f"| ${current:.2f} ({change:+.1f}%)"
            result += f"| {pe} |\n"

        return result


# 全局实例
_report_service: Optional[ReportService] = None


def get_report_service() -> ReportService:
    """获取报告服务单例"""
    global _report_service
    if _report_service is None:
        _report_service = ReportService()
    return _report_service