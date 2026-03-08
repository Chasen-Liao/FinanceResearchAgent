"""
报告生成子Agent - 负责生成专业的研究报告

该Agent专门用于将分析结果转化为结构化、专业的投资研究报告。
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
_report_generator: Optional[Any] = None


def get_model():
    """获取配置的LLM模型（硅基流动API）"""
    return get_llm(
        model="deepseek_v3",
        temperature=0.6,  # 报告生成使用中等温度，平衡准确性和可读性
        max_tokens=8192,  # 报告需要更长的输出
    )


def create_report_generator() -> Any:
    """
    创建报告生成子Agent

    Returns:
        配置好的报告生成Agent实例
    """
    global _report_generator

    if _report_generator is not None:
        return _report_generator

    if not DEEP_AGENTS_AVAILABLE:
        raise ImportError(
            "deepagents包未安装，请运行: uv add deepagents 或 pip install deepagents"
        )

    # 报告生成Agent的系统提示词
    system_prompt = """你是报告撰写专家，负责将分析数据转化为专业、结构化的投资研究报告。

## 你的职责
1. 整合数据收集和分析结果
2. 生成格式规范、内容专业的投资研究报告
3. 确保报告的可读性和投资价值

## 报告类型

### 1. 综合研究报告（Comprehensive）
- 执行摘要
- 公司概况
- 行业分析
- 财务分析
- 技术分析
- 风险评估
- 投资建议

### 2. 技术分析报告（Technical）
- 价格走势概览
- 技术指标分析
- 图表形态识别
- 支撑/阻力位
- 交易建议

### 3. 基本面分析报告（Fundamental）
- 财务数据概览
- 盈利能力分析
- 估值分析
- 竞争优势
- 投资评级

## 报告结构
请按以下结构生成报告：

```
# [股票名称] ([股票代码]) 投资研究报告

## 执行摘要
- 核心观点
- 关键数据
- 投资建议

## 一、公司概况
- 基本信息
- 业务范围
- 发展历程

## 二、行业分析
- 行业概况
- 竞争格局
- 发展趋势

## 三、财务分析
- 营收和利润
- 财务比率
- 现金流

## 四、技术分析
- 价格走势
- 技术指标
- 形态分析

## 五、风险评估
- 市场风险
- 行业风险
- 公司风险

## 六、投资建议
- 评级（买入/持有/卖出）
- 目标价
- 风险提示
```

## 输出要求
1. 使用专业的金融术语
2. 数据必须准确，标注数据来源
3. 提供明确的投资建议和风险提示
4. 报告应逻辑清晰，层次分明
5. 针对不同受众（机构投资者/个人投资者）调整语言
6. 包含足够的细节支持投资决策

## 注意事项
1. 不要编造或推测数据
2. 客观呈现分析结果，避免过度乐观
3. 明确标注不确定性和局限性
4. 提供及时的更新说明
"""

    # 创建Agent
    _report_generator = create_deep_agent(
        name="report-generator",
        model=get_model(),
        system_prompt=system_prompt,
    )

    return _report_generator


def get_report_generator() -> Any:
    """获取或创建报告生成Agent实例（单例模式）"""
    if _report_generator is None:
        return create_report_generator()
    return _report_generator


async def generate_report(
    stock_symbol: str,
    data: Dict[str, Any],
    analysis: Dict[str, Any],
    report_type: str = "comprehensive",
    thread_id: str = "default"
) -> Dict[str, Any]:
    """
    生成投资研究报告

    Args:
        stock_symbol: 股票代码
        data: 收集的数据
        analysis: 分析结果
        report_type: 报告类型
        thread_id: 线程ID

    Returns:
        生成的研究报告
    """
    agent = get_report_generator()

    # 构造报告生成请求
    request = f"""请为股票 {stock_symbol} 生成一份{report_type}投资研究报告。

收集的数据：
{data}

分析结果：
{analysis}
"""

    # 配置线程
    config = {
        "configurable": {
            "thread_id": f"{thread_id}_report"
        }
    }

    # 运行Agent
    result = await agent.ainvoke(
        {"messages": [("user", request)]},
        config=config
    )

    return {
        "stock_symbol": stock_symbol,
        "report_type": report_type,
        "result": result,
        "thread_id": thread_id,
    }


def reset_report_generator() -> None:
    """重置报告生成Agent实例"""
    global _report_generator
    _report_generator = None