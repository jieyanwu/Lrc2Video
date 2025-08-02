#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件处理工具函数
"""

import re
import subprocess
from pathlib import Path
import pysubs2
from .encoding_detector import read_text_file_safe

def parse_lrc_manually(lrc_path):
    """手动解析LRC文件"""
    try:
        # 使用安全的文件读取方法
        content, encoding = read_text_file_safe(lrc_path)
        print(f"LRC文件编码: {encoding}")
    except Exception as e:
        raise ValueError(f"无法读取LRC文件: {str(e)}")
    
    if not content.strip():
        raise ValueError("LRC文件内容为空")

    # 解析LRC内容
    subs = pysubs2.SSAFile()
    time_pattern = r'\[(\d{1,2}):(\d{1,2})(?:\.(\d{1,3}))?\]'
    
    lines_processed = 0
    lines_with_time = 0
    
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
            
        lines_processed += 1
        matches = list(re.finditer(time_pattern, line))
        text = re.sub(time_pattern, '', line).strip()
        
        if matches and text:
            lines_with_time += 1
            for match in matches:
                try:
                    m, s, cs = int(match[1]), int(match[2]), int(match[3] or 0)
                    # 确保时间值在合理范围内
                    if m > 59:  # 如果分钟数过大，可能是小时:分钟格式
                        h = m // 60
                        m = m % 60
                        start_ms = (h * 3600 + m * 60 + s) * 1000 + cs * 10
                    else:
                        start_ms = (m * 60 + s) * 1000 + cs * 10
                    
                    # 创建字幕事件，默认持续3秒
                    event = pysubs2.SSAEvent(start=start_ms, end=start_ms + 3000, text=text)
                    subs.append(event)
                except (ValueError, IndexError) as e:
                    print(f"解析时间标签时出错: {match.group()} - {e}")
                    continue
    
    print(f"处理了 {lines_processed} 行，找到 {lines_with_time} 行包含时间标签")
    
    if not subs:
        raise ValueError(f"LRC文件中没有找到有效的歌词时间标签。处理了 {lines_processed} 行文本。")
    
    # 按时间排序
    subs.sort()
    
    # 调整结束时间
    for i in range(len(subs)-1): 
        if subs[i].end > subs[i+1].start:
            subs[i].end = subs[i+1].start
    
    # 最后一个字幕的结束时间
    if subs: 
        subs[-1].end = subs[-1].start + 3000
    
    print(f"成功解析 {len(subs)} 条歌词")
    return subs

def extract_cover_image(audio_path, cover_path):
    """从音频文件提取封面图片"""
    try:
        cmd = ['ffmpeg', '-y', '-i', str(audio_path), '-an', '-vcodec', 'copy', str(cover_path)]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return cover_path.exists()
    except:
        return False

def get_audio_duration(audio_path):
    """获取音频文件时长"""
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', str(audio_path)
        ], capture_output=True, text=True)
        return float(result.stdout.strip())
    except: 
        return 300  # 默认5分钟

def scan_folder_for_files(folder_path):
    """扫描文件夹中的音频和歌词文件"""
    folder = Path(folder_path)
    if not folder.exists():
        return [], "文件夹不存在"
    
    # 查找音频文件
    audio_extensions = {'.mp3', '.flac', '.wav', '.m4a', '.aac'}
    audio_files = {}
    
    for file in folder.rglob('*'):
        if file.suffix.lower() in audio_extensions:
            name = file.stem
            audio_files[name] = file
    
    # 查找对应的歌词文件
    file_pairs = []
    missing_files = []
    
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
            file_pairs.append((audio_file, lrc_file))
        else:
            missing_files.append(audio_file)
    
    return file_pairs, missing_files