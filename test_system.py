#!/usr/bin/env python3
"""
质检管理系统功能测试脚本
用于验证系统各项功能是否正常工作
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_api_endpoint(endpoint, params=None, name="API"):
    """测试单个API端点"""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {name}: 成功 (返回 {len(str(data))} 字节数据)")
            return True
        else:
            print(f"❌ {name}: 失败 (状态码: {response.status_code})")
            print(f"   错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"❌ {name}: 错误 - {e}")
        return False

def test_complete_workflow():
    """测试完整的工作流程"""
    print("=" * 60)
    print("质检管理系统功能测试")
    print("=" * 60)
    
    # 测试参数
    test_params = {
        'product_code': 'DF-100',
        'test_item': 'solid_content',
        'start_date': '2025-07-01',
        'end_date': '2025-08-24'
    }
    
    # 测试各个API端点
    tests = [
        ('/api/search-products/', test_params, "产品搜索API"),
        ('/api/chart-data/', test_params, "质量趋势图API"),
        ('/api/moving-range-data/', test_params, "移动极差图API"),
        ('/api/capability-analysis/', test_params, "能力分析API"),
    ]
    
    results = []
    for endpoint, params, name in tests:
        results.append(test_api_endpoint(endpoint, params, name))
    
    # 测试主页访问
    try:
        response = requests.get(BASE_URL, timeout=10)
        if response.status_code == 200:
            print("✅ 主页访问: 成功")
            results.append(True)
        else:
            print(f"❌ 主页访问: 失败 (状态码: {response.status_code})")
            results.append(False)
    except Exception as e:
        print(f"❌ 主页访问: 错误 - {e}")
        results.append(False)
    
    # 测试管理后台
    try:
        response = requests.get(f"{BASE_URL}/admin/", timeout=10)
        if response.status_code in [200, 302]:  # 302 是重定向到登录页
            print("✅ 管理后台: 可访问")
            results.append(True)
        else:
            print(f"❌ 管理后台: 失败 (状态码: {response.status_code})")
            results.append(False)
    except Exception as e:
        print(f"❌ 管理后台: 错误 - {e}")
        results.append(False)
    
    # 汇总结果
    print("=" * 60)
    success_count = sum(results)
    total_count = len(results)
    
    if success_count == total_count:
        print(f"🎉 所有测试通过! ({success_count}/{total_count})")
        print("\n系统功能完整，可以正常使用。")
        return True
    else:
        print(f"⚠️  部分测试失败 ({success_count}/{total_count})")
        print("\n请检查失败的API端点。")
        return False

if __name__ == "__main__":
    if not test_complete_workflow():
        sys.exit(1)
