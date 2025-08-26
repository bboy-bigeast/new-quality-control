import os
import sys
import django
from django.conf import settings

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quality_control.settings')
django.setup()

from raw_materials.models import RawMaterialStandard
import csv

csv_file = 'raw_material_standards.csv'

print('开始导入CSV数据到数据库...')
# 尝试不同的编码方式
encodings = ['utf-8-sig', 'gbk', 'gb2312', 'latin-1', 'cp936']

for encoding in encodings:
    try:
        with open(csv_file, 'r', encoding=encoding) as f:
            reader = csv.DictReader(f)
            records = list(reader)
        print(f'使用编码 {encoding} 成功读取文件')
        break
    except UnicodeDecodeError:
        continue
else:
    print('无法使用任何编码读取CSV文件')
    exit(1)

print(f'准备导入 {len(records)} 条记录')

imported_count = 0
skipped_count = 0

for record in records:
    # 修复编码问题
    material_name = record['material_name'].replace('£¨', '(').replace('£©', ')')
    
    # 检查是否已存在相同记录
    exists = RawMaterialStandard.objects.filter(
        material_name=material_name,
        test_item=record['test_item'],
        standard_type=record.get('standard_type', 'external_control')
    ).exists()
    
    if exists:
        print(f'跳过已存在记录: {material_name} - {record["test_item"]}')
        skipped_count += 1
        continue
    
    # 创建新记录
    standard = RawMaterialStandard(
        material_name=material_name,
        test_item=record['test_item'],
        standard_type=record.get('standard_type', 'external_control'),
        lower_limit=float(record['lower_limit']) if record['lower_limit'] else None,
        upper_limit=float(record['upper_limit']) if record['upper_limit'] else None,
        target_value=float(record['target_value']) if record['target_value'] else None,
        supplier=record.get('supplier', '')
    )
    standard.save()
    imported_count += 1
    print(f'导入记录: {material_name} - {record["test_item"]}')

print(f'导入完成: 成功导入 {imported_count} 条记录, 跳过 {skipped_count} 条重复记录')
