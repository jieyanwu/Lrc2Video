#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件编码检测工具
"""

import os
from pathlib import Path

def detect_file_encoding(file_path):
    """
    检测文件编码
    返回: (encoding, confidence)
    """
    try:
        import chardet
    except ImportError:
        # 如果没有chardet，使用简单的启发式检测
        return detect_encoding_heuristic(file_path)
    
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        
        result = chardet.detect(raw_data)
        encoding = result.get('encoding', 'utf-8')
        confidence = result.get('confidence', 0.0)
        
        # 一些编码的特殊处理
        if encoding:
            encoding = encoding.lower()
            # 将一些编码映射到更标准的形式
            encoding_map = {
                'gb2312': 'gbk',
                'gb18030': 'gbk',
                'iso-8859-1': 'latin1',
                'windows-1252': 'cp1252'
            }
            encoding = encoding_map.get(encoding, encoding)
        
        return encoding, confidence
        
    except Exception as e:
        print(f"编码检测失败: {e}")
        return detect_encoding_heuristic(file_path)

def detect_encoding_heuristic(file_path):
    """
    启发式编码检测（不依赖chardet）
    """
    encodings_to_try = [
        ('utf-8', 0.9),
        ('utf-8-sig', 0.9),  # UTF-8 with BOM
        ('gbk', 0.7),
        ('gb2312', 0.6),
        ('gb18030', 0.6),
        ('big5', 0.5),
        ('latin1', 0.3),
        ('cp1252', 0.3)
    ]
    
    for encoding, confidence in encodings_to_try:
        try:
            with open(file_path, 'r', encoding=encoding, errors='strict') as f:
                content = f.read(1024)  # 读取前1024字符测试
            
            # 检查内容是否包含常见的中文字符
            if encoding in ['gbk', 'gb2312', 'gb18030', 'big5']:
                chinese_chars = sum(1 for char in content if '\u4e00' <= char <= '\u9fff')
                if chinese_chars > 0:
                    confidence += 0.2
            
            return encoding, confidence
            
        except (UnicodeDecodeError, UnicodeError):
            continue
        except Exception:
            continue
    
    # 如果所有编码都失败，返回utf-8作为默认值
    return 'utf-8', 0.1

def read_text_file_safe(file_path, encoding=None):
    """
    安全读取文本文件
    """
    if encoding:
        encodings_to_try = [encoding]
    else:
        detected_encoding, confidence = detect_file_encoding(file_path)
        encodings_to_try = [detected_encoding, 'utf-8', 'gbk', 'latin1']
    
    # 去重并保持顺序
    seen = set()
    unique_encodings = []
    for enc in encodings_to_try:
        if enc and enc not in seen:
            seen.add(enc)
            unique_encodings.append(enc)
    
    last_error = None
    for encoding in unique_encodings:
        try:
            with open(file_path, 'r', encoding=encoding, errors='strict') as f:
                content = f.read()
            print(f"成功使用 {encoding} 编码读取文件: {file_path}")
            return content, encoding
        except Exception as e:
            last_error = e
            continue
    
    # 最后尝试忽略错误
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        print(f"使用 utf-8 编码忽略错误读取文件: {file_path}")
        return content, 'utf-8'
    except Exception as e:
        raise ValueError(f"无法读取文件 {file_path}: {last_error or e}")

def test_encoding_detection():
    """测试编码检测功能"""
    test_dir = Path("test_files")
    if not test_dir.exists():
        print("测试目录不存在")
        return
    
    for file_path in test_dir.glob("*.lrc"):
        print(f"\n测试文件: {file_path}")
        try:
            encoding, confidence = detect_file_encoding(file_path)
            print(f"检测到编码: {encoding} (置信度: {confidence:.2f})")
            
            content, actual_encoding = read_text_file_safe(file_path)
            print(f"实际使用编码: {actual_encoding}")
            print(f"文件长度: {len(content)} 字符")
            
        except Exception as e:
            print(f"处理失败: {e}")

if __name__ == "__main__":
    test_encoding_detection()