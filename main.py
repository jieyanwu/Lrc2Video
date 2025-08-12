#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序入口 - 增强调试版本
"""

import sys
import os
import logging
from datetime import datetime
from pathlib import Path
from tkinter import Tk, messagebox
from gui.main_window import LyricsVideoGenerator

# 配置调试日志
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# 设置日志格式 - 控制台只显示INFO及以上，文件记录所有级别
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(message)s'))

file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s - %(name)s - %(message)s'))

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[file_handler, console_handler]
)

logger = logging.getLogger(__name__)

# 添加调试信息打印
print("=" * 60)
print("🎵 歌词视频生成器 - 调试模式")
print("=" * 60)
print(f"📁 工作目录: {os.getcwd()}")
print(f"📊 日志文件: {log_file}")
print(f"🐍 Python版本: {sys.version}")
print("=" * 60)

def print_system_info():
    """打印系统信息"""
    try:
        import platform
        print(f"💻 系统: {platform.system()} {platform.release()}")
        print(f"🎯 架构: {platform.machine()}")
        print(f"🗂️  进程ID: {os.getpid()}")
        
        # 检查关键依赖
        dependencies = [
            'tkinter', 'openai', 'pysubs2'
        ]
        for dep in dependencies:
            try:
                __import__(dep)
                print(f"✅ {dep}: 已安装")
            except ImportError:
                print(f"❌ {dep}: 未安装")
                
    except Exception as e:
        logger.error(f"获取系统信息失败: {e}")

def main():
    """主程序入口 - 带调试信息"""
    logger.info("🚀 启动歌词视频生成器")
    
    try:
        # 打印系统信息
        print_system_info()
        
        # 检查必要目录
        required_dirs = ['config', 'output', 'logs', 'style_templates']
        for dir_name in required_dirs:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
                logger.info(f"📁 创建目录: {dir_name}")
            else:
                logger.info(f"📂 目录已存在: {dir_name}")
        
        # 检查配置文件
        config_files = [
            'config/config.json',
            'config/config.json.example'
        ]
        for config_file in config_files:
            if os.path.exists(config_file):
                logger.info(f"⚙️ 配置文件: {config_file} 已就绪")
            else:
                logger.warning(f"⚠️ 配置文件缺失: {config_file}")
        
        # 创建主窗口
        logger.info("🖥️  初始化GUI界面")
        root = Tk()
        
        # 设置窗口图标和样式
        try:
            root.iconbitmap(default='icon.ico')
            logger.info("🎨 窗口图标加载成功")
        except Exception as e:
            logger.warning(f"⚠️ 窗口图标加载失败: {e}")
        
        # 创建应用实例
        logger.info("🏗️  创建应用实例")
        app = LyricsVideoGenerator(root)
        logger.info("✅ 应用初始化完成")
        
        # 优雅退出处理
        def on_closing():
            if messagebox.askokcancel("退出", "确定要退出程序吗？"):
                logger.info("👋 用户选择退出应用")
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # 启动主循环
        logger.info("🎬 启动主事件循环")
        root.mainloop()
        
    except Exception as e:
        logger.error(f"💥 程序启动失败: {e}", exc_info=True)
        messagebox.showerror("启动失败", f"程序启动失败:\n{str(e)}")
        raise

if __name__ == '__main__':
    main()