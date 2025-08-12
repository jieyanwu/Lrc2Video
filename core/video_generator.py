#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频生成核心功能
"""

import os
import logging
import subprocess
from pathlib import Path
import pysubs2
from utils.file_utils import parse_lrc_manually, extract_cover_image, get_audio_duration
from utils.ai_title_generator import generate_video_title

logger = logging.getLogger(__name__)

class VideoGenerator:
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback
        self.stop_flag = False
        self.current_process = None
        logger.info("🎬 视频生成器初始化完成")
    
    def set_stop_flag(self, stop=True):
        """设置停止标志"""
        self.stop_flag = stop
        if stop and self.current_process:
            self.terminate_ffmpeg_process()
    
    def update_progress(self, current, total, message=""):
        """更新进度 - 带调试"""
        if self.progress_callback:
            self.progress_callback(current, total, message)
        # 只在重要节点记录INFO日志，减少DEBUG噪音
        if current in [0, 20, 40, 60, 80, 100] or current % 10 == 0:
            logger.info(f"进度: {current}% - {message}")
        else:
            logger.debug(f"进度: {current}% - {message}")
            

    def hex_to_ass_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        # ASS颜色格式是BGR顺序的十六进制整数，包含透明度(FF)
        color_int = int(f"00{b:02x}{g:02x}{r:02x}", 16)
        print(f"原始颜色: {hex_color}, 转换后: {color_int} (&H00{b:02x}{g:02x}{r:02x})")  # 调试日志
        return color_int

    def apply_subtitle_style(self, subs, config):
        print(f"接收到的颜色配置: {config.get('font_color')}")  # 调试日志
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
        style.primarycolor = self.hex_to_ass_color(config.get('font_color', '#FFFFFF'))
        style.outlinecolor = self.hex_to_ass_color(config.get('outline_color', '#000000'))
        style.backcolor = self.hex_to_ass_color(config.get('shadow_color', '#000000'))
        
        # 为每个字幕事件添加特效
        for event in subs:
            # 添加淡入淡出效果和对齐方式
            fade_in = config.get('fade_in', 500)
            fade_out = config.get('fade_out', 500)
            event.text = f"{{\\an2\\fad({fade_in},{fade_out})}}" + event.text
    
    def generate_video(self, audio_path, lrc_path, config, bg_image_path=None, output_path=None, use_ai_title=True):
        """生成单个视频 - 带详细调试"""
        logger.info(f"🎬 开始生成视频: {audio_path}")
        logger.info(f"📄 歌词文件: {lrc_path}")
        logger.info(f"🎨 配置: {config}")
        logger.info(f"🖼️  背景图片: {bg_image_path}")
        logger.info(f"📁 输出路径: {output_path}")
        
        try:
            if self.stop_flag:
                return False, "操作已取消"
                
            # 检查文件存在性
            if not os.path.exists(audio_path):
                logger.error(f"❌ 音频文件不存在: {audio_path}")
                return False, f"音频文件不存在: {audio_path}"
            
            if not os.path.exists(lrc_path):
                logger.error(f"❌ 歌词文件不存在: {lrc_path}")
                return False, f"歌词文件不存在: {lrc_path}"
                
            logger.info("✅ 文件检查通过")
                
            # 生成AI标题
            song_name = Path(audio_path).stem
            artist = config.get('artist', None)
            
            if use_ai_title:
                print("🤖 AI标题生成中...")
                from utils.ai_title_generator import generate_video_title
                ai_title = generate_video_title(song_name, artist, use_ai=True)
                if ai_title and ai_title.strip():
                    print(f"✅ AI标题: {ai_title}")
                    final_title = ai_title
                else:
                    print("⚠️ AI生成失败，使用默认标题")
                    final_title = f"{artist} - {song_name}" if artist else f"{song_name} - 音乐MV"
            else:
                final_title = f"{artist} - {song_name}" if artist else f"{song_name} - 音乐MV"
                print(f"📄 默认标题: {final_title}")
            
            if output_path is None:
                # 使用AI生成的标题作为输出文件名
                safe_title = "".join(c for c in final_title if c.isalnum() or c in (' ', '-', '_', '.', '《', '》', '【', '】', '（', '）', '！', '？', '~')).rstrip()
                output_path = Path(f"{safe_title}.mp4")
            
            self.update_progress(0, 100, "解析歌词文件...")
            # 简化日志输出
            print(f"📄 解析歌词: {Path(lrc_path).name}")
            
            # 解析歌词文件
            try:
                subs = pysubs2.load(str(lrc_path), format_='lrc', encoding='utf-8')
            except:
                try:
                    subs = parse_lrc_manually(lrc_path)
                except Exception as e:
                    logger.error(f"💥 LRC文件解析失败: {e}")
                    return False, f"LRC文件解析失败: {str(e)}"
            
            if not subs:
                logger.error("💥 LRC文件中没有找到有效的歌词")
                return False, "LRC文件中没有找到有效的歌词"
                
            print(f"✅ 歌词: {len(subs)}行")
            
            if self.stop_flag:
                return False, "操作已取消"
            
            self.update_progress(20, 100, "应用字幕样式...")
            logger.info("🎨 应用字幕样式...")
            
            # 应用字幕样式
            self.apply_subtitle_style(subs, config)
            
            # 保存字幕文件 - 使用音频文件名作为临时文件名，保存到temp目录
            audio_name = Path(audio_path).stem
            temp_dir = Path('temp')
            temp_dir.mkdir(exist_ok=True)
            ass_path = temp_dir / f'temp_{audio_name}_ass.ass'
            subs.save(str(ass_path), encoding='utf-8')
            logger.info(f"✅ 字幕样式应用完成，临时文件: {ass_path}")
            
            if self.stop_flag:
                return False, "操作已取消"
            
            self.update_progress(40, 100, "获取音频信息...")
            logger.info("⏱️  获取音频信息...")
            
            # 获取音频时长和码率
            duration = get_audio_duration(audio_path)
            audio_bitrate = self.get_audio_bitrate(audio_path)
            logger.info(f"✅ 音频时长: {duration:.2f}s, 码率: {audio_bitrate}")
            
            if self.stop_flag:
                return False, "操作已取消"
            
            self.update_progress(50, 100, "处理背景图片...")
            
            # 尝试从音频文件提取封面 - 使用音频文件名作为临时文件名，保存到temp目录
            if not bg_image_path:
                audio_name = Path(audio_path).stem
                temp_dir = Path('temp')
                temp_dir.mkdir(exist_ok=True)
                cover_path = temp_dir / f'temp_{audio_name}_pic.jpg'
                if extract_cover_image(audio_path, cover_path):
                    bg_image_path = cover_path
                    print(f"🖼️ 封面: {cover_path.name}")
                else:
                    print("🎨 纯色背景")
            else:
                print(f"🖼️ 背景: {Path(bg_image_path).name}")
            
            if self.stop_flag:
                return False, "操作已取消"
            
            self.update_progress(60, 100, "生成视频...")
            
            # 生成FFmpeg命令
            cmd = self.build_ffmpeg_command(audio_path, bg_image_path, config, duration, audio_bitrate, ass_path, output_path)
            print(f"🎬 生成: {output_path.name}")
            
            # 执行FFmpeg命令
            self.current_process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        encoding='utf-8',
                        errors='replace'
                    )
            
            # 实时进度监控 - 简化为单行输出
            logger.info("🎬 FFmpeg处理中...")
            last_logged_progress = -1
            start_time = None
            
            while True:
                if self.stop_flag:
                    logger.warning("⚠️  用户取消操作")
                    self.terminate_ffmpeg_process()
                    return False, "操作已取消"
                
                output = self.current_process.stderr.readline()
                if output == '' and self.current_process.poll() is not None:
                    break
                
                if output and 'time=' in output:
                    progress = self.parse_ffmpeg_progress(output, duration)
                    if progress is not None:
                        current_step = int(60 + (progress * 0.35))
                        # 每10%记录一次，使用单行更新
                        rounded_progress = int(progress // 10) * 10
                        if rounded_progress != last_logged_progress and rounded_progress % 10 == 0:
                            self.update_progress(current_step, 100, f"视频生成中... {rounded_progress}%")
                            # 使用回车符在同一行更新进度
                            print(f"\r🎬 视频进度: {rounded_progress}% [{'█' * (rounded_progress//10)}{'░' * (10-rounded_progress//10)}]", end="", flush=True)
                            last_logged_progress = rounded_progress
                        else:
                            self.update_progress(current_step, 100, f"视频生成中... {progress:.1f}%")
                            # 只在文件中记录详细进度，不输出到控制台
                            logger.debug(f"FFmpeg详细进度: {progress:.1f}%")
            
            # 完成后的换行
            print()  # 换行
            
            if self.current_process.returncode != 0:
                error_output = self.current_process.stderr.read()
                logger.error(f"💥 FFmpeg错误: {error_output}")
                return False, f"FFmpeg错误: {error_output}"
            
            print(f"✅ 完成: {output_path.name}")
            
            # 清理进程引用
            self.current_process = None
            
            # 清理临时文件
            self.cleanup_temp_files(ass_path)
            
            self.update_progress(100, 100, "完成")
            return True, str(output_path.absolute())
            
        except Exception as e:
            logger.error(f"💥 视频生成失败: {e}", exc_info=True)
            # 清理临时文件
            audio_name = Path(audio_path).stem
            temp_dir = Path('temp')
            temp_ass_path = temp_dir / f'temp_{audio_name}_ass.ass'
            self.cleanup_temp_files(temp_ass_path)
            return False, f"生成失败: {str(e)}"
            
    def parse_lrc(self, lrc_path):
        """解析LRC文件（用于调试日志）"""
        try:
            subs = pysubs2.load(str(lrc_path), format_='lrc', encoding='utf-8')
            return [(line.start, line.end, line.text) for line in subs]
        except:
            return parse_lrc_manually(lrc_path)
    
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
        # 获取优化配置
        preset = config.get('preset', 'medium')
        tune = config.get('tune', 'film')
        crf = config.get('crf', 23)
        hwaccel = config.get('hwaccel', 'none')
        thread_count = config.get('thread_count', 0)  # 0表示自动
        
        # 基础命令
        cmd = ['ffmpeg', '-y']
        
        # 添加线程配置（仅软件编码有效）
        if hwaccel == 'none' and thread_count > 0:
            cmd.extend(['-threads', str(thread_count)])
        
        if bg_image_path and Path(bg_image_path).exists():
            # 有背景图片的情况
            # 处理字幕路径中的反斜杠问题
            subtitles_path = str(ass_path).replace('\\', '/')
            cmd.extend([
                '-loop', '1', '-i', str(bg_image_path),
                '-i', str(audio_path),
                '-filter_complex', 
                f'[0:v]scale={config.get("width",1920)}:{config.get("height",1080)}:force_original_aspect_ratio=increase,crop={config.get("width",1920)}:{config.get("height",1080)},subtitles={subtitles_path}[v]',
                '-map', '[v]', '-map', '1:a',
                '-c:a', 'copy',
                '-t', str(duration),
                '-shortest'
            ])
        else:
            # 纯色背景的情况
            bg_color = config.get('background_color', '#000000').lstrip('#')
            # 处理字幕路径中的反斜杠问题
            subtitles_path = str(ass_path).replace('\\', '/')
            cmd.extend([
                '-f', 'lavfi',
                '-i', f'color=c={bg_color}:s={config.get("width", 1920)}x{config.get("height", 1080)}:r=25',
                '-i', str(audio_path),
                '-filter_complex', f'[0:v]subtitles={subtitles_path}[v]',
                '-map', '[v]', '-map', '1:a',
                '-c:a', 'copy',
                '-t', str(duration),
                '-shortest'
            ])
        
        # 根据硬件加速类型配置编码器
        if hwaccel == 'nvenc':
            # NVIDIA NVENC
            nvenc_preset = 'fast' if preset in ['ultrafast', 'superfast', 'veryfast', 'faster'] else 'slow'
            cmd.extend(['-c:v', 'h264_nvenc', '-preset', nvenc_preset])
            
        elif hwaccel == 'qsv':
            # Intel Quick Sync Video
            qsv_preset = 'veryfast' if preset in ['ultrafast', 'superfast', 'veryfast'] else 'medium'
            cmd.extend(['-c:v', 'h264_qsv', '-preset', qsv_preset])
            
        elif hwaccel == 'amf':
            # AMD AMF
            amf_usage = 'lowlatency' if preset in ['ultrafast', 'superfast', 'veryfast'] else 'balanced'
            cmd.extend(['-c:v', 'h264_amf', '-usage', amf_usage])
            
        elif hwaccel == 'videotoolbox':
            # macOS VideoToolbox
            cmd.extend(['-c:v', 'h264_videotoolbox', '-allow_sw', '1'])
            
        else:
            # 软件编码 (libx264)
            cmd.extend(['-c:v', 'libx264', '-preset', preset, '-tune', tune, '-crf', str(crf)])
        
        # 添加输出路径
        cmd.append(str(output_path))
        
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
            # 清理指定路径的临时文件
            if ass_path.exists(): 
                ass_path.unlink()
            
            # 清理temp目录下的所有临时文件
            temp_dir = Path('temp')
            if temp_dir.exists():
                # 清理字幕文件
                for temp_file in temp_dir.glob('temp_*_ass.ass'):
                    if temp_file.exists():
                        temp_file.unlink()
                
                # 清理封面文件
                for temp_file in temp_dir.glob('temp_*_pic.jpg'):
                    if temp_file.exists():
                        temp_file.unlink()
                        
                # 如果temp目录为空，也删除目录
                try:
                    temp_dir.rmdir()
                except:
                    pass  # 目录不为空，保留
                    
        except Exception as e:
            logger.debug(f"清理临时文件时出错: {e}")

    def terminate_ffmpeg_process(self):
        """终止FFmpeg进程"""
        try:
            if self.current_process and self.current_process.poll() is None:
                self.current_process.terminate()
                # 等待进程终止，最多等待3秒
                try:
                    self.current_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    # 如果terminate不起作用，使用kill强制终止
                    self.current_process.kill()
                    self.current_process.wait()
                finally:
                    self.current_process = None
        except Exception as e:
            print(f"终止FFmpeg进程时出错: {e}")
            self.current_process = None

    def __del__(self):
        """析构函数，确保清理资源"""
        if self.current_process and self.current_process.poll() is None:
            self.terminate_ffmpeg_process()