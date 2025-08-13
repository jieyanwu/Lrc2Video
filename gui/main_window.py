#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口GUI - 现代化界面设计 - 调试增强版
"""

import os
import json
import logging
import threading
from pathlib import Path
from tkinter import *
from tkinter import ttk, filedialog, messagebox, colorchooser
from tkinter.scrolledtext import ScrolledText
from .modern_theme import COLORS, FONTS, create_modern_button, create_modern_entry, create_modern_label, create_modern_frame

from core.video_generator import VideoGenerator
from utils.file_utils import scan_folder_for_files

# 设置日志
logger = logging.getLogger(__name__)

class LyricsVideoGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("歌词视频生成器")
        self.root.geometry("1000x800")
        self.root.configure(bg="#f5f5f5")
        self.root.option_add('*Font', ('Segoe UI', 10))
        
        # 设置窗口图标
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        # 存储文件列表
        self.file_pairs = []  # [(audio_path, lrc_path), ...]
        self.debug_files_loaded = 0
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # 文件路径变量
        self.audio_var = StringVar()
        self.lrc_var = StringVar()
        self.bg_var = StringVar()
        self.folder_var = StringVar()
        self.output_var = StringVar(value=str(self.output_dir))
        
        # 样式配置变量
        self.font_family = StringVar(value="Arial")
        self.font_size = IntVar(value=24)
        self.font_color = StringVar(value="#ffffff")
        self.outline_width = IntVar(value=2)
        self.outline_color = StringVar(value="#000000")
        self.bg_color = StringVar(value="#000000")
        self.margin_bottom = IntVar(value=50)
        self.fade_in = IntVar(value=500)
        self.fade_out = IntVar(value=500)
        self.bold_var = BooleanVar(value=True)
        self.italic_var = BooleanVar(value=False)
        self.concurrency_var = IntVar(value=2)
        self.resolution = StringVar(value="1920x1080")
        
        # AI标题生成相关变量
        self.ai_title_enabled = BooleanVar(value=False)
        
        # AI标题生成相关变量
        self.ai_title_enabled = BooleanVar(value=False)
        self.openai_api_key = StringVar(value="")
        
        # 视频生成器
        self.video_generator = VideoGenerator(progress_callback=self.update_progress)
        
        # 进度相关变量
        self.current_file_progress = 0
        self.total_files_progress = 0
        self.current_file_name = ""
        
        # 配置管理器
        from utils.config_manager import get_config
        self.config_manager = get_config()
        self.user_preferences = {}
        self.preferences_file = Path("config") / "config.json"
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 加载用户偏好
        self.load_user_preferences()
        
        self.setup_ui()
        
        # 应用保存的偏好设置
        self.apply_user_preferences()
        
        # 添加调试状态栏
        self.setup_debug_status_bar()
        logger.info("🎨 主窗口初始化完成")
        
    def setup_ui(self):
        # 设置主题样式
        self.setup_styles()
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 主框架 - 现代化设计
        main_frame = Frame(self.root, bg=COLORS['background'])
        main_frame.pack(fill=BOTH, expand=True, padx=0, pady=0)
        
        # # 顶部标题栏 - 渐变效果
        # header_frame = Frame(main_frame, bg=COLORS['primary'], height=80)
        # header_frame.pack(fill=X)
        # header_frame.pack_propagate(False)
        
        # title_label = Label(header_frame, text="🎵 歌词视频生成器", 
        #                    font=FONTS['title'], bg=COLORS['primary'], fg='white')
        # title_label.pack(pady=20)
        
        # 内容区域
        content_frame = Frame(main_frame, bg=COLORS['background'], padx=30, pady=20)
        content_frame.pack(fill=BOTH, expand=True)
        
        # 创建现代化Notebook
        style = ttk.Style()
        style.theme_use('clam')
        
        # 自定义Notebook样式
        style.configure('Modern.TNotebook', 
                       background='#ffffff',
                       borderwidth=0,
                       tabmargins=[0, 0, 0, 0])
        style.configure('Modern.TNotebook.Tab',
                       background='#f5f5f5',
                       foreground='#666666',
                       padding=[20, 10],
                       font=('Segoe UI', 11),
                       borderwidth=0)
        style.map('Modern.TNotebook.Tab',
                 background=[('selected', '#ffffff'), ('active', '#e0e0e0')],
                 foreground=[('selected', '#2196F3'), ('active', '#666666')])
        
        # 创建Notebook
        notebook = ttk.Notebook(content_frame, style='Modern.TNotebook')
        notebook.pack(fill=BOTH, expand=True)
        
        # 创建页面框架
        frames = []
        for tab_name in ["📁 文件选择", "🎨 样式设置", "⚙️ 批量处理"]:
            frame = Frame(notebook, bg='#ffffff', padx=25, pady=20)
            frames.append(frame)
            notebook.add(frame, text=tab_name)
        
        file_frame, style_frame, batch_frame = frames
        
        # 设置各页面
        self.setup_file_page(file_frame)
        self.setup_style_page(style_frame)
        self.setup_batch_page(batch_frame)
        
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        # file_menu.add_command(label="新建项目", command=self.new_project)
        # file_menu.add_command(label="打开项目", command=self.open_project)
        # file_menu.add_separator()  横线
        file_menu.add_command(label="退出", command=self.on_closing)
        
        # 设置菜单
        settings_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="设置", menu=settings_menu)
        settings_menu.add_command(label="AI标题配置", command=self.open_ai_config)
        settings_menu.add_separator()
        settings_menu.add_command(label="首选项", command=self.open_preferences)
        
        # 帮助菜单
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def open_ai_config(self):
        """打开AI配置对话框"""
        try:
            from .ai_config_dialog import AIConfigDialog
            dialog = AIConfigDialog(self.root)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开AI配置：{str(e)}")
    
    # def new_project(self):
    #     """新建项目"""
    #     # 清空当前选择
    #     self.audio_var.set("")
    #     self.lrc_var.set("")
    #     self.bg_var.set("")
    #     self.folder_var.set("")
        
    #     # 清空文件列表
    #     for item in self.file_tree.get_children():
    #         self.file_tree.delete(item)
    #     self.file_pairs.clear()
        
    #     self.log("已创建新项目")
    
    # def open_project(self):
    #     """打开项目"""
    #     # 这里可以添加项目文件支持
    #     messagebox.showinfo("提示", "项目文件功能开发中...")
    
    def open_preferences(self):
        """打开首选项"""
        messagebox.showinfo("提示", "首选项功能开发中...")
    
    def show_help(self):
        """显示帮助"""
        help_text = """🎵 歌词视频生成器使用说明

        1. 文件选择
        • 单个文件：选择音频文件、歌词文件和背景图片
        • 批量处理：选择文件夹自动扫描配对文件

        2. 样式设置
        • 调整字体、颜色、大小等参数
        • 预览效果并保存样式配置

        3. AI标题生成
        • 在设置中配置AI标题功能
        • 支持OpenAI、OpenRouter、Moonshot AI
        • 自动为视频生成吸引人的标题

        4. 开始生成
        • 点击生成按钮开始处理
        • 实时查看进度和日志"""
        
        messagebox.showinfo("使用说明", help_text)
    
    def show_about(self):
        """显示关于信息"""
        about_text = """🎵 歌词视频生成器 v2.1

    一个现代化的歌词视频生成工具
    支持AI智能标题生成和批量处理

    功能特点：
    • 支持多种音频格式
    • 智能歌词同步
    • AI标题生成
    • 批量处理

    © 2025 - 歌词视频生成器"""
        
        messagebox.showinfo("关于", about_text)
    
    def setup_styles(self):
        """设置现代化样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 定义颜色主题
        self.colors = {
            'primary': '#2196F3',
            'primary_dark': '#1976D2',
            'secondary': '#FF4081',
            'background': '#ffffff',
            'surface': '#f5f5f5',
            'text_primary': '#212121',
            'text_secondary': '#666666',
            'border': '#e0e0e0',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'error': '#F44336'
        }
        
        # 按钮样式
        style.configure('Modern.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       borderwidth=0,
                       focusthickness=0,
                       focuscolor='none',
                       font=('Segoe UI', 10),
                       padding=[16, 8])
        style.map('Modern.TButton',
                 background=[('active', self.colors['primary_dark'])])
        
        # 输入框样式
        style.configure('Modern.TEntry',
                       fieldbackground='white',
                       background='white',
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       relief='solid')
        
        # 标签框架样式
        style.configure('Modern.TLabelframe',
                       background=self.colors['background'],
                       borderwidth=1,
                       relief='solid')
        style.configure('Modern.TLabelframe.Label',
                       background=self.colors['background'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 11, 'bold'))

    def create_modern_button(self, parent, text, command=None, style='primary'):
        """创建现代化按钮"""
        colors = {
            'primary': {'bg': '#2196F3', 'active': '#1976D2'},
            'secondary': {'bg': '#f5f5f5', 'active': '#e0e0e0'},
            'success': {'bg': '#4CAF50', 'active': '#45a049'},
            'danger': {'bg': '#F44336', 'active': '#da190b'}
        }
        
        btn = Button(parent, text=text, command=command,
                    bg=colors[style]['bg'], fg='white' if style != 'secondary' else '#333',
                    activebackground=colors[style]['active'], activeforeground='white' if style != 'secondary' else '#333',
                    relief='flat', bd=0, font=('Segoe UI', 10), cursor='hand2',
                    padx=16, pady=8)
        return btn

    def create_modern_label(self, parent, text, font_size=10, bold=False, text_color=None):
        """创建现代化标签"""
        font = ('Segoe UI', font_size, 'bold' if bold else 'normal')
        color = text_color if text_color else '#333333'
        return Label(parent, text=text, font=font, bg='#ffffff', fg=color)

    def create_modern_frame(self, parent, title=None):
        """创建现代化框架"""
        if title:
            frame = LabelFrame(parent, text=title, bg='#ffffff', 
                             font=('Segoe UI', 11, 'bold'), fg='#333333',
                             relief='solid', bd=1, padx=15, pady=15)
        else:
            frame = Frame(parent, bg='#ffffff')
        return frame

    def setup_debug_status_bar(self):
        """设置调试状态栏"""
        # 创建状态栏框架
        status_frame = Frame(self.root, bg='#f0f0f0', height=25)
        status_frame.pack(side=BOTTOM, fill=X)
        status_frame.pack_propagate(False)
        
        # 左侧状态标签
        self.status_label = Label(
            status_frame, 
            text="就绪", 
            bg='#f0f0f0', 
            fg='#666666', 
            font=('Segoe UI', 9)
        )
        self.status_label.pack(side=LEFT, padx=10)
        
        # 右侧调试信息
        debug_label = Label(
            status_frame, 
            text="调试模式已启用", 
            bg='#f0f0f0', 
            fg='#2196F3', 
            font=('Segoe UI', 9)
        )
        debug_label.pack(side=RIGHT, padx=10)
        
        # 文件计数器
        self.file_count_label = Label(
            status_frame, 
            text="文件: 0", 
            bg='#f0f0f0', 
            fg='#666666', 
            font=('Segoe UI', 9)
        )
        self.file_count_label.pack(side=RIGHT, padx=5)
        
    def update_debug_status(self, message, level="info"):
        """更新调试状态信息"""
        colors = {
            "info": "#2196F3",
            "success": "#4CAF50", 
            "warning": "#FF9800",
            "error": "#F44336"
        }
        
        self.status_label.config(text=message, fg=colors.get(level, "#666666"))
        logger.info(f"状态更新: {message}")
        
        # 更新文件计数
        count = len(self.file_pairs)
        self.file_count_label.config(text=f"文件: {count}")
        
        # 强制更新界面
        self.root.update_idletasks()

    def load_user_preferences(self):
        """加载用户偏好设置"""
        try:
            # 使用新的统一配置管理器
            from utils.config_manager import get_config
            config_manager = get_config()
            self.user_preferences = config_manager._config
            
            # 检查是否需要询问用户是否使用上次设置
            last_session = self.user_preferences.get('app', {}).get('last_session', {})
            if last_session.get('remember_folders', True) and last_session.get('audio_folder'):
                # 询问用户是否使用上次设置
                if messagebox.askyesno(
                    "恢复上次设置",
                    f"是否恢复上次使用的文件夹？\n\n"
                    f"音频文件夹: {last_session.get('audio_folder', 'N/A')}\n"
                    f"输出文件夹: {last_session.get('output_folder', 'N/A')}\n"

                ):
                    return True
        except Exception as e:
            print(f"加载用户偏好失败: {e}")
            self.create_default_preferences()
        return False

    def create_default_preferences(self):
        """创建默认用户偏好 - 使用新的统一配置结构"""
        self.user_preferences = {
            "app": {
                "theme": "light",
                "language": "zh-CN",
                "auto_save": True,
                "show_tooltips": True,
                "window_size": "1200x800",
                "split_pane_position": 0.6,
                "last_session": {
                    "audio_folder": "",
                    "output_folder": "output",

                    "ai_title_enabled": False,
                    "openai_api_key": "",
                    "remember_folders": True
                }
            },
            "video": {
                "font_family": "Microsoft YaHei",
                "font_size": 36,
                "font_color": "#FFFFFF",
                "outline_width": 3,
                "outline_color": "#000000",
                "background_color": "#000000",
                "bold": True,
                "italic": False,
                "margin_bottom": 50,
                "fade_in": 500,
                "fade_out": 500,
                "concurrency": 2,
                "resolution": "1920x1080",
                "preset": "medium",
                "tune": "film",
                "crf": 23,
                "hardware_acceleration": "none",
                "thread_count": 0
            },
            "ai": {
                "ai_title_enabled": False,
                "ai_title_prompt": "请为这首歌曲生成一个15-25字的视频标题",
                "auto_cleanup": True,
                "fallback_to_default": True
            },
            "lyrics": {
                "sync_offset": 0,
                "line_spacing": 1.2,
                "karaoke_mode": False
            },
            "paths": {
                "output_dir": "output",
                "temp_dir": "temp"
            }
        }

    def apply_user_preferences(self):
        """应用用户偏好设置到界面"""
        style_config = self.user_preferences.get('video', {})
        ai_config = self.user_preferences.get('ai', {})
        last_session = self.user_preferences.get('app', {}).get('last_session', {})
        
        # 应用样式配置
        if 'font_family' in style_config:
            self.font_family.set(style_config['font_family'])
        if 'font_size' in style_config:
            self.font_size.set(style_config['font_size'])
        if 'font_color' in style_config:
            self.font_color.set(style_config['font_color'])
            self.font_color_btn.config(bg=style_config['font_color'])
        if 'outline_width' in style_config:
            self.outline_width.set(style_config['outline_width'])
        if 'outline_color' in style_config:
            self.outline_color.set(style_config['outline_color'])
            self.outline_color_btn.config(bg=style_config['outline_color'])
        if 'background_color' in style_config:
            self.bg_color.set(style_config['background_color'])
            self.bg_color_btn.config(bg=style_config['background_color'])
        if 'bold' in style_config:
            self.bold_var.set(style_config['bold'])
        if 'italic' in style_config:
            self.italic_var.set(style_config['italic'])
        if 'margin_bottom' in style_config:
            self.margin_bottom.set(style_config['margin_bottom'])
        if 'fade_in' in style_config:
            self.fade_in.set(style_config['fade_in'])
        if 'fade_out' in style_config:
            self.fade_out.set(style_config['fade_out'])
        if 'concurrency' in style_config:
            self.concurrency_var.set(style_config['concurrency'])
        if 'resolution' in style_config:
            self.resolution.set(style_config['resolution'])
        
        # 应用AI配置
        if 'ai_title_enabled' in ai_config:
            self.ai_title_enabled.set(ai_config['ai_title_enabled'])
        
        # 应用API配置 (从会话设置中获取)
        api_key = last_session.get('openai_api_key', '')
        if api_key:
            self.openai_api_key.set(api_key)
        
        # 应用优化配置 (从视频配置中获取)
        if hasattr(self, 'hwaccel_var') and 'hardware_acceleration' in style_config:
            self.hwaccel_var.set(style_config['hardware_acceleration'])
        if hasattr(self, 'preset_var') and 'preset' in style_config:
            self.preset_var.set(style_config['preset'])
        if hasattr(self, 'crf_var') and 'crf' in style_config:
            self.crf_var.set(style_config['crf'])
        if hasattr(self, 'tune_var') and 'tune' in style_config:
            self.tune_var.set(style_config['tune'])
        if hasattr(self, 'thread_count') and 'thread_count' in style_config:
            self.thread_count.set(style_config['thread_count'])
        
        # 应用会话设置
        if last_session.get('audio_folder') and os.path.exists(last_session['audio_folder']):
            self.folder_var.set(last_session['audio_folder'])
        if last_session.get('output_folder') and os.path.exists(last_session['output_folder']):
            self.output_var.set(last_session['output_folder'])
            self.output_dir = Path(last_session['output_folder'])

        if last_session.get('ai_title_enabled'):
            self.ai_title_enabled.set(True)
        if last_session.get('openai_api_key'):
            self.openai_api_key.set(last_session['openai_api_key'])

    def save_user_preferences(self):
        """保存用户偏好设置"""
        try:
            # 获取当前配置
            current_config = self.get_config()
            
            # 更新用户偏好
            self.user_preferences['video'] = current_config
            self.user_preferences['ai']['ai_title_enabled'] = self.ai_title_enabled.get()
            
            # 更新会话设置
            self.user_preferences['app']['last_session'] = {
                "audio_folder": self.folder_var.get(),
                "output_folder": str(self.output_dir),
                "ai_title_enabled": self.ai_title_enabled.get(),
                "openai_api_key": self.openai_api_key.get(),
                "remember_folders": True
            }
            
            # 使用配置管理器保存
            from utils.config_manager import get_config
            config = get_config()
            config._config = self.user_preferences
            config.save_config()
                
            print("用户偏好已保存")
                
        except Exception as e:
            print(f"保存用户偏好失败: {e}")

    def auto_save_preferences(self):
        """自动保存偏好设置（延迟保存，避免频繁操作）"""
        if hasattr(self, '_save_timer'):
            self.root.after_cancel(self._save_timer)
        self._save_timer = self.root.after(1000, self.save_user_preferences)  # 1秒后保存

    def get_config(self):
        """获取当前配置"""
        config = {
            "font_family": self.font_family.get(),
            "font_size": self.font_size.get(),
            "font_color": self.font_color.get(),
            "outline_width": self.outline_width.get(),
            "outline_color": self.outline_color.get(),
            "background_color": self.bg_color.get(),
            "bold": self.bold_var.get(),
            "italic": self.italic_var.get(),
            "margin_bottom": self.margin_bottom.get(),
            "fade_in": self.fade_in.get(),
            "fade_out": self.fade_out.get(),
            "concurrency": self.concurrency_var.get(),
            "resolution": self.resolution.get()
        }
        
        # 添加新的配置项（如果存在对应的变量）
        if hasattr(self, 'preset_var'):
            config["preset"] = self.preset_var.get()
        if hasattr(self, 'tune_var'):
            config["tune"] = self.tune_var.get()
        if hasattr(self, 'crf_var'):
            config["crf"] = self.crf_var.get()
        if hasattr(self, 'hwaccel_var'):
            config["hwaccel"] = self.hwaccel_var.get()
        if hasattr(self, 'thread_count'):
            config["thread_count"] = self.thread_count.get()
            
        return config

    def setup_file_page(self, parent):
        """设置现代化文件选择页面"""
        
        # 单文件模式
        single_frame = self.create_modern_frame(parent, "📁 单文件模式")
        single_frame.pack(fill=X, pady=(0, 20))
        
        # 文件选择行
        file_rows = [
            ("音频文件", self.audio_var, self.select_audio, "🎵"),
            ("歌词文件", self.lrc_var, self.select_lrc, "📝"),
            ("背景图片", self.bg_var, self.select_background, "🖼️")
        ]
        
        for label, var, cmd, icon in file_rows:
            row = Frame(single_frame, bg=COLORS['surface'])
            row.pack(fill=X, pady=8)
            
            create_modern_label(row, f"{icon} {label}:").pack(side=LEFT)
            entry = create_modern_entry(row, textvariable=var, width=45)
            entry.pack(side=LEFT, padx=(10, 5), fill=X, expand=True)
            create_modern_button(row, "浏览", cmd).pack(side=LEFT)
        
        # 批量处理区域
        batch_frame = self.create_modern_frame(parent, "📂 批量处理")
        batch_frame.pack(fill=X, pady=(0, 20))
        
        # 文件夹选择
        folder_row = Frame(batch_frame, bg=COLORS['surface'])
        folder_row.pack(fill=X, pady=8)
        
        create_modern_label(folder_row, "📁 选择文件夹:").pack(side=LEFT)
        folder_entry = create_modern_entry(folder_row, textvariable=self.folder_var, width=40)
        folder_entry.pack(side=LEFT, padx=(10, 5), fill=X, expand=True)
        
        folder_btn_frame = Frame(folder_row, bg=COLORS['surface'])
        folder_btn_frame.pack(side=LEFT)
        create_modern_button(folder_btn_frame, "浏览", self.select_folder).pack(side=LEFT, padx=2)
        create_modern_button(folder_btn_frame, "🔍 扫描", self.scan_folder).pack(side=LEFT, padx=2)
        
        # 文件列表
        tree_frame = Frame(batch_frame, bg=COLORS['surface'])
        tree_frame.pack(fill=BOTH, expand=True, pady=(10, 0))
        
        # 创建Treeview样式
        style = ttk.Style()
        style.configure('Modern.Treeview',
                       background=COLORS['surface'],
                       foreground=COLORS['text_primary'],
                       fieldbackground=COLORS['surface'],
                       borderwidth=0,
                       relief='flat')
        style.configure('Modern.Treeview.Heading',
                       background=COLORS['background'],
                       foreground=COLORS['text_primary'],
                       relief='flat',
                       font=FONTS['body'])
        
        self.file_tree = ttk.Treeview(tree_frame, columns=('audio', 'lrc', 'background'), 
                                    show='headings', height=6, style='Modern.Treeview')
        self.file_tree.heading('audio', text='🎵 音频文件')
        self.file_tree.heading('lrc', text='📝 歌词文件')
        self.file_tree.heading('background', text='🖼️ 背景图片')
        self.file_tree.column('audio', width=200)
        self.file_tree.column('lrc', width=200)
        self.file_tree.column('background', width=150)
        
        # 滚动条
        tree_scroll = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.file_tree.pack(side=LEFT, fill=BOTH, expand=True)
        tree_scroll.pack(side=RIGHT, fill=Y)
        
        # 输出目录
        output_frame = self.create_modern_frame(parent, "📤 输出设置")
        output_frame.pack(fill=X, pady=(0, 20))
        
        output_row = Frame(output_frame, bg=COLORS['surface'])
        output_row.pack(fill=X, pady=8)
        
        create_modern_label(output_row, "📁 输出目录:").pack(side=LEFT)
        output_entry = create_modern_entry(output_row, textvariable=self.output_var, width=45)
        output_entry.pack(side=LEFT, padx=(10, 5), fill=X, expand=True)
        create_modern_button(output_row, "浏览", self.select_output_dir).pack(side=LEFT)
        
    def get_system_fonts(self):
        """获取系统中已安装的字体列表"""
        try:
            import matplotlib.font_manager as fm
            print(f"Fonts: {fm.findSystemFonts()}")
            # 获取系统中所有字体
            font_list = fm.findSystemFonts(fontpaths=None, fontext='ttf')
            
            # 提取字体名称（去除路径和扩展名）
            fonts = []
            for font_path in font_list:
                try:
                    font_prop = fm.FontProperties(fname=font_path)
                    font_name = font_prop.get_name()
                    if font_name and font_name not in fonts:
                        fonts.append(font_name)
                except:
                    # 如果无法获取字体信息，使用文件名
                    font_name = os.path.basename(font_path).replace('.ttf', '').replace('.TTF', '')
                    if font_name and font_name not in fonts:
                        fonts.append(font_name)
            
            # 排序并返回
            fonts.sort()
            
            # 确保包含一些常用中文字体
            common_fonts = ["Microsoft YaHei", "SimHei", "SimSun", "KaiTi", "FangSong", "Arial", "Times New Roman"]
            for font in common_fonts:
                if font not in fonts:
                    fonts.insert(0, font)
            
            return fonts[:60]  # 限制数量避免列表过长
            
        except ImportError:
            # 如果没有matplotlib，返回常用字体列表
            return ["Microsoft YaHei", "SimHei", "SimSun", "KaiTi", "FangSong", 
                   "Arial", "Times New Roman", "Helvetica", "Courier New", "宋体", "黑体"]
        except Exception as e:
            print(f"获取系统字体失败: {e}")
            return ["Microsoft YaHei", "SimHei", "Arial", "Times New Roman", "宋体", "黑体"]

    def setup_style_page(self, parent):
        """设置现代化样式页面"""
        
        # 样式导入导出
        import_frame = self.create_modern_frame(parent, "🎨 样式管理")
        import_frame.pack(fill=X, pady=(0, 20))

        import_row = Frame(import_frame, bg=COLORS['surface'])
        import_row.pack(fill=X, pady=8)
        
        create_modern_button(import_row, "📤 导出样式", self.export_style_config).pack(side=LEFT, padx=5)
        create_modern_button(import_row, "📥 导入样式", self.import_style_config).pack(side=LEFT, padx=5)
        
        # 并发设置
        concurrency_row = Frame(import_frame, bg=COLORS['surface'])
        concurrency_row.pack(fill=X, pady=(10, 0))
        
        create_modern_label(concurrency_row, "⚡ 并发线程数:").pack(side=LEFT)
        concurrency_scale = Scale(concurrency_row, from_=1, to=8, orient=HORIZONTAL, 
                                  variable=self.concurrency_var, length=150,
                                  command=lambda v: self.auto_save_preferences())
        concurrency_scale.pack(side=LEFT, padx=(10, 5))
        create_modern_label(concurrency_row, "(根据CPU核心数调整)").pack(side=LEFT)
        
        # 设置网格布局
        container = Frame(parent, bg=COLORS['background'])
        container.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # 网格布局配置
        container.grid_columnconfigure(0, weight=1, uniform='col')
        container.grid_columnconfigure(1, weight=1, uniform='col')
        
        # 字体设置
        font_frame = self.create_modern_frame(container, "📝 字体设置")
        font_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # 获取系统字体
        system_fonts = self.get_system_fonts()
        
        # 字体族
        font_row = Frame(font_frame, bg=COLORS['surface'])
        font_row.pack(fill=X, pady=8)
        create_modern_label(font_row, "字体:").pack(side=LEFT)
        font_combo = ttk.Combobox(font_row, textvariable=self.font_family, 
                                 values=system_fonts,
                                 state="readonly", width=20, font=FONTS['body'])
        font_combo.pack(side=LEFT, padx=(10, 5))
        font_combo.bind('<<ComboboxSelected>>', lambda e: self.auto_save_preferences())
        
        # 字体大小
        size_row = Frame(font_frame, bg=COLORS['surface'])
        size_row.pack(fill=X, pady=8)
        create_modern_label(size_row, "字体大小:").pack(side=LEFT)
        size_scale = Scale(size_row, from_=16, to=72, orient=HORIZONTAL, variable=self.font_size,
                         length=150, command=lambda v: self.auto_save_preferences())
        size_scale.pack(side=LEFT, padx=(10, 5))
        
        # 字体颜色
        color_row = Frame(font_frame, bg=COLORS['surface'])
        color_row.pack(fill=X, pady=8)
        create_modern_label(color_row, "字体颜色:").pack(side=LEFT)
        self.font_color_btn = Button(color_row, text="🎨 选择颜色", bg=self.font_color.get(), 
                                   fg='white' if self.font_color.get() == '#000000' else 'black',
                                   command=lambda: self.choose_color(self.font_color, self.font_color_btn))
        self.font_color_btn.pack(side=LEFT, padx=(10, 5))
        
        # 字体样式
        style_row = Frame(font_frame, bg=COLORS['surface'])
        style_row.pack(fill=X, pady=8)
        bold_check = Checkbutton(style_row, text="粗体", variable=self.bold_var,
                               command=self.auto_save_preferences, bg=COLORS['surface'])
        bold_check.pack(side=LEFT, padx=(0, 15))
        italic_check = Checkbutton(style_row, text="斜体", variable=self.italic_var,
                               command=self.auto_save_preferences, bg=COLORS['surface'])
        italic_check.pack(side=LEFT)
        
        # 描边设置
        outline_frame = self.create_modern_frame(container, "🖋️ 描边设置")
        outline_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        
        # 描边宽度
        outline_width_row = Frame(outline_frame, bg='#ffffff')
        outline_width_row.pack(fill=X, pady=8)
        self.create_modern_label(outline_width_row, "描边宽度:", font_size=10).pack(side=LEFT)
        outline_scale = Scale(outline_width_row, from_=0, to=10, orient=HORIZONTAL,
                            variable=self.outline_width, length=150,
                            command=lambda v: self.auto_save_preferences())
        outline_scale.pack(side=LEFT, padx=(10, 5))
        
        # 描边颜色
        outline_color_row = Frame(outline_frame, bg='#ffffff')
        outline_color_row.pack(fill=X, pady=8)
        self.create_modern_label(outline_color_row, "描边颜色:", font_size=10).pack(side=LEFT)
        self.outline_color_btn = Button(outline_color_row, text="🎨 选择颜色", 
                                      bg=self.outline_color.get(),
                                      fg='white' if self.outline_color.get() == '#000000' else 'black',
                                      command=lambda: [self.choose_color(self.outline_color, self.outline_color_btn), 
                                                       self.auto_save_preferences()])
        self.outline_color_btn.pack(side=LEFT, padx=(10, 5))
        
        # 位置设置
        position_frame = self.create_modern_frame(container, "📍 位置设置")
        position_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        
        # 底部边距
        margin_row = Frame(position_frame, bg='#ffffff')
        margin_row.pack(fill=X, pady=8)
        self.create_modern_label(margin_row, "底部边距:", font_size=10).pack(side=LEFT)
        margin_scale = Scale(margin_row, from_=0, to=200, orient=HORIZONTAL,
                           variable=self.margin_bottom, length=150,
                           command=lambda v: self.auto_save_preferences())
        margin_scale.pack(side=LEFT, padx=(10, 5))
        
        # 特效设置
        effect_frame = self.create_modern_frame(container, "✨ 特效设置")
        effect_frame.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)
        
        # 淡入时间
        fade_in_row = Frame(effect_frame, bg='#ffffff')
        fade_in_row.pack(fill=X, pady=8)
        self.create_modern_label(fade_in_row, "淡入时间(ms):", font_size=10).pack(side=LEFT)
        fade_in_scale = Scale(fade_in_row, from_=0, to=2000, orient=HORIZONTAL,
                            variable=self.fade_in, length=150,
                            command=lambda v: self.auto_save_preferences())
        fade_in_scale.pack(side=LEFT, padx=(10, 5))
        
        # 淡出时间
        fade_out_row = Frame(effect_frame, bg='#ffffff')
        fade_out_row.pack(fill=X, pady=8)
        self.create_modern_label(fade_out_row, "淡出时间(ms):", font_size=10).pack(side=LEFT)
        fade_out_scale = Scale(fade_out_row, from_=0, to=2000, orient=HORIZONTAL,
                             variable=self.fade_out, length=150,
                             command=lambda v: self.auto_save_preferences())
        fade_out_scale.pack(side=LEFT, padx=(10, 5))
        
        # 背景设置
        bg_frame = self.create_modern_frame(container, "🎨 背景设置")
        bg_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        
        # 背景颜色
        bg_color_row = Frame(bg_frame, bg='#ffffff')
        bg_color_row.pack(fill=X, pady=8)
        self.create_modern_label(bg_color_row, "背景颜色:", font_size=10).pack(side=LEFT)
        self.bg_color_btn = Button(bg_color_row, text="🎨 选择颜色", 
                                 bg=self.bg_color.get(),
                                 fg='white' if self.bg_color.get() == '#000000' else 'black',
                                 command=lambda: [self.choose_color(self.bg_color, self.bg_color_btn),
                                                  self.auto_save_preferences()])
        self.bg_color_btn.pack(side=LEFT, padx=(10, 5))
        
        # 视频尺寸
        size_frame = self.create_modern_frame(container, "📐 视频尺寸")
        size_frame.grid(row=2, column=1, sticky='nsew', padx=5, pady=5)
        
        # 分辨率
        size_row = Frame(size_frame, bg='#ffffff')
        size_row.pack(fill=X, pady=8)
        self.create_modern_label(size_row, "分辨率:", font_size=10).pack(side=LEFT)
        resolution_combo = ttk.Combobox(size_row, textvariable=self.resolution,
                                     values=["1920x1080", "1280x720", "1024x768", "800x600"],
                                     state="readonly", width=15, font=('Segoe UI', 10))
        resolution_combo.pack(side=LEFT, padx=(10, 5))
        resolution_combo.bind('<<ComboboxSelected>>', lambda e: self.auto_save_preferences())
        


        # import_export_btn_frame = Frame(import_export_frame, bg='white')
        # import_export_btn_frame.pack(fill=X, pady=5)

        # Button(import_export_btn_frame, text="📤 导出样式", 
        #        command=self.export_style_config, 
        #        bg='#28a745', fg='white').pack(side=LEFT, padx=5)

        # Button(import_export_btn_frame, text="📥 导入样式", 
        #        command=self.import_style_config, 
        #        bg='#007bff', fg='white').pack(side=LEFT, padx=5)

        # Label(import_export_frame, text="导入的样式将覆盖当前所有设置", 
        #       bg='white', fg='#666', font=('Arial', 9)).pack(pady=(5, 0))
        
    def setup_batch_page(self, parent):
        # 创建滚动容器
        canvas = Canvas(parent, bg='white')
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 使用scrollable_frame作为容器
        parent = scrollable_frame
        
        # 控制按钮
        control_frame = Frame(parent, bg='white')
        control_frame.pack(fill=X, pady=(0, 20))
        
        self.single_generate_btn = Button(control_frame, text="🎬 生成单个视频", 
                                         command=self.generate_single_video, 
                                         bg='#007bff', fg='white', font=("Arial", 12))
        self.single_generate_btn.pack(side=LEFT, padx=10)
        
        self.batch_generate_btn = Button(control_frame, text="🎬 批量生成视频", 
                                        command=self.start_batch_generation, 
                                        bg='#28a745', fg='white', font=("Arial", 12))
        self.batch_generate_btn.pack(side=LEFT, padx=10)
        
        self.stop_btn = Button(control_frame, text="⏹ 停止", 
                              command=self.stop_generation,
                              bg='#dc3545', fg='white', font=("Arial", 12), state=DISABLED)
        self.stop_btn.pack(side=LEFT, padx=10)
        
        # 进度显示区域
        progress_frame = LabelFrame(parent, text="处理进度", padx=10, pady=10, bg='white')
        progress_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # 当前文件信息
        current_file_frame = Frame(progress_frame, bg='white')
        current_file_frame.pack(fill=X, pady=5)
        
        Label(current_file_frame, text="当前文件:", bg='white', width=10, anchor='w').pack(side=LEFT)
        self.current_file_var = StringVar(value="无")
        Label(current_file_frame, textvariable=self.current_file_var, bg='white', fg='#007bff').pack(side=LEFT, padx=10)
        
        # 当前文件进度
        current_progress_frame = Frame(progress_frame, bg='white')
        current_progress_frame.pack(fill=X, pady=5)
        
        Label(current_progress_frame, text="文件进度:", bg='white', width=10, anchor='w').pack(side=LEFT)
        self.current_file_progress_var = StringVar(value="0%")
        Label(current_progress_frame, textvariable=self.current_file_progress_var, bg='white').pack(side=LEFT, padx=10)
        
        self.current_file_progress_bar = ttk.Progressbar(current_progress_frame, mode='determinate')
        self.current_file_progress_bar.pack(side=LEFT, fill=X, expand=True, padx=10)
        
        # 总体进度（仅批量模式显示）
        total_progress_frame = Frame(progress_frame, bg='white')
        total_progress_frame.pack(fill=X, pady=5)
        
        Label(total_progress_frame, text="总体进度:", bg='white', width=10, anchor='w').pack(side=LEFT)
        self.total_progress_var = StringVar(value="0/0")
        Label(total_progress_frame, textvariable=self.total_progress_var, bg='white').pack(side=LEFT, padx=10)
        
        self.total_progress_bar = ttk.Progressbar(total_progress_frame, mode='determinate')
        self.total_progress_bar.pack(side=LEFT, fill=X, expand=True, padx=10)
        
        # 状态信息
        self.status_var = StringVar(value="准备就绪")
        status_label = Label(progress_frame, textvariable=self.status_var, bg='white', font=("Arial", 10))
        status_label.pack(pady=5)
        
        # 日志显示
        self.log_text = ScrolledText(progress_frame, height=15, wrap=WORD)
        self.log_text.pack(fill=BOTH, expand=True, pady=10)
        
    def select_audio(self):
        filename = filedialog.askopenfilename(
            title="选择音频文件",
            filetypes=[("音频文件", "*.mp3 *.flac *.wav *.m4a *.aac"), ("所有文件", "*.*")]
        )
        if filename:
            self.audio_var.set(filename)
            
    def select_lrc(self):
        filename = filedialog.askopenfilename(
            title="选择歌词文件",
            filetypes=[("歌词文件", "*.lrc"), ("所有文件", "*.*")]
        )
        if filename:
            self.lrc_var.set(filename)
            
    def select_background(self):
        filename = filedialog.askopenfilename(
            title="选择背景图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif"), ("所有文件", "*.*")]
        )
        if filename:
            self.bg_var.set(filename)
            
    def select_folder(self):
        folder = filedialog.askdirectory(title="选择包含音频和歌词文件的文件夹")
        if folder:
            self.folder_var.set(folder)
            
    def select_output_dir(self):
        folder = filedialog.askdirectory(title="选择输出目录")
        if folder:
            self.output_var.set(folder)
            self.output_dir = Path(folder)
            
    def choose_color(self, color_var, button):
        color = colorchooser.askcolor(title="选择颜色", color=color_var.get())
        if color[1]:
            color_var.set(color[1])
            button.config(bg=color[1])
            
    def scan_folder(self):
        folder_path = self.folder_var.get()
        if not folder_path:
            messagebox.showwarning("警告", "请先选择文件夹")
            return
        
        # 清空现有列表
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        self.file_pairs.clear()
        
        try:
            file_pairs, missing_files = scan_folder_for_files(folder_path)
            self.file_pairs = file_pairs
            
            # 显示找到的配对文件
            for audio_file, lrc_file in file_pairs:
                # 检查对应的背景图片
                bg_image = "无"
                for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                    bg_file = audio_file.parent / f"{audio_file.stem}{ext}"
                    if bg_file.exists():
                        bg_image = bg_file.name
                        break
                
                if bg_image == "无":
                    for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                        bg_file = lrc_file.parent / f"{lrc_file.stem}{ext}"
                        if bg_file.exists():
                            bg_image = bg_file.name
                            break
                
                self.file_tree.insert('', 'end', values=(audio_file.name, lrc_file.name, bg_image))
            
            # 显示缺少歌词的文件
            for audio_file in missing_files:
                self.file_tree.insert('', 'end', values=(audio_file.name, "未找到匹配的歌词文件", "-"), tags=('missing',))
            
            self.file_tree.tag_configure('missing', background='#ffcccc')
            
            self.log(f"扫描完成：找到 {len(file_pairs)} 个有效的音频-歌词配对，{len(missing_files)} 个文件缺少歌词")
            self.update_debug_status(f"扫描完成: {len(file_pairs)}个有效文件", "success")
            
            # 显示详细的文件配对信息
            if file_pairs:
                self.log("\n📋 文件配对详情：")
                for i, (audio_file, lrc_file) in enumerate(file_pairs, 1):
                    bg_info = "无背景图片"
                    for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                        bg_file = audio_file.parent / f"{audio_file.stem}{ext}"
                        if bg_file.exists():
                            bg_info = f"使用背景: {bg_file.name}"
                            break
                    
                    if bg_info == "无背景图片":
                        for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                            bg_file = lrc_file.parent / f"{lrc_file.stem}{ext}"
                            if bg_file.exists():
                                bg_info = f"使用背景: {bg_file.name}"
                                break
                    
                    self.log(f"  {i}. {audio_file.name} ↔ {lrc_file.name} ({bg_info})")
            
        except Exception as e:
            messagebox.showerror("错误", f"扫描文件夹时出错：{str(e)}")
            self.update_debug_status("扫描失败", "error")
            logger.error(f"扫描文件夹失败: {e}")
            
    def get_config(self):
        width, height = self.resolution.get().split('x')
        return {
            'font_family': self.font_family.get(),
            'font_size': self.font_size.get(),
            'font_color': self.font_color.get(),
            'outline_width': self.outline_width.get(),
            'outline_color': self.outline_color.get(),
            'background_color': self.bg_color.get(),
            'bold': self.bold_var.get(),
            'italic': self.italic_var.get(),
            'width': int(width),
            'height': int(height),
            'margin_left': 10,
            'margin_right': 10,
            'margin_bottom': self.margin_bottom.get(),
            'fade_in': self.fade_in.get(),
            'fade_out': self.fade_out.get(),
            'shadow_color': '#000000',
            'shadow_offset': 2,
            'concurrency': self.concurrency_var.get(),
            'artist': None  # 可以从文件名解析艺术家信息
        }
        
    def export_style_config(self):
        """导出当前样式配置到JSON文件"""
        try:
            config = self.get_config()
            
            # 保存文件对话框
            filename = filedialog.asksaveasfilename(
                title="导出样式配置",
                defaultextension=".json",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
            )
            
            if filename:
                import json
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("成功", f"样式配置已导出到：\n{filename}")
                self.log(f"样式配置已导出：{filename}")
                
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{str(e)}")
            self.log(f"样式导出失败：{str(e)}")

    def import_style_config(self):
        """从JSON文件导入样式配置"""
        try:
            # 选择文件对话框
            filename = filedialog.askopenfilename(
                title="导入样式配置",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
            )
            
            if filename:
                import json
                with open(filename, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 验证必要的配置项
                required_keys = ['font_family', 'font_size', 'font_color', 'outline_width', 'outline_color']
                missing_keys = [key for key in required_keys if key not in config]
                
                if missing_keys:
                    messagebox.showerror("错误", f"配置文件缺少必要项：{', '.join(missing_keys)}")
                    return
                
                # 应用配置到界面
                self.apply_config_to_ui(config)
                
                # 保存到配置文件
                self.save_user_preferences()
                
                messagebox.showinfo("成功", "样式配置已导入并应用")
                self.log(f"样式配置已导入：{filename}")
                
        except json.JSONDecodeError:
            messagebox.showerror("错误", "配置文件格式错误")
            self.log("样式导入失败：配置文件格式错误")
        except Exception as e:
            messagebox.showerror("错误", f"导入失败：{str(e)}")
            self.log(f"样式导入失败：{str(e)}")

    def apply_config_to_ui(self, config):
        """将配置应用到界面控件"""
        # 字体设置
        if 'font_family' in config:
            self.font_family.set(config['font_family'])
        if 'font_size' in config:
            self.font_size.set(config['font_size'])
        if 'font_color' in config:
            self.font_color.set(config['font_color'])
            self.font_color_btn.config(bg=config['font_color'])
        
        # 描边设置
        if 'outline_width' in config:
            self.outline_width.set(config['outline_width'])
        if 'outline_color' in config:
            self.outline_color.set(config['outline_color'])
            self.outline_color_btn.config(bg=config['outline_color'])
        
        # 背景设置
        if 'background_color' in config:
            self.bg_color.set(config['background_color'])
            self.bg_color_btn.config(bg=config['background_color'])
        
        # 字体样式
        if 'bold' in config:
            self.bold_var.set(config['bold'])
        if 'italic' in config:
            self.italic_var.set(config['italic'])
        
        # 位置设置
        if 'margin_bottom' in config:
            self.margin_bottom.set(config['margin_bottom'])
        
        # 特效设置
        if 'fade_in' in config:
            self.fade_in.set(config['fade_in'])
        if 'fade_out' in config:
            self.fade_out.set(config['fade_out'])
        
        # 视频尺寸
        if 'width' in config and 'height' in config:
            resolution = f"{config['width']}x{config['height']}"
            if resolution in ["1920x1080", "1280x720", "1024x768", "800x600"]:
                self.resolution.set(resolution)
        
        # 并发设置
        if 'concurrency' in config:
            self.concurrency_var.set(min(8, max(1, config['concurrency'])))

    def log(self, message):
        self.log_text.insert(END, f"{message}\n")
        self.log_text.see(END)
        self.root.update_idletasks()
        
    def update_progress(self, current, total, message=""):
        """更新进度回调函数"""
        self.current_file_progress = current
        
        # 更新当前文件进度
        self.current_file_progress_var.set(f"{current}%")
        self.current_file_progress_bar['value'] = current
        
        # 更新状态信息
        if message:
            self.status_var.set(message)
        
        self.root.update_idletasks()
        
    def update_total_progress(self, current_file, total_files):
        """更新总体进度"""
        self.total_files_progress = current_file
        self.total_progress_var.set(f"{current_file}/{total_files}")
        self.total_progress_bar['maximum'] = total_files
        self.total_progress_bar['value'] = current_file
        self.root.update_idletasks()
        
    def generate_single_video(self):
        audio_path = self.audio_var.get()
        lrc_path = self.lrc_var.get()
        
        if not audio_path or not lrc_path:
            messagebox.showwarning("警告", "请选择音频和歌词文件")
            return
            
        bg_image_path = self.bg_var.get() if self.bg_var.get() else None
        config = self.get_config()
        
        # 设置环境变量用于AI标题生成
        if self.ai_title_enabled.get() and self.openai_api_key.get():
            import os
            os.environ['OPENAI_API_KEY'] = self.openai_api_key.get()
        
        # 使用AI标题时，先生成标题再构造输出路径
        if self.ai_title_enabled.get():
            from utils.ai_title_generator import generate_video_title
            song_name = Path(audio_path).stem
            artist = config.get('artist', None)
            ai_title = generate_video_title(song_name, artist)
            # 清理文件名中的特殊字符
            safe_title = "".join(c for c in ai_title if c.isalnum() or c in (' ', '-', '_', '.', '《', '》', '【', '】', '（', '）', '！', '？', '~')).rstrip()
            output_path = self.output_dir / f"{safe_title}.mp4"
        else:
            output_path = self.output_dir / f"{Path(audio_path).stem}.mp4"
        
        # 更新UI状态
        self.single_generate_btn.config(state=DISABLED)
        self.current_file_var.set(Path(audio_path).name)
        self.total_progress_var.set("1/1")
        self.total_progress_bar['maximum'] = 1
        self.total_progress_bar['value'] = 0
        
        def progress_callback(current, total, message=""):
            # 更新进度条
            if total > 0:
                progress = int((current / total) * 100)
                self.current_file_progress_bar['value'] = progress
                self.current_file_progress_var.set(f"{progress}%")
            if message:
                self.status_var.set(message)
            # 允许GUI更新
            self.root.update_idletasks()

        def generate():
            try:
                # 创建新的视频生成器实例
                generator = VideoGenerator(progress_callback)
                success, result = generator.generate_video(
                    audio_path, lrc_path, config, bg_image_path, output_path, 
                    use_ai_title=self.ai_title_enabled.get()
                )
                if success:
                    self.log(f"✅ 视频生成成功：{result}")
                    self.status_var.set("生成完成")
                    self.current_file_progress_bar['value'] = 100
                    self.current_file_progress_var.set("100%")
                    messagebox.showinfo("成功", f"视频已保存到：{result}")
                else:
                    self.log(f"❌ 单个生成失败：{result}")
                    self.status_var.set("单个生成失败")
                    messagebox.showerror("错误", f"单个生成失败：{result}")
            except Exception as e:
                self.log(f"❌ 生成过程异常：{str(e)}")
                self.status_var.set("生成异常")
                messagebox.showerror("错误", f"生成过程异常：{str(e)}")
            finally:
                self.single_generate_btn.config(state=NORMAL)
                self.current_file_var.set("无")
                self.current_file_progress_bar['value'] = 0
                self.current_file_progress_var.set("0%")
                
        threading.Thread(target=generate, daemon=True).start()
        
    def start_batch_generation(self):
        if not self.file_pairs:
            messagebox.showwarning("警告", "没有找到有效的文件配对，请先扫描文件夹")
            return
            
        # 重置视频生成器的停止标志
        self.video_generator.set_stop_flag(False)
        
        # 更新UI状态
        self.batch_generate_btn.config(state=DISABLED)
        self.stop_btn.config(state=NORMAL)
        self.total_progress_bar['maximum'] = len(self.file_pairs)
        self.total_progress_bar['value'] = 0
        
        def batch_generate():
            import os
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            config = self.get_config()
            success_count = 0
            total_files = len(self.file_pairs)
            
            # 设置环境变量用于AI标题生成
            if self.ai_title_enabled.get() and self.openai_api_key.get():
                os.environ['OPENAI_API_KEY'] = self.openai_api_key.get()
            
            # 使用用户配置的并发度
            max_workers = min(8, max(1, config.get('concurrency', 2)))
            self.log(f"🚀 启动并发处理，使用 {max_workers} 个线程")
            
            # 创建线程池执行器
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有任务
                future_to_file = {}
                
                for i, (audio_path, lrc_path) in enumerate(self.file_pairs):
                    if self.video_generator.stop_flag:
                        break
                    
                    output_path = self.output_dir / f"{audio_path.stem}.mp4"
                    
                    # 检查是否有同名背景图片（在音频文件所在目录查找）
                    bg_image_path = None
                    for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                        bg_file = audio_path.parent / f"{audio_path.stem}{ext}"
                        if bg_file.exists():
                            bg_image_path = bg_file
                            break
                    
                    # 检查是否有同名背景图片（在歌词文件所在目录查找，确保每个文件使用自己的背景）
                    if bg_image_path is None:
                        for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                            bg_file = lrc_path.parent / f"{lrc_path.stem}{ext}"
                            if bg_file.exists():
                                bg_image_path = bg_file
                                break
                    
                    # 提交任务到线程池
                    future = executor.submit(
                        self.process_single_file,
                        audio_path, lrc_path, config, bg_image_path, output_path, i+1, total_files
                    )
                    future_to_file[future] = (audio_path, i+1)
                
                # 收集结果
                completed = 0
                for future in as_completed(future_to_file):
                    if self.video_generator.stop_flag:
                        # 取消未完成的任务
                        for f in future_to_file:
                            f.cancel()
                        break
                    
                    audio_path, file_num = future_to_file[future]
                    
                    try:
                        success, result = future.result()
                        if success:
                            success_count += 1
                            self.log(f"✅ [{file_num}/{total_files}] {audio_path.name} 生成成功")
                        else:
                            self.log(f"❌ [{file_num}/{total_files}] {audio_path.name} 生成失败：{result}")
                    except Exception as e:
                        self.log(f"❌ [{file_num}/{total_files}] {audio_path.name} 处理异常：{str(e)}")
                    
                    completed += 1
                    self.update_total_progress(completed, total_files)
            
            # 完成后更新UI
            if not self.video_generator.stop_flag:
                self.status_var.set(f"批量生成完成：成功 {success_count}/{total_files}")
                messagebox.showinfo("完成", f"批量生成完成！\n成功：{success_count}\n总计：{total_files}")
            else:
                self.log("❌ 批量生成已停止")
            
            self.batch_generate_btn.config(state=NORMAL)
            self.stop_btn.config(state=DISABLED)
            self.current_file_var.set("无")
        
        threading.Thread(target=batch_generate, daemon=True).start()
    
    def process_single_file(self, audio_path, lrc_path, config, bg_image_path, output_path, file_num, total_files):
        """处理单个文件的包装函数"""
        try:
            # 创建独立的视频生成器实例（线程安全）
            from core.video_generator import VideoGenerator
            from utils.ai_title_generator import generate_video_title
            
            # 记录使用的文件路径，确保每个文件使用正确的资源
            print(f"📝 处理文件 {file_num}/{total_files}:")
            print(f"   音频: {audio_path}")
            print(f"   歌词: {lrc_path}")
            print(f"   背景: {bg_image_path}")
            
            # 处理AI标题
            final_output_path = output_path
            if self.ai_title_enabled.get():
                try:
                    song_name = audio_path.stem
                    artist = config.get('artist', None)
                    ai_title = generate_video_title(song_name, artist)
                    # 清理文件名中的特殊字符，但保留中文符号
                    safe_title = "".join(c for c in ai_title if c.isalnum() or c in (' ', '-', '_', '.', '《', '》', '【', '】', '（', '）', '！', '？', '~')).rstrip()
                    final_output_path = output_path.parent / f"{safe_title}.mp4"
                    print(f"   AI标题: {safe_title}")
                    print(f"   输出: {final_output_path}")
                except Exception as e:
                    print(f"   AI标题生成失败，使用原文件名: {e}")
                    final_output_path = output_path
            else:
                print(f"   输出: {final_output_path}")
            
            def progress_callback(current, total, message=""):
                # 使用after方法确保线程安全地更新GUI
                def update_gui():
                    progress_percent = int((current / total) * 100) if total > 0 else 0
                    self.current_file_progress_var.set(f"{progress_percent}%")
                    self.current_file_progress_bar['value'] = progress_percent
                    
                    # 更新状态信息
                    if message:
                        self.current_file_var.set(f"[{file_num}/{total_files}] {audio_path.name} - {message}")
                    else:
                        self.current_file_var.set(f"[{file_num}/{total_files}] {audio_path.name} ({progress_percent}%)")
                
                # 使用after方法在主线程中更新GUI
                try:
                    self.root.after(0, update_gui)
                except:
                    # 如果root已被销毁，直接返回
                    pass
            
            generator = VideoGenerator(progress_callback)
            return generator.generate_video(
                audio_path, lrc_path, config, bg_image_path, final_output_path,
                use_ai_title=self.ai_title_enabled.get()
            )
            
        except Exception as e:
            return False, str(e)
        
    def stop_generation(self):
        self.video_generator.set_stop_flag(True)
        self.stop_btn.config(state=DISABLED)
        self.status_var.set("正在停止...")
    
    def on_closing(self):
        """窗口关闭事件处理"""
        try:
            # 保存用户偏好设置
            self.save_user_preferences()
            
            # 设置停止标志
            self.video_generator.set_stop_flag(True)
            
            # 终止FFmpeg进程
            self.video_generator.terminate_ffmpeg_process()
            
            # 延迟关闭，确保进程清理完成
            self.root.after(100, self.root.destroy)
        except Exception as e:
            print(f"关闭窗口时出错: {e}")
            # 无论如何都要关闭窗口
            self.root.destroy()
    
    def toggle_ai_title(self):
        """切换AI标题生成功能"""
        if self.ai_title_enabled.get():
            self.show_api_key_dialog()
        self.auto_save_preferences()
    
    def show_api_key_dialog(self):
        """显示OpenAI API密钥输入对话框"""
        dialog = Toplevel(self.root)
        dialog.title("OpenAI API密钥设置")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.geometry(f"+{self.root.winfo_x() + 100}+{self.root.winfo_y() + 100}")
        
        # 设置样式
        dialog.configure(bg=COLORS['background'])
        
        # 标题
        title_label = Label(dialog, text="🤖 OpenAI API密钥", 
                           font=FONTS['subtitle'], bg=COLORS['background'], 
                           fg=COLORS['text_primary'])
        title_label.pack(pady=(20, 10))
        
        # 说明文字
        hint_label = Label(dialog, text="请输入您的OpenAI API密钥：", 
                          font=FONTS['body'], bg=COLORS['background'], 
                          fg=COLORS['text_secondary'])
        hint_label.pack(pady=(0, 10))
        
        # 输入框
        api_key_entry = Entry(dialog, textvariable=self.openai_api_key, 
                            font=FONTS['body'], width=40, show="*")
        api_key_entry.pack(pady=(0, 20), padx=20)
        api_key_entry.focus()
        
        # 按钮区域
        btn_frame = Frame(dialog, bg=COLORS['background'])
        btn_frame.pack(pady=(0, 20))
        
        def save_and_close():
            api_key = self.openai_api_key.get().strip()
            if api_key:
                # 验证API密钥格式（支持OpenAI和OpenRouter）
                import re
                is_valid = False
                
                # OpenAI格式：sk- + 48字符
                openai_pattern = r'^sk-[a-zA-Z0-9]{48}$'
                # OpenRouter格式：sk-or-v1- + 64十六进制字符
                openrouter_pattern = r'^sk-or-v1-[a-f0-9]{64}$'
                
                if re.match(openai_pattern, api_key):
                    is_valid = True
                elif re.match(openrouter_pattern, api_key):
                    is_valid = True
                
                if not is_valid:
                    messagebox.showwarning("格式错误", 
                        "API密钥格式不正确！\n\n"
                        "支持的格式：\n"
                        "• OpenAI: sk-开头，后面跟48个字母数字字符\n"
                        "• OpenRouter: sk-or-v1-开头，后面跟64个十六进制字符\n\n"
                        "例如：\n"
                        "sk-abcdefghijklmnopqrstuvwxyz123456\n")
                    return
            
            self.auto_save_preferences()
            dialog.destroy()
        
        def cancel():
            self.ai_title_enabled.set(False)
            dialog.destroy()
        
        create_modern_button(btn_frame, "保存", save_and_close, 'primary').pack(side=LEFT, padx=5)
        create_modern_button(btn_frame, "取消", cancel, 'secondary').pack(side=LEFT, padx=5)
        
        # 绑定回车键
        api_key_entry.bind('<Return>', lambda e: save_and_close())