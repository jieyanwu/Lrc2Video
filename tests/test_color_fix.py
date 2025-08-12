#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
颜色设置验证脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.video_generator import VideoGenerator
import pysubs2
from pathlib import Path

def test_color_conversion():
    """测试颜色转换功能"""
    generator = VideoGenerator()
    
    # 测试颜色转换
    test_colors = {
        '#56fb48': '绿色字体',
        '#c60005': '红色描边', 
        '#000000': '黑色阴影'
    }
    
    print("=== 颜色转换测试 ===")
    for hex_color, desc in test_colors.items():
        ass_color = generator.hex_to_ass_color(hex_color)
        print(f"{desc}: {hex_color} -> {ass_color}")
    
    # 创建测试字幕文件
    print("\n=== 测试字幕样式应用 ===")
    
    # 创建测试配置
    config = {
        'font_family': 'Microsoft YaHei',
        'font_size': 36,
        'font_color': '#56fb48',      # 绿色
        'outline_width': 4,
        'outline_color': '#c60005',   # 红色
        'background_color': '#000000',
        'bold': True,
        'italic': False,
        'width': 1920,
        'height': 1080,
        'margin_left': 10,
        'margin_right': 10,
        'margin_bottom': 50,
        'fade_in': 500,
        'fade_out': 500,
        'shadow_color': '#000000',
        'shadow_offset': 2
    }
    
    # 创建测试字幕
    subs = pysubs2.SSAFile()
    subs.append(pysubs2.SSAEvent(start=0, end=3000, text="测试字幕颜色"))
    
    # 应用样式
    generator.apply_subtitle_style(subs, config)
    
    # 保存测试文件
    test_file = Path('test_color_sub.ass')
    subs.save(str(test_file), encoding='utf-8')
    
    print(f"测试字幕已保存到: {test_file}")
    
    # 读取并显示样式
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
        for line in content.split('\n'):
            if line.startswith('Style:'):
                print(f"样式行: {line}")
                break
    
    # 清理测试文件
    if test_file.exists():
        test_file.unlink()

if __name__ == '__main__':
    test_color_conversion()