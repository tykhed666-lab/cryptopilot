# CryptoPilot

[![Backend CI](https://github.com/tykhed666-lab/cryptopilot/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/tykhed666-lab/cryptopilot/actions/workflows/backend-ci.yml)

CryptoPilot（币研智策）是一个面向币安生态的研究与交易双通道 Agent 项目。

项目计划结合 RAG、LangGraph、实时行情、确定性风控和人工审批机制，
为行业研究、交易决策支持和受控订单执行提供统一的 AI 应用后端。

> 当前处于工程基础阶段。币安接入、RAG、LangGraph 和交易执行功能尚未实现。

## Current status

Day 1 已完成：

- Python 3.12 `src` layout 可安装包
- uv 依赖与虚拟环境管理
- FastAPI 应用工厂
- `/health/live` 健康检查接口
- Ruff、mypy 和 pytest
- pre-commit 本地质量门禁
- GitHub Actions 后端 CI

## Planned capabilities

- Binance REST 与 WebSocket 实时行情
- 币安账户只读查询
- PDF 和 Markdown 知识导入
- Dense + Sparse 混合 RAG
- Milvus 向量检索
- LangChain 模型与工具集成
- LangGraph 研究工作流
- 行业研究报告生成
- 模拟交易与 Spot Testnet
- 币安 Agent OS / MCP 接入
- 确定性交易风控
- 真实订单逐单人工批准

## Safety

默认运行模式为 `research_only`。

在未显式配置和人工批准的情况下，系统不得：

- 使用真实交易凭据
- 创建真实订单
- 绕过确定性风险检查
- 自动批准资金操作

本项目仅用于技术学习和工程展示，不构成投资建议。

## Project structure

```text
CryptoPilot/
├── backend/
│   ├── src/cryptopilot/
│   │   └── api/
│   ├── tests/
│   ├── pyproject.toml
│   └── uv.lock
├── docs/
├── .github/workflows/
└── .pre-commit-config.yaml
```

## Development

要求：

- Python 3.12
- uv
- Git

安装依赖：

```powershell
Set-Location E:\CryptoPilot\backend
uv sync --locked --all-groups
```

执行质量检查：

```powershell
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest -m "not live"
```

启动开发服务：

```powershell
uv run uvicorn cryptopilot.api.app:app --reload
```

启动后访问：

```text
http://127.0.0.1:8000/health/live
http://127.0.0.1:8000/docs
```

## Development workflow

功能开发遵循：

```text
Issue / Task
→ feature branch
→ local checks
→ commit
→ Pull Request
→ GitHub Actions
→ review
→ merge
```

不要直接在 `main` 分支开发。

## License

A license has not been selected yet.
