#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频生成优化设置示例
运行此脚本查看当前系统的优化建议
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.hardware_detector import detect_hardware_acceleration, get_recommended_settings
from utils.optimization_manager import optimization_manager

def main():
    print("=== 视频生成优化指南 ===\n")
    
    # 检测硬件信息
    hardware_info = optimization_manager.get_hardware_info()
    
    print("【硬件检测结果】")
    print(f"支持的硬件加速: {', '.join(hardware_info['supported_hw'])}")
    print(f"GPU信息: {hardware_info['recommended_settings']['gpu_info']}")
    print()
    
    print("【当前优化配置】")
    current_config = optimization_manager.current_config
    print(f"编码预设: {current_config['preset']}")
    print(f"硬件加速: {current_config['hwaccel']}")
    print(f"质量因子 (CRF): {current_config['crf']}")
    print(f"调优设置: {current_config['tune']}")
    print()
    
    print("【优化建议】")
    tips = optimization_manager.get_optimization_tips()
    for tip in tips:
        print(f"• {tip}")
    print()
    
    print("【性能预设选项】")
    profiles = {
        "speed_priority": "速度优先 - 最快生成，文件较大",
        "balanced": "平衡模式 - 速度与质量平衡",
        "quality_priority": "质量优先 - 最佳质量，较慢"
    }
    
    for profile, desc in profiles.items():
        print(f"• {desc}")
    print()
    
    # 预估生成时间示例
    print("【生成时间预估】（3分钟音频示例）")
    for complexity in ["low", "medium", "high"]:
        time_info = optimization_manager.estimate_generation_time(180, complexity)
        print(f"复杂度{complexity}: 约 {time_info['estimated_minutes']:.1f} 分钟")
    print()
    
    print("【如何应用优化设置】")
    print("1. 修改配置文件: config/optimization_settings.json")
    print("2. 在代码中使用: optimization_manager.apply_performance_profile('balanced')")
    print("3. 手动设置参数: config['preset'] = 'fast'")
    print()
    
    print("【推荐设置】")
    recommended = hardware_info['recommended_settings']
    if recommended['default_hwaccel'] != 'none':
        print(f"• 启用 {recommended['default_hwaccel']} 硬件加速")
        print("• 使用 fast 或 faster 预设")
        print("• CRF值设为23-25")
    else:
        print("• 使用软件编码")
        print("• 根据CPU性能选择 preset")
        print("• 多核CPU可设置 thread_count=0 自动检测")

if __name__ == "__main__":
    main()