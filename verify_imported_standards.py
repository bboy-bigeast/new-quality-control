#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quality_control.settings')
django.setup()

from raw_materials.models import RawMaterialStandard

def verify_imported_standards():
    """
    验证导入的原料标准数据
    """
    print("开始验证导入的原料标准数据...")
    
    # 获取所有导入的原料标准记录
    standards = RawMaterialStandard.objects.all()
    total_count = standards.count()
    
    print(f"数据库中总共有 {total_count} 条原料标准记录")
    
    if total_count == 0:
        print("没有找到任何原料标准记录，请检查导入过程")
        return
    
    # 按原料名称分组统计
    materials = {}
    for standard in standards:
        if standard.material_name not in materials:
            materials[standard.material_name] = []
        materials[standard.material_name].append(standard)
    
    print(f"\n按原料名称统计:")
    for material_name, standards_list in materials.items():
        print(f"  {material_name}: {len(standards_list)} 条标准")
    
    # 按检测项目统计
    test_items = {}
    for standard in standards:
        if standard.test_item not in test_items:
            test_items[standard.test_item] = 0
        test_items[standard.test_item] += 1
    
    print(f"\n按检测项目统计:")
    for test_item, count in test_items.items():
        print(f"  {test_item}: {count} 条标准")
    
    # 显示前10条记录的详细信息
    print(f"\n前10条记录的详细信息:")
    for i, standard in enumerate(standards[:10]):
        print(f"  {i+1}. {standard.material_name} - {standard.test_item}: "
              f"下限={standard.lower_limit}, 上限={standard.upper_limit}, "
              f"目标值={standard.target_value}")
    
    # 检查是否有空值或异常数据
    print(f"\n数据完整性检查:")
    null_lower = standards.filter(lower_limit__isnull=True).count()
    null_upper = standards.filter(upper_limit__isnull=True).count()
    null_target = standards.filter(target_value__isnull=True).count()
    
    print(f"  下限为空的记录: {null_lower}")
    print(f"  上限为空的记录: {null_upper}")
    print(f"  目标值为空的记录: {null_target}")
    
    # 检查标准类型分布
    standard_types = standards.values_list('standard_type', flat=True).distinct()
    print(f"  标准类型: {list(standard_types)}")
    
    print(f"\n验证完成!")

if __name__ == '__main__':
    verify_imported_standards()
