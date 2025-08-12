# Lrc2Video 项目结构说明

## 📁 项目目录结构

```
Lrc2Video/
├── main.py                 # 程序入口文件
├── requirements.txt        # 项目依赖
├── README.md              # 项目说明文档
├── icon.ico              # 程序图标
├── style.json            # 样式配置文件
├──
├── core/                 # 核心功能模块
│   ├── __init__.py
│   └── video_generator.py    # 视频生成核心逻辑
│
├── gui/                  # 图形界面模块
│   ├── __init__.py
│   └── main_window.py        # 主窗口界面
│
├── utils/                # 工具模块
│   ├── __init__.py
│   ├── file_utils.py       # 文件操作工具
│   ├── hardware_detector.py    # 硬件检测工具
│   └── optimization_manager.py # 优化配置管理
│
├── config/               # 配置目录
│   └── optimization_config.json  # 优化配置模板
│
├── style_templates/      # 样式模板
│   ├── default_style.json
│   └── modern_style.json
│
├── examples/             # 示例和使用指南
│   ├── api_usage_example.py    # API使用示例
│   └── optimization_guide.py   # 优化指南
│
├── tests/                # 测试文件
│   ├── __init__.py
│   ├── test_basic.py          # 基础测试
│   ├── test_api.py          # API测试
│   └── test_color_fix.py    # 颜色修复测试
│
├── docs/                 # 文档目录
│   ├── __init__.py
│   ├── API.md              # API文档
│   └── PROJECT_STRUCTURE.md # 项目结构说明
│
├── logs/                 # 日志目录
│   └── __init__.py
│
├── output/               # 输出目录（生成的视频文件）
├── cp/                   # 测试文件目录（歌词和音频）
└── temp/                 # 临时文件目录
```

## 🎯 模块说明

### 核心模块 (core/)
- **video_generator.py**: 视频生成的核心逻辑，包括FFmpeg命令构建、进度监控、错误处理等

### 界面模块 (gui/)
- **main_window.py**: Tkinter图形界面，包含文件选择、样式配置、API控制等功能

### 工具模块 (utils/)
- **file_utils.py**: 文件操作相关工具函数
- **hardware_detector.py**: 硬件加速检测和推荐
- **optimization_manager.py**: 优化配置管理和生成时间预估

### 配置相关
- **config/optimization_config.json**: 视频生成优化配置模板
- **style_templates/**: 预定义的样式配置文件
- **style.json**: 用户当前的样式配置

### 文档和示例
- **docs/**: 项目文档，包括API文档和项目结构说明
- **examples/**: 使用示例和最佳实践指南
- **tests/**: 测试脚本，用于验证功能

## 🚀 使用方式

### 1. 图形界面使用
```bash
python main.py
```

### 2. API调用
```bash
# 确保API已启用
python examples/api_usage_example.py
```

### 3. 运行测试
```bash
python tests/test_api.py
python tests/test_basic.py
```

## 📋 文件分类

### 可执行文件
- `main.py` - 主程序入口

### 配置文件
- `requirements.txt` - Python依赖
- `style.json` - 样式配置
- `config/optimization_config.json` - 优化配置

### 文档
- `README.md` - 项目说明
- `docs/API.md` - API使用文档
- `docs/PROJECT_STRUCTURE.md` - 项目结构说明

### 测试文件
- `tests/` 目录下的所有测试脚本

### 临时文件
- `temp/` - 临时文件存储
- `logs/` - 日志文件存储
- `output/` - 生成的视频文件

## 🔄 建议的开发流程

1. **开发新功能** → 修改对应模块
2. **测试功能** → 使用 `tests/` 下的测试脚本
3. **更新文档** → 更新 `docs/` 和 `examples/` 相关内容
4. **验证兼容性** → 运行所有测试确保不破坏现有功能

这个结构清晰分离了各个功能模块，便于维护和扩展。