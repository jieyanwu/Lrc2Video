"""
LRC2Video - Gradio Web UI
"""
import gradio as gr
import os
import uuid
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from core.video_generator import VideoGenerator

# 创建必要目录
Path("uploads").mkdir(exist_ok=True)
Path("outputs").mkdir(exist_ok=True)

# 预览歌词
PREVIEW_LYRICS = ["抛弃了理想", "谁人都可以"]

# 占位图片
PLACEHOLDER_IMAGE = "https://p1.music.126.net/jjrXIIIWm7YSSsOUAs1Fug==/17797794719234759.jpg?param=150y150"

# API 功能开关
API_ENABLED = os.getenv("LRC2VIDEO_API_ENABLED", "true").lower() == "true"

# API 文档内容
API_DOCS = {
    "中文": """## 📡 API 使用说明

### 预览样式

**接口：** `POST /gradio_api/call/preview`

**参数说明：**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| font_family | string | "方正行楷_GBK" | 字体名称 |
| font_file | string/null | null | 自定义字体文件路径 |
| font_size | integer | 36 | 字体大小 |
| font_color | string | "#FFFFFF" | 字体颜色 |
| outline_color | string | "#000000" | 描边颜色 |
| outline_width | number | 3 | 描边宽度 |
| bold | boolean | true | 是否加粗 |
| pos_x | string | "中" | 水平位置: 左/中/右 |
| pos_y | string | "中" | 垂直位置: 上/中/下 |
| margin_h | integer | 10 | 水平边距 |
| margin_v | integer | 50 | 垂直边距 |
| bg_color | string | "#000000" | 背景颜色 |
| resolution | string | "1920x1080" | 分辨率 |

**调用示例：**
```bash
# 1. 调用接口
curl -X POST http://localhost:7860/gradio_api/call/preview \\
  -H "Content-Type: application/json" \\
  -d '{"data": ["方正行楷_GBK", null, 36, "#FFFFFF", "#000000", 3, true, "中", "中", 10, 50, "#000000", "1920x1080"]}'

# 返回: {"event_id": "xxx"}

# 2. 获取结果
curl -N http://localhost:7860/gradio_api/call/preview/<event_id>
```

### 生成视频

**接口：** `POST /gradio_api/call/generate`

**调用示例：**
```bash
curl -X POST http://localhost:7860/gradio_api/call/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "data": [
      {"path": "/path/to/audio.mp3", "meta": {"_type": "gradio.FileData"}},
      {"path": "/path/to/lyrics.lrc", "meta": {"_type": "gradio.FileData"}},
      "方正行楷_GBK", null, 36, "#FFFFFF", "#000000", 3, true,
      "中", "中", 10, 50, 500, 500, "#000000", "1920x1080"
    ]
  }'
```

### Python 示例

```python
import requests

# 预览样式
response = requests.post(
    "http://localhost:7860/gradio_api/call/preview",
    json={"data": ["方正行楷_GBK", None, 36, "#FFFFFF", "#000000", 3, True, "中", "中", 10, 50, "#000000", "1920x1080"]}
)
event_id = response.json()["event_id"]

# 获取结果
result = requests.get(f"http://localhost:7860/gradio_api/call/preview/{event_id}", stream=True)
```

---
📖 详细文档见项目根目录：`API_README.md`
""",

    "English": """## 📡 API Documentation

### Preview Style

**Endpoint:** `POST /gradio_api/call/preview`

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| font_family | string | "方正行楷_GBK" | Font name |
| font_file | string/null | null | Custom font file path |
| font_size | integer | 36 | Font size |
| font_color | string | "#FFFFFF" | Font color |
| outline_color | string | "#000000" | Outline color |
| outline_width | number | 3 | Outline width |
| bold | boolean | true | Bold text |
| pos_x | string | "中" | Horizontal: 左/中/右 |
| pos_y | string | "中" | Vertical: 上/中/下 |
| margin_h | integer | 10 | Horizontal margin |
| margin_v | integer | 50 | Vertical margin |
| bg_color | string | "#000000" | Background color |
| resolution | string | "1920x1080" | Resolution |

**Example:**
```bash
# 1. Call API
curl -X POST http://localhost:7860/gradio_api/call/preview \\
  -H "Content-Type: application/json" \\
  -d '{"data": ["方正行楷_GBK", null, 36, "#FFFFFF", "#000000", 3, true, "中", "中", 10, 50, "#000000", "1920x1080"]}'

# Returns: {"event_id": "xxx"}

# 2. Get result
curl -N http://localhost:7860/gradio_api/call/preview/<event_id>
```

### Generate Video

**Endpoint:** `POST /gradio_api/call/generate`

**Example:**
```bash
curl -X POST http://localhost:7860/gradio_api/call/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "data": [
      {"path": "/path/to/audio.mp3", "meta": {"_type": "gradio.FileData"}},
      {"path": "/path/to/lyrics.lrc", "meta": {"_type": "gradio.FileData"}},
      "方正行楷_GBK", null, 36, "#FFFFFF", "#000000", 3, true,
      "中", "中", 10, 50, 500, 500, "#000000", "1920x1080"
    ]
  }'
```

### Python Example

```python
import requests

# Preview style
response = requests.post(
    "http://localhost:7860/gradio_api/call/preview",
    json={"data": ["方正行楷_GBK", None, 36, "#FFFFFF", "#000000", 3, True, "中", "中", 10, 50, "#000000", "1920x1080"]}
)
event_id = response.json()["event_id"]

# Get result
result = requests.get(f"http://localhost:7860/gradio_api/call/preview/{event_id}", stream=True)
```

---
📖 See detailed docs: `API_README.md`
"""
}


