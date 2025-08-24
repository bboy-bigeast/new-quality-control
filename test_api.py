#!/usr/bin/env python3
"""
API测试脚本 - 用于验证新的首页功能API端点
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000"

def test_chart_data_api():
    """测试图表数据API"""
    print("测试图表数据API...")
    try:
        # 构建查询参数
        params = {
            'test_item': 'solid_content',
            'start_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'end_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        response = requests.get(f"{BASE_URL}/api/chart-data/", params=params)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"返回数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def test_search_products_api():
    """测试产品查询API"""
    print("\n测试产品查询API...")
    try:
        params = {
            'start_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'end_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        response = requests.get(f"{BASE_URL}/api/search-products/", params=params)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"找到 {len(data.get('products', []))} 个产品")
            return True
        else:
            print(f"错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def test_moving_range_api():
    """测试移动极差API"""
    print("\n测试移动极差API...")
    try:
        params = {
            'test_item': 'solid_content',
            'start_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'end_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        response = requests.get(f"{BASE_URL}/api/moving-range-data/", params=params)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"移动极差数据获取成功")
            return True
        else:
            print(f"错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def test_capability_analysis_api():
    """测试能力分析API"""
    print("\n测试能力分析API...")
    try:
        params = {
            'test_item': 'solid_content',
            'start_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'end_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        response = requests.get(f"{BASE_URL}/api/capability-analysis/", params=params)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"能力分析数据获取成功")
            return True
        else:
            print(f"错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("质检管理系统API测试")
    print("=" * 50)
    
    # 运行所有测试
    tests = [
        test_chart_data_api,
        test_search_products_api,
        test_moving_range_api,
        test_capability_analysis_api
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    
    for i, result in enumerate(results):
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{tests[i].__name__}: {status}")
    
    all_passed = all(results)
    print(f"\n总体结果: {'所有测试通过!' if all_passed else '部分测试失败!'}")
    
    if all_passed:
        print("\n可以访问 http://127.0.0.1:8000 查看新的首页功能")
    else:
        print("\n请检查数据库是否有测试数据，或查看服务器日志获取详细信息")
