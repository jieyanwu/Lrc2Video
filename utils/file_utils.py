#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件处理工具函数
"""

import re
import subprocess
from pathlib import Path
import pysubs2

def parse_lrc_manually(lrc_path):
    """手动解析LRC文件"""
    try:
        with open(lrc_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"成功使用 utf-8 读取文件: {lrc_path}")
    except UnicodeDecodeError:
        for enc in ['gbk', 'gb2312', 'latin-1', 'cp1252']:
            try:
                with open(lrc_path, 'r', encoding=enc) as f:
                    content = f.read()
                    print(f"成功使用 {enc} 读取文件: {lrc_path}")
                break
            except: 
                continue
        else:
            raise ValueError("无法识别 LRC 文件编码")

    subs = pysubs2.SSAFile()
    time_pattern = r'\[(\d{1,2}):(\d{1,2})(?:\.(\d{1,3}))?\]'
    for line in content.splitlines():
        matches = list(re.finditer(time_pattern, line))
        text   = re.sub(time_pattern, '', line).strip()
        if matches and text:
            # 只取最早的那个时间戳
            m, s, cs = map(int, matches[0].groups(default='0'))
            start_ms = (m * 60 + s) * 1000 + cs * 10
            subs.append(pysubs2.SSAEvent(start=start_ms,
                                        end=start_ms + 3000,
                                        text=text))
    # for line in content.splitlines():
    #     matches = list(re.finditer(time_pattern, line))
    #     text = re.sub(time_pattern, '', line).strip()
    #     if matches and text:
    #         for match in matches:
    #             m, s, cs = int(match[1]), int(match[2]), int(match[3] or 0)
    #             start_ms = (m * 60 + s) * 1000 + cs * 10
    #             subs.append(pysubs2.SSAEvent(start=start_ms, end=start_ms + 3000, text=text))
    
    # 调整结束时间
    for i in range(len(subs)-1): 
        subs[i].end = subs[i+1].start
    if subs: 
        subs[-1].end = subs[-1].start + 3000
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