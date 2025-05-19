# DLC-WebUI

基于DeepLabCut的动物行为分析Web界面 / DeepLabCut-based Animal Behavior Analysis Web Interface

## 功能特点 / Features

### 视频预处理 / Video Preprocessing
- 视频拼接 / Video Concatenation
  - 支持多个视频文件合并 / Support multiple video file merging
  - GPU加速处理 / GPU-accelerated processing
- 视频裁剪 / Video Cropping
  - 精确区域选择 / Precise area selection
  - 批量处理支持 / Batch processing support

### 行为分析 / Behavior Analysis
- 小鼠抓挠行为分析 / Mouse Scratch Behavior Analysis
  - 自动检测抓挠动作 / Automatic scratch detection
  - 行为持续时间统计 / Behavior duration statistics
- 小鼠理毛行为分析 / Mouse Grooming Behavior Analysis
  - 识别不同理毛模式 / Identify different grooming patterns
  - 行为序列分析 / Behavior sequence analysis
- 小鼠游泳行为分析 / Mouse Swimming Behavior Analysis
  - 游泳轨迹追踪 / Swimming trajectory tracking
  - 速度和距离计算 / Speed and distance calculation
- 三箱实验分析 / Three-Chamber Test Analysis
  - 停留时间统计 / Stay duration statistics
  - 社交偏好分析 / Social preference analysis
- 两鼠社交互动分析 / Two-Mouse Social Interaction Analysis
  - 互动行为识别 / Interaction behavior recognition
  - 社交距离分析 / Social distance analysis
- 条件化位置偏好分析 / Conditioned Place Preference Analysis
  - 区域偏好统计 / Area preference statistics
  - 时间分布分析 / Time distribution analysis

### 数据管理 / Data Management
- 实验数据组织 / Experimental Data Organization
  - 分类存储管理 / Categorized storage management
  - 批量导入导出 / Batch import and export
- 结果可视化 / Result Visualization
  - 图表展示 / Chart display
  - 数据导出 / Data export

### 系统功能 / System Features
- 用户认证 / User Authentication
  - 多用户支持 / Multi-user support
  - 权限管理 / Permission management
- GPU资源管理 / GPU Resource Management
  - 显存监控 / Memory monitoring
  - 任务调度 / Task scheduling
- 日志记录 / Logging
  - 操作日志 / Operation logs
  - 错误追踪 / Error tracking

## 安装要求 / Requirements

### 硬件要求 / Hardware Requirements
- CPU: 4核或以上 / 4 cores or more
- 内存: 16GB或以上 / 16GB RAM or more
- GPU: NVIDIA GPU with 8GB或以上显存 / NVIDIA GPU with 8GB VRAM or more
- 硬盘空间: 50GB或以上 / 50GB disk space or more

### 软件要求 / Software Requirements
- 操作系统 / Operating System
  - Windows 10/11
  - Ubuntu 20.04/22.04
  - macOS 12或以上 / macOS 12 or later
- Python 3.8或以上 / Python 3.8 or later
- CUDA 11.0或以上 / CUDA 11.0 or later
- cuDNN 8.0或以上 / cuDNN 8.0 or later

### 依赖包 / Dependencies
```bash
streamlit>=1.28.0
opencv-python>=4.8.0
numpy>=1.24.0
pandas>=2.0.0
pillow>=10.0.0
deeplabcut>=2.3.10
scikit-learn>=1.3.0
tensorflow>=2.12.0
pyyaml>=6.0.1
streamlit-authenticator>=0.2.3
GPUtil>=1.4.0
```

## 安装步骤 / Installation

1. 克隆仓库 / Clone repository
```bash
git clone https://github.com/yourusername/DLC-WebUI.git
cd DLC-WebUI
```

2. 安装依赖 / Install dependencies
```bash
pip install -r requirements.txt
```

3. 运行应用 / Run application
```bash
python app.py
```

## 使用说明 / Usage

1. 访问Web界面 / Access web interface
   - 打开浏览器访问 / Open browser: http://localhost:8501
   - 使用用户名和密码登录 / Login with username and password

2. 视频预处理 / Video preprocessing
   - 上传视频文件 / Upload video files
   - 选择处理方式 / Choose processing method
   - 设置处理参数 / Set processing parameters

3. 行为分析 / Behavior analysis
   - 选择分析类型 / Choose analysis type
   - 上传预处理后的视频 / Upload preprocessed videos
   - 等待分析完成 / Wait for analysis completion
   - 查看分析结果 / View analysis results

4. 数据导出 / Data export
   - 选择导出格式 / Choose export format
   - 下载分析结果 / Download analysis results

## 目录结构 / Directory Structure

```
DLC-WebUI/
├── src/                # 源代码目录 / Source code directory
│   ├── core/          # 核心功能 / Core functionality
│   │   ├── config/   # 配置管理 / Configuration management
│   │   ├── gpu/      # GPU相关 / GPU related
│   │   ├── utils/    # 通用工具和辅助函数 / Common utilities and helpers
│   │   ├── processors/ # 数据处理和分析 / Data processing and analysis
│   │   └── models/   # 模型定义 / Model definitions
│   ├── ui/           # 界面相关 / UI related
│   │   ├── pages/    # 页面组件 / Page components
│   │   ├── components/ # 可复用组件 / Reusable components
│   │   ├── layouts/  # 页面布局 / Page layouts
│   │   └── styles/   # CSS样式 / CSS styles
│   └── common/       # 通用定义 / Common definitions
├── data/             # 数据目录 / Data directory
├── models/           # 模型目录 / Model directory
├── logs/            # 日志目录 / Log directory
├── docs/            # 文档 / Documentation
├── tests/           # 测试 / Tests
└── scripts/         # 工具脚本 / Utility scripts
```

## 贡献指南 / Contributing

请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何贡献代码。
Please refer to [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## 许可证 / License

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
