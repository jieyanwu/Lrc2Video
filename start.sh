#!/bin/bash
# Lrc2Video 启动脚本
# 用法: bash start.sh

cd "$(dirname "$0")"

# 如果有虚拟环境，激活它
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 创建必要目录
mkdir -p uploads outputs logs

# 启动 Gradio Web UI
echo "🚀 启动 Lrc2Video..."
echo "📱 浏览器访问: http://localhost:7860"
python app.py
