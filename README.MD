# 🎵 Lrc2Video - 智能歌词视频生成器

一个现代化的Python桌面应用，专为音乐创作者和内容制作者设计，将歌词文件（LRC）与音频文件智能合成为精美的歌词视频。支持批量处理、AI智能标题生成、丰富的样式自定义，让您的音乐内容更具视觉吸引力。

## ✨ 核心功能特色

### 🎬 智能处理模式
- **单文件模式**：一键生成单个歌词视频，适合精修单个作品
- **批量处理**：智能扫描文件夹，自动匹配音频和歌词文件，批量生成效率提升10倍
- **智能匹配**：基于文件名智能匹配音频、歌词和背景图片，减少手动操作

### 🤖 AI智能增强
- **智能标题生成**：基于OpenAI GPT模型，自动生成吸引人的视频标题和描述
- **多语言支持**：支持中文、英文等多语言标题生成
- **自定义提示词**：可自定义AI生成标题的风格和格式
- **实时预览**：生成前可预览AI建议的标题内容

### 🎨 专业样式系统
- **系统字体检测**：自动获取系统已安装字体，告别固定字体限制
- **实时样式预览**：调整参数时实时显示效果预览
- **预设样式模板**：内置多种专业样式模板（现代、经典、复古等）
- **样式导入导出**：支持JSON格式样式配置的导入导出，便于团队协作
- **自动保存**：所有样式设置自动保存，下次打开无需重新配置

### 📊 智能进度管理
- **双进度显示**：同时显示当前文件进度和总体处理进度
- **详细日志**：每个文件的处理状态、耗时、错误信息完整记录
- **断点续传**：批量处理中断后可从中断处继续
- **错误恢复**：单个文件处理失败不影响其他文件

### 🖼️ 背景智能处理
- **自动封面提取**：自动从音频文件中提取封面作为背景
- **智能背景适配**：自动调整背景图片尺寸和比例
- **纯色背景**：支持自定义纯色背景，适合不同风格需求
- **透明度控制**：背景图片透明度可调，确保字幕清晰可见

### 🔧 专业音频处理
- **无损音质**：保持原音频文件的码率和质量
- **格式兼容**：支持MP3、FLAC、WAV、M4A、AAC等主流格式
- **音量标准化**：可选的音频音量标准化处理
- **音频预览**：内置音频播放器，可预览处理前的音频效果

## 🔧 系统要求

### 必需组件
- **Python**: 3.7+ (推荐 3.9+)
- **FFmpeg**: 4.0+ (必须添加到系统PATH)
- **操作系统**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 18.04+)

### 可选组件
- **OpenAI API**: 用于AI标题生成功能
- **GPU支持**: NVIDIA显卡 + CUDA (加速视频处理)

### 硬件建议
- **内存**: 8GB RAM (推荐16GB+)
- **存储**: 2GB可用空间 (推荐SSD)
- **处理器**: 4核CPU (推荐8核+)

## 📦 安装指南

### 🚀 一键安装 (Windows)
```bash
# 1. 克隆项目
git clone https://github.com/jieyanwu/Lrc2Video.git
cd Lrc2Video

# 2. 一键安装脚本 (自动安装Python依赖和FFmpeg)
python scripts/install.py

# 3. 启动应用
python main.py
```

### 📋 手动安装

#### 1. 克隆项目
```bash
git clone https://github.com/jieyanwu/Lrc2Video.git
cd Lrc2Video
```

#### 2. 创建虚拟环境 (推荐)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### 3. 安装Python依赖
```bash
pip install -r requirements.txt
```

#### 4. 安装FFmpeg

<details>
<summary><b>Windows安装FFmpeg</b></summary>

1. 下载FFmpeg: https://ffmpeg.org/download.html
2. 解压到 `C:\ffmpeg`
3. 添加 `C:\ffmpeg\bin` 到系统PATH
4. 验证安装: `ffmpeg -version`

</details>

<details>
<summary><b>macOS安装FFmpeg</b></summary>

```bash
# 使用Homebrew
brew install ffmpeg

# 验证安装
ffmpeg -version
```

</details>

<details>
<summary><b>Linux安装FFmpeg</b></summary>

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg

