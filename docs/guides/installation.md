# 安装指南 / Installation Guide

## 系统要求 / System Requirements

### 硬件要求 / Hardware Requirements
- CPU: 4核或以上 / 4 cores or more
- 内存: 16GB或以上 / 16GB RAM or more
- GPU: NVIDIA GPU with 8GB或以上显存（可选） / NVIDIA GPU with 8GB VRAM or more (optional)
- 硬盘空间: 50GB或以上 / 50GB disk space or more

### 软件要求 / Software Requirements
- 操作系统 / Operating System:
  - Windows 10/11
  - Ubuntu 20.04/22.04
  - macOS 12或以上 / macOS 12 or later
- Python 3.8+（CI 同时验证 3.8 与 3.10） / Python 3.8+ (CI validates 3.8 and 3.10)

## 安装步骤 / Installation Steps

### 1. 克隆项目 / Clone Project
```bash
git clone https://github.com/guanliangyu/DLCv3-WebUI-Pytorch.git
cd DLCv3-WebUI-Pytorch
```

### 2. 推荐安装方式（Ubuntu） / Recommended setup (Ubuntu)
```bash
bash install_dlc_env_ubuntu.sh DLCv3-WebUI
conda activate DLCv3-WebUI
```

### 3. 锁定环境重建（可选） / Rebuild from lock file (optional)
```bash
mamba env create -f environment.DLCv3-WebUI.lock.yml
conda activate DLCv3-WebUI
```

### 4. 手动安装（开发模式） / Manual install (dev mode)
```bash
pip install -e .
pip install -e .[dev]
```

### 5. 配置设置 / Configure Settings
- 编辑 `src/core/config/config.yaml`，配置认证信息、数据路径和模型路径。
- 生产环境建议使用环境变量或本地忽略文件存放敏感信息。

## 验证安装 / Verify Installation

### 1. 运行测试 / Run Tests
```bash
pytest --cov=src --cov-report=term-missing --cov-fail-under=1
```

### 2. 启动应用 / Start Application
```bash
streamlit run Home.py
```

### 3. 访问Web界面 / Access Web Interface
- 打开浏览器访问 / Open browser and visit: http://localhost:8501

## 常见问题 / Common Issues

### 1. CUDA相关问题 / CUDA Related Issues
- 确保 CUDA 与驱动版本匹配 / Ensure CUDA and driver versions are compatible
- GPU 不可用时可走 CPU 流程 / CPU fallback is supported when GPU is unavailable

### 2. 依赖安装问题 / Dependency Installation Issues
- 优先使用 `install_dlc_env_ubuntu.sh` 或锁定文件重建环境。
- 检查 Python 版本与依赖兼容性 / Check Python-version compatibility.

### 3. 运行时错误 / Runtime Errors
- 检查 `logs/` 中的应用日志 / Check app logs under `logs/`
- 验证目录权限与路径配置 / Verify path settings and permissions
