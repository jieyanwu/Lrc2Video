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
        self.file_tree = ttk.Treeview(folder_frame, columns=('audio', 'lrc'), show='headings', height=8)
        self.file_tree.heading('audio', text='音频文件')
        self.file_tree.heading('lrc', text='歌词文件')
        self.file_tree.column('audio', width=300)
        self.file_tree.column('lrc', width=300)
        
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
        # 字体设置
        font_frame = LabelFrame(parent, text="字体设置", padx=10, pady=10, bg='white')
        font_frame.pack(fill=X, pady=(0, 10))
        
        # 字体族
        font_family_frame = Frame(font_frame, bg='white')
        font_family_frame.pack(fill=X, pady=5)
        Label(font_family_frame, text="字体:", bg='white', width=15, anchor='w').pack(side=LEFT)
        self.font_family = StringVar(value="Microsoft YaHei")
        font_combo = ttk.Combobox(font_family_frame, textvariable=self.font_family, 
                                 values=["Microsoft YaHei", "SimHei", "Arial", "Times New Roman", "宋体", "黑体"],
                                 state="readonly", width=20)
        font_combo.pack(side=LEFT, padx=10)
        
        # 字体大小
        size_frame = Frame(font_frame, bg='white')
        size_frame.pack(fill=X, pady=5)
        Label(size_frame, text="字体大小:", bg='white', width=15, anchor='w').pack(side=LEFT)
        self.font_size = IntVar(value=36)
        Scale(size_frame, from_=16, to=72, orient=HORIZONTAL, variable=self.font_size).pack(side=LEFT, fill=X, expand=True, padx=10)
        
        # 字体颜色
        color_frame = Frame(font_frame, bg='white')
        color_frame.pack(fill=X, pady=5)
        Label(color_frame, text="字体颜色:", bg='white', width=15, anchor='w').pack(side=LEFT)
        self.font_color = StringVar(value="#FFFFFF")
        self.font_color_btn = Button(color_frame, text="选择颜色", bg=self.font_color.get(),
                                    command=lambda: self.choose_color(self.font_color, self.font_color_btn))
        self.font_color_btn.pack(side=LEFT, padx=10)
        # 假设 self.font_color 已经是 "#FFFFFF" 这样的值
        
        # 字体样式
        style_frame = Frame(font_frame, bg='white')
        style_frame.pack(fill=X, pady=5)
        self.bold_var = BooleanVar(value=True)
        self.italic_var = BooleanVar(value=False)
        Checkbutton(style_frame, text="粗体", variable=self.bold_var, bg='white').pack(side=LEFT, padx=10)
        Checkbutton(style_frame, text="斜体", variable=self.italic_var, bg='white').pack(side=LEFT, padx=10)
        
        # 描边设置
        outline_frame = LabelFrame(parent, text="描边设置", padx=10, pady=10, bg='white')
        outline_frame.pack(fill=X, pady=(0, 10))
        
        # 描边宽度
        outline_width_frame = Frame(outline_frame, bg='white')
        outline_width_frame.pack(fill=X, pady=5)
        Label(outline_width_frame, text="描边宽度:", bg='white', width=15, anchor='w').pack(side=LEFT)
        self.outline_width = IntVar(value=3)
        Scale(outline_width_frame, from_=0, to=10, orient=HORIZONTAL, variable=self.outline_width).pack(side=LEFT, fill=X, expand=True, padx=10)
        
        # 描边颜色
        outline_color_frame = Frame(outline_frame, bg='white')
        outline_color_frame.pack(fill=X, pady=5)
        Label(outline_color_frame, text="描边颜色:", bg='white', width=15, anchor='w').pack(side=LEFT)
        self.outline_color = StringVar(value="#000000")
        self.outline_color_btn = Button(outline_color_frame, text="选择颜色", bg=self.outline_color.get(),
                                       command=lambda: self.choose_color(self.outline_color, self.outline_color_btn))
        self.outline_color_btn.pack(side=LEFT, padx=10)
        # 假设 self.font_color 已经是 "#FFFFFF" 这样的值
        # 位置设置
        position_frame = LabelFrame(parent, text="位置设置", padx=10, pady=10, bg='white')
        position_frame.pack(fill=X, pady=(0, 10))
        
        # 底部边距
        margin_frame = Frame(position_frame, bg='white')
        margin_frame.pack(fill=X, pady=5)
        Label(margin_frame, text="底部边距:", bg='white', width=15, anchor='w').pack(side=LEFT)
        self.margin_bottom = IntVar(value=50)
        Scale(margin_frame, from_=0, to=200, orient=HORIZONTAL, variable=self.margin_bottom).pack(side=LEFT, fill=X, expand=True, padx=10)
        
        # 特效设置
        effect_frame = LabelFrame(parent, text="特效设置", padx=10, pady=10, bg='white')
        effect_frame.pack(fill=X, pady=(0, 10))
        
        # 淡入淡出时间
        fade_frame = Frame(effect_frame, bg='white')
        fade_frame.pack(fill=X, pady=5)
        Label(fade_frame, text="淡入时间(ms):", bg='white', width=15, anchor='w').pack(side=LEFT)
        self.fade_in = IntVar(value=500)
        Scale(fade_frame, from_=0, to=2000, orient=HORIZONTAL, variable=self.fade_in).pack(side=LEFT, fill=X, expand=True, padx=10)
        
        fade_out_frame = Frame(effect_frame, bg='white')
        fade_out_frame.pack(fill=X, pady=5)
        Label(fade_out_frame, text="淡出时间(ms):", bg='white', width=15, anchor='w').pack(side=LEFT)
        self.fade_out = IntVar(value=500)
        Scale(fade_out_frame, from_=0, to=2000, orient=HORIZONTAL, variable=self.fade_out).pack(side=LEFT, fill=X, expand=True, padx=10)
        
        # 背景设置
        bg_frame = LabelFrame(parent, text="背景设置", padx=10, pady=10, bg='white')
        bg_frame.pack(fill=X, pady=(0, 10))
        
        # 背景颜色（无背景图片时使用）
        bg_color_frame = Frame(bg_frame, bg='white')
        bg_color_frame.pack(fill=X, pady=5)
        Label(bg_color_frame, text="背景颜色:", bg='white', width=15, anchor='w').pack(side=LEFT)
        self.bg_color = StringVar(value="#000000")
        self.bg_color_btn = Button(bg_color_frame, text="选择颜色", bg=self.bg_color.get(),
                                  command=lambda: self.choose_color(self.bg_color, self.bg_color_btn))
        self.bg_color_btn.pack(side=LEFT, padx=10)
        # 假设 self.font_color 已经是 "#FFFFFF" 这样的值
        
        # 视频尺寸
        size_frame = LabelFrame(parent, text="视频尺寸", padx=10, pady=10, bg='white')
        size_frame.pack(fill=X)
        
        resolution_frame = Frame(size_frame, bg='white')
        resolution_frame.pack(fill=X, pady=5)
        Label(resolution_frame, text="分辨率:", bg='white', width=15, anchor='w').pack(side=LEFT)
        self.resolution = StringVar(value="1920x1080")
        ttk.Combobox(resolution_frame, textvariable=self.resolution, 
                    values=["1920x1080", "1280x720", "1024x768", "800x600"], 
                    state="readonly").pack(side=LEFT, padx=10)
        
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
                self.file_tree.insert('', 'end', values=(audio_file.name, lrc_file.name))
            
            # 显示缺少歌词的文件
            for audio_file in missing_files:
                self.file_tree.insert('', 'end', values=(audio_file.name, "未找到匹配的歌词文件"), tags=('missing',))
            
            self.file_tree.tag_configure('missing', background='#ffcccc')
            self.log(f"扫描完成：找到 {len(file_pairs)} 个有效的音频-歌词配对，{len(missing_files)} 个文件缺少歌词")
            
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
            'shadow_offset': 2
        }
        
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
            config = self.get_config()
            success_count = 0
            
            for i, (audio_path, lrc_path) in enumerate(self.file_pairs):
                if self.video_generator.stop_flag:
                    self.log("❌ 批量生成已停止")
                    break
                
                # 更新当前处理的文件
                self.current_file_var.set(audio_path.name)
                self.update_total_progress(i, len(self.file_pairs))
                
                output_path = self.output_dir / f"{audio_path.stem}.mp4"
                
                try:
                    # 检查是否有同名背景图片
                    bg_image_path = None
                    for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                        bg_file = audio_path.parent / f"{audio_path.stem}{ext}"
                        if bg_file.exists():
                            bg_image_path = bg_file
                            break
                    
                    success, result = self.video_generator.generate_video(audio_path, lrc_path, config, bg_image_path, output_path)
                    if success:
                        self.log(f"✅ [{i+1}/{len(self.file_pairs)}] {audio_path.name} 生成成功")
                        success_count += 1
                    else:
                        self.log(f"❌ [{i+1}/{len(self.file_pairs)}] {audio_path.name} 11生成失败：{result}")
                        
                except Exception as e:
                    self.log(f"❌ [{i+1}/{len(self.file_pairs)}] {audio_path.name} 处理异常：{str(e)}")
            
            # 完成后更新UI
            self.update_total_progress(len(self.file_pairs), len(self.file_pairs))
            if not self.video_generator.stop_flag:
                self.status_var.set(f"批量生成完成：成功 {success_count}/{len(self.file_pairs)}")
                messagebox.showinfo("完成", f"批量生成完成！\n成功：{success_count}\n总计：{len(self.file_pairs)}")
            
            self.batch_generate_btn.config(state=NORMAL)
            self.stop_btn.config(state=DISABLED)
            self.current_file_var.set("无")
            
        threading.Thread(target=batch_generate, daemon=True).start()
        
    def stop_generation(self):
        self.video_generator.set_stop_flag(True)
        self.stop_btn.config(state=DISABLED)
        self.status_var.set("正在停止...")