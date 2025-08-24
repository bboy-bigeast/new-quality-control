#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
sys.path.append('C:/Users/12719/Desktop/my study/py/projects/newapp/new-quality-control/new-quality-control')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quality_control.settings')
django.setup()

from products.models import ProductStandard

def test_new_fields():
    """测试新添加的字段"""
    print("测试新添加的字段...")
    
    # 创建一个测试产品标准
    standard = ProductStandard.objects.create(
        product_code="TEST001",
        test_item="固含",
        standard_type="内控标准",
        lower_limit=40.0,
        upper_limit=50.0,
        target_value=45.0,
        test_condition="25°C恒温测试",
        unit="%",
        analysis_method="重量法"
    )
    
    print(f"创建的产品标准: {standard}")
    print(f"检测条件: {standard.test_condition}")
    print(f"单位: {standard.unit}")
    print(f"分析方法/标准: {standard.analysis_method}")
    
    # 验证字段值
    assert standard.test_condition == "25°C恒温测试"
    assert standard.unit == "%"
    assert standard.analysis_method == "重量法"
    
    print("所有字段测试通过！")
    
    # 清理测试数据
    standard.delete()
    print("测试数据已清理")

if __name__ == "__main__":
    test_new_fields()
