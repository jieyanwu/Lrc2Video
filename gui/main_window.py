#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口GUI
"""

import os
import threading
from pathlib import Path
from tkinter import *
from tkinter import ttk, filedialog, messagebox, colorchooser
from tkinter.scrolledtext import ScrolledText

from core.video_generator import VideoGenerator
from utils.file_utils import scan_folder_for_files

class LyricsVideoGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 歌词视频生成器")
        self.root.geometry("900x700")
        self.root.configure(bg="#6090da")
        
        # 存储文件列表
        self.file_pairs = []  # [(audio_path, lrc_path), ...]
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # 视频生成器
        self.video_generator = VideoGenerator(progress_callback=self.update_progress)
        
        # 进度相关变量
        self.current_file_progress = 0
        self.total_files_progress = 0
        self.current_file_name = ""
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.setup_ui()
        
    def setup_ui(self):
        # 主框架
        main_frame = Frame(self.root, bg="#c7daf7", padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # 标题
        title_label = Label(main_frame, text="歌词视频生成器", 
                           font=("Arial", 20, "bold"), bg='#f0f2f5', fg='#333')
        title_label.pack(pady=(0, 20))
        
        # 创建Notebook用于分页
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=BOTH, expand=True)
        
        # 文件选择页面
        file_frame = Frame(notebook, bg='white', padx=20, pady=20)
        notebook.add(file_frame, text="文件选择")
        
        # 样式设置页面
        style_frame = Frame(notebook, bg='white', padx=20, pady=20)
        notebook.add(style_frame, text="样式设置")
        
        # 批量处理页面
        batch_frame = Frame(notebook, bg='white', padx=20, pady=20)
        notebook.add(batch_frame, text="批量处理")
        
        # 测试页面
        test_frame = Frame(notebook, bg='white', padx=20, pady=20)
        notebook.add(test_frame, text="测试")

        self.setup_file_page(file_frame)
        self.setup_style_page(style_frame)
        self.setup_batch_page(batch_frame)
        self.setup_test_page(test_frame)
        
    def setup_test_page(self, parent):
        Label(parent, text="测试页面内容待开发...", bg='white', font=("Arial", 14)).pack(pady=20)

    def setup_file_page(self, parent):
        # API功能开关区域
        api_frame = LabelFrame(parent, text="API功能", padx=10, pady=10, bg='white')
        api_frame.pack(fill=X, pady=(0, 20))
        
        # API开关
        self.api_enabled = BooleanVar(value=False)
        self.api_server = None
        
        api_switch_frame = Frame(api_frame, bg='white')
        api_switch_frame.pack(fill=X, pady=5)
        
        Checkbutton(api_switch_frame, text="启用API功能", variable=self.api_enabled, 
                   command=self.toggle_api, bg='white').pack(side=LEFT, padx=5)
        
        # API地址显示
        self.api_url_var = StringVar(value="http://localhost:8000")
        api_url_frame = Frame(api_frame, bg='white')
        api_url_frame.pack(fill=X, pady=5)
        
        Label(api_url_frame, text="API地址:", bg='white', width=12, anchor='w').pack(side=LEFT)
        Entry(api_url_frame, textvariable=self.api_url_var, width=40, state='readonly').pack(side=LEFT, padx=5)
        Button(api_url_frame, text="复制地址", command=self.copy_api_url).pack(side=LEFT, padx=5)
        Button(api_url_frame, text="打开文档", command=self.open_api_docs).pack(side=LEFT)
        
        # API状态
        self.api_status_var = StringVar(value="API已关闭")
        Label(api_frame, textvariable=self.api_status_var, bg='white', fg='gray').pack()
        
        # 单文件选择区域
        single_frame = LabelFrame(parent, text="单文件模式", padx=10, pady=10, bg='white')
        single_frame.pack(fill=X, pady=(0, 20))
        
        # 音频文件选择
        audio_frame = Frame(single_frame, bg='white')
        audio_frame.pack(fill=X, pady=5)
        Label(audio_frame, text="音频文件:", bg='white', width=12, anchor='w').pack(side=LEFT)
        self.audio_var = StringVar()
        Entry(audio_frame, textvariable=self.audio_var, width=50).pack(side=LEFT, padx=5)
        Button(audio_frame, text="浏览", command=self.select_audio).pack(side=LEFT)
        
        # 歌词文件选择
        lrc_frame = Frame(single_frame, bg='white')
        lrc_frame.pack(fill=X, pady=5)
        Label(lrc_frame, text="歌词文件:", bg='white', width=12, anchor='w').pack(side=LEFT)
        self.lrc_var = StringVar()
        Entry(lrc_frame, textvariable=self.lrc_var, width=50).pack(side=LEFT, padx=5)
        Button(lrc_frame, text="浏览", command=self.select_lrc).pack(side=LEFT)
        
        # 背景图片选择
        bg_frame = Frame(single_frame, bg='white')
        bg_frame.pack(fill=X, pady=5)
        Label(bg_frame, text="背景图片:", bg='white', width=12, anchor='w').pack(side=LEFT)
        self.bg_var = StringVar()
        Entry(bg_frame, textvariable=self.bg_var, width=50).pack(side=LEFT, padx=5)
        Button(bg_frame, text="浏览", command=self.select_background).pack(side=LEFT)
        
        # 文件夹批量导入区域
        folder_frame = LabelFrame(parent, text="文件夹批量导入", padx=10, pady=10, bg='white')
        folder_frame.pack(fill=X, pady=(0, 20))
        
        folder_select_frame = Frame(folder_frame, bg='white')
        folder_select_frame.pack(fill=X, pady=5)
        Label(folder_select_frame, text="选择文件夹:", bg='white', width=12, anchor='w').pack(side=LEFT)
        self.folder_var = StringVar()
        Entry(folder_select_frame, textvariable=self.folder_var, width=50).pack(side=LEFT, padx=5)
        Button(folder_select_frame, text="浏览", command=self.select_folder).pack(side=LEFT, padx=5)
        Button(folder_select_frame, text="扫描", command=self.scan_folder).pack(side=LEFT)
        
        # 文件匹配显示
        self.file_tree = ttk.Treeview(folder_frame, columns=('audio', 'lrc', 'background'), show='headings', height=8)
        self.file_tree.heading('audio', text='音频文件')
        self.file_tree.heading('lrc', text='歌词文件')
        self.file_tree.heading('background', text='背景图片')
        self.file_tree.column('audio', width=180)
        self.file_tree.column('lrc', width=180)
        self.file_tree.column('background', width=120)
        
        tree_scroll = ttk.Scrollbar(folder_frame, orient=VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=tree_scroll.set)
        
        tree_frame = Frame(folder_frame, bg='white')
        tree_frame.pack(fill=BOTH, expand=True, pady=10)
        self.file_tree.pack(side=LEFT, fill=BOTH, expand=True)
        tree_scroll.pack(side=RIGHT, fill=Y)
        
        # 输出目录选择
        output_frame = Frame(parent, bg='white')
        output_frame.pack(fill=X, pady=10)
        Label(output_frame, text="输出目录:", bg='white', width=12, anchor='w').pack(side=LEFT)
        self.output_var = StringVar(value=str(self.output_dir))
        Entry(output_frame, textvariable=self.output_var, width=50).pack(side=LEFT, padx=5)
        Button(output_frame, text="浏览", command=self.select_output_dir).pack(side=LEFT)
        
    def setup_style_page(self, parent):
        # 创建网格布局容器
        container = Frame(parent, bg='white')
        container.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # 配置网格列权重，实现响应式布局
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=0)
        container.grid_rowconfigure(1, weight=0)
        container.grid_rowconfigure(2, weight=0)
        container.grid_rowconfigure(3, weight=0)
        container.grid_rowconfigure(4, weight=0)

        # 字体设置 - 左侧
        font_frame = LabelFrame(container, text="字体设置", padx=15, pady=15, bg='white', relief=GROOVE)
        font_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        
        # 字体族
        Label(font_frame, text="字体:", bg='white', font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)
        self.font_family = StringVar(value="Microsoft YaHei")
        font_combo = ttk.Combobox(font_frame, textvariable=self.font_family, 
                                 values=["Microsoft YaHei", "SimHei", "Arial", "Times New Roman", "宋体", "黑体"],
                                 state="readonly", width=15)
        font_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        # 字体大小
        Label(font_frame, text="字体大小:", bg='white', font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=5)
        self.font_size = IntVar(value=36)
        Scale(font_frame, from_=16, to=72, orient=HORIZONTAL, variable=self.font_size, 
              length=120).grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        # 字体颜色
        Label(font_frame, text="字体颜色:", bg='white', font=('Arial', 10)).grid(row=2, column=0, sticky='w', pady=5)
        color_frame = Frame(font_frame, bg='white')
        color_frame.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        self.font_color = StringVar(value="#FFFFFF")
        self.font_color_btn = Button(color_frame, text="选择", bg=self.font_color.get(), width=8,
                                    command=lambda: self.choose_color(self.font_color, self.font_color_btn))
        self.font_color_btn.pack(side=LEFT)
        
        # 字体样式
        style_frame = Frame(font_frame, bg='white')
        style_frame.grid(row=3, column=0, columnspan=2, sticky='w', pady=5)
        self.bold_var = BooleanVar(value=True)
        self.italic_var = BooleanVar(value=False)
        Checkbutton(style_frame, text="粗体", variable=self.bold_var, bg='white').pack(side=LEFT, padx=5)
        Checkbutton(style_frame, text="斜体", variable=self.italic_var, bg='white').pack(side=LEFT, padx=5)
        
        font_frame.grid_columnconfigure(1, weight=1)

        # 描边设置 - 右侧
        outline_frame = LabelFrame(container, text="描边设置", padx=15, pady=15, bg='white', relief=GROOVE)
        outline_frame.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)
        
        # 描边宽度
        Label(outline_frame, text="描边宽度:", bg='white', font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)
        self.outline_width = IntVar(value=3)
        Scale(outline_frame, from_=0, to=10, orient=HORIZONTAL, variable=self.outline_width,
              length=120).grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        # 描边颜色
        Label(outline_frame, text="描边颜色:", bg='white', font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=5)
        color_frame2 = Frame(outline_frame, bg='white')
        color_frame2.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        self.outline_color = StringVar(value="#000000")
        self.outline_color_btn = Button(color_frame2, text="选择", bg=self.outline_color.get(), width=8,
                                       command=lambda: self.choose_color(self.outline_color, self.outline_color_btn))
        self.outline_color_btn.pack(side=LEFT)
        
        outline_frame.grid_columnconfigure(1, weight=1)

        # 位置设置 - 左侧
        position_frame = LabelFrame(container, text="位置设置", padx=15, pady=15, bg='white', relief=GROOVE)
        position_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        
        # 底部边距
        Label(position_frame, text="底部边距:", bg='white', font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)
        self.margin_bottom = IntVar(value=50)
        Scale(position_frame, from_=0, to=200, orient=HORIZONTAL, variable=self.margin_bottom,
              length=120).grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        position_frame.grid_columnconfigure(1, weight=1)

        # 特效设置 - 右侧
        effect_frame = LabelFrame(container, text="特效设置", padx=15, pady=15, bg='white', relief=GROOVE)
        effect_frame.grid(row=2, column=1, sticky='nsew', padx=5, pady=5)
        
        # 淡入时间
        Label(effect_frame, text="淡入时间(ms):", bg='white', font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)
        self.fade_in = IntVar(value=500)
        Scale(effect_frame, from_=0, to=2000, orient=HORIZONTAL, variable=self.fade_in,
              length=120).grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        # 淡出时间
        Label(effect_frame, text="淡出时间(ms):", bg='white', font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=5)
        self.fade_out = IntVar(value=500)
        Scale(effect_frame, from_=0, to=2000, orient=HORIZONTAL, variable=self.fade_out,
              length=120).grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        effect_frame.grid_columnconfigure(1, weight=1)

        # 背景设置 - 左侧
        bg_frame = LabelFrame(container, text="背景设置", padx=15, pady=15, bg='white', relief=GROOVE)
        bg_frame.grid(row=3, column=0, sticky='nsew', padx=5, pady=5)
        
        # 背景颜色
        Label(bg_frame, text="背景颜色:", bg='white', font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)
        color_frame3 = Frame(bg_frame, bg='white')
        color_frame3.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        self.bg_color = StringVar(value="#000000")
        self.bg_color_btn = Button(color_frame3, text="选择", bg=self.bg_color.get(), width=8,
                                  command=lambda: self.choose_color(self.bg_color, self.bg_color_btn))
        self.bg_color_btn.pack(side=LEFT)
        
        bg_frame.grid_columnconfigure(1, weight=1)

        # 视频尺寸 - 右侧
        size_frame = LabelFrame(container, text="视频尺寸", padx=15, pady=15, bg='white', relief=GROOVE)
        size_frame.grid(row=3, column=1, sticky='nsew', padx=5, pady=5)
        
        # 分辨率
        Label(size_frame, text="分辨率:", bg='white', font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)
        self.resolution = StringVar(value="1920x1080")
        ttk.Combobox(size_frame, textvariable=self.resolution, 
                    values=["1920x1080", "1280x720", "1024x768", "800x600"], 
                    state="readonly", width=15).grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        size_frame.grid_columnconfigure(1, weight=1)

        # 样式导入导出 - 全宽（置顶）
        import_export_frame = LabelFrame(container, text="样式导入导出", padx=15, pady=15, bg='white', relief=GROOVE)
        import_export_frame.grid(row=0, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
        
        import_export_btn_frame = Frame(import_export_frame, bg='white')
        import_export_btn_frame.pack(fill=X, pady=5)

        Button(import_export_btn_frame, text="📤 导出样式", 
               command=self.export_style_config, 
               bg='#28a745', fg='white', width=12).pack(side=LEFT, padx=5)
        
        Button(import_export_btn_frame, text="📥 导入样式", 
               command=self.import_style_config, 
               bg='#007bff', fg='white', width=12).pack(side=LEFT, padx=5)

        # 并发设置
        concurrency_frame = Frame(import_export_frame, bg='white')
        concurrency_frame.pack(fill=X, pady=(10, 0))
        
        Label(concurrency_frame, text="并发线程数:", bg='white').pack(side=LEFT)
        self.concurrency_var = IntVar(value=2)
        Scale(concurrency_frame, from_=1, to=8, orient=HORIZONTAL, variable=self.concurrency_var,
              length=120).pack(side=LEFT, padx=(5, 10))
        Label(concurrency_frame, text="(根据CPU核心数调整)", bg='white', fg='#666', font=('Arial', 9)).pack(side=LEFT)
        


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
        progress_frame.pack(fill=BOTH, expand=True)
        
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
            'concurrency': self.concurrency_var.get()
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
        print(config)
        output_path = self.output_dir / f"{Path(audio_path).stem}.mp4"
        
        # 更新UI状态
        self.single_generate_btn.config(state=DISABLED)
        self.current_file_var.set(Path(audio_path).name)
        self.total_progress_var.set("1/1")
        self.total_progress_bar['maximum'] = 1
        self.total_progress_bar['value'] = 0
        
        def generate():
            try:
                success, result = self.video_generator.generate_video(audio_path, lrc_path, config, bg_image_path, output_path)
                if success:
                    self.log(f"✅ 视频生成成功：{result}")
                    self.status_var.set("生成完成")
                    self.total_progress_bar['value'] = 1
                    messagebox.showinfo("成功", f"视频已保存到：{result}")
                else:
                    self.log(f"❌ 单个生成失败：{result}")
                    self.status_var.set("单个生成失败")
                    messagebox.showerror("错误", f"单个生成失败：{result}")
            finally:
                self.single_generate_btn.config(state=NORMAL)
                self.current_file_var.set("无")
                
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
            
            # 记录使用的文件路径，确保每个文件使用正确的资源
            print(f"📝 处理文件 {file_num}/{total_files}:")
            print(f"   音频: {audio_path}")
            print(f"   歌词: {lrc_path}")
            print(f"   背景: {bg_image_path}")
            print(f"   输出: {output_path}")
            
            def progress_callback(current, total, message=""):
                # 这里可以添加更细粒度的进度显示
                pass
            
            generator = VideoGenerator(progress_callback)
            return generator.generate_video(audio_path, lrc_path, config, bg_image_path, output_path)
            
        except Exception as e:
            return False, str(e)
        
    def stop_generation(self):
        self.video_generator.set_stop_flag(True)
        self.stop_btn.config(state=DISABLED)
        self.status_var.set("正在停止...")
    
    def on_closing(self):
        """窗口关闭事件处理"""
        try:
            # 停止API服务器
            if self.api_server and self.api_enabled.get():
                self.stop_api_server()
            
            # 设置停止标志
            self.video_generator.set_stop_flag(True)
            
            # 终止FFmpeg进程
            self.video_generator.terminate_ffmpeg_process()
            
            # 延迟关闭，确保进程清理完成
            self.root.after(100, self.root.destroy)
        except:
            # 无论如何都要关闭窗口
            self.root.destroy()
    
    def toggle_api(self):
        """切换API功能开关"""
        if self.api_enabled.get():
            self.start_api_server()
        else:
            self.stop_api_server()
    
    def start_api_server(self):
        """启动API服务器"""
        try:
            from flask import Flask, request, jsonify
            import threading
            
            self.app = Flask(__name__)
            self.app.config['JSON_AS_ASCII'] = False
            
            @self.app.route('/api/generate', methods=['POST'])
            def api_generate():
                """API生成接口"""
                try:
                    data = request.json
                    audio_path = data.get('audio_path')
                    lrc_path = data.get('lrc_path')
                    bg_image_path = data.get('bg_image_path')
                    output_path = data.get('output_path')
                    config = data.get('config', {})
                    
                    if not audio_path or not lrc_path:
                        return jsonify({"error": "缺少音频或歌词文件路径"}), 400
                    
                    # 使用当前样式配置
                    current_config = self.get_config()
                    current_config.update(config)
                    
                    # 生成视频
                    success, message = self.video_generator.generate_video(
                        audio_path, lrc_path, current_config, bg_image_path, output_path
                    )
                    
                    if success:
                        return jsonify({"success": True, "output_path": message})
                    else:
                        return jsonify({"error": message}), 500
                        
                except Exception as e:
                    return jsonify({"error": str(e)}), 500
            
            @self.app.route('/api/status', methods=['GET'])
            def api_status():
                """获取API状态"""
                return jsonify({
                    "status": "running",
                    "supported_endpoints": [
                        "/api/generate",
                        "/api/status",
                        "/api/config",
                        "/api/styles"
                    ]
                })
            
            @self.app.route('/api/config', methods=['GET', 'POST'])
            def api_config():
                """获取或设置配置"""
                if request.method == 'GET':
                    return jsonify(self.get_config())
                else:
                    # 更新配置（待实现）
                    return jsonify({"message": "配置更新功能待实现"})
            
            @self.app.route('/api/styles', methods=['GET'])
            def api_styles():
                """获取可用样式"""
                return jsonify({
                    "styles": ["default", "modern"],
                    "current": "default"
                })
            
            # 启动服务器
            def run_server():
                self.app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)
            
            self.api_server = threading.Thread(target=run_server, daemon=True)
            self.api_server.start()
            
            self.api_status_var.set("API运行中 (端口: 8000)")
            print("API服务器已启动")
            
        except ImportError:
            messagebox.showerror("错误", "需要安装Flask库: pip install flask")
            self.api_enabled.set(False)
        except Exception as e:
            messagebox.showerror("错误", f"启动API服务器失败: {e}")
            self.api_enabled.set(False)
    
    def stop_api_server(self):
        """停止API服务器"""
        try:
            if hasattr(self, 'app'):
                # 关闭Flask服务器
                import requests
                try:
                    requests.post('http://localhost:8000/shutdown', timeout=1)
                except:
                    pass
            
            self.api_status_var.set("API已关闭")
            print("API服务器已停止")
            
        except Exception as e:
            print(f"停止API服务器时出错: {e}")
    
    def copy_api_url(self):
        """复制API地址到剪贴板"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.api_url_var.get())
            messagebox.showinfo("提示", "API地址已复制到剪贴板")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {e}")
    
    def open_api_docs(self):
        """打开API文档"""
        docs_text = """
歌词视频生成器 API 文档

基础URL: http://localhost:8000

端点说明:

1. POST /api/generate
   生成歌词视频
   参数:
   - audio_path: 音频文件路径
   - lrc_path: 歌词文件路径
   - bg_image_path: 背景图片路径 (可选)
   - output_path: 输出文件路径 (可选)
   - config: 样式配置 (可选)

2. GET /api/status
   获取API状态

3. GET /api/config
   获取当前配置

4. GET /api/styles
   获取可用样式

示例请求:
curl -X POST http://localhost:8000/api/generate \\
  -H "Content-Type: application/json" \\
  -d '{"audio_path": "song.mp3", "lrc_path": "song.lrc"}'
        """
        
        # 创建文档窗口
        docs_window = Toplevel(self.root)
        docs_window.title("API文档")
        docs_window.geometry("600x500")
        docs_window.configure(bg='white')
        
        text_widget = ScrolledText(docs_window, wrap=WORD, padx=10, pady=10)
        text_widget.pack(fill=BOTH, expand=True)
        text_widget.insert('1.0', docs_text)
        text_widget.configure(state='disabled')