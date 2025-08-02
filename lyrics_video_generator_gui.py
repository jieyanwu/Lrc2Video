#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tkinter桌面版 - 歌词视频生成器（支持文件夹批量导入）
"""

import os
import subprocess
import re
import json
import threading
from pathlib import Path
from tkinter import *
from tkinter import ttk, filedialog, messagebox, colorchooser
from tkinter.scrolledtext import ScrolledText
import pysubs2

class LyricsVideoGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 歌词视频生成器")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f2f5')
        
        # 存储文件列表
        self.file_pairs = []  # [(audio_path, lrc_path), ...]
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        self.setup_ui()
        
    def setup_ui(self):
        # 主框架
        main_frame = Frame(self.root, bg='#f0f2f5', padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # 标题
        title_label = Label(main_frame, text="🎵 歌词视频生成器", 
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
        
        self.setup_file_page(file_frame)
        self.setup_style_page(style_frame)
        self.setup_batch_page(batch_frame)
        
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
        
        # 进度显示
        progress_frame = LabelFrame(parent, text="处理进度", padx=10, pady=10, bg='white')
        progress_frame.pack(fill=BOTH, expand=True)
        
        self.progress_var = StringVar(value="准备就绪")
        progress_label = Label(progress_frame, textvariable=self.progress_var, bg='white', font=("Arial", 10))
        progress_label.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill=X, pady=5)
        
        # 日志显示
        self.log_text = ScrolledText(progress_frame, height=15, wrap=WORD)
        self.log_text.pack(fill=BOTH, expand=True, pady=10)
        
        self.stop_flag = False
        
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
            
        folder = Path(folder_path)
        if not folder.exists():
            messagebox.showerror("错误", "文件夹不存在")
            return
            
        # 清空现有列表
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        self.file_pairs.clear()
        
        # 查找音频文件
        audio_extensions = {'.mp3', '.flac', '.wav', '.m4a', '.aac'}
        audio_files = {}
        
        for file in folder.rglob('*'):
            if file.suffix.lower() in audio_extensions:
                name = file.stem
                audio_files[name] = file
                
        # 查找对应的歌词文件
        for name, audio_file in audio_files.items():
            lrc_file = None
            # 在同一目录查找
            potential_lrc = audio_file.parent / f"{name}.lrc"
            if potential_lrc.exists():
                lrc_file = potential_lrc
            else:
                # 在整个文件夹查找
                for lrc in folder.rglob(f"{name}.lrc"):
                    lrc_file = lrc
                    break
                    
            if lrc_file:
                self.file_pairs.append((audio_file, lrc_file))
                self.file_tree.insert('', 'end', values=(audio_file.name, lrc_file.name))
            else:
                self.file_tree.insert('', 'end', values=(audio_file.name, "未找到匹配的歌词文件"), tags=('missing',))
                
        self.file_tree.tag_configure('missing', background='#ffcccc')
        self.log(f"扫描完成：找到 {len(self.file_pairs)} 个有效的音频-歌词配对")
        
    def get_config(self):
        width, height = self.resolution.get().split('x')
        return {
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
            'shadow_offset': 2
        }
        
    def log(self, message):
        self.log_text.insert(END, f"{message}\n")
        self.log_text.see(END)
        self.root.update_idletasks()
        
    def generate_single_video(self):
        audio_path = self.audio_var.get()
        lrc_path = self.lrc_var.get()
        
        if not audio_path or not lrc_path:
            messagebox.showwarning("警告", "请选择音频和歌词文件")
            return
            
        bg_image_path = self.bg_var.get() if self.bg_var.get() else None
        config = self.get_config()
        output_path = self.output_dir / f"{Path(audio_path).stem}.mp4"
        
        self.single_generate_btn.config(state=DISABLED)
        self.progress_var.set("正在生成视频...")
        
        def generate():
            try:
                success, result = self.generate_video(audio_path, lrc_path, config, bg_image_path, output_path)
                if success:
                    self.log(f"✅ 视频生成成功：{result}")
                    self.progress_var.set("生成完成")
                    messagebox.showinfo("成功", f"视频已保存到：{result}")
                else:
                    self.log(f"❌ 生成失败：{result}")
                    self.progress_var.set("生成失败")
                    messagebox.showerror("错误", f"生成失败：{result}")
            finally:
                self.single_generate_btn.config(state=NORMAL)
                
        threading.Thread(target=generate, daemon=True).start()
        
    def start_batch_generation(self):
        if not self.file_pairs:
            messagebox.showwarning("警告", "没有找到有效的文件配对，请先扫描文件夹")
            return
            
        self.stop_flag = False
        self.batch_generate_btn.config(state=DISABLED)
        self.stop_btn.config(state=NORMAL)
        self.progress_bar['maximum'] = len(self.file_pairs)
        self.progress_bar['value'] = 0
        
        def batch_generate():
            config = self.get_config()
            success_count = 0
            
            for i, (audio_path, lrc_path) in enumerate(self.file_pairs):
                if self.stop_flag:
                    self.log("❌ 批量生成已停止")
                    break
                    
                self.progress_var.set(f"正在处理 {i+1}/{len(self.file_pairs)}: {audio_path.name}")
                self.progress_bar['value'] = i
                
                output_path = self.output_dir / f"{audio_path.stem}.mp4"
                
                try:
                    # 检查是否有同名背景图片
                    bg_image_path = None
                    for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                        bg_file = audio_path.parent / f"{audio_path.stem}{ext}"
                        if bg_file.exists():
                            bg_image_path = bg_file
                            break
                    
                    success, result = self.generate_video(audio_path, lrc_path, config, bg_image_path, output_path)
                    if success:
                        self.log(f"✅ [{i+1}/{len(self.file_pairs)}] {audio_path.name} 生成成功")
                        success_count += 1
                    else:
                        self.log(f"❌ [{i+1}/{len(self.file_pairs)}] {audio_path.name} 生成失败：{result}")
                except Exception as e:
                    self.log(f"❌ [{i+1}/{len(self.file_pairs)}] {audio_path.name} 处理异常：{str(e)}")
                    
            self.progress_bar['value'] = len(self.file_pairs)
            if not self.stop_flag:
                self.progress_var.set(f"批量生成完成：成功 {success_count}/{len(self.file_pairs)}")
                messagebox.showinfo("完成", f"批量生成完成！\n成功：{success_count}\n总计：{len(self.file_pairs)}")
            
            self.batch_generate_btn.config(state=NORMAL)
            self.stop_btn.config(state=DISABLED)
            
        threading.Thread(target=batch_generate, daemon=True).start()
        
    def stop_generation(self):
        self.stop_flag = True
        self.stop_btn.config(state=DISABLED)
        
    def parse_lrc_manually(self, lrc_path):
        try:
            with open(lrc_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            for enc in ['gbk', 'gb2312', 'latin-1', 'cp1252']:
                try:
                    with open(lrc_path, 'r', encoding=enc) as f:
                        content = f.read()
                    break
                except: 
                    continue
            else:
                raise ValueError("无法识别 LRC 文件编码")

        subs = pysubs2.SSAFile()
        time_pattern = r'\[(\d{1,2}):(\d{1,2})(?:\.(\d{1,3}))?\]'
        for line in content.splitlines():
            matches = list(re.finditer(time_pattern, line))
            text = re.sub(time_pattern, '', line).strip()
            if matches and text:
                for match in matches:
                    m, s, cs = int(match[1]), int(match[2]), int(match[3] or 0)
                    start_ms = (m * 60 + s) * 1000 + cs * 10
                    subs.append(pysubs2.SSAEvent(start=start_ms, end=start_ms + 3000, text=text))
        
        for i in range(len(subs)-1): 
            subs[i].end = subs[i+1].start
        if subs: 
            subs[-1].end = subs[-1].start + 3000
        return subs

    def extract_cover_image(self, audio_path, cover_path):
        try:
            cmd = ['ffmpeg', '-y', '-i', str(audio_path), '-an', '-vcodec', 'copy', str(cover_path)]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return cover_path.exists()
        except:
            return False

    def generate_video(self, audio_path, lrc_path, config, bg_image_path=None, output_path=None):
        try:
            if output_path is None:
                output_path = Path(f"{Path(audio_path).stem}.mp4")
            
            # 解析歌词文件
            try:
                subs = pysubs2.load(str(lrc_path), format_='lrc', encoding='utf-8')
            except:
                subs = self.parse_lrc_manually(lrc_path)
            
            if not subs:
                return False, "LRC文件中没有找到有效的歌词"

            # 设置字幕样式
            style = subs.styles['Default']
            style.fontname = config.get('font_family', '猫啃网风雅宋')
            style.fontsize = config.get('font_size', 36)
            style.alignment = 5  # 中心对齐
            style.marginv = 0
            style.marginl = config.get('margin_left', 10)
            style.marginr = config.get('margin_right', 10)
            style.outline = config.get('outline_width', 3)
            style.shadow = config.get('shadow_offset', 2)
            style.bold = -1 if config.get('bold', True) else 0
            style.italic = -1 if config.get('italic', False) else 0

            def hex_to_ass_color(hex_color):
                hex_color = hex_color.lstrip('#')
                r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                return (b << 16) | (g << 8) | r

            style.primarycolour = hex_to_ass_color(config.get('font_color', '#FFFFFF'))
            style.outlinecolour = hex_to_ass_color(config.get('outline_color', '#000000'))

            # 添加淡入淡出效果
            for event in subs:
                event.text = "{\\an5\\fad(500,500)}" + event.text

            # 保存字幕文件
            ass_path = Path('temp_sub.ass')
            subs.save(str(ass_path))

            # 获取音频时长
            duration = 300
            try:
                result = subprocess.run([
                    'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1', str(audio_path)
                ], capture_output=True, text=True)
                duration = float(result.stdout.strip())
            except: 
                pass

            # 尝试从音频文件提取封面
            if not bg_image_path:
                cover_path = Path('temp_cover.jpg')
                if self.extract_cover_image(audio_path, cover_path):
                    bg_image_path = cover_path

            # 生成FFmpeg命令
            if bg_image_path and Path(bg_image_path).exists():
                cmd = [
                    'ffmpeg', '-loop', '1', '-i', str(bg_image_path), '-i', str(audio_path),
                    '-filter_complex', f'[0:v]scale={config.get("width",1920)}:{config.get("height",1080)},subtitles=temp_sub.ass[v]',
                    '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-t', str(duration),
                    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-y', str(output_path)
                ]
            else:
                bg_color = config.get('background_color', '#000000').lstrip('#')
                cmd = [
                    'ffmpeg', '-f', 'lavfi',
                    '-i', f'color=c={bg_color}:s={config.get("width", 1920)}x{config.get("height", 1080)}:r=25',
                    '-i', str(audio_path),
                    '-filter_complex', f'[0:v]subtitles=temp_sub.ass[v]',
                    '-map', '[v]', '-map', '1:a',
                    '-c:v', 'libx264', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-y',
                    str(output_path)
                ]

            # 执行FFmpeg命令
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # 清理临时文件
            if ass_path.exists(): 
                ass_path.unlink()
            temp_cover = Path('temp_cover.jpg')
            if temp_cover.exists():
                temp_cover.unlink()
                
            return True, str(output_path.absolute())

        except subprocess.CalledProcessError as e:
            return False, f"FFmpeg错误: {e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)}"
        except Exception as e:
            return False, str(e)

def main():
    root = Tk()
    app = LyricsVideoGenerator(root)
    
    # 设置窗口图标和样式
    try:
        root.iconbitmap(default='icon.ico')  # 如果有图标文件
    except:
        pass
    
    # 优雅退出处理
    def on_closing():
        if messagebox.askokcancel("退出", "确定要退出程序吗？"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == '__main__':
    main()