"""
FFmpeg 可执行文件定位工具

优先使用项目内置的 ffmpeg，其次使用系统 PATH 中的。
将 ffmpeg 放入 <项目>/ffmpeg/bin/ 目录即可自动识别。
"""

import os
import subprocess
import sys
from pathlib import Path


def get_ffmpeg_dir() -> Path:
    """获取项目内的 ffmpeg 目录"""
    return Path(__file__).parent.parent / "ffmpeg" / "bin"


def locate_ffmpeg() -> str:
    """定位 ffmpeg 可执行文件路径"""
    exe_name = "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg"
    local_path = get_ffmpeg_dir() / exe_name
    if local_path.exists():
        return str(local_path)
    return "ffmpeg"


def locate_ffprobe() -> str:
    """定位 ffprobe 可执行文件路径"""
    exe_name = "ffprobe.exe" if sys.platform == "win32" else "ffprobe"
    local_path = get_ffmpeg_dir() / exe_name
    if local_path.exists():
        return str(local_path)
    return "ffprobe"
