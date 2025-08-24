#!/usr/bin/env python
"""
测试脚本：验证修复后的selected_items字段处理和日期格式问题
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

def test_fixes():
    """测试所有修复"""
    print("=" * 50)
    print("测试修复验证")
    print("=" * 50)
    
    # 创建测试客户端
    client = Client()
    
    # 检查用户是否存在，如果不存在则创建
    try:
        user = User.objects.get(username='testuser_fix')
        print("  使用现有用户: testuser_fix")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser_fix',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        print("  创建新用户: testuser_fix")
    
    # 登录用户
    login_success = client.login(username='testuser_fix', password='testpass123')
    print(f"  登录结果: {'成功' if login_success else '失败'}")
    
    # 测试1：字符串数组格式的selected_items
    print("\n1. 测试字符串数组格式的selected_items...")
    report_data = {
        'report_type': 'dryfilm',
        'product_code': 'TEST001',
        'batch_number': 'BATCH001',
        'production_date': '2024-01-01',
        'inspector': 'Test Inspector',
        'selected_items': ['solid_content', 'viscosity'],  # 字符串数组格式
        'remarks': 'Test remarks for fix verification'
    }
    
    response = client.post('/reports/create/', 
                          json.dumps(report_data), 
                          content_type='application/json')
    print(f"  响应状态码: {response.status_code}")
    
    if response.status_code == 200:  # JSON响应表示成功
        response_data = json.loads(response.content)
        if response_data.get('success'):
            print("  ✅ 字符串数组格式处理成功")
            print(f"  创建的报告ID: {response_data['report_id']}")
            print(f"  报告编号: {response_data['report_number']}")
            
            # 测试2：访问报告详情页面（测试日期格式修复）
            print("\n2. 测试报告详情页面日期格式...")
            detail_response = client.get(f'/reports/{response_data["report_id"]}/')
            print(f"  详情页面响应状态码: {detail_response.status_code}")
            
            if detail_response.status_code == 200:
                print("  ✅ 报告详情页面日期格式修复成功")
            else:
                print("  ❌ 报告详情页面访问失败")
        else:
            print("  ❌ 字符串数组格式处理失败")
            print(f"  错误信息: {response_data.get('error')}")
    else:
        print("  ❌ 请求失败")
        print(f"  响应内容: {response.content}")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == '__main__':
    test_fixes()
