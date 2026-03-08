"""
投资研究Agent命令行界面
"""
import sys
from typing import Optional

from agent import ResearchAgent


class CLI:
    """交互式命令行界面"""

    def __init__(self):
        self.agent = ResearchAgent()
        self.running = True

    def print_welcome(self):
        print("=" * 60)
        print("  投资研究与决策支持Agent")
        print("  Investment Research & Decision Support Agent")
        print("=" * 60)
        print()
        print("输入您的研究需求 (例如: '分析苹果公司股票/AAPL')")
        print("输入 'help' 查看帮助")
        print("输入 'quit' 或 'exit' 退出")
        print()

    def print_help(self):
        print("""
可用命令:
  help              - 显示帮助信息
  status            - 查看当前任务状态
  recent            - 查看最近的研究报告
  clear             - 清除屏幕
  quit/exit         - 退出程序

示例:
  - 分析苹果公司股票
  - 分析AAPL的投资价值
  - 生成特斯拉(TSLA)的最新研究报告
  - 对比亚马逊和谷歌的财务数据
""")

    def handle_input(self, user_input: str) -> Optional[bool]:
        """处理用户输入"""
        user_input = user_input.strip().lower()

        if user_input in ["quit", "exit", "q"]:
            print("感谢使用，再见！")
            return False
        elif user_input == "help":
            self.print_help()
        elif user_input == "status":
            print("当前任务状态: 等待输入...")
        elif user_input == "clear":
            print("\033[2J\033[H")  # 清屏
        elif user_input:
            # 处理研究请求
            self.process_research_request(user_input)

        return None

    def process_research_request(self, query: str):
        """处理研究请求"""
        print(f"\n正在处理您的请求: {query}")
        print("-" * 40)

        try:
            result = self.agent.research(query)
            print("\n研究结果:")
            print(result)
        except Exception as e:
            print(f"错误: {e}")
            print("请稍后重试或修改您的请求。")

    def run(self):
        """运行CLI主循环"""
        self.print_welcome()

        while self.running:
            try:
                user_input = input("\n> ")
                if not user_input:
                    continue

                result = self.handle_input(user_input)
                if result is False:
                    break

            except KeyboardInterrupt:
                print("\n\n感谢使用，再见！")
                break
            except EOFError:
                break


def main():
    """主入口"""
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()