def get_api_doc(lang):
    """获取指定语言的 API 文档"""
    return API_DOCS.get(lang, API_DOCS["中文"])


def generate_preview(font_family, font_file, font_size, font_color, outline_color,
                     outline_width, bold, pos_x, pos_y, margin_h, margin_v,
                     bg_color, resolution):
    """使用 FFmpeg 生成样式预览图，保证与实际效果 1:1"""
    import requests
    import subprocess

    # 解析分辨率
    width, height = map(int, resolution.split('x'))

    # 创建临时目录
    temp_dir = Path("temp_preview")
    temp_dir.mkdir(exist_ok=True)

    # 处理自定义字体
    custom_font = None
    if font_file and os.path.exists(font_file):
        font_path = Path(font_file)
        # 确保目标文件有正确的扩展名
        if not font_path.suffix:
            dest = temp_dir / f"{font_path.name}.ttf"
        else:
            dest = temp_dir / font_path.name
        shutil.copy(font_file, dest)
        custom_font = str(dest)
        print(f"🔍 使用自定义字体: {custom_font}")

    # 下载占位图片
    bg_path = temp_dir / "bg.jpg"
    try:
        response = requests.get(PLACEHOLDER_IMAGE, timeout=5)
        with open(bg_path, 'wb') as f:
            f.write(response.content)
    except:
        img = Image.new('RGB', (width, height), bg_color)
        img.save(bg_path)

    # 创建预览歌词的 LRC 文件
    lrc_path = temp_dir / "preview.lrc"
    with open(lrc_path, 'w', encoding='utf-8') as f:
        for i, lyric in enumerate(PREVIEW_LYRICS):
            f.write(f"[00:0{i+1}.00]{lyric}\n")

    # 创建静音音频（3秒）
    audio_path = temp_dir / "preview.mp3"
    subprocess.run([
        'ffmpeg', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
        '-t', '3', '-q:a', '9', str(audio_path)
    ], capture_output=True, timeout=10)

    # 计算 ASS alignment（1-9）
    # 7=左上, 8=中上, 9=右上
    # 4=左中, 5=居中, 6=右中
    # 1=左下, 2=中下, 3=右下
    align_map = {
        ("左", "上"): 7, ("中", "上"): 8, ("右", "上"): 9,
        ("左", "中"): 4, ("中", "中"): 5, ("右", "中"): 6,
        ("左", "下"): 1, ("中", "下"): 2, ("右", "下"): 3,
    }
    alignment = align_map.get((pos_x, pos_y), 2)

    # 生成预览视频
    output_path = temp_dir / "preview.mp4"
    config = {
        "font_family": custom_font if custom_font else font_family,
        "font_size": font_size,
        "font_color": font_color,
        "outline_color": outline_color,
        "outline_width": outline_width,
        "bold": bold,
        "fade_in": 0,  # 无渐进
        "fade_out": 0,  # 无渐出
        "background_color": bg_color,
        "resolution": resolution,
        "alignment": alignment,
        "margin_left": margin_h,
        "margin_right": margin_h,
        "margin_bottom": margin_v,
        "margin_top": margin_v,
        "subtitle_effect": "typewriter",  # 打字机模式
        "typewriter_mode": "sync",  # 同步模式
        "mood": None  # 情绪（可选）
    }

    try:
        generator = VideoGenerator()
        print(f"🔍 预览配置: font_family={config.get('font_family')}")
        generator.generate_video(
            audio_path=str(audio_path),
            lrc_path=str(lrc_path),
            config=config,
            bg_image_path=str(bg_path),
            output_path=str(output_path),
            use_ai_title=False
        )

        # 从视频中截取第2帧作为预览
        preview_img_path = temp_dir / "preview.png"
        subprocess.run([
            'ffmpeg', '-y', '-i', str(output_path),
            '-vf', 'select=eq(n\,30)', '-vframes', '1',
            str(preview_img_path)
        ], capture_output=True, timeout=10)

        if preview_img_path.exists():
            return Image.open(preview_img_path)

    except Exception as e:
        print(f"预览生成失败: {e}")

    # 失败时返回纯色图
    return Image.new('RGB', (480, 270), bg_color)


