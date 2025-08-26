#!/usr/bin/env python
import os
import sys
import django
import pandas as pd
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quality_control.settings')
django.setup()

from raw_materials.models import RawMaterial

def import_excel_to_raw_material(excel_file_path):
    """
    将Excel文件中的原料检测数据导入到RawMaterial模型
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(excel_file_path, sheet_name='原料检测数据')
        print(f"成功读取Excel文件，共{len(df)}条记录")
        
        # 显示数据前几行和列名
        print("数据列名:", df.columns.tolist())
        print("\n前5行数据:")
        print(df.head())
        
        # 字段映射关系
        field_mapping = {
            '测试日期': 'test_date',
            '原料名称': 'material_name',
            '供货商': 'supplier',
            '生产商': 'distributor',
            '批号': 'material_batch',
            '纯度（GC）/（%）': 'purity',
            'MEHQ含量（ppm）': 'inhibitor_content',
            '水分含量/（%）': 'moisture_content',
            '酸度/游离酸': 'acidity',
            '色度': 'color',
            '判定结果': 'final_judgment',
            '不合格描述': 'remarks',
            '处置结果': 'remarks',
            '纠防反馈情况': 'remarks'
        }
        
        imported_count = 0
        skipped_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                # 检查必要字段
                if pd.isna(row.get('原料名称')) or pd.isna(row.get('批号')):
                    print(f"跳过第{index+1}行: 缺少原料名称或批号")
                    skipped_count += 1
                    continue
                

                
                # 创建RawMaterial对象
                raw_material = RawMaterial()
                
                # 映射字段
                for excel_field, model_field in field_mapping.items():
                    if excel_field in row and not pd.isna(row[excel_field]):
                        value = row[excel_field]
                        
                        # 特殊处理日期字段
                        if excel_field == '测试日期':
                            if isinstance(value, str):
                                try:
                                    value = datetime.strptime(value, '%Y-%m-%d').date()
                                except ValueError:
                                    value = datetime.strptime(value, '%Y/%m/%d').date()
                            elif hasattr(value, 'date'):
                                value = value.date()
                        
                        # 特殊处理数值字段
                        elif excel_field in ['纯度（GC）/（%）', 'MEHQ含量（ppm）', '水分含量/（%）', '酸度/游离酸', '色度']:
                            try:
                                value = float(value)
                            except (ValueError, TypeError):
                                value = None
                        
                        # 处理备注字段（合并多个字段）
                        elif excel_field in ['不合格描述', '处置结果', '纠防反馈情况']:
                            current_remarks = getattr(raw_material, 'remarks', '') or ''
                            if current_remarks:
                                current_remarks += f"; {excel_field}: {value}"
                            else:
                                current_remarks = f"{excel_field}: {value}"
                            value = current_remarks
                        
                        setattr(raw_material, model_field, value)
                
                # 设置其他必要字段
                raw_material.inspector = '系统导入'
                raw_material.sample_category = '来料'
                raw_material.modified_by = '系统导入'
                raw_material.modification_reason = '从Excel文件导入历史检测数据'
                
                # 保存对象
                raw_material.save()
                imported_count += 1
                
                if imported_count % 100 == 0:
                    print(f"已导入 {imported_count} 条记录...")
                    
            except Exception as e:
                print(f"导入第{index+1}行时出错: {str(e)}")
                error_count += 1
                continue
        
        print(f"\n导入完成!")
        print(f"成功导入: {imported_count} 条记录")
        print(f"跳过: {skipped_count} 条记录 (已存在或缺少必要字段)")
        print(f"错误: {error_count} 条记录")
        
        return imported_count, skipped_count, error_count
        
    except Exception as e:
        print(f"读取Excel文件时出错: {str(e)}")
        return 0, 0, 1

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("用法: python import_excel_to_raw_material.py <excel文件路径>")
        sys.exit(1)
    
    excel_file_path = sys.argv[1]
    
    if not os.path.exists(excel_file_path):
        print(f"错误: 文件 {excel_file_path} 不存在")
        sys.exit(1)
    
    print(f"开始导入Excel文件: {excel_file_path}")
    imported, skipped, errors = import_excel_to_raw_material(excel_file_path)
    
    if imported > 0:
        print("\n导入成功！您可以在原料管理系统中查看导入的数据。")
    else:
        print("\n没有数据被导入，请检查Excel文件格式和内容。")
