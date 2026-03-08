"""
数据收集子Agent - 负责获取股票市场数据、财务数据、新闻等

该Agent专门用于从各种数据源收集投资研究所需的原始数据。
"""

from typing import Optional, Any, Dict, List

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
_data_collector: Optional[Any] = None


def get_model():
    """获取配置的LLM模型（硅基流动API）"""
    return get_llm(
        model="deepseek_v3",
        temperature=0.3,  # 数据收集使用较低的温度以保持准确性
        max_tokens=4096,
    )


def create_data_collector() -> Any:
    """
    创建数据收集子Agent

    Returns:
        配置好的数据收集Agent实例
    """
    global _data_collector

    if _data_collector is not None:
        return _data_collector

    if not DEEP_AGENTS_AVAILABLE:
        raise ImportError(
            "deepagents包未安装，请运行: uv add deepagents 或 pip install deepagents"
        )

    # 数据收集Agent的系统提示词
    system_prompt = """你是数据收集专家，负责获取股票市场数据、财务数据、公司信息和新闻等。

## 你的职责
1. 根据主Agent的请求，收集特定的财经数据
2. 确保数据的准确性、完整性和时效性
3. 将收集到的数据以结构化格式返回

## 数据类型
你需要收集以下类型的数据：

### 1. 市场数据
- 历史价格数据（开盘价、收盘价、最高价、最低价、成交量）
- 股票基本信息（代码、名称、市值、板块）
- 实时行情数据

### 2. 财务数据
- 财务报表（资产负债表、利润表、现金流量表）
- 财务比率（PE、PB、ROE、ROA、负债率等）
- 关键财务指标

### 3. 基本面数据
- 公司概况（成立时间、业务范围、管理层）
- 营收和利润趋势
- 分析师评级和目标价

### 4. 市场新闻
- 最新公司新闻
- 行业动态
- 市场情绪指标

## 数据源
- 首选：yfinance（Yahoo Finance API）
- 备用：其他公开财经数据API

## 输出格式
请以结构化格式返回数据，包含：
```
{
    "stock_symbol": "股票代码",
    "data_type": "数据类型",
    "data": {...},  // 实际数据
    "source": "数据来源",
    "timestamp": "数据时间戳",
    "notes": "备注说明"
}
```

## 注意事项
1. 优先使用可靠的数据源
2. 检查数据的时效性，过期数据应标注
3. 遇到数据获取失败时，明确说明原因
4. 返回尽可能完整的数据，但不要编造不存在的数据
"""

    # 创建Agent
    _data_collector = create_deep_agent(
        name="data-collector",
        model=get_model(),
        system_prompt=system_prompt,
    )

    return _data_collector


def get_data_collector() -> Any:
    """获取或创建数据收集Agent实例（单例模式）"""
    if _data_collector is None:
        return create_data_collector()
    return _data_collector


async def collect_stock_data(
    stock_symbol: str,
    data_types: List[str] = None,
    thread_id: str = "default"
) -> Dict[str, Any]:
    """
    收集股票数据

    Args:
        stock_symbol: 股票代码
        data_types: 需要收集的数据类型列表
        thread_id: 线程ID

    Returns:
        收集到的数据
    """
    agent = get_data_collector()

    if data_types is None:
        data_types = ["market_data", "financial_data", "news"]

    # 构造数据请求
    data_types_str = ", ".join(data_types)
    request = f"""请收集股票 {stock_symbol} 的以下数据：{data_types_str}。"""

    # 配置线程
    config = {
        "configurable": {
            "thread_id": f"{thread_id}_data"
        }
    }

    # 运行Agent
    result = await agent.ainvoke(
        {"messages": [("user", request)]},
        config=config
    )

    return {
        "stock_symbol": stock_symbol,
        "data_types": data_types,
        "result": result,
        "thread_id": thread_id,
    }


def reset_data_collector() -> None:
    """重置数据收集Agent实例"""
    global _data_collector
    _data_collector = None