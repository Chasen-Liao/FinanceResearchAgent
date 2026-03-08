"""
测试财经数据工具
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# 添加项目根目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestFinanceTools:
    """测试finance_tools模块"""

    def test_get_stock_price_tool_exists(self):
        """测试get_stock_price工具是否存在"""
        from financieresearchagent.tools.finance_tools import get_stock_price
        assert get_stock_price is not None
        assert hasattr(get_stock_price, 'name')
        assert get_stock_price.name == "get_stock_price"

    def test_get_stock_info_tool_exists(self):
        """测试get_stock_info工具是否存在"""
        from financieresearchagent.tools.finance_tools import get_stock_info
        assert get_stock_info is not None
        assert hasattr(get_stock_info, 'name')

    def test_get_financial_data_tool_exists(self):
        """测试get_financial_data工具是否存在"""
        from financieresearchagent.tools.finance_tools import get_financial_data
        assert get_financial_data is not None

    def test_get_market_summary_tool_exists(self):
        """测试get_market_summary工具是否存在"""
        from financieresearchagent.tools.finance_tools import get_market_summary
        assert get_market_summary is not None


class TestAnalysisTools:
    """测试analysis_tools模块"""

    def test_calculate_technical_indicators_exists(self):
        """测试calculate_technical_indicators工具是否存在"""
        from financieresearchagent.tools.analysis_tools import calculate_technical_indicators
        assert calculate_technical_indicators is not None

    def test_analyze_fundamentals_exists(self):
        """测试analyze_fundamentals工具是否存在"""
        from financieresearchagent.tools.analysis_tools import analyze_fundamentals
        assert analyze_fundamentals is not None

    def test_analyze_price_trend_exists(self):
        """测试analyze_price_trend工具是否存在"""
        from financieresearchagent.tools.analysis_tools import analyze_price_trend
        assert analyze_price_trend is not None


class TestMarketTools:
    """测试market_tools模块"""

    def test_get_market_news_exists(self):
        """测试get_market_news工具是否存在"""
        from financieresearchagent.tools.market_tools import get_market_news
        assert get_market_news is not None

    def test_get_market_indices_exists(self):
        """测试get_market_indices工具是否存在"""
        from financieresearchagent.tools.market_tools import get_market_indices
        assert get_market_indices is not None

    def test_get_sector_performance_exists(self):
        """测试get_sector_performance工具是否存在"""
        from financieresearchagent.tools.market_tools import get_sector_performance
        assert get_sector_performance is not None


class TestReportTools:
    """测试report_tools模块"""

    def test_generate_research_report_exists(self):
        """测试generate_research_report工具是否存在"""
        from financieresearchagent.tools.report_tools import generate_research_report
        assert generate_research_report is not None

    def test_generate_market_summary_exists(self):
        """测试generate_market_summary工具是否存在"""
        from financieresearchagent.tools.report_tools import generate_market_summary
        assert generate_market_summary is not None

    def test_generate_stock_analysis_exists(self):
        """测试generate_stock_analysis工具是否存在"""
        from financieresearchagent.tools.report_tools import generate_stock_analysis
        assert generate_stock_analysis is not None


class TestProjectStructure:
    """测试项目结构"""

    def test_project_structure(self):
        """测试项目目录结构"""
        root = project_root

        # 核心目录
        assert (root / "financeresearchagent").exists()
        assert (root / "financeresearchagent" / "agents").exists()
        assert (root / "financeresearchagent" / "tools").exists()
        assert (root / "financeresearchagent" / "config").exists()
        assert (root / "skills").exists()

    def test_pyproject_toml(self):
        """测试pyproject.toml配置"""
        pyproject = project_root / "pyproject.toml"
        assert pyproject.exists()

        import tomllib
        with open(pyproject, "rb") as f:
            config = tomllib.load(f)

        assert config["project"]["name"] == "financeresearchagent"
        assert "dependencies" in config["project"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])