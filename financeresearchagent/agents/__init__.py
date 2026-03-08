"""
Agents模块 - 投资研究Agent核心实现

包含主Agent和子Agent的创建与配置。
"""

from .main_agent import create_main_agent, get_main_agent
from .data_collector import create_data_collector, get_data_collector
from .analyst import create_analyst, get_analyst
from .report_generator import create_report_generator, get_report_generator

__all__ = [
    "create_main_agent",
    "get_main_agent",
    "create_data_collector",
    "get_data_collector",
    "create_analyst",
    "get_analyst",
    "create_report_generator",
    "get_report_generator",
]