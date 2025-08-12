# 📝 配置文件说明

## 📋 新的统一配置系统

从v2.0.0开始，Lrc2Video使用统一的配置文件 `config/config.json`，替代了原来的多个配置文件。

## 🔄 迁移说明

### 自动迁移
运行以下命令自动迁移旧配置：
```bash
python scripts/migrate_config.py
```

### 手动配置
1. 复制示例配置文件：
   ```bash
   cp config/config.json.example config/config.json
   ```

2. 编辑配置文件，填入你的API密钥等信息

## 📁 配置文件结构

### 统一配置文件：`config.json`
```json
{
  "app": {
    "theme": "light",
    "language": "zh-CN",
    "window_geometry": "800x600"
  },
  "ai": {
    "enabled": false,
    "provider": "openai",
    "max_tokens": 50,
    "temperature": 0.7
  },
  "video": {
    "resolution": "1920x1080",
    "fps": 30,
    "hardware_acceleration": "none"
  },
  "lyrics": {
    "font_family": "Microsoft YaHei",
    "font_size": 24,
    "font_color": "#FFFFFF"
  },
  "paths": {
    "audio_folder": "",
    "output_folder": "output"
  }
}
```

## 🔧 配置项说明

### 应用配置 (`app`)
- `theme`: 界面主题 (`light`, `dark`)
- `language`: 界面语言 (`zh-CN`, `en`)
- `window_geometry`: 窗口大小

### AI配置 (`ai`)
- `enabled`: 是否启用AI功能
- `provider`: 默认AI提供商
- `max_tokens`: 最大token数量
- `temperature`: 温度参数

### 视频配置 (`video`)
- `resolution`: 输出分辨率
- `fps`: 帧率
- `hardware_acceleration`: 硬件加速类型
- `encoding_preset`: 编码预设
- `crf_value`: 质量因子 (18-28)

### 歌词配置 (`lyrics`)
- `font_family`: 字体
- `font_size`: 字体大小
- `font_color`: 字体颜色
- `outline_width`: 描边宽度
- `outline_color`: 描边颜色

### 路径配置 (`paths`)
- `audio_folder`: 音频文件目录
- `output_folder`: 输出目录
- `remember_folders`: 记住上次使用的目录

## 🛡️ 安全提示

1. **API密钥安全**
   - 在设置对话框中配置API密钥
   - 密钥保存在 `config/config.json` 中，不会被Git跟踪

2. **备份配置**
   - 在修改配置前备份 `config.json`
   - 使用版本控制管理配置变更

## 🚀 快速开始

1. **首次使用**
   ```bash
   python scripts/migrate_config.py
   ```

2. **配置AI功能**
   - 在设置对话框中配置API密钥
   - 设置 `ai.enabled: true`

3. **自定义样式**
   - 修改 `lyrics` 部分的配置
   - 调整 `video` 部分的编码参数

## 🐛 常见问题

### Q: 配置文件不生效？
A: 检查文件格式是否正确，重启应用后生效

### Q: 如何重置配置？
A: 删除 `config/config.json` 重新运行迁移脚本

### Q: 如何备份配置？
A: 直接复制 `config/config.json` 到安全位置

## 📞 技术支持

如有配置问题，请查看日志文件或提交Issue。