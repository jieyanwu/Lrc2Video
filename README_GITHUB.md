# 🎵 Lrc2Video - 智能歌词视频生成器

> 将 LRC 歌词 + 音频 + 封面 → 自动生成打字机同步歌词 MV

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Gradio](https://img.shields.io/badge/Gradio-WebUI-orange.svg)](https://gradio.app)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-4.0+-green.svg)](https://ffmpeg.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 特性

| 功能 | 说明 |
|------|------|
| 🎬 **打字机同步** | 逐字显示歌词，和演唱速度完全同步 |
| 🎨 **AI智能配色** | 根据歌词情感自动匹配配色方案 |
| 🖼️ **封面背景** | 自动使用专辑封面作为视频背景 |
| 📦 **批量处理** | 一次处理多首歌曲 |
| 🌐 **Web UI** | Gradio 网页界面，浏览器操作 |
| 🔌 **API 接口** | 完整 REST API，支持自动化集成 |
| 🖥️ **桌面 GUI** | PyQt5 原生桌面应用 |
| 🎯 **多格式** | 支持 MP3/FLAC/WAV/M4A 音频 + LRC 歌词 |

## 📸 效果预览

```
┌─────────────────────────────────────┐
│                                     │
│    ┌─────────────────────────┐      │
│    │                         │      │
│    │   🖼️  专辑封面背景       │      │
│    │                         │      │
│    │      我 还 不 清 楚      │      │  ← 打字机效果
│    │      怎 样 的 速 度      │      │
│    │                         │      │
│    └─────────────────────────┘      │
│                                     │
│         1920 x 1080 · 320kbps       │
└─────────────────────────────────────┘
```

## 🚀 快速开始（3步跑起来）

### 1. 克隆项目

```bash
git clone https://github.com/jieyanwu/Lrc2Video.git
cd Lrc2Video
```

### 2. 一键安装

```bash
bash setup.sh
```

自动完成：创建虚拟环境 + 安装依赖 + 下载中文字体 + 生成配置

### 3. 启动

```bash
bash start.sh
```

打开浏览器访问 **http://localhost:7860** 🎉

---

### 手动安装（不使用 setup.sh）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 安装 FFmpeg
sudo apt install ffmpeg   # Ubuntu/Debian
brew install ffmpeg       # macOS

# 3. 放入中文字体到 fonts/ 目录

# 4. 启动
python app.py
```

## 📁 项目结构

```
Lrc2Video/
├── app.py                  # Gradio Web UI 主入口
├── main.py                 # PyQt5 桌面 GUI 入口
├── core/
│   └── video_generator.py  # 视频生成核心引擎
├── gui/
│   ├── main_window.py      # 桌面主窗口
│   ├── ai_config_dialog.py # AI 配置对话框
│   └── modern_theme.py     # 现代化主题
├── utils/
│   ├── audio_analyzer.py   # 音频分析
│   ├── ai_title_generator.py # AI 标题生成
│   ├── config_manager.py   # 配置管理
│   ├── file_utils.py       # 文件工具
│   ├── ffmpeg_locate.py    # FFmpeg 定位
│   └── hardware_detector.py # 硬件检测
├── templates/
│   └── api_doc.html        # API 文档页面
├── fonts/                  # 字体文件（用户自备）
├── style_templates/        # 样式模板
├── requirements.txt        # Python 依赖
├── start.sh                # 启动脚本
├── API_README.md           # API 接口文档
└── README.MD               # 详细说明文档
```

## 🎨 样式自定义

支持精细控制视频样式：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 字体 | 方正行楷 | 支持系统所有字体 |
| 字号 | 36px | 可调节 |
| 字体颜色 | #f5e6d3 | 支持任意颜色 |
| 描边颜色 | #2d2416 | 文字描边 |
| 描边宽度 | 3px | 描边粗细 |
| 位置 | 居中 | 上/中/下 × 左/中/右 |
| 渐入 | 0 | 无渐入效果 |
| 渐出 | 0 | 无渐出效果 |
| 分辨率 | 1920x1080 | 全高清 |

## 🔌 API 使用

```bash
# 启动服务
python app.py

# 通过 API 生成视频
curl -X POST http://localhost:7860/gradio_api/call/generate \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"path": "/path/to/audio.flac", "meta": {"_type": "gradio.FileData"}},
      {"path": "/path/to/lyrics.lrc", "meta": {"_type": "gradio.FileData"}},
      {"path": "/path/to/cover.jpg", "meta": {"_type": "gradio.FileData"}},
      "方正行楷_GBK", null, 36,
      "#f5e6d3", "#2d2416", 3, true,
      "中", "中", 10, 50,
      0, 0,
      "#1a1512", "1920x1080"
    ]
  }'
```

详细 API 文档见 [API_README.md](API_README.md)

## 🤖 AI 功能

集成 OpenAI 兼容接口，支持：

- **智能标题生成**：根据歌词内容自动生成视频标题
- **情感配色分析**：自动匹配最佳配色方案
- **自定义提示词**：可配置生成风格

配置方法见 [CONFIG.md](CONFIG.md)

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| Web UI | Gradio 4.x |
| 桌面 GUI | PyQt5 |
| 视频处理 | FFmpeg |
| 图像处理 | Pillow |
| 音频分析 | librosa (可选) |
| AI 接口 | OpenAI 兼容 API |

## 📋 系统要求

- Python 3.8+
- FFmpeg 4.0+
- 操作系统：Windows / macOS / Linux

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

MIT License

---

> 💡 **提示**：如果觉得有用，给个 ⭐ Star 吧！
