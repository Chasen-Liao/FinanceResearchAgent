"""
应用配置 - 使用Pydantic Settings进行配置管理

支持从环境变量或.env文件加载配置。
"""

import os
from typing import Optional, List
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    应用配置类

    从环境变量加载配置，支持以下来源：
    1. 环境变量
    2. .env文件

    示例：
    ```bash
    # 设置API密钥 (硅基流动)
    export SILICONFLOW_API_KEY="sk-xxxxx"

    # 设置数据目录
    export DATA_DIR="/path/to/data"
    ```
    """

    # 模型配置 - 硅基流动 API
    siliconflow_api_key: Optional[str] = Field(
        default=None,
        description="硅基流动API密钥，用于LLM调用"
    )
    siliconflow_base_url: str = Field(
        default="https://api.siliconflow.cn/v1",
        description="硅基流动API基础URL"
    )
    model_name: str = Field(
        default="deepseek-ai/DeepSeek-V3",
        description="使用的LLM模型名称（硅基流动模型）"
    )
    model_temperature: float = Field(
        default=0.7,
        description="LLM温度参数"
    )
    model_max_tokens: int = Field(
        default=4096,
        description="LLM最大输出token数"
    )

    # Agent配置
    agent_thread_id: str = Field(
        default="default",
        description="默认线程ID"
    )
    enable_checkpointer: bool = Field(
        default=True,
        description="是否启用状态持久化"
    )

    # 数据源配置
    data_source: str = Field(
        default="yfinance",
        description="主要数据源（yfinance等）"
    )
    data_cache_ttl: int = Field(
        default=3600,
        description="数据缓存TTL（秒）"
    )

    # 文件目录配置
    base_dir: str = Field(
        default=".",
        description="项目基础目录"
    )
    reports_dir: str = Field(
        default="reports",
        description="报告输出目录"
    )
    data_dir: str = Field(
        default="data",
        description="数据存储目录"
    )
    analysis_dir: str = Field(
        default="analysis",
        description="分析结果目录"
    )
    logs_dir: str = Field(
        default="logs",
        description="日志目录"
    )

    # 报告配置
    default_report_type: str = Field(
        default="comprehensive",
        description="默认报告类型"
    )
    report_formats: List[str] = Field(
        default=["markdown", "html"],
        description="支持的报告格式"
    )

    # 风险配置
    risk_threshold_high: float = Field(
        default=0.7,
        description="高风险阈值"
    )
    risk_threshold_medium: float = Field(
        default=0.4,
        description="中等风险阈值"
    )

    # 交易配置（可选）
    trading_enabled: bool = Field(
        default=False,
        description="是否启用交易功能"
    )

    # 日志配置
    log_level: str = Field(
        default="INFO",
        description="日志级别"
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )

    # MCP服务器配置（可选）
    mcp_servers: Optional[str] = Field(
        default=None,
        description="MCP服务器配置JSON字符串"
    )

    # 开发配置
    debug: bool = Field(
        default=False,
        description="调试模式"
    )
    dev_mode: bool = Field(
        default=False,
        description="开发模式"
    )

    # Pydantic Settings配置
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # 环境变量不区分大小写
        extra="ignore",  # 忽略额外字段
    )


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置实例（单例模式，使用缓存）

    Returns:
        Settings实例
    """
    return Settings()


def reload_settings() -> Settings:
    """
    重新加载配置（清除缓存）

    Returns:
        新的Settings实例
    """
    get_settings.cache_clear()
    return get_settings()


# 便捷函数：获取特定配置
def get_api_key() -> Optional[str]:
    """获取硅基流动API密钥"""
    return get_settings().siliconflow_api_key


def get_model_config() -> dict:
    """获取模型配置"""
    settings = get_settings()
    return {
        "model_name": settings.model_name,
        "temperature": settings.model_temperature,
        "max_tokens": settings.model_max_tokens,
    }


def get_directory_config() -> dict:
    """获取目录配置"""
    settings = get_settings()
    return {
        "base_dir": settings.base_dir,
        "reports_dir": settings.reports_dir,
        "data_dir": settings.data_dir,
        "analysis_dir": settings.analysis_dir,
        "logs_dir": settings.logs_dir,
    }


# 示例：如何在代码中使用配置
"""
from .settings import get_settings, get_api_key, get_model_config

# 获取完整配置
settings = get_settings()
print(f"模型名称: {settings.model_name}")

# 获取API密钥
api_key = get_api_key()

# 获取模型配置
model_cfg = get_model_config()

# 检查是否启用某功能
if settings.debug:
    print("调试模式已启用")
"""