# 验证安装
ffmpeg -version
```

</details>

### ⚙️ 可选配置

#### OpenAI API配置 (AI标题功能)
1. 注册OpenAI账号: https://platform.openai.com
2. 获取API密钥
3. 在应用设置中配置API密钥

#### GPU加速 (可选)
```bash
# 安装CUDA支持的FFmpeg (高级用户)
# 请参考FFmpeg官方文档配置GPU加速
```

## 🚀 使用指南

### 🎯 快速开始 (3分钟上手)

#### 1. 启动应用
```bash
python main.py
```

#### 2. 创建你的第一个歌词视频

<details>
<summary><b>📹 单文件模式 (推荐新手)</b></summary>

1. **文件选择** 📁
   - 点击"选择音频" → 选择你的音乐文件
   - 支持的格式：MP3、FLAC、WAV、M4A、AAC
   - 点击"选择歌词" → 选择对应的LRC歌词文件

2. **背景设置** 🖼️
   - 可选：点击"选择背景"添加背景图片
   - 或保持默认，使用纯色背景

3. **样式调整** 🎨
   - 在"样式设置"页面调整字体、颜色、特效
   - 实时预览效果，所见即所得

4. **生成视频** ▶️
   - 点击"生成单个视频"
   - 等待处理完成，视频将保存在"output"文件夹

</details>

<details>
<summary><b>📊 批量处理模式 (效率神器)</b></summary>

1. **选择文件夹** 📂
   - 点击"选择文件夹" → 选择包含音频和歌词的文件夹
   - 程序会自动扫描并匹配文件

2. **智能匹配** 🔍
   - 查看文件匹配列表，确认无误
   - 程序支持模糊匹配，如"song.mp3"匹配"song.lrc"

3. **统一样式** 🎨
   - 设置统一的样式模板
   - 或导入预设的样式配置文件

4. **批量生成** 🚀
   - 点击"批量生成视频"
   - 支持中途暂停和继续
   - 实时显示每个文件的处理进度

</details>

### 🎬 实战示例

#### 示例1：制作抖音热门歌词视频
```
音频文件：love_song.mp3
歌词文件：love_song.lrc
背景图片：love_song.jpg
样式设置：
- 字体：微软雅黑 Bold
- 颜色：粉色渐变 (#FF69B4 → #FFB6C1)
- 特效：淡入淡出 500ms
- 分辨率：1080x1920 (竖屏)
```

#### 示例2：YouTube音乐频道批量制作
```
文件夹结构：
music_folder/
├── song1.mp3 + song1.lrc
├── song2.flac + song2.lrc
└── song3.m4a + song3.lrc

批量设置：
- 统一字体：Arial Bold
- 品牌色彩：#00FF00
- 固定分辨率：1920x1080
- 批量处理：50首歌曲同时处理
```

## 📁 项目结构详解

```
Lrc2Video/
├── 📄 main.py                    # 应用入口点，启动GUI界面
├── 📋 requirements.txt           # Python依赖列表
├── 📄 README.md                  # 项目文档
├── 🖼️ icon.ico                   # 应用图标
├── 🎨 style.json                 # 默认样式配置
├── 📁 style_templates/           # 样式模板库
│   ├── default_style.json        # 经典样式模板
│   └── modern_style.json         # 现代样式模板
├── 📁 config/                    # 配置管理
│   ├── config.json               # 用户配置 (自动生成)
│   └── config.json.example       # 配置示例文件
├── 📁 core/                      # 核心引擎
│   ├── __init__.py
│   ├── video_generator.py        # 视频生成引擎 (FFmpeg封装)
│   └── ai_title_generator.py     # AI标题生成器 (OpenAI API)
├── 📁 gui/                       # 图形界面
│   ├── __init__.py
│   ├── main_window.py            # 主窗口 (Tkinter)
│   ├── ai_config_dialog.py       # AI配置对话框
│   └── modern_theme.py           # 现代化主题样式
├── 📁 utils/                     # 工具库
│   ├── __init__.py
│   ├── file_utils.py             # 文件操作工具
│   ├── config_manager.py         # 配置管理器
│   └── hardware_detector.py      # 硬件检测工具
├── 📁 scripts/                   # 安装和工具脚本
│   └── migrate_config.py         # 配置迁移工具
└── 📁 output/                    # 输出目录 (自动生成)
    └── .gitkeep                  # 保持空目录
```

## ⚙️ 配置说明

详细配置文档请参考 [CONFIG.md](CONFIG.md) 文件。

### AI标题设置
- **OpenAI API密钥**：在设置菜单中配置
- **启用AI标题**：可选择是否为每个视频生成智能标题
- **自定义提示词**：支持自定义AI生成标题的提示词

### 字体设置
- **字体族**：支持多种中英文字体
- **字体大小**：16-72像素可调
- **字体样式**：粗体、斜体支持
- **字体颜色**：自定义颜色选择

### 描边设置
- **描边宽度**：0-10像素可调
- **描边颜色**：自定义颜色选择

### 位置设置
- **底部边距**：调整字幕距离底部的距离

### 特效设置
- **淡入时间**：字幕出现时的淡入效果
- **淡出时间**：字幕消失时的淡出效果

### 视频设置
- **分辨率**：支持1920x1080、1280x720等常见分辨率
- **背景颜色**：无背景图片时使用的纯色背景

### 样式管理
- **导出样式**：将当前样式设置保存为JSON文件
- **导入样式**：从JSON文件导入样式配置
- **自动保存**：所有设置自动保存到配置文件

## 📋 文件命名与格式规范

### 🎯 智能匹配规则

#### 音频与歌词匹配
程序支持多种智能匹配模式：

```
精确匹配：
song.mp3 + song.lrc ✓

模糊匹配：
My Song - Artist.mp3 + My Song.lrc ✓
2023_Hit_Music.flac + 2023_Hit_Music.lrc ✓

子文件夹匹配：
Album/
├── song1.mp3
├── song1.lrc
└── cover.jpg
```

#### 背景图片自动匹配
系统会自动寻找以下背景图片：
- 同名图片：`song.mp3` → `song.jpg`/`song.png`
- 文件夹封面：`cover.jpg`/`folder.jpg`
- 音频内嵌封面：自动提取音频文件的封面图片

### 📊 支持的文件格式

#### 音频格式
- **MP3** (.mp3) - 最常用，兼容性最好
- **FLAC** (.flac) - 无损音质，推荐
- **WAV** (.wav) - 无压缩，文件较大
- **M4A** (.m4a) - Apple设备常用
- **AAC** (.aac) - 高效压缩格式

#### 歌词格式
- **LRC** (.lrc) - 标准歌词格式，支持时间轴
- **增强LRC** - 支持多语言、翻译等扩展标签

#### 图片格式
- **JPG/JPEG** (.jpg/.jpeg) - 压缩格式，文件小
- **PNG** (.png) - 支持透明度，质量高
- **BMP** (.bmp) - 无压缩，文件大

## 📊 进度显示

### 单文件模式
- 显示当前文件处理进度（0-100%）
- 实时状态信息

### 批量模式
- **当前文件进度**：当前正在处理文件的进度
- **总体进度**：已完成文件数/总文件数
- **详细日志**：每个文件的处理结果

## 🔧 故障排除与FAQ

### 🚨 常见问题快速解决

#### 1. 启动问题

<details>
<summary><b>❌ "FFmpeg未找到" 错误</b></summary>

**症状**：启动时提示"FFmpeg not found"或视频生成失败

**解决方案**：
1. 打开命令行，运行：`ffmpeg -version`
2. 如果提示未找到命令，说明FFmpeg未安装或未添加到PATH
3. Windows用户：重新安装FFmpeg并确保添加到系统PATH
4. 重启应用后重试

**验证**：运行`ffmpeg -version`应显示版本信息

</details>

#### 2. 样式问题

<details>
<summary><b>🎨 字体显示异常或样式不生效</b></summary>

**症状**：字幕显示为默认字体，颜色或大小设置无效

**解决方案**：
1. 检查字体是否在系统中存在：
   - Windows：在`C:\Windows\Fonts`中查找
   - macOS：在"字体册"中查找
   - Linux：运行`fc-list`命令
2. 尝试使用系统常用字体："Microsoft YaHei", "Arial", "SimHei"
3. 重启应用使字体设置生效

**高级**：使用系统字体检测功能，自动获取可用字体

</details>

#### 3. 文件处理问题

<details>
<summary><b>📁 LRC文件编码错误或乱码</b></summary>

**症状**：歌词显示为乱码或时间轴错误

**解决方案**：
1. 用文本编辑器打开LRC文件
2. 另存为UTF-8编码格式
3. 确保时间格式正确：`[mm:ss.xx]`
4. 检查是否有特殊字符或BOM头

**示例正确格式**：
```
[00:12.34]这是第一行歌词
[00:15.67]这是第二行歌词
```

</details>

#### 4. 音频问题

<details>
<summary><b>🔊 生成的视频没有声音</b></summary>

**症状**：视频画面正常但无音频

**解决方案**：
1. 检查音频文件是否完整：用播放器测试
2. 确认音频格式被支持：MP3、FLAC、WAV、M4A、AAC
3. 检查音频文件权限：确保有读取权限
4. 尝试用其他音频文件测试

**调试命令**：
```bash
ffmpeg -i your_audio.mp3 -f null -
```

</details>

#### 5. AI功能问题

<details>
<summary><b>🤖 AI标题生成功能无法使用</b></summary>

**症状**：点击"生成AI标题"无响应或报错

**解决方案**：
1. 检查网络连接：确保能访问api.openai.com
2. 验证API密钥：在OpenAI控制台测试密钥
3. 检查API余额：确保账户有足够余额
4. 检查API密钥权限：确保有GPT模型访问权限

**测试命令**：
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.openai.com/v1/models
```

</details>

### 📊 性能优化建议

#### 提升处理速度
- **硬件建议**：使用SSD硬盘，16GB+内存
- **批量处理**：建议一次处理不超过100个文件
- **后台处理**：处理时可最小化窗口，减少资源占用

#### 减少内存占用
- **关闭其他应用**：处理前关闭不必要的程序
- **分批次处理**：大量文件建议分批处理
- **监控资源**：使用任务管理器监控内存使用情况

### 🛠️ 高级调试

#### 启用调试模式
1. 启动应用时添加参数：`python main.py --debug`
2. 查看详细日志：`logs/app.log`
3. 提交Issue时附上日志文件

#### 性能测试
```bash
# 测试FFmpeg性能
ffmpeg -benchmark -i input.mp3 -f null -

# 测试系统字体
python -c "from matplotlib import font_manager; print(len(font_manager.findSystemFonts()))"
```

## 📄 许可证与贡献

### 📋 开源许可
本项目基于 **MIT License** 开源，您可以：
- ✅ 自由使用、修改和分发
- ✅ 用于商业项目
- ✅ 创建衍生作品
- ❌ 需要保留原作者版权声明

### 🤝 如何贡献

我们欢迎所有形式的贡献！

#### 💡 贡献方式
- **🐛 报告Bug**: 提交详细的Issue报告
- **✨ 功能建议**: 提出新功能的想法
- **📝 文档改进**: 改进README或添加教程
- **🎨 样式模板**: 创建新的样式模板
- **🔧 代码贡献**: 提交Pull Request

#### 📋 贡献指南
1. Fork本项目
2. 创建功能分支：`git checkout -b feature/AmazingFeature`
3. 提交更改：`git commit -m 'Add some AmazingFeature'`
4. 推送分支：`git push origin feature/AmazingFeature`
5. 创建Pull Request

#### 🏆 贡献者荣誉
感谢所有[贡献者](https://github.com/jieyanwu/Lrc2Video/graphs/contributors)！

### 📮 联系方式与支持

#### 💬 获取帮助
- **📧 GitHub Issues**: [提交问题](https://github.com/jieyanwu/Lrc2Video/issues)
- **💬 Discussions**: [参与讨论](https://github.com/jieyanwu/Lrc2Video/discussions)
- **📖 Wiki**: [查看文档](https://github.com/jieyanwu/Lrc2Video/wiki)

#### 🌟 支持项目
如果本项目对您有帮助，请给我们一个⭐！

#### 📊 项目统计
- ⭐ **Stars**: 项目受欢迎程度
- 🍴 **Forks**: 分支数量
- 👀 **Watchers**: 关注者数量

---

<div align="center">

**🎵 Lrc2Video - 让每一首歌都有专属的视觉故事**

[⭐ Star项目](https://github.com/jieyanwu/Lrc2Video) • [🐛 报告问题](https://github.com/jieyanwu/Lrc2Video/issues) • [🤝 贡献代码](https://github.com/jieyanwu/Lrc2Video/pulls)

</div>