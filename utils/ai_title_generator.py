"""
AI标题生成器
集成到视频保存环节的AI标题生成功能
使用标准OpenAI客户端库格式
"""

import os
import logging
from pathlib import Path

# 抑制OpenAI的HTTP请求日志
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

try:
    from openai import OpenAI
    HAS_OPENAI_LIB = True
except ImportError:
    HAS_OPENAI_LIB = False
    OpenAI = None

# 导入配置管理器
from .config_manager import get_config

class AITitleGenerator:
    """AI标题生成器 - 集成版本"""
    
    def __init__(self, api_key=None, base_url=None, model=None):
        """初始化AI标题生成器"""
        # 使用新的配置管理器
        if api_key is None and base_url is None and model is None:
            # 从配置管理器获取配置
            config = get_config()
            ai_config = config.get("ai", {})
            provider = ai_config.get("provider", "openrouter")
            providers = ai_config.get("providers", {})
            provider_config = providers.get(provider, {})
            
            self.api_key = provider_config.get("api_key", "")
            self.base_url = provider_config.get("base_url", "")
            self.model = provider_config.get("model", "")
        else:
            # 使用显式参数
            self.api_key = api_key
            self.base_url = base_url or (
                os.getenv("LRC2VIDEO_API_BASE_URL") or 
                "https://openrouter.ai/api/v1"
            )
            self.model = model or os.getenv("LRC2VIDEO_MODEL") or "moonshotai/kimi-k2:free"
        
        self.enabled = bool(self.api_key) and HAS_OPENAI_LIB
        
        if self.enabled:
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
            )
        else:
            self.client = None
    
    def generate_title(self, song_name, artist=None):
        """为音乐视频生成AI标题"""
        if not self.enabled:
            return None
            
        # 根据歌手和歌曲名分析风格特征
        style_context = self._analyze_music_style(song_name, artist)
        
        prompt = f"""你是一个专业的音乐视频标题策划师！根据以下信息为这首歌曲量身定制一个独特的爆款标题：

                    🎵 歌曲信息：
                    歌曲名：《{song_name}》
                    歌手：{artist if artist else '未知'}
                    风格特征：{style_context}

                    🎯 创作要求：
                    1. **个性化**：必须体现这首歌的独特气质和歌手风格
                    2. **情感共鸣**：针对{style_context}的特点，精准触发对应情感
                    3. **记忆钩子**：创造专属的记忆点，避免千篇一律的模板
                    4. **平台适配**：B站/抖音风格，但保持音乐质感
                    5. **长度控制**：15-25字，朗朗上口

                    💡 创作思路：
                    - 如果是抒情歌曲：突出治愈、回忆、遗憾等情感
                    - 如果是摇滚/电音：强调炸裂、燃爆、震撼等感受  
                    - 如果是民谣：营造故事感、生活化、温暖氛围
                    - 如果是Live版：突出现场魅力、真实感动
                    - 根据歌手特色：比如周杰伦的"青春"、林俊杰的"治愈"、邓紫棋的"爆发力"

                    🚀 爆款公式：
                    【歌名】+ 专属记忆点 + 情感爆点
                    避免使用"听完直接破防"这类通用模板！

                    🎭 风格示例：
                    - 周杰伦【晴天】：前奏一响就是整个青春
                    - 林俊杰【江南】：江南一响，多少人的意难平
                    - 邓紫棋【光年之外】：高音一出直接头皮发麻
                    - 五月天【倔强】：万人合唱现场，这就是青春啊

                    请根据《{song_name}》{f'和{artist}的风格' if artist else ''}，创作一个独一无二的标题！
                    直接返回标题，不要解释！"""
        
        try:
            import time
            
            # 静默重试机制，最多2次尝试
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    completion = self.client.chat.completions.create(
                        extra_headers={
                            "HTTP-Referer": "https://github.com/Lrc2Video",
                            "X-Title": "Lrc2Video",
                        },
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=50,
                        temperature=0.8,
                        timeout=8
                    )
                    
                    title = completion.choices[0].message.content.strip()
                    
                    # 确保标题长度合适且去除可能的引号
                    title = title.strip('"\'')
                    if len(title) < 10:
                        title = f"【{song_name}】绝美音乐MV"
                    elif len(title) > 25:
                        # 智能截断
                        if "】" in title:
                            parts = title.split("】", 1)
                            if len(parts) == 2:
                                title = parts[0] + "】" + parts[1][:25-len(parts[0])-1]
                        else:
                            title = title[:25]
                    
                    return title
                    
                except Exception as api_error:
                    # 只在最后一次失败时输出错误信息
                    if attempt == max_retries - 1:
                        break
                    # 静默重试，不输出重试信息
                    time.sleep(1)
            
            # 所有重试都失败，返回None让调用方处理
            return None
                        
        except Exception as e:
            # 静默处理所有错误，不输出到控制台
            return None
    
    def is_configured(self):
        """检查是否已配置API密钥"""
        return self.enabled
    
    def _analyze_music_style(self, song_name, artist=None):
        """根据歌手和歌曲名分析音乐风格特征"""
        # 歌手风格特征库
        artist_styles = {
            "周杰伦": "青春回忆、华语经典、R&B融合、青春校园",
            "林俊杰": "治愈系、情歌王子、高音震撼、情感细腻",
            "邓紫棋": "爆发力、高音炸裂、实力派、舞台王者",
            "五月天": "青春摇滚、万人合唱、治愈系、正能量",
            "陈奕迅": "情感深沉、唱功顶级、故事感、港风经典",
            "薛之谦": "深情款款、歌词走心、情感共鸣、都市情歌",
            "Taylor Swift": "青春故事、情感真挚、乡村转流行、创作才女",
            "Ed Sheeran": "温暖治愈、民谣风、情歌王子、欧美经典",
            "Adele": "灵魂歌姬、情感爆发、唱功顶级、欧美天后",
            "Billie Eilish": "暗黑系、独特声线、年轻态度、另类流行"
        }
        
        # 歌曲关键词特征
        song_keywords = {
            "live": "现场版、真实感动、Live魅力",
            "Live": "现场版、真实感动、Live魅力",
            "live版": "现场版、真实感动、Live魅力",
            "Live版": "现场版、真实感动、Live魅力",
            "remix": "电音、混音、节奏感、夜店风",
            "Remix": "电音、混音、节奏感、夜店风",
            "acoustic": "不插电、纯净、民谣风、温暖",
            "Acoustic": "不插电、纯净、民谣风、温暖",
            "cover": "翻唱、全新演绎、致敬经典",
            "Cover": "翻唱、全新演绎、致敬经典"
        }
        
        # 情感关键词
        emotion_keywords = {
            "爱": "情感、爱情、温暖",
            "泪": "感动、泪目、深情",
            "心": "情感、共鸣、触动",
            "夜": "夜晚、孤独、思念",
            "雨": "伤感、忧郁、思念",
            "风": "回忆、青春、时光",
            "光": "希望、温暖、治愈",
            "梦": "梦想、青春、回忆",
            "你": "情感、思念、共鸣",
            "我": "个人情感、自我表达"
        }
        
        style_parts = []
        
        # 分析歌手风格
        if artist and artist in artist_styles:
            style_parts.append(artist_styles[artist])
        
        # 分析歌曲版本特征
        song_lower = str(song_name).lower()
        for keyword, style in song_keywords.items():
            if keyword.lower() in song_lower:
                style_parts.append(style)
                break
        
        # 分析情感特征
        for keyword, emotion in emotion_keywords.items():
            if keyword in str(song_name):
                style_parts.append(emotion)
                break
        
        # 默认风格判断
        if not style_parts:
            # 根据歌名长度和用词判断
            if len(str(song_name)) <= 4:
                style_parts.append("华语经典、情感共鸣")
            elif any(word in str(song_name) for word in ['的', '了', '我', '你']):
                style_parts.append("华语流行、情感表达")
            else:
                style_parts.append("音乐MV、情感共鸣")
        
        return '、'.join(set(style_parts))

def get_default_title(song_name, artist=None):
    """获取默认标题（当AI生成失败时）"""
    # 为默认标题也增加一些吸引力
    if artist:
        return f"【{song_name}】{artist}的封神现场！"
    return f"【{song_name}】听完直接破防的音乐MV"

def generate_video_title(song_name, artist=None, use_ai=True):
    """
    生成视频标题的主函数
    
    Args:
        song_name: 歌曲名称
        artist: 艺术家名称
        use_ai: 是否使用AI生成
    
    Returns:
        str: 最终的视频标题
    """
    if not use_ai:
        return get_default_title(song_name, artist)
    
    generator = AITitleGenerator()
    if not generator.is_configured():
        return get_default_title(song_name, artist)
    
    ai_title = generator.generate_title(song_name, artist)
    if ai_title:
        return ai_title
    else:
        return get_default_title(song_name, artist)