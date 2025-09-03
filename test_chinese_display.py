#!/usr/bin/env python3
"""
测试脚本：验证检测项目中文名称显示问题
"""

import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quality_control.settings')
django.setup()

# 从views.py导入映射
from reports.views import TEST_ITEM_MAPPING

# DryFilmProduct模型的所有检测项目字段
dryfilm_fields = [
    'appearance', 'solid_content', 'viscosity', 'acid_value', 'moisture',
    'residual_monomer', 'weight_avg_molecular_weight', 'pdi', 'color',
    'polymerization_inhibitor', 'conversion_rate', 'loading_temperature',
    'dispersion', 'stability'
]

# AdhesiveProduct模型的所有检测项目字段
adhesive_fields = [
    'appearance', 'solid_content', 'viscosity', 'acid_value', 'moisture',
    'residual_monomer', 'weight_avg_molecular_weight', 'pdi', 'color',
    'initial_tack', 'peel_strength', 'high_temperature_holding',
    'room_temperature_holding', 'constant_load_peel'
]

print("=== 检测项目中英文映射验证 ===")
print(f"映射字典包含 {len(TEST_ITEM_MAPPING)} 个项目")

print("\n=== DryFilmProduct 字段检查 ===")
for field in dryfilm_fields:
    chinese_name = TEST_ITEM_MAPPING.get(field, "未找到映射")
    print(f"{field}: {chinese_name}")

print("\n=== AdhesiveProduct 字段检查 ===")
for field in adhesive_fields:
    chinese_name = TEST_ITEM_MAPPING.get(field, "未找到映射")
    print(f"{field}: {chinese_name}")

# 检查是否有字段在模型中但不在映射中
print("\n=== 缺失映射的字段 ===")
all_fields = set(dryfilm_fields + adhesive_fields)
mapped_fields = set(TEST_ITEM_MAPPING.keys())
missing_fields = all_fields - mapped_fields

if missing_fields:
    print("以下字段缺少中文映射:")
    for field in missing_fields:
        print(f"  - {field}")
else:
    print("所有字段都有中文映射")

# 检查是否有字段在映射中但不在模型中
extra_fields = mapped_fields - all_fields
if extra_fields:
    print("\n以下字段在映射中但不在模型中:")
    for field in extra_fields:
        print(f"  - {field}")

print(f"\n总计: {len(all_fields)} 个字段, {len(mapped_fields)} 个映射, {len(missing_fields)} 个缺失")
