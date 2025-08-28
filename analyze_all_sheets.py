import pandas as pd

# 读取Excel文件
excel_file = pd.ExcelFile('QRAJF-QA-053 原料质量标准库-20250515.xlsx')
print('所有工作表名称:', excel_file.sheet_names)

# 分析每个工作表
for sheet_name in excel_file.sheet_names:
    print(f'\n=== {sheet_name} ===')
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        print('数据形状:', df.shape)
        print('列名:')
        for i, col in enumerate(df.columns):
            print(f'  {i}: {repr(col)}')
        
        print('\n前3行数据:')
        print(df.head(3).to_string())
        
        print('\n' + '='*50)
        
    except Exception as e:
        print(f"读取工作表 {sheet_name} 时出错: {str(e)}")
