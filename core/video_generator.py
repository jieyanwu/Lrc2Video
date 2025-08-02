#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频生成核心功能
"""

import subprocess
from pathlib import Path
import pysubs2
from utils.file_utils import parse_lrc_manually, extract_cover_image, get_audio_duration

class VideoGenerator:
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback
        self.stop_flag = False
    
    def set_stop_flag(self, stop=True):
        """设置停止标志"""
        self.stop_flag = stop
    
    def update_progress(self, current, total, message=""):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback(current, total, message)
    
    def hex_to_ass_color(self, hex_color):
        """将十六进制颜色转换为ASS颜色格式"""
        hex_color = hex_color.lstrip('#')
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return (b << 16) | (g << 8) | r
    
    def apply_subtitle_style(self, subs, config):
        """应用字幕样式"""
        # 获取默认样式，如果不存在则创建
        if 'Default' not in subs.styles:
            subs.styles['Default'] = pysubs2.SSAStyle()
        
        style = subs.styles['Default']
        
        # 设置字体和大小
        style.fontname = config.get('font_family', 'Arial')
        style.fontsize = config.get('font_size', 36)
        
        # 设置对齐方式（中心对齐）
        style.alignment = 2  # 底部中心对齐
        
        # 设置边距
        style.marginv = config.get('margin_bottom', 50)  # 底部边距
        style.marginl = config.get('margin_left', 10)
        style.marginr = config.get('margin_right', 10)
        
        # 设置描边和阴影
        style.outline = config.get('outline_width', 3)
        style.shadow = config.get('shadow_offset', 2)
        
        # 设置字体样式
        style.bold = -1 if config.get('bold', True) else 0
        style.italic = -1 if config.get('italic', False) else 0
        
        # 设置颜色
        style.primarycolour = self.hex_to_ass_color(config.get('font_color', '#FFFFFF'))
        style.outlinecolour = self.hex_to_ass_color(config.get('outline_color', '#000000'))
        style.backcolour = self.hex_to_ass_color(config.get('shadow_color', '#000000'))
        
        # 为每个字幕事件添加特效
        for event in subs:
            # 添加淡入淡出效果和对齐方式
            fade_in = config.get('fade_in', 500)
            fade_out = config.get('fade_out', 500)
            event.text = f"{{\\an2\\fad({fade_in},{fade_out})}}" + event.text
    
    def generate_video(self, audio_path, lrc_path, config, bg_image_path=None, output_path=None):
        """生成单个视频"""
        try:
            if self.stop_flag:
                return False, "操作已取消"
                
            if output_path is None:
                output_path = Path(f"{Path(audio_path).stem}.mp4")
            
            self.update_progress(0, 100, "解析歌词文件...")
            
            # 解析歌词文件
            try:
                subs = pysubs2.load(str(lrc_path), format_='lrc', encoding='utf-8')
            except:
                try:
                    subs = parse_lrc_manually(lrc_path)
                except Exception as e:
                    return False, f"LRC文件解析失败: {str(e)}"
            
            if not subs:
                return False, "LRC文件中没有找到有效的歌词"
            
            if self.stop_flag:
                return False, "操作已取消"
            
            self.update_progress(20, 100, "应用字幕样式...")
            
            # 应用字幕样式
            self.apply_subtitle_style(subs, config)
            
            # 保存字幕文件
            ass_path = Path('temp_sub.ass')
            subs.save(str(ass_path), encoding='utf-8')
            
            if self.stop_flag:
                return False, "操作已取消"
            
            self.update_progress(40, 100, "获取音频信息...")
            
            # 获取音频时长和码率
            duration = get_audio_duration(audio_path)
            audio_bitrate = self.get_audio_bitrate(audio_path)
            
            if self.stop_flag:
                return False, "操作已取消"
            
            self.update_progress(50, 100, "处理背景图片...")
            
            # 尝试从音频文件提取封面
            if not bg_image_path:
                cover_path = Path('temp_cover.jpg')
                if extract_cover_image(audio_path, cover_path):
                    bg_image_path = cover_path
            
            if self.stop_flag:
                return False, "操作已取消"
            
            self.update_progress(60, 100, "生成视频...")
            
            # 生成FFmpeg命令
            cmd = self.build_ffmpeg_command(audio_path, bg_image_path, config, duration, audio_bitrate, ass_path, output_path)
            
            # 执行FFmpeg命令
            # process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        encoding='utf-8',  # ✅ 关键
                        errors='replace'   # 可选：防止极端字符导致崩溃
                    )
            
            # 监控FFmpeg进度
            while True:
                if self.stop_flag:
                    process.terminate()
                    return False, "操作已取消"
                
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                
                if output:
                    # 解析FFmpeg进度输出
                    progress = self.parse_ffmpeg_progress(output, duration)
                    if progress is not None:
                        self.update_progress(60 + int(progress * 0.35), 100, f"生成视频... {progress:.1f}%")
            
            if process.returncode != 0:
                error_output = process.stderr.read()
                return False, f"FFmpeg错误: {error_output}"
            
            self.update_progress(95, 100, "清理临时文件...")
            
            # 清理临时文件
            self.cleanup_temp_files(ass_path)
            
            self.update_progress(100, 100, "完成")
            
            return True, str(output_path.absolute())
            
        except Exception as e:
            # 清理临时文件
            self.cleanup_temp_files(Path('temp_sub.ass'))
            return False, f"生成失败: {str(e)}"
    
    def get_audio_bitrate(self, audio_path):
        """获取音频码率"""
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'error', '-select_streams', 'a:0',
                '-show_entries', 'stream=bit_rate', '-of', 'csv=p=0', str(audio_path)
            ], capture_output=True, text=True)
            bitrate = int(result.stdout.strip())
            return f"{bitrate//1000}k"
        except:
            return "192k"  # 默认码率
    
    def build_ffmpeg_command(self, audio_path, bg_image_path, config, duration, audio_bitrate, ass_path, output_path):
        """构建FFmpeg命令"""
        if bg_image_path and Path(bg_image_path).exists():
            # 有背景图片的情况
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1', '-i', str(bg_image_path),
                '-i', str(audio_path),
                '-filter_complex', 
                f'[0:v]scale={config.get("width",1920)}:{config.get("height",1080)}:force_original_aspect_ratio=increase,crop={config.get("width",1920)}:{config.get("height",1080)},subtitles={ass_path}[v]',
                '-map', '[v]', '-map', '1:a',
                '-c:v', 'libx264', '-preset', 'medium',
                '-c:a', 'copy',  # 保持原音频码率
                '-t', str(duration),
                '-shortest',
                str(output_path)
            ]
        else:
            # 纯色背景的情况
            bg_color = config.get('background_color', '#000000').lstrip('#')
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'color=c={bg_color}:s={config.get("width", 1920)}x{config.get("height", 1080)}:r=25',
                '-i', str(audio_path),
                '-filter_complex', f'[0:v]subtitles={ass_path}[v]',
                '-map', '[v]', '-map', '1:a',
                '-c:v', 'libx264', '-preset', 'medium',
                '-c:a', 'copy',  # 保持原音频码率
                '-t', str(duration),
                '-shortest',
                str(output_path)
            ]
        
        return cmd
    
    def parse_ffmpeg_progress(self, output_line, total_duration):
        """解析FFmpeg进度输出"""
        import re
        # 匹配时间格式 time=00:01:23.45
        time_match = re.search(r'time=(\d{2}):(\d{2}):(\d{2}\.\d{2})', output_line)
        if time_match:
            h, m, s = time_match.groups()
            current_time = int(h) * 3600 + int(m) * 60 + float(s)
            if total_duration > 0:
                return (current_time / total_duration) * 100
        return None
    
    def cleanup_temp_files(self, ass_path):
        """清理临时文件"""
        try:
            if ass_path.exists(): 
                ass_path.unlink()
            temp_cover = Path('temp_cover.jpg')
            if temp_cover.exists():
                temp_cover.unlink()
        except:
            pass