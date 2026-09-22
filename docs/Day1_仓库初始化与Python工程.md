# Day 1：仓库初始化与 Python 工程

> 今天的目标不是写币安业务，而是建立一个后面 41 天都不会拖后腿的工程。
> 工作目录：`E:\CryptoPilot`
> 预计时间：6–8 小时。

## 0. 今天完成后的结果

Day 1 结束时，你应该拥有：

- 一个本地 Git 仓库和一个 GitHub 公开仓库。
- `main` 分支和 `chore/bootstrap-repository` 开发分支。
- Python 3.12 的可安装 `cryptopilot` 包。
- uv 管理的依赖和虚拟环境。
- Ruff、mypy、pytest、pre-commit。
- 一个最小 FastAPI app 和 smoke test。
- GitHub Actions CI。
- README、项目范围 ADR、PR 模板。
- 一个等待合并或已合并的 Day 1 PR。

今天不做：币安 API、WebSocket、Redis、RAG、LangChain、LangGraph、前端、下单。

## 1. 你的电脑环境

已检查到：

```text
Git:        2.55.0
系统 Python: 3.14.5
uv:         0.12.9
Docker:     29.6.2
GitHub CLI: 未安装
uv Python:  已安装 3.12.14
```

本项目固定 Python 3.12。不要直接执行系统的 `python` 来创建环境；使用 `uv` 选择 3.12。

## 2. 第一步：确认 Git 身份

打开 PowerShell：

```powershell
git config --global user.name
git config --global user.email
```

如果没有输出，再填写自己的信息：

```powershell
git config --global user.name "你的 GitHub 用户名或姓名"
git config --global user.email "你的 GitHub 邮箱或 noreply 邮箱"
```

若不想公开私人邮箱，可以在 GitHub 的 Email Settings 中启用隐私邮箱，再把该 noreply 邮箱配置给 Git。

验收：

```powershell
git config --global --list
```

能看到 `user.name` 和 `user.email`。

## 3. 第二步：初始化本地仓库

进入已有项目目录：

```powershell
Set-Location -LiteralPath 'E:\CryptoPilot'
Get-ChildItem -Force
```

此时应看到已有的 `docs` 目录。

初始化仓库：

```powershell
git init -b main
git status
```

预期：Git 显示当前位于 `main`，`docs/` 是未跟踪内容。

### 3.1 创建根目录 `.gitignore`

使用编辑器创建 `E:\CryptoPilot\.gitignore`：

```gitignore
# Secrets
.env
.env.*
!.env.example
*.pem
*.key
secrets/
credentials/

# Python
.venv/
venv/
__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
coverage.xml
htmlcov/
dist/
build/

# IDE and OS
.idea/
.vscode/
*.swp
*.swo
.DS_Store
Thumbs.db

# Runtime data
logs/
data/
volumes/
models/
cache/
tmp/
temp/

# Databases and object storage
milvus_data/
mongo_data/
redis_data/
minio_data/

# Frontend
node_modules/
.vite/
frontend/dist/
```

注意：不要忽略 `uv.lock`，它应该提交到 Git。

### 3.2 创建根目录 `.editorconfig`

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.py]
indent_style = space
indent_size = 4

[*.{json,yaml,yml,toml,md}]
indent_style = space
indent_size = 2

