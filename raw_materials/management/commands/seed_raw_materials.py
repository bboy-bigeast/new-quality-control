from django.core.management.base import BaseCommand
from raw_materials.models import RawMaterial, RawMaterialStandard
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = '添加50个原料测试数据'

    def handle(self, *args, **options):
        # 如果已经有数据，先删除
        if RawMaterial.objects.exists():
            self.stdout.write('已有原料数据，先删除旧数据...')
            RawMaterial.objects.all().delete()
        
        if RawMaterialStandard.objects.exists():
            self.stdout.write('已有原料标准数据，先删除旧数据...')
            RawMaterialStandard.objects.all().delete()

        # 创建原料标准
        self.create_standards()
        
        # 创建50个原料测试数据
        self.create_raw_materials()
        
        self.stdout.write(
            self.style.SUCCESS('成功添加50个原料测试数据！')
        )

    def create_standards(self):
        """创建原料标准"""
        materials = ['丙烯酸', '甲基丙烯酸甲酯', '乙酸乙酯', '过氧化苯甲酰', '偶氮二异丁腈']
        suppliers = ['巴斯夫', '陶氏化学', '杜邦', '三菱化学', 'LG化学']
        
        standards_data = []
        
        for material in materials:
            for supplier in suppliers:
                # 外控标准
                standards_data.extend([
                    (material, 'purity', 'external_control', 98.5, 99.9, 99.2, supplier),
                    (material, 'inhibitor_content', 'external_control', 10, 50, 30, supplier),
                    (material, 'moisture_content', 'external_control', 0.01, 0.1, 0.05, supplier),
                    (material, 'color', 'external_control', 5, 20, 10, supplier),
                    (material, 'acidity', 'external_control', 0.01, 0.1, 0.05, supplier),
                    
                    # 内控标准
                    (material, 'purity', 'internal_control', 99.0, 99.8, 99.4, supplier),
                    (material, 'inhibitor_content', 'internal_control', 15, 45, 30, supplier),
                    (material, 'moisture_content', 'internal_control', 0.02, 0.08, 0.05, supplier),
                    (material, 'color', 'internal_control', 8, 15, 10, supplier),
                    (material, 'acidity', 'internal_control', 0.02, 0.08, 0.05, supplier),
                ])

        for material_name, test_item, standard_type, lower, upper, target, supplier in standards_data:
            RawMaterialStandard.objects.get_or_create(
                material_name=material_name,
                test_item=test_item,
                standard_type=standard_type,
                supplier=supplier,
                defaults={
                    'lower_limit': lower,
                    'upper_limit': upper,
                    'target_value': target,
                    'modified_by': '系统',
                    'modification_reason': '自动生成标准数据'
                }
            )

    def create_raw_materials(self):
        """创建50个原料测试数据"""
        materials = ['丙烯酸', '甲基丙烯酸甲酯', '乙酸乙酯', '过氧化苯甲酰', '偶氮二异丁腈']
        suppliers = ['巴斯夫', '陶氏化学', '杜邦', '三菱化学', 'LG化学']
        distributors = ['上海化工', '北京石化', '广州试剂', '深圳材料', '天津化学']
        inspectors = ['张三', '李四', '王五', '赵六', '钱七']
        sample_categories = ['单批样', '装车样', '掺桶样']
        
        # 创建50天的数据
        today = datetime.now().date()
        batch_counter = 1
        
        for i in range(50):
            test_date = today - timedelta(days=49 - i)
            
            for material in materials:
                # 每个原料每天创建1个批次
                batch_number = f"RM{batch_counter:06d}"
                batch_counter += 1
                
                supplier = random.choice(suppliers)
                distributor = random.choice(distributors)
                
                # 生成在标准范围内的随机数据
                purity = round(random.uniform(99.0, 99.8), 3)
                inhibitor_content = round(random.uniform(15, 45), 1)
                moisture_content = round(random.uniform(0.02, 0.08), 3)
                color = round(random.uniform(8, 15), 1)
                acidity = round(random.uniform(0.02, 0.08), 3)
                
                # 随机添加一些异常数据 (10%的概率)
                if random.random() < 0.1:
                    if random.choice([True, False]):
                        purity = round(random.uniform(98.0, 98.9), 3)  # 低于内控标准
                    else:
                        purity = round(random.uniform(99.9, 100.0), 3)  # 高于内控标准
                
                # 外观描述
                appearances = {
                    '丙烯酸': ['无色透明液体', '微黄色透明液体', '清澈透明'],
                    '甲基丙烯酸甲酯': ['无色透明液体', '水白色', '清澈透明'],
                    '乙酸乙酯': ['无色透明液体', '有水果香味', '清澈透明'],
                    '过氧化苯甲酰': ['白色结晶粉末', '白色粉末', '微黄色粉末'],
                    '偶氮二异丁腈': ['白色结晶粉末', '白色粉末', '微黄色结晶']
                }
                
                raw_material = RawMaterial(
                    material_name=material,
                    material_batch=batch_number,
                    inspector=random.choice(inspectors),
                    sample_category=random.choice(sample_categories),
                    test_date=test_date,
                    supplier=supplier,
                    distributor=distributor,
                    acceptance_form=f"AC{random.randint(1000, 9999)}",
                    logistics_form=f"LG{random.randint(1000, 9999)}",
                    coa_number=f"COA{random.randint(10000, 99999)}",
                    remarks='测试数据',
                    appearance=random.choice(appearances[material]),
                    purity=purity,
                    inhibitor_content=inhibitor_content,
                    moisture_content=moisture_content,
                    color=color,
                    acidity=acidity,
                    modified_by='系统',
                    modification_reason='自动生成测试数据'
                )
                
                raw_material.save()
                
                self.stdout.write(f'创建原料: {material} - {batch_number}')

        self.stdout.write(f'总共创建了 {batch_counter - 1} 个原料测试数据')
