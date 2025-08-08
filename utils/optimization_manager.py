#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化配置管理器
"""

import json
import os
from pathlib import Path
from .hardware_detector import detect_hardware_acceleration, get_recommended_settings

class OptimizationManager:
    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "optimization_settings.json"
        self.default_config = self._get_default_config()
        self.current_config = self.load_config()
    
    def _get_default_config(self):
        """获取默认优化配置"""
        hardware_info = get_recommended_settings()
        
        return {
            "preset": "medium",
            "tune": "film", 
            "crf": 23,
            "hwaccel": hardware_info.get('default_hwaccel', 'none'),
            "thread_count": 0,  # 0表示自动
            "batch_size": 1,
            "performance_profile": "balanced"
        }
    
    def load_config(self):
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合并默认配置
                merged_config = self.default_config.copy()
                merged_config.update(config)
                return merged_config
            else:
                return self.default_config.copy()
        except Exception as e:
            print(f"加载优化配置失败: {e}")
            return self.default_config.copy()
    
    def save_config(self, config=None):
        """保存配置到文件"""
        if config is None:
            config = self.current_config
        
        try:
            self.config_dir.mkdir(exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.current_config = config
            return True
        except Exception as e:
            print(f"保存优化配置失败: {e}")
            return False
    
    def get_hardware_info(self):
        """获取硬件信息"""
        return {
            "supported_hw": detect_hardware_acceleration(),
            "recommended_settings": get_recommended_settings()
        }
    
    def apply_performance_profile(self, profile_name):
        """应用性能预设配置"""
        profiles = {
            "speed_priority": {
                "preset": "ultrafast",
                "tune": "fastdecode",
                "crf": 28,
                "hwaccel": "auto"
            },
            "balanced": {
                "preset": "fast", 
                "tune": "film",
                "crf": 23,
                "hwaccel": "auto"
            },
            "quality_priority": {
                "preset": "slow",
                "tune": "film",
                "crf": 18,
                "hwaccel": "none"
            }
        }
        
        if profile_name in profiles:
            self.current_config.update(profiles[profile_name])
            self.current_config["performance_profile"] = profile_name
            self.save_config()
            return True
        return False
    
    def get_optimization_tips(self):
        """获取优化建议"""
        hardware_info = self.get_hardware_info()
        tips = []
        
        if "nvenc" in hardware_info["supported_hw"]:
            tips.append("检测到NVIDIA GPU，建议使用NVENC硬件加速大幅提升速度")
        elif "qsv" in hardware_info["supported_hw"]:
            tips.append("检测到Intel集成显卡，建议使用QSV硬件加速")
        elif "amf" in hardware_info["supported_hw"]:
            tips.append("检测到AMD GPU，建议使用AMF硬件加速")
        
        if self.current_config["preset"] in ["ultrafast", "superfast", "veryfast"]:
            tips.append("当前使用快速预设，生成速度较快但文件较大")
        elif self.current_config["preset"] in ["slow", "slower", "veryslow"]:
            tips.append("当前使用慢速预设，质量更好但耗时较长")
        
        if self.current_config["hwaccel"] == "none":
            tips.append("当前使用软件编码，启用硬件加速可显著提升速度")
        
        return tips
    
    def estimate_generation_time(self, audio_duration, complexity="medium"):
        """预估生成时间"""
        preset_speed = {
            "ultrafast": 8.0,
            "superfast": 4.0,
            "veryfast": 2.5,
            "faster": 2.0,
            "fast": 1.5,
            "medium": 1.0,
            "slow": 0.5,
            "slower": 0.3,
            "veryslow": 0.2
        }
        
        hw_multiplier = {
            "none": 1.0,
            "nvenc": 3.0,
            "qsv": 2.5,
            "amf": 2.0,
            "videotoolbox": 2.0
        }
        
        complexity_factor = {
            "low": 0.8,
            "medium": 1.0,
            "high": 1.5
        }
        
        preset = self.current_config["preset"]
        hwaccel = self.current_config["hwaccel"]
        
        base_time = audio_duration / preset_speed.get(preset, 1.0)
        hw_boost = hw_multiplier.get(hwaccel, 1.0)
        complexity_mult = complexity_factor.get(complexity, 1.0)
        
        estimated_time = base_time / hw_boost * complexity_mult
        
        return {
            "estimated_seconds": estimated_time,
            "estimated_minutes": estimated_time / 60,
            "preset": preset,
            "hardware": hwaccel
        }

# 全局优化管理器实例
optimization_manager = OptimizationManager()