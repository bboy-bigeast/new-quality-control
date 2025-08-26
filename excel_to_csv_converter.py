import pandas as pd
import re

def excel_to_django_csv(input_excel_path, output_csv_path):
    """
    将Excel中的原料标准数据转换为Django模型兼容的CSV格式
    
    参数:
        input_excel_path: 输入的Excel文件路径
        output_csv_path: 输出的CSV文件路径
    """
    # 读取Excel文件
    df = pd.read_excel(input_excel_path)
    
    # 检测项目映射字典
    test_item_mapping = {
        '纯度（%）': 'purity',
        '水分含量（%）': 'moisture_content',
        '阻聚剂含量（ppm）': 'inhibitor_content',
        '色度（Hazen）': 'color',
        '酸度（w%以Ac/AA/MAA计）': 'acidity',
        '乙醇含量（%）': 'ethanol_content',
        '甲醇含量（%）': 'ethanol_content',  # 映射到乙醇字段
        '丁醇含量（%）': 'ethanol_content',  # 映射到乙醇字段
    }
    
    # 解析标准值的函数
    def parse_standard_value(value):
        if pd.isna(value) or value == '/' or value == '—':
            return None, None, None
        
        value_str = str(value).strip()
        
        # 处理范围值 (如 "100～300")
        if '～' in value_str:
            numbers = re.findall(r"[\d.]+", value_str)
            if len(numbers) >= 2:
                return float(numbers[0]), float(numbers[1]), None
            return None, None, None
        
        # 处理下限值 (如 "≥99.5")
        elif '≥' in value_str:
            number = re.search(r"[\d.]+", value_str)
            if number:
                return float(number.group()), None, None
            return None, None, None
        
        # 处理上限值 (如 "≤0.10")
        elif '≤' in value_str:
            number = re.search(r"[\d.]+", value_str)
            if number:
                return None, float(number.group()), None
            return None, None, None
        
        # 处理目标值 (如 "5")
        else:
            try:
                return None, None, float(value_str)
            except ValueError:
                return None, None, None
    
    # 创建结果列表
    results = []
    
    # 处理每一行数据
    for _, row in df.iterrows():
        print(row)
        material_name = row['单体名称']
        
        # 遍历所有可能的检测项目
        for test_item_display, test_item_key in test_item_mapping.items():
            if test_item_display in row:
                value = row[test_item_display]
                
                # 跳过空值或无效值
                if pd.isna(value) or value == '/' or value == '—':
                    continue
                
                # 解析标准值
                lower, upper, target = parse_standard_value(value)
                
                # 添加到结果列表
                results.append({
                    'material_name': material_name,
                    'test_item': test_item_key,
                    'standard_type': 'external_control',
                    'lower_limit': lower,
                    'upper_limit': upper,
                    'target_value': target,
                    'supplier': ''
                })
    
    # 创建DataFrame并保存为CSV
    result_df = pd.DataFrame(results)
    result_df.to_csv(output_csv_path, index=False, encoding='utf-8')
    
    print(f"转换完成！共生成 {len(results)} 条记录")
    print(f"CSV文件已保存至: {output_csv_path}")

# 使用示例
if __name__ == "__main__":
    input_file = "QRAJF-QA-053 原料质量标准库-20250515.xlsx"  # 替换为你的Excel文件路径
    output_file = "raw_material_standards.csv"
    
    excel_to_django_csv(input_file, output_file)