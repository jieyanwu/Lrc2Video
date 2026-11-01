#!/bin/bash
# LRC2Video Gradio 启动脚本

cd "$(dirname "$0")"

# 创建必要目录
mkdir -p uploads outputs logs

# 安装依赖
pip install -r requirements.txt

# 启动 Gradio 应用
python app.py
