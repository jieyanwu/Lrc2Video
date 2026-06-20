#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序入口 - 增强调试版本
"""

import sys
import os
import logging
import importlib
from datetime import datetime
from pathlib import Path
from tkinter import Tk, messagebox
from gui.main_window import LyricsVideoGenerator

logger = logging.getLogger(__name__)


def _setup_logging():
    """初始化日志系统 — 仅在主入口调用，避免导入时副作用。"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(message)s'))

    file_handler = logging.FileHandler(str(log_file), encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter('[%(asctime)s] %(levelname)s - %(name)s - %(message)s')
    )

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[file_handler, console_handler],
    )
    return file_handler


def _print_banner(file_handler):
    """打印启动横幅信息。"""
    logger.info("=" * 60)
    logger.info("🎵 歌词视频生成器")
    logger.info("=" * 60)
    logger.info(f"📁 工作目录: {Path.cwd()}")
    logger.info(f"📊 日志文件: {file_handler.baseFilename}")
    logger.info(f"🐍 Python版本: {sys.version}")
    logger.info("=" * 60)


def print_system_info():
    """打印系统信息"""
    try:
        import platform
        logger.info(f"💻 系统: {platform.system()} {platform.release()}")
        logger.info(f"🎯 架构: {platform.machine()}")
        logger.info(f"🗂️  进程ID: {os.getpid()}")

        # 检查关键依赖
        dependencies = [
            'tkinter', 'openai', 'pysubs2'
        ]
        for dep in dependencies:
            try:
                importlib.import_module(dep)
                logger.info(f"✅ {dep}: 已安装")
            except ImportError:
                logger.warning(f"❌ {dep}: 未安装")

    except Exception as e:
        logger.error(f"获取系统信息失败: {e}")


def main():
    """主程序入口 - 带调试信息"""
    file_handler = _setup_logging()
    _print_banner(file_handler)

    logger.info("🚀 启动歌词视频生成器")

    try:
        # 打印系统信息
        print_system_info()

        project_root = Path(__file__).resolve().parent

        # 检查必要目录
        required_dirs = ['config', 'output', 'logs', 'style_templates']
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"📁 创建目录: {dir_path}")
            else:
                logger.info(f"📂 目录已存在: {dir_path}")

        # 检查配置文件
        config_files = [
            'config/config.json',
            'config/config.json.example'
        ]
        for config_file in config_files:
            config_path = project_root / config_file
            if config_path.exists():
                logger.info(f"⚙️ 配置文件: {config_path} 已就绪")
            else:
                logger.warning(f"⚠️ 配置文件缺失: {config_path}")

        # 创建主窗口
        logger.info("🖥️  初始化GUI界面")
        root = Tk()

        # 设置窗口图标和样式
        try:
            # 优先使用ICO格式图标（Windows兼容性最好）
            ico_path = str(project_root / 'icon.ico')
            png_path = str(project_root / 'icon.png')

            if Path(ico_path).exists():
                # 使用ICO图标
                root.iconbitmap(default=ico_path)
                logger.info(f"🎨 ICO图标加载成功: {ico_path}")
            elif Path(png_path).exists():
                # 使用PNG图标作为备选
                try:
                    root.iconbitmap(default=png_path)
                    logger.info(f"🎨 PNG图标加载成功: {png_path}")
                except Exception:
                    # PNG格式在某些Windows版本上不兼容，使用PIL方法
                    try:
                        from PIL import Image, ImageTk
                        icon_image = ImageTk.PhotoImage(file=png_path)
                        root.iconphoto(True, icon_image)
                        logger.info("🎨 使用PIL PhotoImage加载PNG图标成功")
                    except ImportError:
                        logger.warning("⚠️ PIL库未安装，无法使用PhotoImage加载图标")
            else:
                logger.warning("⚠️ 图标文件不存在")

        except Exception as e:
            logger.warning(f"⚠️ 窗口图标加载失败: {e}")

        # 创建应用实例
        logger.info("🏗️  创建应用实例")
        app = LyricsVideoGenerator(root)
        logger.info("✅ 应用初始化完成")

        # 启动主循环
        logger.info("🎬 启动主事件循环")
        root.mainloop()

    except Exception as e:
        logger.error(f"💥 程序启动失败: {e}", exc_info=True)
        messagebox.showerror("启动失败", f"程序启动失败:\n{str(e)}")
        raise


if __name__ == '__main__':
    main()
