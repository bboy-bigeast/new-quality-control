#!/usr/bin/env python3
"""
测试原料图表分析API的脚本
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000/raw_materials"

def test_charts_api():
    """测试图表分析API"""
    print("测试图表分析API...")
    
    # 测试时间趋势图表
    params = {
        'test_item': 'purity',
        'start_date': '2024-01-01'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/charts/", params=params)
        if response.status_code == 200:
            data = response.json()
            print("✓ 图表分析API测试成功")
            print(f"  获取到 {data['metadata']['total_samples']} 个样本数据")
            print(f"  时间序列数据点: {len(data['time_series'])}")
            print(f"  分布分析数据点: {len(data['distribution'])}")
        else:
            print(f"✗ 图表分析API测试失败: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"✗ 图表分析API测试异常: {e}")

def test_comparison_api():
    """测试对比分析API"""
    print("\n测试对比分析API...")
    
    # 测试原料对比
    params = {
        'material_name': ['丙烯酸', '甲基丙烯酸甲酯'],  # 假设的原料名称
        'test_item': 'purity'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/comparison/", params=params)
        if response.status_code == 200:
            data = response.json()
            print("✓ 对比分析API测试成功")
            print(f"  对比原料数量: {len(data['comparison_data'])}")
            for material_name, stats in data['comparison_data'].items():
                print(f"  {material_name}: {stats['stats'].get('count', 0)} 个样本")
        else:
            print(f"✗ 对比分析API测试失败: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"✗ 对比分析API测试异常: {e}")

def test_stats_api():
    """测试统计API"""
    print("\n测试统计API...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/stats/")
        if response.status_code == 200:
            data = response.json()
            print("✓ 统计API测试成功")
            print(f"  总样本数: {data['total_stats']['total']}")
            print(f"  合格样本: {data['total_stats']['qualified']}")
            print(f"  不合格样本: {data['total_stats']['unqualified']}")
        else:
            print(f"✗ 统计API测试失败: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"✗ 统计API测试异常: {e}")

if __name__ == "__main__":
    print("开始测试原料图表分析API...")
    print("=" * 50)
    
    test_stats_api()
    test_charts_api()
    test_comparison_api()
    
    print("\n" + "=" * 50)
    print("测试完成！")
