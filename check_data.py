#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quality_control.settings')
django.setup()

from products.models import DryFilmProduct, AdhesiveProduct, ProductStandard
from django.db.models import Count

def check_data():
    print("=== 数据统计 ===")
    
    # 干膜产品
    print("\n干膜产品:")
    print(f"总数: {DryFilmProduct.objects.count()}")
    print("内控判定状态分布:")
    for status in DryFilmProduct.objects.values('internal_final_judgment').annotate(count=Count('id')).order_by('-count'):
        print(f"  {status['internal_final_judgment']}: {status['count']}")
    
    print("外控判定状态分布:")
    for status in DryFilmProduct.objects.values('external_final_judgment').annotate(count=Count('id')).order_by('-count'):
        print(f"  {status['external_final_judgment']}: {status['count']}")
    
    # 胶粘剂产品
    print("\n胶粘剂产品:")
    print(f"总数: {AdhesiveProduct.objects.count()}")
    print("最终判定状态分布:")
    for status in AdhesiveProduct.objects.values('final_judgment').annotate(count=Count('id')).order_by('-count'):
        print(f"  {status['final_judgment']}: {status['count']}")
    
    # 产品标准
    print("\n产品标准:")
    print(f"总数: {ProductStandard.objects.count()}")
    print("标准类型分布:")
    for std_type in ProductStandard.objects.values('standard_type').annotate(count=Count('id')).order_by('-count'):
        print(f"  {std_type['standard_type']}: {std_type['count']}")

if __name__ == "__main__":
    check_data()
