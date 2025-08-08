# Lrc2Video HTTP API 文档

## 概述
Lrc2Video 现在支持通过HTTP API进行歌词视频生成，允许其他程序或脚本调用视频生成功能。

## 快速开始

### 1. 启用API功能
1. 启动 Lrc2Video 主程序
2. 在文件选择页面顶部找到 "API功能" 区域
3. 勾选 "启用API" 开关
4. API服务器将自动启动，默认地址为 `http://127.0.0.1:8000`

### 2. API端点

#### 基础端点
- **GET /api/status** - 获取API状态和系统信息
- **GET /api/styles** - 获取可用样式配置
- **GET /api/config** - 获取当前配置信息

#### 视频生成端点
- **POST /api/generate** - 创建视频生成任务
- **GET /api/status/{task_id}** - 查询任务状态

## 详细API说明

### 获取API状态
```http
GET /api/status
```

**响应示例：**
```json
{
  "status": "running",
  "version": "1.0.0",
  "supported_endpoints": ["/api/generate", "/api/status", "/api/config", "/api/styles"],
  "hardware_acceleration": "nvenc",
  "optimization": {
    "preset": "fast",
    "crf": 23,
    "hardware_acceleration": "nvenc"
  }
}
```

### 创建视频生成任务
```http
POST /api/generate
Content-Type: application/json
```

**请求体：**
```json
{
  "lrc_file": "完整路径/到/歌词文件.lrc",
  "audio_file": "完整路径/到/音频文件.mp3",
  "output_dir": "输出目录路径",
  "style_config": {
    "font_name": "Microsoft YaHei",
    "font_size": 36,
    "font_color": "#FFFFFF",
    "stroke_width": 4,
    "stroke_color": "#000000",
    "alignment": 8,
    "margin_bottom": 50
  },
  "optimization": {
    "preset": "fast",
    "hardware_acceleration": "auto",
    "crf": 23
  }
}
```

**响应示例：**
```json
{
  "task_id": "uuid-任务标识符",
  "status": "accepted",
  "message": "任务已创建"
}
```

### 查询任务状态
```http
GET /api/status/{task_id}
```

**响应示例：**
```json
{
  "task_id": "uuid-任务标识符",
  "state": "processing",  // pending, processing, completed, failed
  "progress": 45,
  "output_file": "输出文件路径.mp4",
  "error": null
}
```

## 配置参数说明

### 样式配置 (style_config)
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| font_name | string | "Microsoft YaHei" | 字体名称 |
| font_size | int | 36 | 字体大小 |
| font_color | string | "#FFFFFF" | 字体颜色 (十六进制) |
| stroke_width | int | 4 | 描边宽度 |
| stroke_color | string | "#000000" | 描边颜色 |
| alignment | int | 8 | 对齐方式 (2=顶部, 8=底部) |
| margin_bottom | int | 50 | 底部边距 |

### 优化配置 (optimization)
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| preset | string | "medium" | 编码预设: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow |
| hardware_acceleration | string | "auto" | 硬件加速: auto, nvenc, qsv, amf, videotoolbox, none |
| crf | int | 23 | 质量因子 (18-28, 数值越小质量越好) |

## 使用示例

### Python 示例
```python
import requests
import json

# API基础URL
API_BASE = "http://127.0.0.1:8000/api"

# 准备数据
payload = {
    "lrc_file": "/path/to/song.lrc",
    "audio_file": "/path/to/song.mp3",
    "output_dir": "./output",
    "style_config": {
        "font_name": "Microsoft YaHei",
        "font_size": 36,
        "font_color": "#FFFFFF",
        "stroke_width": 4,
        "stroke_color": "#000000"
    },
    "optimization": {
        "preset": "fast",
        "hardware_acceleration": "auto"
    }
}

# 创建任务
response = requests.post(f"{API_BASE}/generate", json=payload)
task_info = response.json()
task_id = task_info["task_id"]

# 轮询状态
import time
while True:
    status = requests.get(f"{API_BASE}/status/{task_id}").json()
    if status["state"] in ["completed", "failed"]:
        break
    print(f"进度: {status['progress']}%")
    time.sleep(2)

print("任务完成！")
```

### curl 示例
```bash
# 创建任务
curl -X POST http://127.0.0.1:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "lrc_file": "/path/to/song.lrc",
    "audio_file": "/path/to/song.mp3",
    "output_dir": "./output",
    "style_config": {
      "font_name": "Microsoft YaHei",
      "font_size": 36
    }
  }'

# 查询状态
curl http://127.0.0.1:8000/api/status/{task_id}
```

## 错误处理

### 常见错误码
- **400 Bad Request** - 请求参数错误
- **404 Not Found** - 文件路径不存在
- **500 Internal Server Error** - 服务器内部错误

### 错误响应格式
```json
{
  "error": "错误描述",
  "code": "ERROR_CODE"
}
```

## 性能优化建议

1. **使用硬件加速**: 设置 `"hardware_acceleration": "auto"` 自动检测最佳加速方式
2. **调整预设**: 使用 `"preset": "fast"` 或 `"ultrafast"` 提高生成速度
3. **合理设置CRF**: 平衡质量和文件大小，推荐值 23-28

## 注意事项

1. 所有文件路径必须是绝对路径
2. 确保音频文件和LRC歌词文件匹配
3. API服务器仅在主程序运行时可用
4. 同一时间只能处理一个任务
5. 建议使用SSD存储以提高I/O性能

## 支持

如有问题，请查看程序日志或联系技术支持。