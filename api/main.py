"""
投资研究Agent - FastAPI后端
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
import asyncio

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 导入服务
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent

# 添加services目录到路径
services_path = project_root / "financeresearchagent" / "services"
utils_path = project_root / "financeresearchagent" / "utils"

if str(services_path) not in sys.path:
    sys.path.insert(0, str(services_path))
if str(utils_path) not in sys.path:
    sys.path.insert(0, str(utils_path))

# 从services导入
from data_service import get_data_service
from analysis_service import get_analysis_service
from report_service import get_report_service

# 导入ssl_fix
from ssl_fix import get_yfinance_ticker

# 创建FastAPI应用
app = FastAPI(
    title="投资研究与决策支持Agent API",
    description="基于Deep Agents的AI投资研究助手",
    version="0.1.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class StockRequest(BaseModel):
    symbol: str
    period: Optional[str] = "6mo"


class ReportRequest(BaseModel):
    symbol: str
    report_type: Optional[str] = "comprehensive"


class ComparisonRequest(BaseModel):
    symbols: List[str]


# 存储分析结果（生产环境应使用数据库）
analysis_cache: Dict[str, Any] = {}
report_cache: Dict[str, Any] = {}


@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "投资研究与决策支持Agent API",
        "version": "0.1.0",
        "endpoints": {
            "stock_data": "/api/stock/{symbol}",
            "stock_info": "/api/stock/{symbol}/info",
            "analysis": "/api/analysis/{symbol}",
            "report": "/api/report",
            "compare": "/api/compare",
            "market_indices": "/api/market/indices"
        }
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# 股票数据接口
@app.get("/api/stock/{symbol}")
async def get_stock_data(symbol: str, period: str = "1y"):
    """获取股票历史数据"""
    try:
        data_service = get_data_service()
        data = data_service.get_stock_data(symbol.upper(), period)

        if data.empty:
            raise HTTPException(status_code=404, detail=f"无法获取 {symbol} 的数据")

        # 转换为字典列表
        records = data.reset_index()
        records['Date'] = records['Date'].dt.isoformat()

        return {
            "symbol": symbol.upper(),
            "period": period,
            "data": records.to_dict(orient="records"),
            "count": len(records)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stock/{symbol}/info")
async def get_stock_info(symbol: str):
    """获取股票基本信息"""
    try:
        data_service = get_data_service()
        info = data_service.get_stock_info(symbol.upper())

        if not info:
            raise HTTPException(status_code=404, detail=f"无法获取 {symbol} 的信息")

        # 过滤掉嵌套对象，简化返回
        simplified = {}
        for key, value in info.items():
            if not isinstance(value, (dict, list)):
                simplified[key] = value

        return {
            "symbol": symbol.upper(),
            "info": simplified
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 技术分析接口
@app.get("/api/analysis/{symbol}")
async def analyze_stock(symbol: str):
    """分析股票（技术分析+基本面分析）"""
    try:
        # 检查缓存
        cache_key = f"{symbol.upper()}_analysis"
        if cache_key in analysis_cache:
            cached = analysis_cache[cache_key]
            # 5分钟内使用缓存
            if (datetime.now() - cached.get("cached_at", datetime.min)).total_seconds() < 300:
                return cached["data"]

        analysis_service = get_analysis_service()
        data_service = get_data_service()

        # 技术指标
        technical = analysis_service.calculate_technical_indicators(symbol.upper())

        # 趋势
        trend = analysis_service.analyze_price_trend(symbol.upper())

        # 基本面
        fundamentals = analysis_service.analyze_fundamentals(symbol.upper())

        # 生成信号
        signal = analysis_service.generate_technical_signal(symbol.upper())

        # 股票信息
        info = data_service.get_stock_info(symbol.upper())
        name = info.get('shortName', symbol.upper()) if info else symbol.upper()
        hist = data_service.get_stock_data(symbol.upper(), period="1d")
        current_price = hist['Close'].iloc[-1] if not hist.empty else 0

        result = {
            "symbol": symbol.upper(),
            "name": name,
            "current_price": current_price,
            "technical": technical,
            "trend": trend,
            "fundamentals": fundamentals,
            "signal": signal,
            "report_date": datetime.now().isoformat()
        }

        # 缓存结果
        analysis_cache[cache_key] = {
            "data": result,
            "cached_at": datetime.now()
        }

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 报告生成接口
@app.post("/api/report")
async def generate_report(request: ReportRequest):
    """生成研究报告"""
    try:
        report_service = get_report_service()
        report = report_service.generate_research_report(
            request.symbol.upper(),
            request.report_type
        )

        report_id = str(uuid.uuid4())
        report_cache[report_id] = {
            "symbol": request.symbol.upper(),
            "report": report,
            "created_at": datetime.now()
        }

        return {
            "report_id": report_id,
            "symbol": request.symbol.upper(),
            "report_type": request.report_type,
            "report": report,
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/report/{report_id}")
async def get_report(report_id: str):
    """获取报告"""
    if report_id not in report_cache:
        raise HTTPException(status_code=404, detail="报告不存在")

    return report_cache[report_id]


# 股票对比接口
@app.post("/api/compare")
async def compare_stocks(request: ComparisonRequest):
    """对比多只股票"""
    try:
        data_service = get_data_service()

        results = []
        for symbol in request.symbols:
            info = data_service.get_stock_info(symbol.upper())
            hist = data_service.get_stock_data(symbol.upper(), period="5d")

            if hist.empty:
                continue

            current = hist['Close'].iloc[-1]
            change_5d = ((current - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100

            results.append({
                "symbol": symbol.upper(),
                "name": info.get('shortName', symbol.upper()) if info else symbol.upper(),
                "price": current,
                "change_5d": change_5d,
                "pe_ratio": info.get('peRatio') if info else None,
                "market_cap": info.get('marketCap') if info else None,
                "dividend_yield": info.get('dividendYield') if info else None
            })

        return {
            "symbols": request.symbols,
            "results": results,
            "compare_date": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 市场指数接口
@app.get("/api/market/indices")
async def get_market_indices():
    """获取市场指数"""
    try:
        data_service = get_data_service()
        indices = data_service.get_market_indices()

        return {
            "indices": indices,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 板块表现接口
@app.get("/api/market/sectors")
async def get_sector_performance():
    """获取板块表现"""
    try:
        sectors = {
            'XLK': '科技',
            'XLF': '金融',
            'XLE': '能源',
            'XLV': '医疗',
            'XLP': '消费',
            'XLY': '非必需消费',
            'XLI': '工业',
            'XLB': '原材料',
            'XLU': '公用事业'
        }

        results = []
        for symbol, name in sectors.items():
            try:
                etf = get_yfinance_ticker(symbol)
                hist = etf.history(period="1mo")
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    month_start = hist['Close'].iloc[0]
                    change = ((current - month_start) / month_start) * 100
                    results.append({
                        "sector": name,
                        "symbol": symbol,
                        "change": change
                    })
            except:
                continue

        # 按涨跌幅排序
        results.sort(key=lambda x: x['change'], reverse=True)

        return {
            "sectors": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)