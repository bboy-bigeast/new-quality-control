#!/usr/bin/env python
"""
测试批量更新功能的脚本
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quality_control.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib import messages
from django.contrib.messages.storage.fallback import FallbackStorage

# 导入Admin类
from raw_materials.admin import RawMaterialAdmin
from products.admin import DryFilmProductAdmin, AdhesiveProductAdmin

# 导入模型
from raw_materials.models import RawMaterial
from products.models import DryFilmProduct, AdhesiveProduct

def test_bulk_update_functionality():
    """测试批量更新功能"""
    print("=" * 50)
    print("测试批量更新功能")
    print("=" * 50)
    
    # 创建测试请求对象
    factory = RequestFactory()
    request = factory.get('/admin/')
    
    # 设置用户和消息存储
    try:
        user = User.objects.first()
        if user:
            request.user = user
        else:
            # 创建测试用户
            user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
            request.user = user
    except:
        request.user = None
    
    # 设置消息存储
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    
    # 测试RawMaterial批量更新
    print("\n1. 测试RawMaterial批量更新:")
    raw_materials = RawMaterial.objects.all()[:3]  # 取前3条记录测试
    if raw_materials.exists():
        admin = RawMaterialAdmin(RawMaterial, None)
        queryset = RawMaterial.objects.filter(pk__in=[m.pk for m in raw_materials])
        print(f"  找到 {queryset.count()} 条RawMaterial记录进行测试")
        
        # 模拟批量更新操作
        try:
            admin.update_judgments_action(request, queryset)
            print("  ✅ RawMaterial批量更新功能正常")
        except Exception as e:
            print(f"  ❌ RawMaterial批量更新失败: {e}")
    else:
        print("  ⚠️ 没有RawMaterial记录可供测试")
    
    # 测试DryFilmProduct批量更新
    print("\n2. 测试DryFilmProduct批量更新:")
    dryfilm_products = DryFilmProduct.objects.all()[:3]
    if dryfilm_products.exists():
        admin = DryFilmProductAdmin(DryFilmProduct, None)
        queryset = DryFilmProduct.objects.filter(pk__in=[p.pk for p in dryfilm_products])
        print(f"  找到 {queryset.count()} 条DryFilmProduct记录进行测试")
        
        try:
            admin.update_judgments_action(request, queryset)
            print("  ✅ DryFilmProduct批量更新功能正常")
        except Exception as e:
            print(f"  ❌ DryFilmProduct批量更新失败: {e}")
    else:
        print("  ⚠️ 没有DryFilmProduct记录可供测试")
    
    # 测试AdhesiveProduct批量更新
    print("\n3. 测试AdhesiveProduct批量更新:")
    adhesive_products = AdhesiveProduct.objects.all()[:3]
    if adhesive_products.exists():
        admin = AdhesiveProductAdmin(AdhesiveProduct, None)
        queryset = AdhesiveProduct.objects.filter(pk__in=[p.pk for p in adhesive_products])
        print(f"  找到 {queryset.count()} 条AdhesiveProduct记录进行测试")
        
        try:
            admin.update_judgments_action(request, queryset)
            print("  ✅ AdhesiveProduct批量更新功能正常")
        except Exception as e:
            print(f"  ❌ AdhesiveProduct批量更新失败: {e}")
    else:
        print("  ⚠️ 没有AdhesiveProduct记录可供测试")
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    test_bulk_update_functionality()
