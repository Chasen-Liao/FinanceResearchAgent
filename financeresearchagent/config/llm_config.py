"""
LLM配置模块 - 使用硅基流动(SiliconFlow) API

统一管理 LLM 配置，避免重复代码
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# SiliconFlow 配置
SILICONFLOW_BASE_URL = "https://api.siliconflow.cn/v1"
SILICONFLOW_API_KEY = os.environ.get("SILICONFLOW_API_KEY")

# 常用模型配置
CHAT_MODELS = {
    "qwen2.5_7b": "Qwen/Qwen2.5-7B-Instruct",
    "qwen2.5_14b": "Qwen/Qwen2.5-14B-Instruct",
    "qwen2.5_32b": "Qwen/Qwen2.5-32B-Instruct",
    "glm4_9b": "THUDM/glm-4-9b-chat",
    "glm4_52b": "THUDM/glm-4-52b",
    "deepseek_v3": "deepseek-ai/DeepSeek-V3",
    "deepseek_v2_5": "deepseek-ai/DeepSeek-V2.5",
}

EMBEDDING_MODELS = {
    "bge_large": "BAAI/bge-large-zh-v1.5",
    "bge_base": "BAAI/bge-base-zh-v1.5",
    "bge_small": "BAAI/bge-small-zh-v1.5",
}

# 默认模型
DEFAULT_CHAT_MODEL = "deepseek_v3"  # 使用DeepSeek V2.5作为默认
DEFAULT_EMBEDDING_MODEL = "bge_base"


def get_llm(
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    **kwargs
):
    """
    创建 ChatOpenAI 实例（使用硅基流动API）

    Args:
        model: 模型名称，默认使用 DEFAULT_CHAT_MODEL
        temperature: 温度参数，控制随机性
        max_tokens: 最大 token 数
        **kwargs: 其他传递给 ChatOpenAI 的参数

    Returns:
        ChatOpenAI 实例
    """
    from langchain_openai import ChatOpenAI

    if not SILICONFLOW_API_KEY:
        raise ValueError(
            "未找到 SILICONFLOW_API_KEY 环境变量！\n"
            "请在 .env 文件中设置：SILICONFLOW_API_KEY=your-api-key\n"
            "或设置环境变量：$env:SILICONFLOW_API_KEY='your-api-key'"
        )

    # 获取实际模型名称
    model_name = model or DEFAULT_CHAT_MODEL
    if model_name in CHAT_MODELS:
        model_name = CHAT_MODELS[model_name]

    return ChatOpenAI(
        model=model_name,
        base_url=SILICONFLOW_BASE_URL,
        api_key=SILICONFLOW_API_KEY,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )


def get_embeddings(model: str = None):
    """
    创建 Embeddings 实例（使用硅基流动API）

    Args:
        model: Embedding 模型名称，默认使用 DEFAULT_EMBEDDING_MODEL

    Returns:
        OpenAIEmbeddings 实例
    """
    from langchain_openai import OpenAIEmbeddings

    if not SILICONFLOW_API_KEY:
        raise ValueError("未找到 SILICONFLOW_API_KEY 环境变量！")

    # 获取实际模型名称
    model_name = model or DEFAULT_EMBEDDING_MODEL
    if model_name in EMBEDDING_MODELS:
        model_name = EMBEDDING_MODELS[model_name]

    return OpenAIEmbeddings(
        model=model_name,
        base_url=SILICONFLOW_BASE_URL,
        api_key=SILICONFLOW_API_KEY
    )


def check_api_key() -> bool:
    """检查API Key是否配置"""
    return bool(SILICONFLOW_API_KEY)


def list_available_models() -> dict:
    """列出可用的模型"""
    return {
        "chat": CHAT_MODELS,
        "embedding": EMBEDDING_MODELS,
        "default_chat": DEFAULT_CHAT_MODEL,
        "default_embedding": DEFAULT_EMBEDDING_MODEL
    }