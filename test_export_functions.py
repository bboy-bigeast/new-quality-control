#!/usr/bin/env python
"""
测试脚本用于验证所有数据导出功能
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quality_control.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User

# 导入所有Admin类
from raw_materials.admin import RawMaterialAdmin, RawMaterialStandardAdmin
from products.admin import DryFilmProductAdmin, ProductStandardAdmin, AdhesiveProductAdmin, PilotProductAdmin
from reports.admin import InspectionReportAdmin

# 导入模型
from raw_materials.models import RawMaterial, RawMaterialStandard
from products.models import DryFilmProduct, ProductStandard, AdhesiveProduct, PilotProduct
from reports.models import InspectionReport

def test_export_functions():
    """测试所有导出功能"""
    print("开始测试数据导出功能...")
    
    # 创建模拟请求
    factory = RequestFactory()
    request = factory.get('/admin/')
    request.user = User.objects.first() or User.objects.create_user('testuser', password='testpass')
    
    # 创建Admin实例
    site = AdminSite()
    
    # 测试 raw_materials 模块
    print("\n=== 测试 raw_materials 模块 ===")
    raw_material_admin = RawMaterialAdmin(RawMaterial, site)
    raw_material_standard_admin = RawMaterialStandardAdmin(RawMaterialStandard, site)
    
    # 获取查询集
    raw_materials_qs = RawMaterial.objects.all()[:5]
    standards_qs = RawMaterialStandard.objects.all()[:5]
    
    # 测试CSV导出
    try:
        response = raw_material_admin.export_raw_materials_csv(request, raw_materials_qs)
        print(f"✓ RawMaterial CSV导出成功: {response.status_code}")
    except Exception as e:
        print(f"✗ RawMaterial CSV导出失败: {e}")
    
    try:
        response = raw_material_standard_admin.export_standards_csv(request, standards_qs)
        print(f"✓ RawMaterialStandard CSV导出成功: {response.status_code}")
    except Exception as e:
        print(f"✗ RawMaterialStandard CSV导出失败: {e}")
    
    # 测试 products 模块
    print("\n=== 测试 products 模块 ===")
    dryfilm_admin = DryFilmProductAdmin(DryFilmProduct, site)
    product_standard_admin = ProductStandardAdmin(ProductStandard, site)
    adhesive_admin = AdhesiveProductAdmin(AdhesiveProduct, site)
    pilot_admin = PilotProductAdmin(PilotProduct, site)
    
    dryfilm_qs = DryFilmProduct.objects.all()[:5] if DryFilmProduct.objects.exists() else []
    product_standard_qs = ProductStandard.objects.all()[:5] if ProductStandard.objects.exists() else []
    adhesive_qs = AdhesiveProduct.objects.all()[:5] if AdhesiveProduct.objects.exists() else []
    pilot_qs = PilotProduct.objects.all()[:5] if PilotProduct.objects.exists() else []
    
    # 测试CSV导出
    try:
        if dryfilm_qs:
            response = dryfilm_admin.export_dryfilm_products_csv(request, dryfilm_qs)
            print(f"✓ DryFilmProduct CSV导出成功: {response.status_code}")
        else:
            print("⚠ DryFilmProduct 无数据可测试")
    except Exception as e:
        print(f"✗ DryFilmProduct CSV导出失败: {e}")
    
    try:
        if product_standard_qs:
            response = product_standard_admin.export_product_standards_csv(request, product_standard_qs)
            print(f"✓ ProductStandard CSV导出成功: {response.status_code}")
        else:
            print("⚠ ProductStandard 无数据可测试")
    except Exception as e:
        print(f"✗ ProductStandard CSV导出失败: {e}")
    
    # 测试 reports 模块
    print("\n=== 测试 reports 模块 ===")
    report_admin = InspectionReportAdmin(InspectionReport, site)
    report_qs = InspectionReport.objects.all()[:5] if InspectionReport.objects.exists() else []
    
    try:
        if report_qs:
            response = report_admin.export_reports_csv(request, report_qs)
            print(f"✓ InspectionReport CSV导出成功: {response.status_code}")
        else:
            print("⚠ InspectionReport 无数据可测试")
    except Exception as e:
        print(f"✗ InspectionReport CSV导出失败: {e}")
    
    print("\n=== 测试完成 ===")
    print("请访问Admin后台手动测试Excel导出功能，因为Excel导出需要额外的库支持")

if __name__ == "__main__":
    test_export_functions()
