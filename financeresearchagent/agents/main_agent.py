"""
主研究Agent - 负责协调整个投资研究工作流程

该Agent使用Deep Agents框架创建，配置了以下中间件：
- TodoListMiddleware: 任务规划与分解
- FilesystemMiddleware: 文件操作管理
- SubAgentMiddleware: 子任务委托
"""

from typing import Optional, Any, Dict
from langgraph.checkpoint.memory import MemorySaver

# 导入硅基流动LLM配置
from financieresearchagent.config.llm_config import get_llm

# 导入中间件
# 注意：这些中间件类在实际使用deepagents时会从deepagents导入
# 这里提前定义好导入路径
try:
    from deepagents import (
        create_deep_agent,
        TodoListMiddleware,
        FilesystemMiddleware,
        SubAgentMiddleware,
    )
    DEEP_AGENTS_AVAILABLE = True
except ImportError:
    DEEP_AGENTS_AVAILABLE = False
    # 如果deepagents不可用，使用占位符
    create_deep_agent = None
    TodoListMiddleware = None
    FilesystemMiddleware = None
    SubAgentMiddleware = None

# 全局Agent实例缓存
_main_agent: Optional[Any] = None


def get_model():
    """获取配置的LLM模型（硅基流动API）"""
    return get_llm(
        model="deepseek_v3",
        temperature=0.7,
        max_tokens=4096,
    )


def create_main_agent() -> Any:
    """
    创建主研究Agent

    Returns:
        配置好的主Agent实例
    """
    global _main_agent

    if _main_agent is not None:
        return _main_agent

    if not DEEP_AGENTS_AVAILABLE:
        raise ImportError(
            "deepagents包未安装，请运行: uv add deepagents 或 pip install deepagents"
        )

    # 创建checkpointer用于状态持久化
    checkpointer = MemorySaver()

    # 创建中间件实例
    todo_middleware = TodoListMiddleware()
    filesystem_middleware = FilesystemMiddleware(
        allowed_dirs=["reports/", "data/", "analysis/"]
    )
    subagent_middleware = SubAgentMiddleware()

    # 主Agent的系统提示词
    system_prompt = """你是投资研究Agent，负责分析股票市场并生成专业的研究报告。

## 你的职责
1. 接收用户的研究请求（如"分析AAPL股票"或"生成腾讯控股的深度报告"）
2. 规划任务步骤并分配给子Agent
3. 协调数据收集、分析、报告生成的工作流程
4. 整合最终结果并呈现给用户

## 可用工具
- write_todos: 规划和管理任务步骤
- ls/read_file/write_file: 文件系统操作
- task: 委托子任务给专门的Agent

## 子任务类型
- data_collector: 负责收集财经数据、财务报表、市场新闻等
- analyst: 负责技术分析、基本面分析、风险评估
- report_generator: 负责生成专业的研究报告文档

## 工作流程
1. 理解用户请求，明确研究目标
2. 使用write_todos规划任务步骤
3. 依次委托子任务：
   - 首先委托data_collector收集数据
   - 然后委托analyst进行数据分析
   - 最后委托report_generator生成报告
4. 整合所有结果，返回完整的研究报告
5. 将报告保存到指定目录

## 输出格式
提供清晰、结构化的分析结果，包含：
- 执行摘要
- 数据来源说明
- 分析方法论
- 详细分析内容
- 投资建议和风险提示
"""

    # 创建Agent
    _main_agent = create_deep_agent(
        name="research-agent",
        model=get_model(),
        system_prompt=system_prompt,
        checkpointer=checkpointer,
        middleware=[
            todo_middleware,
            filesystem_middleware,
            subagent_middleware,
        ],
    )

    return _main_agent


def get_main_agent() -> Any:
    """获取或创建主Agent实例（单例模式）"""
    if _main_agent is None:
        return create_main_agent()
    return _main_agent


async def run_research(
    stock_symbol: str,
    report_type: str = "comprehensive",
    thread_id: str = "default"
) -> Dict[str, Any]:
    """
    运行投资研究任务

    Args:
        stock_symbol: 股票代码（如 "AAPL"）
        report_type: 报告类型（"comprehensive", "technical", "fundamental"）
        thread_id: 线程ID，用于状态管理

    Returns:
        包含研究结果的字典
    """
    agent = get_main_agent()

    # 构造研究请求
    request = f"""请对股票 {stock_symbol} 进行{report_type}分析研究，生成完整的研究报告。"""

    # 配置线程
    config = {
        "configurable": {
            "thread_id": thread_id
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


def reset_main_agent() -> None:
    """重置主Agent实例（用于测试或重新配置）"""
    global _main_agent
    _main_agent = None