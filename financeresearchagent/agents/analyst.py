"""
分析子Agent - 负责技术分析、基本面分析和风险评估

该Agent专门用于对收集到的数据进行深入分析，提供投资决策支持。
"""

from typing import Optional, Any, Dict

# 导入硅基流动LLM配置
from financieresearchagent.config.llm_config import get_llm

# 导入deepagents
try:
    from deepagents import create_deep_agent
    DEEP_AGENTS_AVAILABLE = True
except ImportError:
    DEEP_AGENTS_AVAILABLE = False
    create_deep_agent = None

# 全局Agent实例缓存
_analyst: Optional[Any] = None


def get_model():
    """获取配置的LLM模型（硅基流动API）"""
    return get_llm(
        model="deepseek_v3",
        temperature=0.5,  # 分析使用中等温度，平衡创造性和准确性
        max_tokens=4096,
    )


def create_analyst() -> Any:
    """
    创建分析子Agent

    Returns:
        配置好的分析Agent实例
    """
    global _analyst

    if _analyst is not None:
        return _analyst

    if not DEEP_AGENTS_AVAILABLE:
        raise ImportError(
            "deepagents包未安装，请运行: uv add deepagents 或 pip install deepagents"
        )

    # 分析Agent的系统提示词
    system_prompt = """你是金融分析专家，负责对股票进行技术分析、基本面分析和风险评估。

## 你的职责
1. 对收集到的市场数据和财务数据进行深入分析
2. 识别投资机会和潜在风险
3. 提供基于数据的投资建议

## 分析类型

### 1. 技术分析
- 趋势分析：识别价格走势（上升、下降、横盘）
- 形态分析：识别图表形态（头肩顶、双底、三角形等）
- 指标分析：
  - 移动平均线（MA5、MA10、MA20、MA60、MA120、MA250）
  - MACD（Moving Average Convergence Divergence）
  - RSI（Relative Strength Index）
  - 布林带（Bollinger Bands）
  - 成交量分析
- 支撑位和阻力位识别

### 2. 基本面分析
- 财务健康度评估：
  - 盈利能力（毛利率、净利率、ROE、ROA）
  - 偿债能力（流动比率、速动比率、资产负债率）
  - 运营效率（存货周转率、应收账款周转率）
  - 成长性（营收增长率、利润增长率）
- 估值分析：
  - PE（市盈率）分析
  - PB（市净率）分析
  - DCF（现金流折现）估值
  - 股息率分析
- 行业地位分析：
  - 市场份额
  - 竞争优势（护城河）
  - 管理层评估

### 3. 风险评估
- 市场风险：系统性风险、波动性
- 行业风险：行业周期、政策影响
- 公司风险：经营风险、财务风险
- 估值风险：过高估值风险

## 输出格式
请以结构化格式返回分析结果，包含：
```
{
    "analysis_type": "分析类型",
    "stock_symbol": "股票代码",
    "findings": {
        // 具体发现和分析结果
    },
    "indicators": {
        // 关键指标数值
    },
    "conclusion": "分析结论",
    "risk_level": "风险等级（低/中/高）"
}
```

## 注意事项
1. 所有分析必须基于实际数据，不要推测不存在的数据
2. 提供客观的分析结果，同时说明分析的局限性
3. 给出明确的投资建议，但需标注风险提示
4. 使用专业术语，但要让非专业人士也能理解核心观点
"""

    # 创建Agent
    _analyst = create_deep_agent(
        name="analyst",
        model=get_model(),
        system_prompt=system_prompt,
    )

    return _analyst


def get_analyst() -> Any:
    """获取或创建分析Agent实例（单例模式）"""
    if _analyst is None:
        return create_analyst()
    return _analyst


async def perform_analysis(
    stock_symbol: str,
    data: Dict[str, Any],
    analysis_types: list = None,
    thread_id: str = "default"
) -> Dict[str, Any]:
    """
    执行股票分析

    Args:
        stock_symbol: 股票代码
        data: 收集到的数据
        analysis_types: 分析类型列表
        thread_id: 线程ID

    Returns:
        分析结果
    """
    agent = get_analyst()

    if analysis_types is None:
        analysis_types = ["technical", "fundamental", "risk"]

    # 构造分析请求
    analysis_types_str = ", ".join(analysis_types)
    request = f"""请对股票 {stock_symbol} 进行以下分析：{analysis_types_str}。

提供的数据：
{data}
"""

    # 配置线程
    config = {
        "configurable": {
            "thread_id": f"{thread_id}_analysis"
        }
    }

    # 运行Agent
    result = await agent.ainvoke(
        {"messages": [("user", request)]},
        config=config
    )

    return {
        "stock_symbol": stock_symbol,
        "analysis_types": analysis_types,
        "result": result,
        "thread_id": thread_id,
    }


def reset_analyst() -> None:
    """重置分析Agent实例"""
    global _analyst
    _analyst = None