def generate_video(audio_file, lrc_file, bg_image_file, font_family, font_file, font_size, font_color,
                   outline_color, outline_width, bold, pos_x, pos_y,
                   margin_h, margin_v, fade_in, fade_out,
                   bg_color, resolution, progress=gr.Progress()):
    """生成视频"""
    import subprocess as sp

    if not audio_file or not lrc_file:
        return None, "请上传音频和 LRC 文件"

    # 生成任务 ID
    task_id = str(uuid.uuid4())[:8]

    # 复制文件到上传目录
    upload_dir = Path("uploads") / task_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    audio_path = upload_dir / Path(audio_file).name
    lrc_path = upload_dir / Path(lrc_file).name
    shutil.copy(audio_file, audio_path)
    shutil.copy(lrc_file, lrc_path)

    # 先从原始音频提取封面（转换后会丢失）
    cover_path = upload_dir / "cover.jpg"
    has_cover = False
    try:
        from utils.file_utils import extract_cover_image
        has_cover = extract_cover_image(audio_path, cover_path)
        if has_cover:
            print(f"🖼️ 封面提取成功: {cover_path.name}")
    except Exception as e:
        print(f"⚠️ 封面提取失败: {e}")

    # 如果是FLAC等格式，转换为WAV以保证兼容性
    if audio_path.suffix.lower() in ('.flac', '.ogg', '.wma', '.m4a'):
        wav_path = upload_dir / f"{audio_path.stem}.wav"
        print(f"🔄 转换音频格式: {audio_path.name} -> WAV")
        try:
            result = sp.run([
                'ffmpeg', '-y', '-i', str(audio_path),
                '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2',
                str(wav_path)
            ], capture_output=True, text=True, timeout=120)
            if wav_path.exists() and wav_path.stat().st_size > 0:
                audio_path = wav_path
                print(f"✅ 音频转换完成: {wav_path.name}")
            else:
                print(f"⚠️ 音频转换失败: {result.stderr[:200]}")
        except Exception as e:
            print(f"⚠️ 音频转换异常: {e}")

    # 处理自定义字体
    custom_font = None
    if font_file and os.path.exists(font_file):
        font_path = Path(font_file)
        dest = upload_dir / font_path.name
        shutil.copy(font_file, dest)
        custom_font = str(dest)

    # 计算 ASS alignment
    align_map = {
        ("左", "上"): 7, ("中", "上"): 8, ("右", "上"): 9,
        ("左", "中"): 4, ("中", "中"): 5, ("右", "中"): 6,
        ("左", "下"): 1, ("中", "下"): 2, ("右", "下"): 3,
    }
    alignment = align_map.get((pos_x, pos_y), 2)

    # 配置参数
    config = {
        "font_family": custom_font if custom_font else font_family,
        "font_size": font_size,
        "font_color": font_color,
        "outline_color": outline_color,
        "outline_width": outline_width,
        "bold": bold,
        "fade_in": fade_in,
        "fade_out": fade_out,
        "background_color": bg_color,
        "resolution": resolution,
        "alignment": alignment,
        "margin_left": margin_h,
        "margin_right": margin_h,
        "margin_bottom": margin_v,
        "margin_top": margin_v,
        "subtitle_effect": "typewriter",
        "typewriter_mode": "sync"
    }

    # 进度回调（Gradio 进度范围 0-1）
    def progress_callback(current, total, message):
        progress(min(current / 100, 1.0), desc=message)

    # 生成视频
    try:
        generator = VideoGenerator(progress_callback=progress_callback)
        output_path = f"outputs/{task_id}.mp4"

        # 优先使用用户上传的背景图片，其次用音频封面
        if bg_image_file and os.path.exists(bg_image_file):
            bg_ext = Path(bg_image_file).suffix or '.jpg'
            bg_dest = upload_dir / f"bg{bg_ext}"
            shutil.copy(bg_image_file, bg_dest)
            bg_image = str(bg_dest)
            print(f"🖼️ 使用用户上传的背景图片: {bg_dest.name}")
        elif has_cover and cover_path.exists():
            bg_image = str(cover_path)
            print(f"🖼️ 使用音频封面作为背景")
        else:
            bg_image = None
            print(f"🎨 使用纯色背景")

        generator.generate_video(
            audio_path=str(audio_path),
            lrc_path=str(lrc_path),
            config=config,
            bg_image_path=bg_image,
            output_path=output_path
        )

        if os.path.exists(output_path):
            return output_path, "✅ 生成完成！"
        else:
            return None, "❌ 生成失败"

    except Exception as e:
        return None, f"❌ 错误: {str(e)}"


