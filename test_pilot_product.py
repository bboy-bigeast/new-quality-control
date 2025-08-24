#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quality_control.settings')
django.setup()

from products.models import PilotProduct
from django.utils import timezone

def test_pilot_product():
    """测试小试产品功能"""
    print("=" * 50)
    print("测试小试产品功能")
    print("=" * 50)
    
    # 创建测试数据
    test_data = {
        'product_code': '小试产品-001',
        'batch_number': 'TEST-2024-001',
        'production_line': '试验线',
        'inspector': '测试员',
        'test_date': timezone.now().date(),
        'sample_category': '单批样',
        'remarks': '测试用的小试产品数据',
        
        # 产品数据
        'appearance': '透明液体',
        'solid_content': 45.5,
        'viscosity': 1200.0,
        'acid_value': 0.8,
        'moisture': 0.2,
        'residual_monomer': 0.05,
        'weight_avg_molecular_weight': 85000.0,
        'pdi': 2.1,
        'color': 1.5,
        'polymerization_inhibitor': 0.01,
        'conversion_rate': 98.5,
        'loading_temperature': 25.0,
        
        'modified_by': 'system'
    }
    
    try:
        # 创建小试产品
        pilot_product = PilotProduct.objects.create(**test_data)
        print(f"✅ 成功创建小试产品: {pilot_product}")
        
        # 验证数据
        print(f"产品牌号: {pilot_product.product_code}")
        print(f"产品批号: {pilot_product.batch_number}")
        print(f"产线: {pilot_product.production_line}")
        print(f"检测人: {pilot_product.inspector}")
        print(f"测试日期: {pilot_product.test_date}")
        print(f"样品类别: {pilot_product.sample_category}")
        print(f"固含: {pilot_product.solid_content}")
        print(f"粘度: {pilot_product.viscosity}")
        
        # 测试修改功能
        print("\n" + "-" * 30)
        print("测试修改功能")
        print("-" * 30)
        
        pilot_product.solid_content = 46.0
        pilot_product.viscosity = 1250.0
        pilot_product.modified_by = '测试用户'
        pilot_product.save()
        
        print(f"✅ 成功修改小试产品数据")
        print(f"修改后的固含: {pilot_product.solid_content}")
        print(f"修改后的粘度: {pilot_product.viscosity}")
        
        # 检查历史记录
        history_count = pilot_product.pilotproducthistory_set.count()
        print(f"历史记录数量: {history_count}")
        
        if history_count > 0:
            latest_history = pilot_product.pilotproducthistory_set.latest('created_at')
            print(f"最新修改人: {latest_history.modified_by}")
            print(f"修改原因: {latest_history.modification_reason}")
        
        # 测试查询功能
        print("\n" + "-" * 30)
        print("测试查询功能")
        print("-" * 30)
        
        products = PilotProduct.objects.all()
        print(f"总共有 {products.count()} 个小试产品")
        
        for product in products:
            print(f"  - {product.product_code} - {product.batch_number}")
        
        print("\n✅ 所有测试通过！小试产品功能正常")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pilot_product()
