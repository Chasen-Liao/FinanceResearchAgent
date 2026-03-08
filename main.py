"""
投资研究与决策支持Agent - 主入口

本应用使用Deep Agents框架构建，提供专业的投资研究功能。
"""

from dotenv import load_dotenv
import sys
from pathlib import Path

# 加载环境变量
load_dotenv()

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agent import ResearchAgent


def print_banner():
    """打印欢迎横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║       投资研究与决策支持Agent                                      ║
║    Investment Research & Decision Support Agent                  ║
║                                                                  ║
║             基于 Deep Agents + LangChain 构建                      ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def main():
    """主入口函数"""
    print_banner()

    # 检查API Key
    import os
    api_key = os.getenv("SILICONFLOW_API_KEY")
    if not api_key:
        print("警告: 未设置 SILICONFLOW_API_KEY 环境变量")
        print("请在 .env 文件中设置或导出环境变量")
        print()
        print("运行方式:")
        print("  1. 复制 .env.example 为 .env 并填入您的API Key")
        print("  2. 访问 https://siliconflow.cn 获取API Key")
        print("  3. 设置环境变量: $env:SILICONFLOW_API_KEY='your-key'")
        print()

    # 启动交互式CLI
    try:
        from cli import CLI
        cli = CLI()
        cli.run()
    except ImportError:
        # 如果CLI不可用，使用简单测试
        print("尝试简单测试...")
        agent = ResearchAgent()
        result = agent.research("你好，请介绍一下自己")
        print(result)


if __name__ == "__main__":
    main()