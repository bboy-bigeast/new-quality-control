#!/usr/bin/env python3
"""
基本功能测试 - 验证项目核心功能
"""

import os
import django
import sys

# 添加项目路径到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quality_control.settings')
django.setup()

from products.models import DryFilmProduct, AdhesiveProduct, ProductStandard

def test_database_connection():
    """测试数据库连接"""
    print("测试数据库连接...")
    try:
        # 尝试查询一些数据
        dryfilm_count = DryFilmProduct.objects.count()
        adhesive_count = AdhesiveProduct.objects.count()
        standard_count = ProductStandard.objects.count()
        
        print(f"干膜产品记录数: {dryfilm_count}")
        print(f"胶粘剂产品记录数: {adhesive_count}")
        print(f"产品标准记录数: {standard_count}")
        
        return True
    except Exception as e:
        print(f"数据库连接测试失败: {e}")
        return False

def test_model_integrity():
    """测试模型完整性"""
    print("\n测试模型完整性...")
    try:
        # 检查干膜产品模型
        dryfilm_fields = [f.name for f in DryFilmProduct._meta.get_fields()]
        print(f"干膜产品模型字段: {len(dryfilm_fields)} 个")
        
        # 检查胶粘剂产品模型
        adhesive_fields = [f.name for f in AdhesiveProduct._meta.get_fields()]
        print(f"胶粘剂产品模型字段: {len(adhesive_fields)} 个")
        
        # 检查产品标准模型
        standard_fields = [f.name for f in ProductStandard._meta.get_fields()]
        print(f"产品标准模型字段: {len(standard_fields)} 个")
        
        return True
    except Exception as e:
        print(f"模型完整性测试失败: {e}")
        return False

def test_sample_data():
    """测试样本数据"""
    print("\n测试样本数据...")
    try:
        # 获取一些样本数据
        dryfilm_sample = DryFilmProduct.objects.first()
        adhesive_sample = AdhesiveProduct.objects.first()
        standard_sample = ProductStandard.objects.first()
        
        if dryfilm_sample:
            print(f"干膜样本: {dryfilm_sample.product_code} - {dryfilm_sample.batch_number}")
        else:
            print("没有干膜产品数据")
            
        if adhesive_sample:
            print(f"胶粘剂样本: {adhesive_sample.product_code} - {adhesive_sample.batch_number}")
        else:
            print("没有胶粘剂产品数据")
            
        if standard_sample:
            print(f"标准样本: {standard_sample.product_code} - {standard_sample.test_item}")
        else:
            print("没有产品标准数据")
            
        return True
    except Exception as e:
        print(f"样本数据测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("质检管理系统基本功能测试")
    print("=" * 50)
    
    tests = [
        test_database_connection,
        test_model_integrity,
        test_sample_data
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
        print("\n项目基本功能正常，可以继续使用API测试和Web界面")
    else:
        print("\n请检查数据库配置和数据完整性")
