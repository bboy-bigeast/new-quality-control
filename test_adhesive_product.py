#!/usr/bin/env python
"""
测试胶粘剂产品功能的脚本
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quality_control.settings')
django.setup()

from products.models import AdhesiveProduct, ProductStandard
from django.contrib.auth.models import User

def test_adhesive_product():
    """测试胶粘剂产品功能"""
    print("=== 测试胶粘剂产品功能 ===")
    
    # 创建测试用户
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        print("创建测试用户: testuser")
    
    # 创建胶粘剂产品标准
    standards_data = [
        # 理化性能标准
        {'product_code': 'ADH-100', 'test_item': 'solid_content', 'standard_type': 'external_control', 'lower_limit': 45.0, 'upper_limit': 55.0},
        {'product_code': 'ADH-100', 'test_item': 'viscosity', 'standard_type': 'external_control', 'lower_limit': 2000.0, 'upper_limit': 3000.0},
        {'product_code': 'ADH-100', 'test_item': 'acid_value', 'standard_type': 'external_control', 'lower_limit': 0.5, 'upper_limit': 1.5},
        
        # 胶带性能标准
        {'product_code': 'ADH-100', 'test_item': 'initial_tack', 'standard_type': 'external_control', 'lower_limit': 10.0, 'upper_limit': 20.0},
        {'product_code': 'ADH-100', 'test_item': 'peel_strength', 'standard_type': 'external_control', 'lower_limit': 15.0, 'upper_limit': 25.0},
    ]
    
    for std_data in standards_data:
        ProductStandard.objects.get_or_create(**std_data)
    
    print("创建了胶粘剂产品标准")
    
    # 创建合格的胶粘剂产品
    adhesive_product = AdhesiveProduct(
        product_code='ADH-100',
        batch_number='ADH-20240824-001',
        production_line='胶粘剂产线A',
        physical_inspector='张三',
        tape_inspector='李四',
        physical_test_date='2024-08-24',
        tape_test_date='2024-08-24',
        sample_category='单批样',
        remarks='测试胶粘剂产品',
        modified_by='testuser',
        
        # 理化性能数据（合格）
        solid_content=50.0,
        viscosity=2500.0,
        acid_value=1.0,
        
        # 胶带性能数据（合格）
        initial_tack=15.0,
        peel_strength=20.0,
    )
    
    adhesive_product.save()
    print(f"创建胶粘剂产品: {adhesive_product}")
    print(f"理化判定: {adhesive_product.physical_judgment}")
    print(f"胶带判定: {adhesive_product.tape_judgment}")
    print(f"最终判定: {adhesive_product.final_judgment}")
    print(f"判定状态: {adhesive_product.judgment_status}")
    
    # 创建不合格的胶粘剂产品
    adhesive_product_fail = AdhesiveProduct(
        product_code='ADH-100',
        batch_number='ADH-20240824-002',
        production_line='胶粘剂产线A',
        physical_inspector='王五',
        tape_inspector='赵六',
        physical_test_date='2024-08-24',
        tape_test_date='2024-08-24',
        sample_category='单批样',
        remarks='测试不合格胶粘剂产品',
        modified_by='testuser',
        
        # 理化性能数据（不合格）
        solid_content=40.0,  # 低于下限
        viscosity=2500.0,
        acid_value=1.0,
        
        # 胶带性能数据（合格）
        initial_tack=15.0,
        peel_strength=20.0,
    )
    
    adhesive_product_fail.save()
    print(f"\n创建不合格胶粘剂产品: {adhesive_product_fail}")
    print(f"理化判定: {adhesive_product_fail.physical_judgment}")
    print(f"胶带判定: {adhesive_product_fail.tape_judgment}")
    print(f"最终判定: {adhesive_product_fail.final_judgment}")
    print(f"判定状态: {adhesive_product_fail.judgment_status}")
    
    # 检查历史记录
    history_count = adhesive_product.adhesiveproducthistory_set.count()
    print(f"\n产品修改历史记录数量: {history_count}")
    
    # 列出所有胶粘剂产品
    print(f"\n=== 所有胶粘剂产品 ===")
    for product in AdhesiveProduct.objects.all():
        print(f"{product.batch_number}: {product.final_judgment}")

if __name__ == '__main__':
    test_adhesive_product()
