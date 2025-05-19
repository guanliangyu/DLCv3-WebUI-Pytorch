# 贡献指南 / Contributing Guide

## 开发规范 / Development Standards

### 目录结构 / Directory Structure
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
│       ├── constants.py
│       ├── types.py
│       └── exceptions.py
├── data/             # 数据目录 / Data directory
│   ├── scratch/      # 抓挠行为数据 / Scratch behavior data
│   ├── grooming/     # 理毛行为数据 / Grooming behavior data
│   ├── swimming/     # 游泳行为数据 / Swimming behavior data
│   ├── three_chamber/ # 三箱实验数据 / Three-chamber data
│   ├── two_social/   # 社交行为数据 / Social behavior data
│   ├── cpp/          # CPP实验数据 / CPP data
│   ├── video_prepare/ # 视频预处理数据 / Video preparation data
│   ├── temp/         # 临时文件 / Temporary files
│   └── results/      # 分析结果 / Analysis results
├── models/           # 模型目录 / Model directory
├── logs/            # 日志目录 / Log directory
├── docs/            # 文档 / Documentation
├── tests/           # 测试 / Tests
│   ├── unit/        # 单元测试 / Unit tests
│   ├── integration/ # 集成测试 / Integration tests
│   └── e2e/         # 端到端测试 / End-to-end tests
└── scripts/         # 工具脚本 / Utility scripts
```

### 代码规范 / Code Standards

1. **类型提示 / Type Hints**
   - 使用Python类型注解 / Use Python type annotations
   - 为所有函数参数和返回值添加类型提示 / Add type hints for all function parameters and return values
   ```python
   from typing import List, Optional, Dict
   
   def process_video(video_path: str, threshold: float = 0.999) -> Optional[Dict]:
       pass
   ```

2. **文档规范 / Documentation Standards**
   - 使用中英双语注释 / Use bilingual comments (Chinese and English)
   - 为所有类和函数添加文档字符串 / Add docstrings for all classes and functions
   ```python
   def analyze_behavior(data: pd.DataFrame) -> Dict:
       """分析行为数据
       Analyze behavior data
       
       Args:
           data: 包含行为数据的DataFrame / DataFrame containing behavior data
           
       Returns:
           分析结果字典 / Dictionary of analysis results
       
       Raises:
           ProcessingError: 当处理失败时 / When processing fails
       """
       pass
   ```

3. **错误处理 / Error Handling**
   - 使用自定义异常类 / Use custom exception classes
   - 提供详细的错误信息 / Provide detailed error messages
   ```python
   class ProcessingError(Exception):
       """视频处理错误 / Video processing error"""
       pass
   ```

4. **日志记录 / Logging**
   - 使用不同级别的日志 / Use different log levels
   - 包含必要的上下文信息 / Include necessary context information
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.info("开始处理视频 / Start processing video: %s", video_path)
   ```

### 测试规范 / Testing Standards

1. **单元测试 / Unit Tests**
   - 使用pytest框架 / Use pytest framework
   - 测试覆盖率要求90%以上 / Test coverage should be above 90%
   ```python
   def test_process_video():
       result = process_video("test.mp4")
       assert result is not None
   ```

2. **集成测试 / Integration Tests**
   - 测试组件间的交互 / Test interactions between components
   - 模拟真实使用场景 / Simulate real usage scenarios

3. **端到端测试 / End-to-End Tests**
   - 测试完整的用户流程 / Test complete user workflows
   - 包含UI交互测试 / Include UI interaction tests

### Git 工作流 / Git Workflow

1. **分支管理 / Branch Management**
   - main: 主分支，用于发布 / Main branch for releases
   - develop: 开发分支 / Development branch
   - feature/*: 功能分支 / Feature branches
   - bugfix/*: 修复分支 / Bugfix branches

2. **提交规范 / Commit Conventions**
   ```
   <type>(<scope>): <subject>

   <body>

   <footer>
   ```
   类型 / Types:
   - feat: 新功能 / New feature
   - fix: 修复bug / Bug fix
   - docs: 文档更新 / Documentation updates
   - style: 代码格式 / Code style changes
   - refactor: 重构 / Code refactoring
   - test: 测试相关 / Test related
   - chore: 构建过程或辅助工具的变动 / Build process or auxiliary tool changes

3. **Pull Request 流程 / Pull Request Process**
   - 创建功能分支 / Create feature branch
   - 编写代码和测试 / Write code and tests
   - 提交PR请求 / Create pull request
   - 代码审查 / Code review
   - 合并到develop分支 / Merge to develop branch

### 性能优化 / Performance Optimization

1. **GPU资源管理 / GPU Resource Management**
   - 合理分配GPU资源 / Properly allocate GPU resources
   - 及时释放GPU内存 / Release GPU memory timely

2. **异步处理 / Asynchronous Processing**
   - 使用异步函数处理耗时操作 / Use async functions for time-consuming operations
   - 实现并行处理 / Implement parallel processing

3. **缓存机制 / Caching Mechanism**
   - 缓存常用数据 / Cache frequently used data
   - 实现结果缓存 / Implement result caching

### 安全规范 / Security Standards

1. **配置管理 / Configuration Management**
   - 使用环境变量存储敏感信息 / Use environment variables for sensitive information
   - 加密存储用户凭证 / Encrypt stored user credentials

2. **输入验证 / Input Validation**
   - 验证所有用户输入 / Validate all user inputs
   - 防止路径遍历 / Prevent path traversal

3. **权限控制 / Access Control**
   - 实现用户认证 / Implement user authentication
   - 控制资源访问权限 / Control resource access permissions

### 发布流程 / Release Process

1. **版本号规范 / Version Numbering**
   - 主版本号.次版本号.修订号 / Major.Minor.Patch
   - 遵循语义化版本规范 / Follow semantic versioning

2. **发布检查清单 / Release Checklist**
   - 所有测试通过 / All tests pass
   - 文档更新完成 / Documentation updated
   - 更新日志完善 / Changelog updated
   - 依赖列表更新 / Dependencies updated 