[*.md]
trim_trailing_whitespace = false
```

### 3.3 保存已有计划作为仓库出生提交

先确认不会提交敏感内容：

```powershell
git status
git diff --no-index -- NUL .gitignore
```

暂存并提交已有文档和基础规则：

```powershell
git add docs .gitignore .editorconfig
git diff --staged --stat
git commit -m "docs: add project plans and repository rules"
```

查看结果：

```powershell
git log --oneline --decorate -1
git status
```

此时工作区应干净。

## 4. 第三步：在 GitHub 创建空仓库

当前电脑没有 `gh`，使用浏览器：

1. 登录 GitHub。
2. 打开 [Create a new repository](https://github.com/new)。
3. Repository name：`cryptopilot`。
4. Description：`A dual-channel Binance research and trading agent with RAG, LangGraph and human-in-the-loop risk controls.`
5. 选择 Public。
6. 不勾选 README、`.gitignore` 和 License，因为本地已经有仓库。
7. 点击 Create repository。

GitHub 会显示远程地址。回到 PowerShell，将 `<你的GitHub用户名>` 换成真实用户名：

```powershell
git remote add origin https://github.com/<你的GitHub用户名>/cryptopilot.git
git remote -v
git push -u origin main
```

如果 GitHub 弹出浏览器登录，按页面完成授权。不要把 GitHub Token 写入项目文件。

验收：刷新 GitHub 页面，能看到 `docs/`、`.gitignore` 和 `.editorconfig`。

## 5. 第四步：创建 Day 1 开发分支

```powershell
git switch -c chore/bootstrap-repository
git branch --show-current
```

必须输出：

```text
chore/bootstrap-repository
```

后面的工程文件都在这个分支完成，不直接写入 `main`。

## 6. 第五步：创建 Python 3.12 可安装包

### 6.1 创建 backend 工程

```powershell
Set-Location -LiteralPath 'E:\CryptoPilot'
New-Item -ItemType Directory -Path 'backend' -ErrorAction Stop
Set-Location -LiteralPath 'E:\CryptoPilot\backend'
uv init --lib --name cryptopilot --python 3.12
```

检查：

```powershell
Get-ChildItem -Force
Get-ChildItem -Recurse -LiteralPath 'src'
Get-Content -LiteralPath '.python-version'
```

`.python-version` 应是 `3.12`，源码应位于：

```text
backend/src/cryptopilot/
```

### 6.2 安装运行依赖

```powershell
uv add fastapi "uvicorn[standard]" pydantic pydantic-settings httpx websockets redis orjson structlog
```

### 6.3 安装开发依赖

```powershell
uv add --dev pytest pytest-asyncio pytest-cov respx ruff mypy pre-commit
```

### 6.4 创建环境并验证 Python

```powershell
uv sync --all-groups
uv run python --version
uv run python -c "import cryptopilot; print(cryptopilot.__file__)"
```

必须看到 Python 3.12，而不是 3.14。

### 6.5 第一次工程提交

回到根目录：

```powershell
Set-Location -LiteralPath 'E:\CryptoPilot'
git status
git add backend
git diff --staged --stat
git commit -m "chore: bootstrap installable python workspace"
```

不要提交 `backend/.venv`；如果它出现在 `git status`，先检查 `.gitignore`。

## 7. 第六步：配置 Ruff、mypy 和 pytest

打开 `E:\CryptoPilot\backend\pyproject.toml`。

保留 `uv init` 生成的 `[build-system]`、`[project]` 和依赖，在文件末尾追加：

```toml
[tool.ruff]
target-version = "py312"
line-length = 100
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "ASYNC"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.mypy]
python_version = "3.12"
strict = true
files = ["src", "tests"]
warn_unused_configs = true
show_error_codes = true

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = [
  "--strict-config",
  "--strict-markers",
  "--cov=cryptopilot",
  "--cov-report=term-missing",
]
markers = [
  "live: requires external network and is never run in CI",
]

[tool.coverage.run]
branch = true
source = ["cryptopilot"]

[tool.coverage.report]
show_missing = true
skip_covered = true
```

为什么不配置 `pythonpath = ["src"]`：因为项目应该通过安装后导入，而不是让 pytest 绕过打包配置直接找到源码。

先运行格式化：

```powershell
Set-Location -LiteralPath 'E:\CryptoPilot\backend'
uv run ruff format .
uv run ruff check .
uv run mypy src
```

如果此时 pytest 提示没有 tests，下一步会补上。

## 8. 第七步：创建最小 FastAPI 应用

创建目录：

```powershell
New-Item -ItemType Directory -Force -Path 'src\cryptopilot\api'
New-Item -ItemType Directory -Force -Path 'tests'
```

使用编辑器创建空文件：

```text
backend/src/cryptopilot/api/__init__.py
```

创建 `backend/src/cryptopilot/api/app.py`：

```python
from fastapi import FastAPI


def create_app() -> FastAPI:
    """Create the CryptoPilot API application."""
    app = FastAPI(
        title="CryptoPilot API",
        version="0.0.1",
        description="Binance research and trading agent backend.",
    )

    @app.get("/health/live", tags=["health"])
    async def liveness() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
```

这里同时提供：

- `app`：方便执行 `uvicorn cryptopilot.api.app:app`。
- `create_app()`：方便测试和以后做依赖注入。

## 9. 第八步：创建 smoke test

创建 `backend/tests/test_smoke.py`：

```python
from fastapi.testclient import TestClient

from cryptopilot.api.app import create_app


def test_package_is_importable() -> None:
    import cryptopilot

    assert cryptopilot.__name__ == "cryptopilot"


