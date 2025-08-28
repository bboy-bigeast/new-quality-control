#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quality_control.settings')
django.setup()

from raw_materials.models import RawMaterial
from products.models import DryFilmProduct, AdhesiveProduct

def verify_results():
    print("=== 原料记录判定结果统计 ===")
    raw_materials = RawMaterial.objects.all()
    print(f"总数: {raw_materials.count()}")
    print(f"合格: {raw_materials.filter(judgment_status='合格').count()}")
    print(f"不合格: {raw_materials.filter(judgment_status='不合格').count()}")
    print(f"待判定: {raw_materials.filter(judgment_status='待判定').count()}")
    print()
    
    print("=== 干膜产品判定结果统计 ===")
    dryfilm_products = DryFilmProduct.objects.all()
    print(f"总数: {dryfilm_products.count()}")
    print(f"已完成: {dryfilm_products.filter(judgment_status='已完成').count()}")
    print(f"待判定: {dryfilm_products.filter(judgment_status='待判定').count()}")
    print()
    
    print("=== 胶粘剂产品判定结果统计 ===")
    adhesive_products = AdhesiveProduct.objects.all()
    print(f"总数: {adhesive_products.count()}")
    print(f"已完成: {adhesive_products.filter(judgment_status='已完成').count()}")
    print(f"待判定: {adhesive_products.filter(judgment_status='待判定').count()}")
    print()
    
    # 显示一些示例记录
    print("=== 示例记录（前5条）===")
    print("原料记录示例:")
    for material in raw_materials[:5]:
        print(f"  {material.material_name} - {material.material_batch}: {material.judgment_status}")
    
    print("\n干膜产品示例:")
    for product in dryfilm_products[:5]:
        print(f"  {product.product_code} - {product.batch_number}: {product.judgment_status}")
    
    print("\n胶粘剂产品示例:")
    for product in adhesive_products[:5]:
        print(f"  {product.product_code} - {product.batch_number}: {product.judgment_status}")

if __name__ == "__main__":
    verify_results()
