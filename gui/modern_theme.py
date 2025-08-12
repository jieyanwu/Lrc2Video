"""
现代化UI主题样式配置
"""

# 颜色主题
COLORS = {
    'primary': '#2196F3',           # 主色调 - 蓝色
    'secondary': '#FF4081',         # 次要色调 - 粉红色
    'accent': '#00BCD4',            # 强调色 - 青色
    'background': '#FAFAFA',        # 背景色 - 浅灰色
    'surface': '#FFFFFF',           # 表面色 - 白色
    'error': '#F44336',             # 错误色 - 红色
    'warning': '#FF9800',           # 警告色 - 橙色
    'success': '#4CAF50',           # 成功色 - 绿色
    'text_primary': '#212121',      # 主要文本 - 深灰色
    'text_secondary': '#757575',    # 次要文本 - 中灰色
    'text_disabled': '#BDBDBD',     # 禁用文本 - 浅灰色
    'divider': '#E0E0E0',           # 分隔线 - 淡灰色
}

# 字体配置
FONTS = {
    'title': ('Segoe UI', 16, 'bold'),
    'subtitle': ('Segoe UI', 14, 'bold'),
    'body': ('Segoe UI', 11),
    'caption': ('Segoe UI', 9),
    'button': ('Segoe UI', 10, 'bold'),
    'monospace': ('Consolas', 10),
}

# 按钮样式
BUTTON_STYLES = {
    'primary': {
        'bg': COLORS['primary'],
        'fg': 'white',
        'activebackground': '#1976D2',
        'activeforeground': 'white',
        'relief': 'flat',
        'bd': 0,
        'padx': 20,
        'pady': 8,
        'font': FONTS['button'],
        'cursor': 'hand2',
    },
    'secondary': {
        'bg': COLORS['surface'],
        'fg': COLORS['primary'],
        'activebackground': '#E3F2FD',
        'activeforeground': COLORS['primary'],
        'relief': 'flat',
        'bd': 1,
        'highlightthickness': 1,
        'highlightbackground': COLORS['divider'],
        'padx': 20,
        'pady': 8,
        'font': FONTS['button'],
        'cursor': 'hand2',
    },
    'danger': {
        'bg': COLORS['error'],
        'fg': 'white',
        'activebackground': '#D32F2F',
        'activeforeground': 'white',
        'relief': 'flat',
        'bd': 0,
        'padx': 20,
        'pady': 8,
        'font': FONTS['button'],
        'cursor': 'hand2',
    },
}

# 输入框样式
ENTRY_STYLES = {
    'relief': 'flat',
    'bd': 1,
    'highlightthickness': 1,
    'highlightbackground': COLORS['divider'],
    'highlightcolor': COLORS['primary'],
    'bg': COLORS['surface'],
    'fg': COLORS['text_primary'],
    'insertbackground': COLORS['primary'],
    'font': FONTS['body'],
}

# 标签样式
LABEL_STYLES = {
    'bg': COLORS['background'],
    'fg': COLORS['text_primary'],
    'font': FONTS['body'],
}

# 框架样式
FRAME_STYLES = {
    'bg': COLORS['background'],
    'relief': 'flat',
    'bd': 0,
}

# 滑块样式
SCALE_STYLES = {
    'bg': COLORS['background'],
    'fg': COLORS['primary'],
    'troughcolor': COLORS['divider'],
    'activebackground': COLORS['primary'],
    'highlightthickness': 0,
    'bd': 0,
}

def create_modern_button(parent, text, command=None, style='primary'):
    """创建现代化按钮"""
    from tkinter import Button
    btn = Button(parent, text=text, command=command, **BUTTON_STYLES[style])
    return btn

def create_modern_entry(parent, textvariable=None, width=30, show=None):
    """创建现代化输入框"""
    from tkinter import Entry
    entry = Entry(parent, textvariable=textvariable, width=width, show=show, **ENTRY_STYLES)
    return entry

def create_modern_label(parent, text, style='body'):
    """创建现代化标签"""
    from tkinter import Label
    label = Label(parent, text=text, **LABEL_STYLES)
    if style != 'body':
        label.config(font=FONTS[style])
    return label

def create_modern_frame(parent, style='background'):
    """创建现代化框架"""
    from tkinter import Frame
    frame = Frame(parent, **FRAME_STYLES)
    return frame