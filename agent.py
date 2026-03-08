"""
投资研究Agent核心模块
"""
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_openai import ChatOpenAI

# 加载环境变量
load_dotenv()

# 硅基流动配置
SILICONFLOW_BASE_URL = "https://api.siliconflow.cn/v1"
SILICONFLOW_API_KEY = os.environ.get("SILICONFLOW_API_KEY")


def get_siliconflow_model():
    """获取硅基流动模型实例"""
    if not SILICONFLOW_API_KEY:
        raise ValueError(
            "未找到 SILICONFLOW_API_KEY 环境变量！\n"
            "请在 .env 文件中设置：SILICONFLOW_API_KEY=your-api-key"
        )

    return ChatOpenAI(
        model="deepseek-ai/DeepSeek-V3",
        base_url=SILICONFLOW_BASE_URL,
        api_key=SILICONFLOW_API_KEY,
        temperature=0.7,
        max_tokens=4096,
    )


class ResearchAgent:
    """投资研究主Agent"""

    def __init__(self, thread_id: str = "default"):
        self.thread_id = thread_id
        self.agent = self._create_agent()
        self.config = {"configurable": {"thread_id": thread_id}}

    def _create_agent(self):
        """创建Deep Agent实例（使用硅基流动模型）"""
        return create_deep_agent(
            name="research-agent",
            model=get_siliconflow_model(),
            system_prompt="""你是专业的投资研究Agent，负责分析股票市场并生成研究报告。

## 你的能力
1. **数据收集**: 获取股票价格、财务数据、市场新闻
2. **技术分析**: 计算MA、RSI、MACD等技术指标
3. **基本面分析**: 分析P/E、P/B、ROE等财务指标
4. **报告生成**: 生成专业的研究报告

## 工作流程
1. 使用write_todos规划任务
2. 收集所需数据
3. 进行分析
4. 生成报告

## 工具使用
- 使用task工具委托子任务给专业Agent
- 使用filesystem工具管理文件
- 使用write_todos记录任务进度
""",
            subagents=[
                {
                    "name": "data-collector",
                    "description": "收集股票市场数据、财务数据、新闻等",
                    "system_prompt": "你是数据收集专家，负责从各种来源获取股票相关数据。",
                },
                {
                    "name": "analyst",
                    "description": "进行技术分析和基本面分析",
                    "system_prompt": "你是金融分析专家，负责技术分析和基本面分析。",
                },
                {
                    "name": "report-generator",
                    "description": "生成专业的研究报告",
                    "system_prompt": "你是报告撰写专家，负责生成格式规范、内容专业的研究报告。",
                }
            ],
            backend=FilesystemBackend(root_dir=".", virtual_mode=True),
            checkpointer=MemorySaver(),
            store=InMemoryStore(),
            interrupt_on={},
        )

    def research(self, query: str) -> str:
        """
        执行研究请求

        Args:
            query: 用户的研究请求

        Returns:
            研究结果
        """
        result = self.agent.invoke({
            "messages": [{"role": "user", "content": query}]
        }, config=self.config)

        # 提取最终回复
        if "messages" in result:
            return result["messages"][-1].get("content", "No response")
        return str(result)

    def get_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        return self.agent.get_state(self.config)

    def get_todos(self) -> list:
        """获取任务列表"""
        state = self.get_state()
        return state.get("todos", [])


def main():
    """测试入口"""
    agent = ResearchAgent()
    result = agent.research("分析苹果公司(AAPL)的投资价值")
    print(result)


if __name__ == "__main__":
    main()