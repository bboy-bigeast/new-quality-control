#!/usr/bin/env python3
"""
API功能测试 - 验证项目核心API接口
"""

import os
import django
import sys
import json
from django.test import TestCase, Client
from django.urls import reverse

# 添加项目路径到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quality_control.settings')
django.setup()

from products.models import DryFilmProduct, AdhesiveProduct, ProductStandard

class APITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_get_product_data_dryfilm(self):
        """测试获取干膜产品数据API"""
        print("测试干膜产品数据API...")
        
        # 获取一个存在的产品代码
        sample_product = DryFilmProduct.objects.first()
        if not sample_product:
            print("没有干膜产品数据，跳过测试")
            return
            
        url = reverse('product_chart_data', args=['dryfilm'])
        params = {
            'product_code': sample_product.product_code,
            'test_item': 'solid_content'
        }
        
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('labels', data)
        self.assertIn('data', data)
        self.assertIn('statistics', data)
        
        print(f"干膜API测试通过: 返回 {len(data['labels'])} 个数据点")
        
    def test_get_product_data_adhesive(self):
        """测试获取胶粘剂产品数据API"""
        print("测试胶粘剂产品数据API...")
        
        # 获取一个存在的产品代码
        sample_product = AdhesiveProduct.objects.first()
        if not sample_product:
            print("没有胶粘剂产品数据，跳过测试")
            return
            
        url = reverse('product_chart_data', args=['adhesive'])
        params = {
            'product_code': sample_product.product_code,
            'test_item': 'solid_content'
        }
        
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('labels', data)
        self.assertIn('data', data)
        self.assertIn('statistics', data)
        
        print(f"胶粘剂API测试通过: 返回 {len(data['labels'])} 个数据点")
        
    def test_search_products_dryfilm(self):
        """测试搜索干膜产品API"""
        print("测试搜索干膜产品API...")
        
        url = reverse('product_search', args=['dryfilm'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('products', data)
        
        print(f"干膜搜索API测试通过: 找到 {len(data['products'])} 个产品")
        
    def test_search_products_adhesive(self):
        """测试搜索胶粘剂产品API"""
        print("测试搜索胶粘剂产品API...")
        
        url = reverse('product_search', args=['adhesive'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('products', data)
        
        print(f"胶粘剂搜索API测试通过: 找到 {len(data['products'])} 个产品")
        
    def test_moving_range_data(self):
        """测试移动极差数据API"""
        print("测试移动极差数据API...")
        
        # 获取一个存在的产品代码
        sample_product = DryFilmProduct.objects.first()
        if not sample_product:
            print("没有产品数据，跳过测试")
            return
            
        url = reverse('product_moving_range', args=['dryfilm'])
        params = {
            'product_code': sample_product.product_code,
            'test_item': 'solid_content'
        }
        
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('labels', data)
        self.assertIn('data_values', data)
        self.assertIn('moving_ranges', data)
        self.assertIn('statistics', data)
        
        print(f"移动极差API测试通过: 返回 {len(data['data_values'])} 个数据点")
        
    def test_capability_analysis_data(self):
        """测试能力分析数据API"""
        print("测试能力分析数据API...")
        
        # 获取一个存在的产品代码
        sample_product = DryFilmProduct.objects.first()
        if not sample_product:
            print("没有产品数据，跳过测试")
            return
            
        url = reverse('product_capability_analysis', args=['dryfilm'])
        params = {
            'product_code': sample_product.product_code,
            'test_item': 'solid_content'
        }
        
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('histogram', data)
        self.assertIn('normal_distribution', data)
        self.assertIn('statistics', data)
        
        print(f"能力分析API测试通过: 返回统计数据和分布信息")

def run_api_tests():
    """运行所有API测试"""
    print("=" * 60)
    print("质检管理系统API功能测试")
    print("=" * 60)
    
    # 创建测试实例
    test_case = APITestCase()
    test_case.setUp()
    
    tests = [
        test_case.test_get_product_data_dryfilm,
        test_case.test_get_product_data_adhesive,
        test_case.test_search_products_dryfilm,
        test_case.test_search_products_adhesive,
        test_case.test_moving_range_data,
        test_case.test_capability_analysis_data
    ]
    
    results = []
    for test in tests:
        try:
            test()
            results.append(True)
        except Exception as e:
            print(f"测试 {test.__name__} 失败: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("API测试结果汇总:")
    print("=" * 60)
    
    for i, result in enumerate(results):
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{tests[i].__name__}: {status}")
    
    all_passed = all(results)
    print(f"\n总体结果: {'所有API测试通过!' if all_passed else '部分API测试失败!'}")
    
    return all_passed

if __name__ == "__main__":
    run_api_tests()