def test_app_factory_creates_named_application() -> None:
    app = create_app()

    assert app.title == "CryptoPilot API"


def test_liveness_endpoint() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

运行所有检查：

```powershell
uv run ruff format .
uv run ruff check .
uv run mypy src tests
uv run pytest
```

然后启动应用：

```powershell
uv run uvicorn cryptopilot.api.app:app --reload
```

浏览器打开：

```text
http://127.0.0.1:8000/health/live
http://127.0.0.1:8000/docs
```

确认成功后在终端按 `Ctrl+C` 停止服务。

### 第二次工程提交

```powershell
Set-Location -LiteralPath 'E:\CryptoPilot'
git add backend
git diff --staged
git commit -m "test: add fastapi application smoke tests"
```

## 10. 第九步：配置 pre-commit

创建根目录 `E:\CryptoPilot\.pre-commit-config.yaml`：

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: check-toml
      - id: check-yaml
      - id: detect-private-key
      - id: end-of-file-fixer
      - id: trailing-whitespace

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.12.17
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format
```

说明：你的本机 uv 是 0.12.9，但 pre-commit 中 Ruff 使用独立版本，两者不是同一个工具。

安装并执行：

```powershell
Set-Location -LiteralPath 'E:\CryptoPilot\backend'
uv run pre-commit install --config ..\.pre-commit-config.yaml
uv run pre-commit run --all-files --config ..\.pre-commit-config.yaml
```

如果 pre-commit 自动修改文件，再重新运行一次，直到全部通过。

提交：

```powershell
Set-Location -LiteralPath 'E:\CryptoPilot'
git add .pre-commit-config.yaml backend
git commit -m "chore: add local quality hooks"
```

## 11. 第十步：配置 GitHub Actions

创建：

```text
E:\CryptoPilot\.github\workflows\backend-ci.yml
```

内容：

```yaml
name: Backend CI

on:
  pull_request:
    paths:
      - "backend/**"
      - ".github/workflows/backend-ci.yml"
  push:
    branches: [main]
    paths:
      - "backend/**"
      - ".github/workflows/backend-ci.yml"

permissions:
  contents: read

jobs:
  quality:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    defaults:
      run:
        working-directory: backend

    steps:
      - name: Check out repository
        uses: actions/checkout@v5

      - name: Install uv and Python
        uses: astral-sh/setup-uv@v10.2.0
        with:
          python-version: "3.12"
          enable-cache: true

      - name: Install dependencies
        run: uv sync --locked --all-groups

      - name: Ruff lint
        run: uv run ruff check .

      - name: Ruff format
        run: uv run ruff format --check .

      - name: Type check
        run: uv run mypy src tests

      - name: Test
        run: uv run pytest -m "not live"
```

CI 中不填写币安或 LLM Secret，也不访问币安网络。

提交：

```powershell
Set-Location -LiteralPath 'E:\CryptoPilot'
git add .github/workflows/backend-ci.yml
git commit -m "ci: add backend quality workflow"
```

## 12. 第十一步：补 README 和 ADR

### 12.1 根目录 README 必须包含

创建 `E:\CryptoPilot\README.md`，至少写：

```markdown
# CryptoPilot

CryptoPilot is a dual-channel Binance research and trading agent built with
hybrid RAG, LangGraph, deterministic risk controls and human approval.

## Current status

Day 1 / v0.0.1: repository and Python backend foundation.

## Planned capabilities

- Binance REST and WebSocket market data
- PDF/Markdown knowledge ingestion
- Dense + sparse RAG with Milvus
- LangGraph research workflow
- Paper, Spot Testnet and Agent OS MCP execution modes
- Deterministic risk checks and per-order approval

## Safety

The default mode is research-only. Live execution is disabled unless explicitly
configured and approved. This project does not provide investment advice.

## Development

```powershell
cd backend
uv sync --all-groups
uv run pytest
uv run uvicorn cryptopilot.api.app:app --reload
```
```

可以继续补中文介绍，但不要在 README 中声称尚未实现的功能已经完成。

### 12.2 ADR-0001

创建 `docs/adr/0001-project-scope.md`，回答：

- 项目解决什么问题？
- 为什么采用研究 + 交易双通道？
- 为什么第一版只支持 Spot？
- 为什么真实交易必须逐单人工批准？
- 为什么默认模式是 `research_only`？
- 哪些内容明确不做？

### 12.3 PR 模板

创建 `.github/pull_request_template.md`：

```markdown
## Background

