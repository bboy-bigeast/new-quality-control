import pandas as pd

# 读取Excel文件
excel_file = pd.ExcelFile('QRAJF-QA-053 原料质量标准库-20250515.xlsx')
print('工作表名称:', excel_file.sheet_names)

# 分析原料标准工作表
df = pd.read_excel(excel_file, sheet_name='原料标准 ')
print('\n数据形状:', df.shape)
print('列名:')
for i, col in enumerate(df.columns):
    print(f'  {i}: {repr(col)}')

print('\n前10行数据:')
print(df.head(10).to_string())

print('\n数据统计信息:')
print(df.info())

print('\n唯一原料名称:')
if '项目       溶剂名称' in df.columns:
    print(df['项目       溶剂名称'].unique())
elif '溶剂' in df.columns:
    print(df['溶剂'].unique())
