#!/bin/bash
# ============================================
# Lrc2Video 一键安装脚本
# 用法: bash setup.sh
# ============================================

set -e
cd "$(dirname "$0")"

echo "🎵 Lrc2Video 安装脚本"
echo "======================"

# 1. 检查 Python
echo ""
echo "📋 检查环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "  ✅ Python $PY_VERSION"

# 2. 检查 FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "  ⚠️  未找到 FFmpeg"
    echo "  请安装:"
    echo "    Ubuntu/Debian: sudo apt install ffmpeg"
    echo "    macOS:         brew install ffmpeg"
    echo "    Windows:       https://ffmpeg.org/download.html"
    echo ""
    read -p "  是否继续安装? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "  ✅ FFmpeg $(ffmpeg -version 2>&1 | head -1 | cut -d' ' -f3)"
fi

# 3. 创建虚拟环境
echo ""
echo "📦 创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  ✅ 虚拟环境创建完成"
else
    echo "  ✅ 虚拟环境已存在"
fi

# 4. 激活虚拟环境
source venv/bin/activate

# 5. 安装依赖
echo ""
echo "📥 安装依赖..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "  ✅ 依赖安装完成"

# 6. 下载开源中文字体
echo ""
echo "🔤 下载中文字体..."
FONT_DIR="fonts"
mkdir -p "$FONT_DIR"

# 检查是否已有字体
if ls "$FONT_DIR"/*.ttf "$FONT_DIR"/*.TTF "$FONT_DIR"/*.otf 2>/dev/null | head -1 > /dev/null; then
    echo "  ✅ 字体已存在，跳过下载"
else
    echo "  ⬇️  下载 Noto Sans SC (思源黑体 - 开源免费)..."
    
    # 从 Google Fonts 下载
    FONT_URL="https://github.com/google/fonts/raw/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf"
    FONT_FILE="$FONT_DIR/NotoSansSC.ttf"
    
    if curl -L -o "$FONT_FILE" "$FONT_URL" --connect-timeout 15 -s 2>/dev/null && [ -s "$FONT_FILE" ]; then
        echo "  ✅ 字体下载完成: NotoSansSC.ttf"
    else
        echo "  ⚠️  字体下载失败，请手动下载中文字体放到 fonts/ 目录"
        echo "  推荐: Noto Sans SC (思源黑体) 或任何你喜欢的中文字体"
    fi
fi

# 7. 创建必要目录
echo ""
echo "📁 创建目录..."
mkdir -p uploads outputs logs temp_preview
echo "  ✅ uploads/ outputs/ logs/ temp_preview/"

# 8. 创建配置文件
echo ""
echo "⚙️  创建配置..."
if [ ! -f "config.json" ]; then
    cat > config.json << 'EOF'
{
  "font_family": "NotoSansSC",
  "font_size": 36,
  "font_color": "#FFFFFF",
  "outline_color": "#000000",
  "outline_width": 3,
  "bg_color": "#1a1512",
  "resolution": "1920x1080",
  "fade_in": 0,
  "fade_out": 0
}
EOF
    echo "  ✅ config.json 创建完成"
else
    echo "  ✅ config.json 已存在"
fi

# 9. 完成
echo ""
echo "======================"
echo "🎉 安装完成！"
echo ""
echo "启动方式:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "或直接运行:"
echo "  bash start.sh"
echo ""
echo "然后打开浏览器: http://localhost:7860"
echo "======================"