# Gradio 界面
with gr.Blocks(title="LRC2Video - 歌词转视频", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎵 LRC2Video - 歌词转视频")
    gr.Markdown("上传音频和 LRC 歌词文件，生成带字幕的视频")

    with gr.Row():
        with gr.Column(scale=1):
            # 文件上传
            gr.Markdown("## 📁 上传文件")
            audio_input = gr.Audio(label="音频文件", type="filepath")
            lrc_input = gr.File(label="LRC 歌词文件", file_types=[".lrc"])
            bg_image_input = gr.Image(label="背景图片（可选，不传则用音频封面或纯色背景）", type="filepath")

            # 样式配置
            gr.Markdown("## 🎨 样式配置")
            font_family = gr.Dropdown(
                choices=["方正行楷_GBK", "Microsoft YaHei", "SimHei", "KaiTi", "Arial", "Times New Roman"],
                value="方正行楷_GBK",
                label="字体"
            )
            font_upload = gr.File(label="自定义字体（可选，覆盖上方选择）", file_types=[".ttf", ".otf", ".ttc"])
            font_size = gr.Slider(20, 72, value=36, step=2, label="字体大小")
            font_color = gr.ColorPicker(value="#FFFFFF", label="字体颜色")
            outline_color = gr.ColorPicker(value="#000000", label="描边颜色")
            outline_width = gr.Slider(0, 5, value=3, step=0.5, label="描边宽度")
            bold = gr.Checkbox(value=True, label="加粗")

            with gr.Row():
                pos_x = gr.Radio(["左", "中", "右"], value="中", label="水平位置")
                pos_y = gr.Radio(["上", "中", "中"], value="中", label="垂直位置")

            with gr.Row():
                margin_h = gr.Slider(0, 200, value=10, step=10, label="水平边距")
                margin_v = gr.Slider(0, 200, value=50, step=10, label="垂直边距")

            with gr.Row():
                fade_in = gr.Slider(0, 2000, value=500, step=100, label="淡入(ms)")
                fade_out = gr.Slider(0, 2000, value=500, step=100, label="淡出(ms)")

            bg_color = gr.ColorPicker(value="#000000", label="背景颜色")
            resolution = gr.Dropdown(
                choices=["1920x1080", "1280x720", "854x480", "640x360"],
                value="1920x1080",
                label="分辨率"
            )

            with gr.Row():
                # 预览按钮
                preview_btn = gr.Button("👁️ 预览样式", variant="secondary")

                # 生成按钮
                generate_btn = gr.Button("🎬 生成视频", variant="primary", size="lg")

            # API 开关
            gr.Markdown("---")
            gr.Markdown("## ⚙️ 设置")
            api_enabled = gr.Checkbox(
                value=API_ENABLED,
                label="启用 API 接口",
                info="开启后可通过 HTTP API 调用预览和生成功能"
            )
            api_status = gr.Markdown(
                value=f"**API 状态：** {'✅ 已启用' if API_ENABLED else '❌ 已禁用'}"
            )

        with gr.Column(scale=1):
            # 预览区域
            gr.Markdown("## 👁️ 样式预览")
            preview_image = gr.Image(label="预览效果", height=300)

            # 输出区域
            gr.Markdown("## 📺 输出")
            status_text = gr.Textbox(label="状态", value="等待上传文件...", interactive=False)
            video_output = gr.Video(label="生成的视频")

            # API 文档
            if API_ENABLED:
                gr.Markdown("""
                ## 📡 API 使用说明

                **预览样式：**
                ```bash
                curl -X POST http://localhost:7860/gradio_api/call/preview \\
                  -H "Content-Type: application/json" \\
                  -d '{"data": ["方正行楷_GBK", null, 36, "#FFFFFF", "#000000", 3, true, "中", "中", 10, 50, "#000000", "1920x1080"]}'
                ```

                **生成视频：**
                ```bash
                curl -X POST http://localhost:7860/gradio_api/call/generate \\
                  -H "Content-Type: application/json" \\
                  -d '{"data": [...]}'
                ```

                📖 **详细文档：** [API_README.md](./API_README.md)

                🔗 **交互式 API 文档：** [点击打开](/?view=api)
                """)

    # API 开关状态更新函数
    def update_api_status(enabled):
        global API_ENABLED
        API_ENABLED = enabled
        status = "✅ 已启用" if enabled else "❌ 已禁用"
        return f"**API 状态：** {status}"

    # 绑定事件
    # API 开关
    api_enabled.change(
        fn=update_api_status,
        inputs=[api_enabled],
        outputs=[api_status]
    )

    # 预览按钮
    preview_btn.click(
        fn=generate_preview,
        inputs=[font_family, font_upload, font_size, font_color, outline_color,
                outline_width, bold, pos_x, pos_y, margin_h, margin_v,
                bg_color, resolution],
        outputs=[preview_image],
        api_name="preview" if API_ENABLED else None
    )

    # 生成按钮
    generate_btn.click(
        fn=generate_video,
        inputs=[
            audio_input, lrc_input, bg_image_input, font_family, font_upload, font_size, font_color,
            outline_color, outline_width, bold, pos_x, pos_y, margin_h, margin_v,
            fade_in, fade_out, bg_color, resolution
        ],
        outputs=[video_output, status_text],
        api_name="generate" if API_ENABLED else None
    )

    # 实时预览（参数变化时自动更新）
    style_inputs = [font_family, font_upload, font_size, font_color, outline_color,
                    outline_width, bold, pos_x, pos_y, margin_h, margin_v,
                    bg_color, resolution]
    for inp in style_inputs:
        inp.change(
            fn=generate_preview,
            inputs=style_inputs,
            outputs=[preview_image]
        )

# 启动
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        mcp_server=True,
        allowed_paths=["/tmp/gradio", "/root/cc-work/Lrc2Video"]
    )
