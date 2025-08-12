"""
AI配置对话框 - 可视化配置AI标题生成功能
支持标准OpenAI和OpenRouter两种配置方式
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import os
import sys

# 添加utils目录到路径
sys.path.append(str(Path(__file__).parent.parent))
from utils.config_manager import get_config

class AIConfigDialog(tk.Toplevel):
    """AI配置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title("AI标题配置")
        self.geometry("700x650")  # 增大窗口尺寸
        self.resizable(True, True)  # 允许调整大小
        self.minsize(650, 600)    # 设置最小尺寸
        
        # 设置窗口图标
        try:
            icon_path = Path(__file__).parent.parent / "icon.ico"
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except:
            pass
        
        # 居中显示
        self.transient(parent)
        self.grab_set()
        
        # 配置样式
        self.setup_styles()
        
        # 创建界面
        self.create_widgets()
        
        # 加载当前配置
        self.load_config()
        
        # 绑定事件
        self.bind("<Escape>", lambda e: self.destroy())
    
    def setup_styles(self):
        """设置样式"""
        style = ttk.Style()
        
        # 配置样式
        style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("Info.TLabel", foreground="gray")
        style.configure("Test.TButton", padding=5)
        style.configure("Success.TLabel", foreground="green")
        style.configure("Error.TLabel", foreground="red")
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="AI标题配置", style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 启用开关
        self.enabled_var = tk.BooleanVar()
        enabled_frame = ttk.Frame(main_frame)
        enabled_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        enabled_check = ttk.Checkbutton(
            enabled_frame, 
            text="启用AI标题生成功能",
            variable=self.enabled_var
        )
        enabled_check.pack(side=tk.LEFT)
        
        # 提供商选择
        provider_frame = ttk.LabelFrame(main_frame, text="AI提供商", padding="15")
        provider_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.provider_var = tk.StringVar()
        from utils.config_manager import ConfigManager
        config = get_config()
        providers = ConfigManager().get_available_providers()
        
        for i, (key, info) in enumerate(providers.items()):
            radio = ttk.Radiobutton(
                provider_frame,
                text=info["name"],
                value=key,
                variable=self.provider_var,
                command=self.on_provider_change
            )
            radio.grid(row=i, column=0, sticky=tk.W, pady=2)
            
            info_label = ttk.Label(
                provider_frame,
                text=info["description"],
                style="Info.TLabel",
                font=("Segoe UI", 9)
            )
            info_label.grid(row=i, column=1, sticky=tk.W, padx=(20, 0))
        
        # 配置详情框架
        config_frame = ttk.LabelFrame(main_frame, text="配置详情", padding="15")
        config_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # API密钥
        ttk.Label(config_frame, text="API密钥:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(config_frame, textvariable=self.api_key_var, show="*", width=50)
        self.api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        
        # 显示/隐藏密钥按钮
        self.show_key_btn = ttk.Button(
            config_frame,
            text="显示",
            width=8,
            command=self.toggle_key_visibility
        )
        self.show_key_btn.grid(row=0, column=2, padx=(5, 0))
        
        # Base URL
        ttk.Label(config_frame, text="Base URL:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.base_url_var = tk.StringVar()
        self.base_url_entry = ttk.Entry(config_frame, textvariable=self.base_url_var, width=50)
        self.base_url_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        
        # 模型名称
        ttk.Label(config_frame, text="模型:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.model_var = tk.StringVar()
        self.model_entry = ttk.Entry(config_frame, textvariable=self.model_var, width=50)
        self.model_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        
        # 配置列权重
        config_frame.columnconfigure(1, weight=1)
        
        # 测试连接按钮
        test_frame = ttk.Frame(main_frame)
        test_frame.grid(row=4, column=0, columnspan=2, pady=(0, 15))
        
        self.test_btn = ttk.Button(
            test_frame,
            text="测试连接",
            style="Test.TButton",
            command=self.test_connection
        )
        self.test_btn.pack(side=tk.LEFT)
        
        self.test_result_label = ttk.Label(test_frame, text="")
        self.test_result_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 高级选项
        advanced_frame = ttk.LabelFrame(main_frame, text="高级选项", padding="15")
        advanced_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 超时时间
        ttk.Label(advanced_frame, text="超时时间 (秒):").grid(row=0, column=0, sticky=tk.W)
        self.timeout_var = tk.IntVar(value=8)
        timeout_spin = ttk.Spinbox(
            advanced_frame,
            from_=1,
            to=30,
            textvariable=self.timeout_var,
            width=10
        )
        timeout_spin.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # 重试次数
        ttk.Label(advanced_frame, text="最大重试次数:").grid(row=0, column=2, sticky=tk.W, padx=(30, 0))
        self.retries_var = tk.IntVar(value=2)
        retries_spin = ttk.Spinbox(
            advanced_frame,
            from_=0,
            to=5,
            textvariable=self.retries_var,
            width=10
        )
        retries_spin.grid(row=0, column=3, sticky=tk.W, padx=(10, 0))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(20, 0))
        
        save_btn = ttk.Button(button_frame, text="保存", command=self.save_config)
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = ttk.Button(button_frame, text="取消", command=self.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        reset_btn = ttk.Button(button_frame, text="重置", command=self.reset_config)
        reset_btn.pack(side=tk.LEFT)
        
        # 主框架列权重
        main_frame.columnconfigure(1, weight=1)
    
    def load_config(self):
        """加载当前配置"""
        from utils.config_manager import get_config
        config = get_config()
        ai_config = config.get("ai", {})
        
        # 启用状态
        self.enabled_var.set(ai_config.get("enabled", True))
        
        # 提供商
        current_provider = ai_config.get("provider", "openrouter")
        self.provider_var.set(current_provider)
        
        # 加载当前提供商的配置
        providers = ai_config.get("providers", {})
        provider_config = providers.get(current_provider, {})
        self.api_key_var.set(provider_config.get("api_key", ""))
        self.base_url_var.set(provider_config.get("base_url", ""))
        self.model_var.set(provider_config.get("model", ""))
        
        # 高级选项
        self.timeout_var.set(ai_config.get("timeout", 8))
        self.retries_var.set(ai_config.get("max_retries", 2))
    
    def on_provider_change(self):
        """提供商变更时的处理"""
        provider = self.provider_var.get()
        
        # 获取提供商的默认配置
        from utils.config_manager import ConfigManager
        providers = ConfigManager().get_available_providers()
        default_configs = {
            "openai": {
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-3.5-turbo"
            },
            "openrouter": {
                "base_url": "https://openrouter.ai/api/v1",
                "model": "moonshotai/kimi-k2:free"
            },
            "moonshot": {
                "base_url": "https://api.moonshot.cn/v1",
                "model": "kimi-k2-0711-preview"
            }
        }
        
        config = default_configs.get(provider, {})
        self.base_url_var.set(config.get("base_url", ""))
        self.model_var.set(config.get("model", ""))
        
        # 清空API密钥
        self.api_key_var.set("")
    
    def toggle_key_visibility(self):
        """切换密钥显示/隐藏"""
        if self.api_key_entry.cget("show") == "*":
            self.api_key_entry.config(show="")
            self.show_key_btn.config(text="隐藏")
        else:
            self.api_key_entry.config(show="*")
            self.show_key_btn.config(text="显示")
    
    def test_connection(self):
        """测试连接"""
        self.test_btn.config(state="disabled")
        self.test_result_label.config(text="测试中...", style="Info.TLabel")
        
        # 获取当前配置
        provider = self.provider_var.get()
        api_key = self.api_key_var.get()
        base_url = self.base_url_var.get()
        model = self.model_var.get()
        
        if not api_key:
            self.test_result_label.config(text="请先输入API密钥", style="Error.TLabel")
            self.test_btn.config(state="normal")
            return
        
        # 临时更新配置用于测试
        temp_config = {
            "api_key": api_key,
            "base_url": base_url,
            "model": model
        }
        
        # 使用测试线程避免阻塞UI
        import threading
        
        def test_thread():
            try:
                import requests
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                test_data = {
                    "model": model,
                    "messages": [{"role": "user", "content": "测试连接"}],
                    "max_tokens": 1
                }
                
                response = requests.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=test_data,
                    timeout=5
                )
                
                if response.status_code == 200:
                    result = {"success": True, "message": "连接成功"}
                elif response.status_code == 401:
                    result = {"success": False, "message": "API密钥无效"}
                else:
                    result = {"success": False, "message": f"HTTP {response.status_code}"}
                    
            except Exception as e:
                result = {"success": False, "message": str(e)}
            
            # 更新UI
            self.after(0, lambda: self.update_test_result(result))
        
        thread = threading.Thread(target=test_thread)
        thread.daemon = True
        thread.start()
    
    def update_test_result(self, result):
        """更新测试结果"""
        self.test_btn.config(state="normal")
        
        if result["success"]:
            self.test_result_label.config(text=result["message"], style="Success.TLabel")
        else:
            self.test_result_label.config(text=result["message"], style="Error.TLabel")
    
    def save_config(self):
        """保存配置"""
        try:
            # 获取当前配置
            from utils.config_manager import get_config
            config = get_config()
            
            # 更新AI配置
            ai_config = config._config.setdefault("ai", {})
            
            ai_config["enabled"] = self.enabled_var.get()
            ai_config["provider"] = self.provider_var.get()
            ai_config["timeout"] = self.timeout_var.get()
            ai_config["max_retries"] = self.retries_var.get()
            
            # 确保providers存在
            providers = ai_config.setdefault("providers", {})
            
            provider = self.provider_var.get()
            providers[provider] = {
                "api_key": self.api_key_var.get().strip(),
                "base_url": self.base_url_var.get().strip(),
                "model": self.model_var.get().strip()
            }
            
            # 保存配置
            config.save_config()
            
            messagebox.showinfo("成功", "配置已保存")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
    
    def reset_config(self):
        """重置配置"""
        if messagebox.askyesno("确认", "确定要重置为默认配置吗？"):
            try:
                # 重置AI配置为默认值
                from utils.config_manager import get_config
                config = get_config()
                if "ai" in config._config:
                    del config._config["ai"]
                config.save_config()
                
                # 重新加载配置
                self.load_config()
                messagebox.showinfo("成功", "已重置为默认配置")
            except Exception as e:
                messagebox.showerror("错误", f"重置配置失败: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    dialog = AIConfigDialog(root)
    root.wait_window(dialog)
    
    root.destroy()