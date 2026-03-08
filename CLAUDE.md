# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个投资研究与决策支持Agent应用，旨在替代/辅助分析师工作，生成研究报告和市场分析。

## 技术栈与框架

### 核心框架
- **Deep Agents**: 基于LangChain/LangGraph的高层Agent框架，提供任务规划、文件管理、子任务委托等内置中间件
- **包管理**: 使用uv进行Python包管理
- **Python版本**: 3.11（由`.python-version`指定）

### 关键依赖
- **Agent框架**: deepagents, langchain, langgraph
- **数据获取**: yfinance, pandas, numpy, pandas-ta
- **报告生成**: jinja2, markdown, matplotlib, seaborn
- **异步处理**: httpx, aiohttp, asyncio
- **配置管理**: pydantic, pydantic-settings

## 项目架构

### 项目结构
```
financeresearchagent/
├── agents/           # Agent定义和实现
│   ├── main_agent.py      # 主研究Agent
│   ├── data_collector.py  # 数据收集子Agent
│   ├── analyst.py         # 分析子Agent
│   └── report_generator.py # 报告生成子Agent
├── tools/            # Agent工具库
│   ├── finance_tools.py   # 财经数据工具
│   ├── analysis_tools.py  # 分析工具
│   ├── report_tools.py    # 报告工具
│   └── market_tools.py    # 市场分析工具
├── models/           # 数据模型
│   ├── stock.py          # 股票数据模型
│   ├── report.py         # 报告模型
│   └── analysis.py       # 分析结果模型
├── services/         # 服务层
│   ├── data_service.py      # 数据服务
│   ├── analysis_service.py  # 分析服务
│   └── report_service.py    # 报告服务
├── skills/           # Deep Agents技能
│   ├── investment-analysis/SKILL.md
│   ├── report-writing/SKILL.md
│   └── risk-management/SKILL.md
├── utils/            # 工具函数
│   ├── helpers.py       # 通用工具函数
│   └── validators.py    # 数据验证
├── config/           # 配置管理
│   └── settings.py      # 应用配置
├── cli.py            # 命令行界面
├── api/              # API接口（可选）
│   └── main.py
└── tests/            # 测试文件
```

### Deep Agents配置
主研究Agent将使用以下中间件配置：
1. **TodoListMiddleware**: 用于任务分解和规划
2. **FilesystemMiddleware**: 用于文件管理
3. **SubAgentMiddleware**: 用于委托子任务（数据收集、分析、报告生成）
4. **MemoryMiddleware**（可选）: 用于长期记忆存储
5. **HumanInTheLoopMiddleware**（可选）: 用于关键决策审批

## 开发环境

### 环境设置
```bash
# 安装依赖
uv sync

# 激活虚拟环境
uv venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装开发依赖
uv add --group dev pytest pytest-asyncio black ruff mypy
```

### 运行应用
```bash
# 运行主应用
python -m financeresearchagent.cli

# 使用uv运行
uv run python -m financeresearchagent.cli

# 运行测试
uv run pytest

# 代码格式化
uv run black .

# 代码检查
uv run ruff check .

# 类型检查
uv run mypy .
```

### 测试
```bash
# 运行所有测试
uv run pytest

# 运行测试并显示覆盖率
uv run pytest --cov=financeresearchagent

# 运行单个测试文件
uv run pytest tests/test_research_agent.py

# 运行单个测试函数
uv run pytest tests/test_research_agent.py::test_generate_report
```

## 核心功能设计

### 1. 数据收集功能
- 股票数据获取（历史价格、财务数据）
- 市场新闻获取
- 经济指标数据
- 公司基本面数据

### 2. 分析功能
- 技术分析（趋势、指标、图表）
- 基本面分析（财务比率、估值模型）
- 市场情绪分析
- 风险评估

### 3. 报告生成功能
- 研究报告模板系统
- 自动图表生成
- 多格式输出（Markdown、PDF、HTML）
- 定制化报告内容

### 4. Agent工作流
1. **任务接收**: 接收研究任务（如"分析AAPL股票"）
2. **任务分解**: 分解为数据收集、分析、报告生成子任务
3. **子任务执行**: 委托给相应的子Agent
4. **结果整合**: 整合分析结果，生成完整报告
5. **质量检查**: 验证报告质量，必要时请求人工审核

## 实施路线图

### 阶段1：项目基础
- 配置依赖管理（更新pyproject.toml）
- 创建项目目录结构
- 配置环境变量和日志系统

### 阶段2：Deep Agents核心实现
- 实现主研究Agent
- 配置中间件（任务规划、文件管理、子任务委托）
- 实现基础工具库

### 阶段3：数据集成
- 集成财经数据API
- 实现数据获取工具
- 实现数据缓存和更新机制

### 阶段4：分析功能
- 实现技术分析工具
- 实现基本面分析工具
- 实现市场分析工具

### 阶段5：报告系统
- 实现报告模板系统
- 实现自动图表生成
- 实现多格式输出

### 阶段6：技能系统
- 创建投资分析技能
- 创建报告撰写技能
- 创建风险管理技能

### 阶段7：测试与优化
- 实现单元测试和集成测试
- 性能优化
- 用户体验优化

## 验证计划

### 功能验证
1. **启动测试**: 验证Agent能够正常启动和响应
2. **数据获取测试**: 验证财经数据获取功能
3. **分析测试**: 验证技术分析和基本面分析
4. **报告生成测试**: 验证研究报告生成质量
5. **完整工作流测试**: 从数据获取到报告生成的端到端测试

### 性能验证
1. **响应时间**: 关键操作应在可接受时间内完成
2. **内存使用**: 长时间运行不应有内存泄漏
3. **并发处理**: 支持同时处理多个分析任务

### 质量验证
1. **代码质量**: 通过代码审查和静态分析
2. **测试覆盖率**: 核心功能应达到80%以上覆盖率
3. **文档完整性**: API文档和用户指南

## 风险与缓解措施

1. **风险**: Deep Agents框架较新，可能存在不稳定因素
   **缓解**: 密切跟踪框架更新，实现适当的错误处理和回退机制

2. **风险**: 财经数据API的限制和变化
   **缓解**: 抽象数据源层，支持多数据源，实现缓存机制

3. **风险**: 分析结果的准确性问题
   **缓解**: 实现验证机制，提供置信度指标，保留人工审核环节

4. **风险**: 性能问题（大量数据处理）
   **缓解**: 实现增量处理，优化算法，使用缓存

## 扩展方向

1. **多市场支持**: 扩展支持A股、港股、加密货币等
2. **高级分析**: 集成机器学习模型进行预测分析
3. **实时监控**: 实现市场实时监控和预警
4. **多用户系统**: 支持多用户并发使用
5. **移动端应用**: 提供移动端访问界面

## 注意事项

1. **API密钥管理**: 使用环境变量存储敏感信息，不要提交到版本控制
2. **数据隐私**: 确保用户数据的安全性和隐私保护
3. **合规性**: 注意金融数据使用的合规要求
4. **错误处理**: 实现完善的错误处理和日志记录
5. **文档更新**: 随着项目发展，及时更新此文档

