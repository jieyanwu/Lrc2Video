import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """统一的配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.json"
        self.example_file = self.config_dir / "config.json.example"
        self._config = {}
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            else:
                # 如果配置文件不存在，从示例文件创建
                if self.example_file.exists():
                    with open(self.example_file, 'r', encoding='utf-8') as f:
                        self._config = json.load(f)
                    self.save_config()
                else:
                    self._config = self._get_default_config()
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "app": {
                "name": "Lrc2Video",
                "version": "2.0.0",
                "theme": "light",
                "language": "zh-CN",
                "window_geometry": "800x600"
            },
            "ai": {
                "enabled": False,
                "provider": "moonshot",
                "providers": {
                    "moonshot": {
                        "api_key": "",
                        "base_url": "https://api.moonshot.cn/v1",
                        "model": "kimi-k2-turbo-preview",
                        "timeout": 30,
                        "max_retries": 3
                    }
                }
            },
            "video": {
                "resolution": "1920x1080",
                "fps": 30,
                "bitrate": "4000k",
                "hardware_acceleration": "none",
                "encoding_preset": "medium",
                "crf_value": 23,
                "tune_setting": "film",
                "thread_count": 0,
                "batch_size": 1
            },
            "lyrics": {
                "font_family": "Microsoft YaHei",
                "font_size": 24,
                "font_color": "#FFFFFF",
                "outline_width": 2,
                "outline_color": "#000000",
                "line_spacing": 1.5,
                "text_alignment": "center",
                "karaoke_mode": True,
                "highlight_color": "#FF6B6B"
            },
            "paths": {
                "audio_folder": "",
                "output_folder": "output",
                "temp_folder": "temp",
                "logs_folder": "logs",
                "remember_folders": True
            }
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """通过点分隔的路径获取配置值
        
        Args:
            key_path: 例如 'video.resolution' 或 'ai.enabled'
            default: 默认值
        """
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """设置配置值"""
        keys = key_path.split('.')
        config = self._config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def get_ai_config(self, provider: str = None) -> Dict[str, Any]:
        """获取AI配置"""
        if provider is None:
            provider = self.get('ai.provider', 'openai')
        
        providers = self.get('ai.providers', {})
        return providers.get(provider, {})
    
    def set_ai_config(self, provider: str, config: Dict[str, Any]):
        """设置AI配置"""
        providers = self._config.setdefault('ai', {}).setdefault('providers', {})
        providers[provider] = config
    
    def get_video_config(self) -> Dict[str, Any]:
        """获取视频配置"""
        return self.get('video', {})
    
    def get_lyrics_config(self) -> Dict[str, Any]:
        """获取歌词配置"""
        return self.get('lyrics', {})
    
    def get_paths_config(self) -> Dict[str, Any]:
        """获取路径配置"""
        return self.get('paths', {})
    
    def get_performance_profile(self, profile: str = None) -> Dict[str, Any]:
        """获取性能配置文件"""
        if profile is None:
            profile = self.get('video.performance_profile', 'balanced')
        
        profiles = self.get('performance_profiles', {})
        return profiles.get(profile, {})
    
    def save_config(self):
        """保存配置到文件"""
        try:
            self.config_dir.mkdir(exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def reset_config(self):
        """重置为默认配置"""
        self._config = self._get_default_config()
        self.save_config()
    
    def export_config(self, file_path: str):
        """导出配置到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"导出配置失败: {e}")
    
    def import_config(self, file_path: str):
        """从文件导入配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            self.save_config()
        except Exception as e:
            print(f"导入配置失败: {e}")
    
    def get_available_providers(self) -> Dict[str, Dict[str, str]]:
        """获取可用的AI提供商 - 仅保留Moonshot"""
        return {
            "moonshot": {
                "name": "Moonshot",
                "description": "月之暗面 Kimi",
                "models": ["kimi-k2-turbo-preview"]
            }
        }


# 全局配置管理器实例
_config_instance = None


def get_config() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance


def get_config_value(key_path: str, default: Any = None) -> Any:
    """快捷获取配置值"""
    return get_config().get(key_path, default)


def set_config_value(key_path: str, value: Any):
    """快捷设置配置值"""
    get_config().set(key_path, value)
    get_config().save_config()