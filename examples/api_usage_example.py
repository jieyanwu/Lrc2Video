#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API使用示例

这个示例展示了如何通过HTTP API调用歌词视频生成功能
"""

import requests
import json
import os
import time
from pathlib import Path

def api_generate_video_example():
    """
    通过API生成视频的完整示例
    """
    api_base = "http://127.0.0.1:8000/api"
    
    # 准备测试文件
    test_dir = Path("cp")
    lrc_files = list(test_dir.glob("*.lrc"))
    
    if not lrc_files:
        print("未找到.lrc文件，请确保cp目录中有测试文件")
        return
    
    lrc_file = lrc_files[0]
    audio_file = lrc_file.with_suffix('.flac')
    
    if not audio_file.exists():
        audio_file = lrc_file.with_suffix('.mp3')
    
    if not audio_file.exists():
        print(f"未找到对应的音频文件: {audio_file}")
        return
    
    # 构建请求数据
    payload = {
        "lrc_file": str(lrc_file.absolute()),
        "audio_file": str(audio_file.absolute()),
        "output_dir": "output",
        "style_config": {
            "font_name": "Microsoft YaHei",
            "font_size": 36,
            "font_color": "#FFFFFF",
            "stroke_width": 4,
            "stroke_color": "#000000",
            "alignment": 8,  # 底部居中
            "margin_bottom": 50
        },
        "optimization": {
            "preset": "fast",  # 快速模式
            "hardware_acceleration": "auto",
            "crf": 23
        }
    }
    
    print("=== API视频生成示例 ===")
    print(f"LRC文件: {lrc_file}")
    print(f"音频文件: {audio_file}")
    
    try:
        # 发送生成请求
        print("\n1. 发送生成请求...")
        response = requests.post(
            f"{api_base}/generate",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 202:
            task_info = response.json()
            task_id = task_info.get('task_id')
            print(f"✓ 任务已创建: {task_id}")
            
            # 轮询任务状态
            print("\n2. 监控任务进度...")
            while True:
                status_response = requests.get(f"{api_base}/status/{task_id}")
                if status_response.status_code == 200:
                    status = status_response.json()
                    progress = status.get('progress', 0)
                    state = status.get('state', 'unknown')
                    
                    print(f"进度: {progress}% - 状态: {state}")
                    
                    if state == 'completed':
                        output_file = status.get('output_file')
                        print(f"✓ 任务完成！输出文件: {output_file}")
                        break
                    elif state == 'failed':
                        error = status.get('error', '未知错误')
                        print(f"✗ 任务失败: {error}")
                        break
                    
                    time.sleep(2)  # 每2秒检查一次
                else:
                    print("获取任务状态失败")
                    break
        else:
            print(f"请求失败: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"API调用错误: {e}")

def check_api_status():
    """检查API状态"""
    try:
        response = requests.get("http://127.0.0.1:8000/api/status")
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def list_available_styles():
    """获取可用样式配置"""
    try:
        response = requests.get("http://127.0.0.1:8000/api/styles")
        return response.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    # 首先检查API状态
    status = check_api_status()
    print("API状态:", json.dumps(status, indent=2, ensure_ascii=False))
    
    if 'error' not in status:
        print("\nAPI服务运行正常，可以开始生成视频...")
        
        # 展示可用样式
        styles = list_available_styles()
        print("\n可用样式:", json.dumps(styles, indent=2, ensure_ascii=False))
        
        # 运行示例
        api_generate_video_example()
    else:
        print("请先启动主程序并开启API功能")