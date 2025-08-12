#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API功能测试脚本
"""

import requests
import json
import os

def test_api():
    """测试API功能"""
    base_url = "http://127.0.0.1:8000/api"
    
    # 测试API状态
    try:
        response = requests.get(f"{base_url}/status")
        print("API状态:", response.json())
    except Exception as e:
        print("API状态检查失败:", e)
        return
    
    # 测试API文档
    try:
        response = requests.get(f"{base_url}/docs")
        print("API文档可用:", response.status_code == 200)
        if response.status_code == 200:
            print("文档内容预览:")
            docs = response.json()
            print(json.dumps(docs, indent=2, ensure_ascii=False))
    except Exception as e:
        print("API文档检查失败:", e)

if __name__ == '__main__':
    test_api()