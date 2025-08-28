#!/usr/bin/env python
import os
import sys
import django
import pandas as pd
import re

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quality_control.settings')
django.setup()

from raw_materials.models import RawMaterialStandard

def parse_value_range(value_str):
    """
    解析数值范围字符串，如 '≥99.2', '≤0.10', '100～300'
    返回 (lower_limit, upper_limit, target_value)
    """
    if pd.isna(value_str) or value_str == '/' or value_str == '':
        return None, None, None
    
    value_str = str(value_str).strip()
    
    # 处理 ≥ 格式
    if value_str.startswith('≥'):
        try:
            value = float(value_str[1:])
            return value, None, value
        except ValueError:
            return None, None, None
    
    # 处理 ≤ 格式
    elif value_str.startswith('≤'):
        try:
            value = float(value_str[1:])
            return None, value, value
        except ValueError:
            return None, None, None
    
    # 处理 ～ 范围格式
    elif '～' in value_str:
        try:
            parts = value_str.split('～')
            lower = float(parts[0].strip())
            upper = float(parts[1].strip())
            return lower, upper, (lower + upper) / 2
        except (ValueError, IndexError):
            return None, None, None
    
    # 处理 - 范围格式
    elif '-' in value_str and not value_str.startswith('-'):
        try:
            parts = value_str.split('-')
            lower = float(parts[0].strip())
            upper = float(parts[1].strip())
            return lower, upper, (lower + upper) / 2
        except (ValueError, IndexError):
            return None, None, None
    
    # 处理单个数值
    else:
        try:
            value = float(value_str)
            return value, value, value
        except ValueError:
            return None, None, None

def map_test_item(column_name):
    """
    映射Excel列名到模型中的test_item字段
    """
    mapping = {
        '纯度（%）': 'purity',
        '水分含量（%）': 'moisture_content',
        '阻聚剂含量（ppm）': 'inhibitor_content',
        '色度（Hazen）': 'color',
        '乙醇含量': 'ethanol_content',
        '酸度/游离酸': 'acidity',
        '外观': 'appearance'
    }
    
    for key, value in mapping.items():
        if key in column_name:
            return value
    return None

def import_raw_material_standards(excel_file_path):
    """
    导入原料标准数据
    """
    try:
        # 读取原料标准工作表，不跳过标题行
        df = pd.read_excel(excel_file_path, sheet_name='原料标准 ', header=None)
        print(f"成功读取原料标准工作表，共{len(df)}行数据")
        
        # 显示数据信息
        print("前10行数据:")
        print(df.head(10).to_string())
        
        imported_count = 0
        error_count = 0
        
        # 定义列映射 - 根据实际数据分析
        column_mapping = {
            1: ('purity', '纯度（%）'),
            2: ('moisture_content', '水分含量（%）'),
            3: ('inhibitor_content', '阻聚剂含量（ppm）'),
            4: ('color', '色度（Hazen）')
        }
        
        for index, row in df.iterrows():
            # 跳过标题行（第0行）和空行
            if index == 0 or row.isna().all():
                continue
                
            # 处理具体标准数据行
            if not pd.isna(row[0]):  # 第0列是单体名称
                try:
                    material_name = row[0]
                    standard_type = 'external_control'  # 默认为外控标准
                    
                    print(f"处理原料: {material_name}, 标准类型: {standard_type}")
                    
                    # 处理每个检测项目
                    for col_idx, (test_item, col_desc) in column_mapping.items():
                        if col_idx < len(row) and not pd.isna(row[col_idx]):
                            value_str = row[col_idx]
                            
                            # 解析数值范围
                            lower, upper, target = parse_value_range(value_str)
                            
                            if lower is not None or upper is not None:
                                # 创建原料标准记录
                                standard = RawMaterialStandard(
                                    material_name=material_name,  # 直接使用单体名称
                                    test_item=test_item,
                                    standard_type=standard_type,
                                    lower_limit=lower,
                                    upper_limit=upper,
                                    target_value=target,
                                    supplier='',
                                    modified_by='系统导入',
                                    modification_reason='从Excel文件导入原料标准数据'
                                )
                                
                                try:
                                    standard.save()
                                    imported_count += 1
                                    print(f"  导入: {test_item} = {value_str}")
                                except Exception as e:
                                    print(f"  保存标准时出错: {str(e)}")
                                    error_count += 1
                    
                except Exception as e:
                    print(f"处理第{index+1}行时出错: {str(e)}")
                    error_count += 1
                    continue
        
        print(f"\n导入完成!")
        print(f"成功导入: {imported_count} 条标准记录")
        print(f"错误: {error_count} 条记录")
        
        return imported_count, error_count
        
    except Exception as e:
        print(f"读取Excel文件时出错: {str(e)}")
        return 0, 1

if __name__ == '__main__':
    excel_file_path = 'QRAJF-QA-053 原料质量标准库-20250515.xlsx'
    
    if not os.path.exists(excel_file_path):
        print(f"错误: 文件 {excel_file_path} 不存在")
        sys.exit(1)
    
    print(f"开始导入原料标准数据: {excel_file_path}")
    imported, errors = import_raw_material_standards(excel_file_path)
    
    if imported > 0:
        print("\n导入成功！您可以在原料标准管理中查看导入的数据。")
    else:
        print("\n没有数据被导入，请检查Excel文件格式和内容。")
