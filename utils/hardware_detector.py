#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硬件加速检测工具
"""

import subprocess
import re
import platform

def detect_hardware_acceleration():
    """检测系统支持的硬件加速类型"""
    supported_hw = []
    
    try:
        # 检测NVIDIA NVENC
        result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], 
                              capture_output=True, text=True, encoding='utf-8')
        encoders = result.stdout.lower()
        
        if 'h264_nvenc' in encoders:
            supported_hw.append('nvenc')
        
        # 检测Intel Quick Sync Video
        if 'h264_qsv' in encoders:
            supported_hw.append('qsv')
            
        # 检测AMD AMF
        if 'h264_amf' in encoders:
            supported_hw.append('amf')
            
        # 检测macOS VideoToolbox
        if platform.system() == 'Darwin' and 'h264_videotoolbox' in encoders:
            supported_hw.append('videotoolbox')
            
    except Exception as e:
        print(f"硬件检测错误: {e}")
    
    # 始终支持软件编码
    supported_hw.append('none')
    
    return supported_hw

def get_gpu_info():
    """获取GPU信息"""
    gpu_info = []
    
    try:
        if platform.system() == "Windows":
            # Windows使用wmic获取GPU信息
            result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name'], 
                                  capture_output=True, text=True, encoding='utf-8')
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # 跳过标题行
                for line in lines:
                    line = line.strip()
                    if line and line != "Name":
                        gpu_info.append(line)
        
        elif platform.system() == "Linux":
            # Linux使用lspci获取GPU信息
            result = subprocess.run(['lspci', '|', 'grep', '-i', 'vga'], 
                                  capture_output=True, text=True, encoding='utf-8')
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'vga' in line.lower():
                        gpu_info.append(line.split(': ')[1] if ': ' in line else line)
        
        elif platform.system() == "Darwin":
            # macOS使用system_profiler
            result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                                  capture_output=True, text=True, encoding='utf-8')
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if 'Chipset Model:' in line:
                        gpu_info.append(line.split('Chipset Model: ')[1])
    
    except Exception as e:
        print(f"获取GPU信息错误: {e}")
    
    return gpu_info

def get_recommended_settings():
    """获取推荐的编码设置"""
    hw_support = detect_hardware_acceleration()
    gpu_info = get_gpu_info()
    
    recommendations = {
        'supported_hw': hw_support,
        'gpu_info': gpu_info,
        'default_preset': 'medium',
        'default_hwaccel': 'none',
        'quality_settings': {
            'ultrafast': {'speed': '最快', 'quality': '最低', 'file_size': '最大'},
            'superfast': {'speed': '很快', 'quality': '较低', 'file_size': '较大'},
            'veryfast': {'speed': '快', 'quality': '中等', 'file_size': '中等'},
            'faster': {'speed': '较快', 'quality': '较好', 'file_size': '中等'},
            'fast': {'speed': '中等', 'quality': '好', 'file_size': '中等'},
            'medium': {'speed': '中等', 'quality': '很好', 'file_size': '标准'},
            'slow': {'speed': '较慢', 'quality': '很好', 'file_size': '较小'},
            'slower': {'speed': '慢', 'quality': '极好', 'file_size': '较小'},
            'veryslow': {'speed': '最慢', 'quality': '最好', 'file_size': '最小'}
        }
    }
    
    # 根据GPU类型推荐硬件加速
    if 'nvenc' in hw_support:
        recommendations['default_hwaccel'] = 'nvenc'
        recommendations['default_preset'] = 'fast'  # NVENC使用fast预设
    elif 'qsv' in hw_support:
        recommendations['default_hwaccel'] = 'qsv'
        recommendations['default_preset'] = 'veryfast'
    elif 'amf' in hw_support:
        recommendations['default_hwaccel'] = 'amf'
        recommendations['default_preset'] = 'balanced'
    elif 'videotoolbox' in hw_support:
        recommendations['default_hwaccel'] = 'videotoolbox'
        recommendations['default_preset'] = 'medium'
    
    return recommendations

if __name__ == "__main__":
    # 测试硬件检测
    print("=== 硬件加速检测 ===")
    hw = detect_hardware_acceleration()
    print(f"支持的硬件加速: {hw}")
    
    print("\n=== GPU信息 ===")
    gpu = get_gpu_info()
    print(f"GPU信息: {gpu}")
    
    print("\n=== 推荐设置 ===")
    rec = get_recommended_settings()
    print(f"推荐设置: {rec}")