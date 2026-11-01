# LRC2Video API 文档

## 启用 API

API 默认启用，可通过环境变量控制：

```bash
# 禁用 API
export LRC2VIDEO_API_ENABLED=false

# 启用 API（默认）
export LRC2VIDEO_API_ENABLED=true
```

## API 端点

### 1. 预览样式

生成歌词样式预览图。

**端点：** `POST /gradio_api/call/preview`

**请求格式：**
```json
{
  "data": [
    "Microsoft YaHei",  // font_family: 字体名称
    null,               // font_file: 自定义字体文件路径（可选）
    36,                 // font_size: 字体大小
    "#FFFFFF",          // font_color: 字体颜色
    "#000000",          // outline_color: 描边颜色
    3,                  // outline_width: 描边宽度
    true,               // bold: 是否加粗
    "中",               // pos_x: 水平位置 ["左", "中", "右"]
    "下",               // pos_y: 垂直位置 ["上", "中", "下"]
    10,                 // margin_h: 水平边距
    50,                 // margin_v: 垂直边距
    "#000000",          // bg_color: 背景颜色
    "1920x1080"         // resolution: 分辨率
  ]
}
```

**示例：**
```bash
# 1. 调用 API
curl -s -X POST http://localhost:7860/gradio_api/call/preview \
  -H "Content-Type: application/json" \
  -d '{
    "data": ["Microsoft YaHei", null, 36, "#FFFFFF", "#000000", 3, true, "中", "下", 10, 50, "#000000", "1920x1080"]
  }'

# 响应: {"event_id": "xxx"}

# 2. 获取结果
curl -s -N http://localhost:7860/gradio_api/call/preview/<event_id>

# 响应: event: complete
# data: [{"path": "...", "url": "http://localhost:7860/gradio_api/file=..."}]
```

### 2. 生成视频

生成带歌词字幕的视频。

**端点：** `POST /gradio_api/call/generate`

**请求格式：**
```json
{
  "data": [
    {"path": "/path/to/audio.mp3", "meta": {"_type": "gradio.FileData"}},  // audio: 音频文件
    {"path": "/path/to/lyrics.lrc", "meta": {"_type": "gradio.FileData"}},  // lrc: LRC 歌词文件
    "Microsoft YaHei",  // font_family
    null,               // font_file
    36,                 // font_size
    "#FFFFFF",          // font_color
    "#000000",          // outline_color
    3,                  // outline_width
    true,               // bold
    "中",               // pos_x
    "下",               // pos_y
    10,                 // margin_h
    50,                 // margin_v
    500,                // fade_in: 淡入时间(ms)
    500,                // fade_out: 淡出时间(ms)
    "#000000",          // bg_color
    "1920x1080"         // resolution
  ]
}
```

**示例：**
```bash
# 1. 调用 API
curl -s -X POST http://localhost:7860/gradio_api/call/generate \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"path": "/path/to/audio.mp3", "meta": {"_type": "gradio.FileData"}},
      {"path": "/path/to/lyrics.lrc", "meta": {"_type": "gradio.FileData"}},
      "Microsoft YaHei", null, 36, "#FFFFFF", "#000000", 3, true,
      "中", "下", 10, 50, 500, 500, "#000000", "1920x1080"
    ]
  }'

# 响应: {"event_id": "xxx"}

# 2. 获取结果
curl -s -N http://localhost:7860/gradio_api/call/generate/<event_id>

# 响应: event: complete
# data: [{"path": "...", "url": "http://localhost:7860/gradio_api/file=..."}]
```

## Python 调用示例

```python
import requests
import json

# 预览样式
preview_data = {
    "data": [
        "Microsoft YaHei",  # font_family
        None,               # font_file
        36,                 # font_size
        "#FFFFFF",          # font_color
        "#000000",          # outline_color
        3,                  # outline_width
        True,               # bold
        "中",               # pos_x
        "下",               # pos_y
        10,                 # margin_h
        50,                 # margin_v
        "#000000",          # bg_color
        "1920x1080"         # resolution
    ]
}

# 1. 调用 API
response = requests.post(
    "http://localhost:7860/gradio_api/call/preview",
    json=preview_data
)
event_id = response.json()["event_id"]
print(f"Event ID: {event_id}")

# 2. 获取结果
result_response = requests.get(
    f"http://localhost:7860/gradio_api/call/preview/{event_id}",
    stream=True
)
for line in result_response.iter_lines():
    if line:
        print(line.decode())
```

## 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| font_family | string | "Microsoft YaHei" | 字体名称 |
| font_file | string/null | null | 自定义字体文件路径 |
| font_size | integer | 36 | 字体大小 |
| font_color | string | "#FFFFFF" | 字体颜色 |
| outline_color | string | "#000000" | 描边颜色 |
| outline_width | number | 3 | 描边宽度 |
| bold | boolean | true | 是否加粗 |
| pos_x | string | "中" | 水平位置: "左", "中", "右" |
| pos_y | string | "下" | 垂直位置: "上", "中", "下" |
| margin_h | integer | 10 | 水平边距 |
| margin_v | integer | 50 | 垂直边距 |
| fade_in | integer | 500 | 淡入时间(ms) |
| fade_out | integer | 500 | 淡出时间(ms) |
| bg_color | string | "#000000" | 背景颜色 |
| resolution | string | "1920x1080" | 分辨率 |

## 访问地址

- Web UI: http://localhost:7860
- API 文档: http://localhost:7860/gradio_api/info
