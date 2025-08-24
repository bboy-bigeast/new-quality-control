#!/usr/bin/env python
"""
测试原始错误场景：验证"string indices must be integers, not 'str'"错误已被修复
"""

import os
import sys
import django
import json

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quality_control.settings')

# 先配置Django设置
import django
django.setup()

# 现在导入Django模块
from django.test import Client
from django.contrib.auth.models import User

def test_original_error_scenario():
    """测试原始错误场景"""
    print("=" * 60)
    print("测试原始错误场景：string indices must be integers, not 'str'")
    print("=" * 60)
    
    # 创建测试客户端
    client = Client()
    
    # 检查用户是否存在，如果不存在则创建
    try:
        user = User.objects.get(username='testuser_error')
        print("  使用现有用户: testuser_error")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser_error',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        print("  创建新用户: testuser_error")
    
    # 登录用户
    login_success = client.login(username='testuser_error', password='testpass123')
    print(f"  登录结果: {'成功' if login_success else '失败'}")
    
    # 测试1：模拟原始错误场景（对象数组格式）
    print("\n1. 测试对象数组格式的selected_items（原始错误场景）...")
    report_data = {
        'report_type': 'dryfilm',
        'product_code': 'TEST001',
        'batch_number': 'BATCH001',
        'production_date': '2024-01-01',
        'inspector': 'Test Inspector',
        'selected_items': [
            {'name': 'solid_content', 'value': '95%'},
            {'name': 'viscosity', 'value': '1500cps'}
        ],  # 对象数组格式（原始错误格式）
        'remarks': 'Test original error scenario'
    }
    
    response = client.post('/reports/create/', 
                          json.dumps(report_data), 
                          content_type='application/json')
    print(f"  响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        response_data = json.loads(response.content)
        if response_data.get('success'):
            print("  ✅ 对象数组格式处理成功（错误已修复）")
            print(f"  创建的报告ID: {response_data['report_id']}")
            
            # 验证报告详情
            from reports.models import InspectionReport
            report = InspectionReport.objects.get(id=response_data['report_id'])
            print(f"  selected_items字段类型: {type(report.selected_items)}")
            print(f"  selected_items内容: {report.selected_items}")
            
        else:
            print("  ❌ 对象数组格式处理失败")
            print(f"  错误信息: {response_data.get('error')}")
            if "string indices must be integers, not 'str'" in str(response_data.get('error')):
                print("  ❌❌ 原始错误仍然存在！")
            else:
                print("  ✅ 原始错误已被修复，现在是其他错误")
    else:
        print("  ❌ 请求失败")
        print(f"  响应内容: {response.content}")
    
    # 测试2：字符串数组格式（修复后的格式）
    print("\n2. 测试字符串数组格式的selected_items（修复后的格式）...")
    report_data2 = {
        'report_type': 'dryfilm',
        'product_code': 'TEST002',
        'batch_number': 'BATCH002',
        'production_date': '2024-01-02',
        'inspector': 'Test Inspector',
        'selected_items': ['solid_content', 'viscosity', 'ph_value'],  # 字符串数组格式
        'remarks': 'Test fixed format scenario'
    }
    
    response2 = client.post('/reports/create/', 
                           json.dumps(report_data2), 
                           content_type='application/json')
    print(f"  响应状态码: {response2.status_code}")
    
    if response2.status_code == 200:
        response_data2 = json.loads(response2.content)
        if response_data2.get('success'):
            print("  ✅ 字符串数组格式处理成功")
            print(f"  创建的报告ID: {response_data2['report_id']}")
        else:
            print("  ❌ 字符串数组格式处理失败")
            print(f"  错误信息: {response_data2.get('error')}")
    else:
        print("  ❌ 请求失败")
        print(f"  响应内容: {response2.content}")
    
    print("\n" + "=" * 60)
    print("测试完成 - 原始错误场景验证")
    print("=" * 60)

if __name__ == '__main__':
    test_original_error_scenario()
