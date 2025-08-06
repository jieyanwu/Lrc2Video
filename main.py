#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序入口
"""

from tkinter import Tk, messagebox
from gui.main_window import LyricsVideoGenerator

def main():
    root = Tk()
    app = LyricsVideoGenerator(root)
    # 设置窗口图标和样式
    try:
        root.iconbitmap(default='icon.ico')  # 如果有图标文件
    except:
        pass
    
    # 优雅退出处理
    def on_closing():
        if messagebox.askokcancel("退出", "确定要退出程序吗？"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == '__main__':
    main()