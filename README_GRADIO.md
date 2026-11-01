# LRC2Video - Gradio Web UI

## 简介

基于 Gradio 的 LRC 歌词转视频 Web 应用。

## 功能

- 🎵 上传音频文件（MP3、WAV、FLAC）
- 📝 上传 LRC 歌词文件
- 🎨 自定义字幕样式
- 🎬 生成带字幕的视频
- 📥 下载生成的视频

## 安装

```bash
pip install -r requirements.txt
```

## 启动

```bash
python app.py
```

访问 http://localhost:7860

## 配置参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| 字体 | 字体样式 | Microsoft YaHei |
| 字体大小 | 字号 | 36 |
| 字体颜色 | 颜色 | #FFFFFF |
| 描边颜色 | 描边颜色 | #000000 |
| 描边宽度 | 描边粗细 | 3 |
| 加粗 | 是否加粗 | 是 |
| 淡入 | 淡入时间(ms) | 500 |
| 淡出 | 淡出时间(ms) | 500 |
| 背景颜色 | 背景色 | #000000 |
| 分辨率 | 视频分辨率 | 1920x1080 |

## 项目结构

```
Lrc2Video/
├── app.py              # Gradio 主应用
├── core/               # 核心功能
├── utils/              # 工具函数
├── uploads/            # 上传文件
├── outputs/            # 输出视频
├── requirements.txt    # 依赖
└── start.sh            # 启动脚本
```
