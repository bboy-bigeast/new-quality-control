#!/usr/bin/env python
"""
原料管理系统测试脚本
用于验证原料管理功能是否正常工作
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quality_control.settings')
django.setup()

from raw_materials.models import RawMaterial, RawMaterialStandard
from django.contrib.auth.models import User
from datetime import datetime

def test_raw_material_creation():
    """测试原料创建功能"""
    print("=== 测试原料创建功能 ===")
    
    try:
        # 创建测试原料
        material = RawMaterial.objects.create(
            material_name="测试原料A",
            material_batch="TEST-2024-001",
            sample_category="单批样",
            supplier="测试供应商",
            inspector="测试人员",
            test_date=datetime.now().date(),
            judgment_status="合格",
            purity=99.8,
            moisture_content=0.05,
            remarks="这是一个测试原料",
            modified_by="测试系统"
        )
        
        print(f"✅ 原料创建成功: {material.material_name} (批号: {material.material_batch})")
        print(f"   判定状态: {material.judgment_status}")
        print(f"   纯度: {material.purity}%")
        print(f"   水分含量: {material.moisture_content}%")
        
        return material
        
    except Exception as e:
        print(f"❌ 原料创建失败: {e}")
        return None

def test_standard_creation():
    """测试标准创建功能"""
    print("\n=== 测试标准创建功能 ===")
    
    try:
        # 创建测试标准
        standard = RawMaterialStandard.objects.create(
            material_name="测试原料A",
            test_item="purity",
            standard_type="internal_control",
            lower_limit=99.5,
            upper_limit=100.0,
            target_value=99.8,
            supplier="测试供应商",
            modified_by="测试系统",
            modification_reason="测试创建标准"
        )
        
        print(f"✅ 标准创建成功: {standard.material_name} (检测项目: {standard.get_test_item_display()})")
        print(f"   标准类型: {standard.get_standard_type_display()}")
        print(f"   下限: {standard.lower_limit}")
        print(f"   上限: {standard.upper_limit}")
        
        return standard
        
    except Exception as e:
        print(f"❌ 标准创建失败: {e}")
        return None

def test_url_routing():
    """测试URL路由配置"""
    print("\n=== 测试URL路由配置 ===")
    
    try:
        from django.urls import reverse, resolve
        
        # 测试原料列表URL
        list_url = reverse('raw_materials:raw_material_list')
        print(f"✅ 原料列表URL: {list_url}")
        
        # 测试原料详情URL
        detail_url = reverse('raw_materials:raw_material_detail', kwargs={'pk': 1})
        print(f"✅ 原料详情URL: {detail_url}")
        
        # 测试标准列表URL
        standards_url = reverse('raw_materials:raw_material_standards')
        print(f"✅ 标准列表URL: {standards_url}")
        
        # 测试仪表板URL
        dashboard_url = reverse('raw_materials:raw_material_dashboard')
        print(f"✅ 仪表板URL: {dashboard_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ URL路由测试失败: {e}")
        return False

def test_admin_registration():
    """测试Admin注册"""
    print("\n=== 测试Admin注册 ===")
    
    try:
        from django.contrib import admin
        from raw_materials.admin import RawMaterialAdmin, RawMaterialStandardAdmin
        
        # 检查模型是否在Admin中注册
        if admin.site.is_registered(RawMaterial):
            print("✅ RawMaterial模型已在Admin注册")
        else:
            print("❌ RawMaterial模型未在Admin注册")
            
        if admin.site.is_registered(RawMaterialStandard):
            print("✅ RawMaterialStandard模型已在Admin注册")
        else:
            print("❌ RawMaterialStandard模型未在Admin注册")
            
        return True
        
    except Exception as e:
        print(f"❌ Admin注册测试失败: {e}")
        return False

def cleanup_test_data():
    """清理测试数据"""
    print("\n=== 清理测试数据 ===")
    
    try:
        # 删除测试原料
        RawMaterial.objects.filter(material_name__startswith="测试").delete()
        print("✅ 测试原料数据已清理")
        
        # 删除测试标准
        RawMaterialStandard.objects.filter(material_name__startswith="测试").delete()
        print("✅ 测试标准数据已清理")
        
    except Exception as e:
        print(f"❌ 数据清理失败: {e}")

def main():
    """主测试函数"""
    print("原料管理系统功能测试")
    print("=" * 50)
    
    # 运行测试
    material = test_raw_material_creation()
    standard = test_standard_creation()
    url_test = test_url_routing()
    admin_test = test_admin_registration()
    
    # 清理测试数据
    cleanup_test_data()
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print(f"原料创建: {'✅' if material else '❌'}")
    print(f"标准创建: {'✅' if standard else '❌'}")
    print(f"URL路由: {'✅' if url_test else '❌'}")
    print(f"Admin注册: {'✅' if admin_test else '❌'}")
    
    if all([material, standard, url_test, admin_test]):
        print("\n🎉 所有测试通过！原料管理系统功能正常。")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查相关配置。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
