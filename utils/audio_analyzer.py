#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频分析模块 - BPM检测
用于打字机效果的动态速度控制
"""

import logging

logger = logging.getLogger(__name__)


def detect_bpm(audio_path):
    """
    检测音频BPM
    
    Args:
        audio_path: 音频文件路径
    
    Returns:
        float: BPM值，失败时返回100（默认中速）
    """
    try:
        import librosa
        import numpy as np
        
        # 加载音频（限制时长以加快分析）
        y, sr = librosa.load(audio_path, duration=60)
        
        # 检测节拍
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        
        # 处理numpy数组
        if hasattr(tempo, '__len__'):
            tempo = float(np.mean(tempo))
        else:
            tempo = float(tempo)
        
        # 限制在合理范围
        if tempo < 40 or tempo > 220:
            tempo = 100.0
        
        logger.info(f"检测到BPM: {tempo:.1f}")
        return tempo
        
    except ImportError:
        logger.warning("librosa未安装，使用默认BPM=100")
        return 100.0
    except Exception as e:
        logger.error(f"BPM检测失败: {e}")
        return 100.0


def bpm_to_base_speed(bpm):
    """
    根据BPM计算基础打字速度
    
    Args:
        bpm: BPM值
    
    Returns:
        float: 每个字的显示时间（秒）
    """
    if bpm < 80:
        return 0.12   # 慢歌
    elif bpm < 110:
        return 0.08   # 中速
    elif bpm < 140:
        return 0.06   # 中快
    else:
        return 0.04   # 快歌


def apply_mood_adjustment(base_speed, mood):
    """
    根据情绪微调打字速度
    
    Args:
        base_speed: 基础速度
        mood: 情绪类型
    
    Returns:
        float: 调整后的速度
    """
    # 情绪倍率表
    mood_factors = {
        "深夜emo": 1.3,
        "温暖治愈": 1.1,
        "浪漫甜蜜": 1.0,
        "怀旧经典": 1.15,
        "清新自然": 1.0,
        "热血燃曲": 0.7,
        "炫酷电子": 0.6,
        "暗黑神秘": 1.2,
        "国风中国": 1.05,
        "古风诗意": 1.1,
    }
    
    factor = mood_factors.get(mood, 1.0)
    adjusted = base_speed * factor
    
    # 限制在合理范围
    adjusted = max(0.04, min(0.15, adjusted))
    
    return round(adjusted, 3)


def calculate_dynamic_speed(audio_path, mood=None):
    """
    计算动态打字速度
    
    Args:
        audio_path: 音频文件路径
        mood: 情绪类型（可选）
    
    Returns:
        float: 每个字的显示时间（秒）
    """
    # 检测BPM
    bpm = detect_bpm(audio_path)
    
    # 计算基础速度
    base_speed = bpm_to_base_speed(bpm)
    
    # 应用情绪微调
    if mood:
        final_speed = apply_mood_adjustment(base_speed, mood)
    else:
        final_speed = base_speed
    
    logger.info(f"动态打字速度: BPM={bpm:.0f}, 基础={base_speed}s, 最终={final_speed}s")
    
    return final_speed


if __name__ == "__main__":
    # 测试
    import sys
    if len(sys.argv) > 1:
        bpm = detect_bpm(sys.argv[1])
        speed = calculate_dynamic_speed(sys.argv[1])
        print(f"BPM: {bpm:.1f}")
        print(f"速度: {speed}秒/字")
