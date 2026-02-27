# Repository Guidelines

本指南面向 `DLCv3-WebUI-Pytorch` 贡献者，聚焦“可复现开发、可通过 CI、可审查合并”。

## 项目结构与模块组织
- 应用入口是 `Home.py`；页面位于 `pages/`，文件命名遵循 `数字_描述.py`（如 `pages/1_Mouse_Scratch.py`）。
- 核心逻辑位于 `src/core/`：
  - `processing/` 行为分析与视频处理流水线
  - `helpers/` 复用脚本与批处理辅助
  - `gpu/` GPU 检测与设备选择
  - `config/` 配置与认证初始化
  - `logging/` 运行日志管理
- UI 组件位于 `src/ui/components/`；测试位于 `tests/`；文档位于 `docs/`。
- 扩展模块时通过对应 `__init__.py` 暴露最小 API，避免跨层依赖。

## 构建、测试与开发命令
- 推荐环境构建（Ubuntu）：`bash install_dlc_env_ubuntu.sh DLCv3-WebUI && conda activate DLCv3-WebUI`
- 锁定环境复现：`mamba env create -f environment.DLCv3-WebUI.lock.yml && conda activate DLCv3-WebUI`
- 开发安装：`pip install -e . && pip install -e .[dev]`
- 运行应用：`streamlit run Home.py`（单页调试：`streamlit run pages/<file>.py`）
- 测试：`pytest --cov=src --cov-report=term-missing --cov-fail-under=1`
- 质量检查：`black . && isort . && flake8 && mypy src`

## CI 现状（请与本地保持一致）
- 工作流：`.github/workflows/ci.yml`
- 触发：`push main`、`pull_request main`、`workflow_dispatch`
- Python 矩阵：`3.8` + `3.10`
- `black/isort/flake8/mypy` 仅在 `3.10` 任务执行；测试在 `3.8/3.10` 都执行。

## 编码风格与命名
- Python 3.8+，UTF-8，4 空格缩进。
- Black 行长 88；isort 使用 `profile=black`。
- 函数/变量 `snake_case`，类 `PascalCase`。
- 对复杂逻辑补简洁 docstring 或注释，优先解释“为什么”。

## 测试要求
- 使用 Pytest，文件命名 `test_*.py`。
- 单测保持原子化，通过 fixture/fake 隔离 GPU 与 I/O（参考 `tests/unit/test_gpu_utils.py`）。
- 改动关键路径时补充测试或在 PR 说明未补测原因。

## 提交与 PR 规范
- Commit message 建议使用 Conventional Commits（如 `feat: ...`、`fix: ...`、`chore: ...`）。
- PR 至少包含：背景、方案、验证步骤、风险与回滚点。
- UI 改动建议附截图/GIF，跨模块改动建议先提 issue 对齐方案。

## 安全与仓库卫生
- 禁止提交真实凭据、真实账号密码、生产 cookie key。
- 运行产物不要入库：`__pycache__/`、`*.pyc`、`logs/*` 已在根 `.gitignore` 处理。
- `data/`、`models/` 保持本地存储，不纳入 Git。
- 引入 GPU 依赖时必须说明 CPU fallback 验证结果，确保无 GPU 节点可运行。

## 建议工作流
- 开发前：`git pull --rebase`
- 提交前：`git status` + `git diff` 自查改动范围
- 合并前：确保本地命令与 CI 门禁全部通过
