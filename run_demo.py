"""
投资研究Agent - 快速Demo启动器
同时启动API服务器和静态文件服务
"""

import os
import sys
import webbrowser
import threading
import time
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# 静态文件目录
WWW_DIR = PROJECT_ROOT / "www"
API_DIR = PROJECT_ROOT / "api"


def start_static_server():
    """启动静态文件服务器"""
    PORT = 8080

    # 自定义Handler，明确指定静态文件目录
    class QuietHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(WWW_DIR), **kwargs)

        def log_message(self, format, *args):
            pass  # 静默日志

    with TCPServer(("", PORT), QuietHandler) as httpd:
        print(f"📁 静态文件服务: http://localhost:{PORT}")
        httpd.serve_forever()


def start_api_server():
    """启动FastAPI服务器"""
    import uvicorn
    from dotenv import load_dotenv

    # 加载环境变量
    load_dotenv()

    # 切换回项目根目录
    os.chdir(str(PROJECT_ROOT))

    # 获取端口配置
    port = int(os.getenv("PORT", "8001"))

    print(f"🚀 启动API服务器 (端口 {port})...")
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )


def main():
    from dotenv import load_dotenv
    load_dotenv()

    port = int(os.getenv("PORT", "8001"))

    print("=" * 60)
    print("  投资研究Agent - 快速Demo")
    print("=" * 60)
    print()
    print("服务将在以下地址启动:")
    print("  - 前端界面: http://localhost:8080")
    print(f"  - API后端: http://localhost:{port}")
    print()
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    print()

    # 检查API依赖
    try:
        import fastapi
        import uvicorn
    except ImportError:
        print("❌ 缺少依赖，请运行以下命令安装:")
        print("   uv sync")
        print("   uv add fastapi uvicorn")
        return

    # 启动静态文件服务器（后台）
    static_thread = threading.Thread(target=start_static_server, daemon=True)
    static_thread.start()
    time.sleep(1)

    # 启动API服务器（主线程）
    try:
        # 打开浏览器
        webbrowser.open("http://localhost:8080")

        # 启动API
        start_api_server()
    except KeyboardInterrupt:
        print("\n\n👋 服务已停止")
        sys.exit(0)


if __name__ == "__main__":
    main()