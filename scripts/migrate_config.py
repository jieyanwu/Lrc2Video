#!/usr/bin/env python3
"""
配置迁移脚本
将旧的多个配置文件迁移到新的统一配置文件
"""

import json
import os
import time
import shutil
from pathlib import Path


def migrate_config():
    """迁移配置文件"""
    config_dir = Path("config")
    
    # 检查是否需要迁移
    old_files = [
        "user_preferences.json",
        "ai_config.json"
    ]
    
    existing_old_files = [f for f in old_files if (config_dir / f).exists()]
    
    if not existing_old_files:
        print("✅ 无需迁移，已使用新的统一配置")
        return
    
    print("🔧 开始迁移旧配置文件...")
    
    # 创建备份
    backup_dir = config_dir / ("backup_" + str(int(time.time())))
    backup_dir.mkdir(exist_ok=True)
    
    # 加载旧配置
    old_config = {}
    
    # 迁移 user_preferences.json
    if (config_dir / "user_preferences.json").exists():
        with open(config_dir / "user_preferences.json", 'r', encoding='utf-8') as f:
            user_prefs = json.load(f)
        
        # 迁移应用配置
        if "ui_config" in user_prefs:
            old_config.setdefault("app", {}).update({
                "theme": user_prefs["ui_config"].get("theme", "light"),
                "language": user_prefs["ui_config"].get("language", "zh-CN"),
                "window_geometry": user_prefs["ui_config"].get("window_geometry", "800x600")
            })
        
        # 迁移路径配置
        if "last_session" in user_prefs:
            old_config.setdefault("paths", {}).update({
                "audio_folder": user_prefs["last_session"].get("audio_folder", ""),
                "output_folder": user_prefs["last_session"].get("output_folder", "output"),
                "remember_folders": user_prefs["last_session"].get("remember_folders", True)
            })
        
        # 迁移歌词配置
        if "font_config" in user_prefs:
            old_config.setdefault("lyrics", {}).update(user_prefs["font_config"])
        
        # 迁移视频配置
        if "video_config" in user_prefs:
            old_config.setdefault("video", {}).update(user_prefs["video_config"])
        
        # 迁移AI配置
        if "api_config" in user_prefs:
            api_config = user_prefs["api_config"]
            old_config.setdefault("ai", {}).update({
                "enabled": bool(api_config.get("openai_api_key", "")),
                "provider": "openai",
                "max_tokens": api_config.get("max_tokens", 50),
                "temperature": api_config.get("temperature", 0.7)
            })
    
    # 迁移 ai_config.json
    if (config_dir / "ai_config.json").exists():
        with open(config_dir / "ai_config.json", 'r', encoding='utf-8') as f:
            ai_cfg = json.load(f)
        # 将旧AI配置合并到新配置结构
        old_config.setdefault("ai", {}).update({
            "enabled": bool(ai_cfg.get("api_key", "")),
            "provider": "moonshot",
        })
        old_config.setdefault("ai", {}).setdefault("providers", {})["moonshot"] = {
            "api_key": ai_cfg.get("api_key", ""),
            "base_url": ai_cfg.get("base_url", "https://api.moonshot.cn/v1"),
            "model": ai_cfg.get("model", "kimi-k2-turbo-preview"),
        }
    
    # 系统配置和优化配置已整合到统一配置模板中，无需单独迁移
    
    # 创建新的统一配置文件
    if (config_dir / "config.json.example").exists():
        with open(config_dir / "config.json.example", 'r', encoding='utf-8') as f:
            new_config = json.load(f)
        
        # 合并旧配置到新配置
        def deep_merge(dict1, dict2):
            for key, value in dict2.items():
                if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
                    deep_merge(dict1[key], value)
                else:
                    dict1[key] = value
        
        deep_merge(new_config, old_config)
        
        # 保存新配置
        with open(config_dir / "config.json", 'w', encoding='utf-8') as f:
            json.dump(new_config, f, indent=2, ensure_ascii=False)
        
        # 备份旧文件
        for old_file in existing_old_files:
            shutil.move(config_dir / old_file, backup_dir / old_file)
        
        print(f"✅ 配置迁移完成！")
        print(f"📁 旧配置文件已备份到: {backup_dir}")
        print(f"📄 新的统一配置文件: {config_dir / 'config.json'}")
        print("\n📝 请检查新配置文件，并根据需要更新API密钥等敏感信息")
    else:
        print("❌ 找不到配置文件模板")


if __name__ == "__main__":
    migrate_config()