## Changes

## Verification

- [ ] Ruff passes
- [ ] mypy passes
- [ ] pytest passes
- [ ] No secrets or account data included

## Risks and rollback

## Screenshots or logs
```

提交：

```powershell
git add README.md docs/adr .github/pull_request_template.md
git commit -m "docs: describe architecture scope and contribution flow"
```

## 13. 第十二步：本地最终验收

在根目录先检查 Git：

```powershell
Set-Location -LiteralPath 'E:\CryptoPilot'
git status
git log --oneline --decorate --graph --all
git diff main...HEAD --stat
```

在后端运行质量检查：

```powershell
Set-Location -LiteralPath 'E:\CryptoPilot\backend'
uv sync --locked --all-groups
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest -m "not live"
uv run pre-commit run --all-files --config ..\.pre-commit-config.yaml
```

全部通过后，工作区必须干净：

```powershell
Set-Location -LiteralPath 'E:\CryptoPilot'
git status
```

如果 pre-commit 修改过文件，要重新 `git add` 和提交，不能带着未提交变更创建 PR。

## 14. 第十三步：推送分支和创建 PR

```powershell
git push -u origin chore/bootstrap-repository
```

进入 GitHub 仓库，会出现 Compare & pull request：

- Title：`chore: bootstrap CryptoPilot repository`
- Base：`main`
- Compare：`chore/bootstrap-repository`
- 按 PR 模板填写改动和验证命令。

等待 CI 变绿。如果失败：

1. 点开失败的 job。
2. 找到第一个真正的错误，不要只看最后一行。
3. 在本地复现并修复。
4. 新增 commit 后再次 push。
5. 不要通过删除测试或关闭检查让 CI 变绿。

CI 通过后可以合并 PR，建议选择 Squash and merge 或普通 Merge。学习阶段若希望保留每天的细分 commit，可以使用普通 Merge。

合并后同步本地：

```powershell
git switch main
git pull --ff-only origin main
git branch -d chore/bootstrap-repository
git status
```

Day 1 不需要创建 `v0.1.0` Tag；Tag 留到第一周完整行情版本。可以选择创建早期标签 `v0.0.1`，但不是必需。

## 15. Day 1 验收清单

```text
[ ] Git 姓名和邮箱已配置
[ ] main 已推送到 GitHub
[ ] Day 1 使用独立开发分支和 PR
[ ] backend 使用 Python 3.12
[ ] cryptopilot 可被 import
[ ] pyproject.toml 声明依赖
[ ] uv.lock 已提交
[ ] .venv 没有提交
[ ] FastAPI liveness 返回 200
[ ] Ruff 通过
[ ] mypy 通过
[ ] pytest 通过
[ ] pre-commit 通过
[ ] GitHub Actions 通过
[ ] README 不夸大未实现功能
[ ] 仓库中没有密钥、账户信息和课程源码
```

## 16. 今天必须真正理解的内容

完成操作后，不看笔记回答：

1. `git add` 和 `git commit` 有什么区别？
2. `git commit` 后代码是否已经上传 GitHub？
3. 为什么不直接在 `main` 开发？
4. PR 与 commit 的关系是什么？
5. 为什么 `uv.lock` 要提交而 `.venv` 不能提交？
6. 为什么源码放在 `src/cryptopilot`，导入时却写 `import cryptopilot`？
7. 为什么不在 pytest 配置中加入 `pythonpath = ["src"]`？
8. 为什么能执行一个 `.py` 文件不等于项目可安装？
9. 为什么本项目暂时不用 Python 3.14？
10. CI 为什么不能依赖你电脑上的环境？

如果其中三道以上说不清，先复习再进入 Day 2。

## 17. 出错时的处理原则

- 命令失败后先读第一条错误，不要连续复制更多命令。
- 不执行 `git reset --hard`、递归删除或来源不明的修复命令。
- 不把密钥粘贴进终端历史、Issue、PR 或截图。
- 不因为 mypy/pytest 报错就用 `# type: ignore` 或删除测试。
- 把完整错误、执行命令和当前 `git status` 保存下来再定位。

## 18. 当天提交历史参考

理想的 Day 1 历史类似：

```text
docs: add project plans and repository rules
chore: bootstrap installable python workspace
test: add fastapi application smoke tests
chore: add local quality hooks
ci: add backend quality workflow
docs: describe architecture scope and contribution flow
```

这比一个 `first commit` 塞进几百个文件更能展示工程能力。
