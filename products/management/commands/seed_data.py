from django.core.management.base import BaseCommand
from products.models import DryFilmProduct, AdhesiveProduct, ProductStandard
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = '添加示例数据到数据库'

    def handle(self, *args, **options):
        # 添加产品标准
        self.create_standards()
        
        # 添加干膜产品数据
        self.create_dry_film_products()
        
        # 添加胶粘剂产品标准和数据
        self.create_adhesive_standards()
        self.create_adhesive_products()
        
        self.stdout.write(
            self.style.SUCCESS('成功添加示例数据！')
        )

    def create_standards(self):
        product_codes = ['DF-100', 'DF-200', 'DF-300']
        
        # 为每个产品牌号创建标准
        standards_data = []
        for product_code in product_codes:
            # 外控标准
            standards_data.extend([
                (product_code, 'solid_content', 'external_control', 45.0, 55.0, 50.0),
                (product_code, 'viscosity', 'external_control', 80.0, 120.0, 100.0),
                (product_code, 'acid_value', 'external_control', 60.0, 80.0, 70.0),
                (product_code, 'moisture', 'external_control', 0.1, 0.5, 0.3),
                (product_code, 'residual_monomer', 'external_control', 0.05, 0.15, 0.1),
                
                # 内控标准
                (product_code, 'solid_content', 'internal_control', 48.0, 52.0, 50.0),
                (product_code, 'viscosity', 'internal_control', 90.0, 110.0, 100.0),
                (product_code, 'acid_value', 'internal_control', 65.0, 75.0, 70.0),
                (product_code, 'moisture', 'internal_control', 0.2, 0.4, 0.3),
                (product_code, 'residual_monomer', 'internal_control', 0.08, 0.12, 0.1),
            ])

        for product_code, test_item, standard_type, lower, upper, target in standards_data:
            ProductStandard.objects.get_or_create(
                product_code=product_code,
                test_item=test_item,
                standard_type=standard_type,
                defaults={
                    'lower_limit': lower,
                    'upper_limit': upper,
                    'target_value': target
                }
            )

    def create_dry_film_products(self):
        # 如果已经有数据，就不重复添加
        if DryFilmProduct.objects.exists():
            self.stdout.write('已有干膜产品数据，跳过添加示例数据')
            return

        product_codes = ['DF-100', 'DF-200', 'DF-300']
        production_lines = ['A线', 'B线', 'C线']
        inspectors = ['张三', '李四', '王五', '赵六']
        
        # 创建30天的示例数据
        today = datetime.now().date()
        batch_counter = 1  # 全局批次计数器确保唯一性
        
        for i in range(30):
            test_date = today - timedelta(days=29 - i)
            
            for product_code in product_codes:
                for production_line in production_lines:
                    # 每个产品每天每个产线创建1-2个批次
                    for batch_num in range(1, random.randint(2, 3)):
                        # 使用全局计数器确保批次号唯一
                        batch_number = f"DF{batch_counter:06d}"
                        batch_counter += 1
                        
                        # 生成在标准范围内的随机数据
                        solid_content = round(random.uniform(48.0, 52.0), 2)
                        viscosity = round(random.uniform(90.0, 110.0), 1)
                        acid_value = round(random.uniform(65.0, 75.0), 1)
                        moisture = round(random.uniform(0.2, 0.4), 3)
                        residual_monomer = round(random.uniform(0.08, 0.12), 3)
                        
                        # 随机添加一些异常数据
                        if random.random() < 0.1:  # 10%的概率出现异常
                            if random.choice([True, False]):
                                solid_content = round(random.uniform(44.0, 47.9), 2)
                            else:
                                solid_content = round(random.uniform(52.1, 56.0), 2)
                        
                        DryFilmProduct.objects.create(
                            product_code=product_code,
                            batch_number=batch_number,
                            production_line=production_line,
                            inspector=random.choice(inspectors),
                            test_date=test_date,
                            sample_category='正常样品',
                            remarks='示例数据',
                            appearance='正常',
                            solid_content=solid_content,
                            viscosity=viscosity,
                            acid_value=acid_value,
                            moisture=moisture,
                            residual_monomer=residual_monomer,
                            weight_avg_molecular_weight=round(random.uniform(80000, 120000), 0),
                            pdi=round(random.uniform(1.8, 2.2), 2),
                            color=round(random.uniform(1.0, 3.0), 1),
                            polymerization_inhibitor=round(random.uniform(50, 150), 1),
                            conversion_rate=round(random.uniform(95.0, 99.9), 1),
                            loading_temperature=round(random.uniform(20.0, 30.0), 1),
                            modified_by='系统',
                            modification_reason='自动生成示例数据'
                        )

    def create_adhesive_standards(self):
        """创建胶粘剂产品标准"""
        adhesive_product_codes = ['AD-500', 'AD-600', 'AD-700']
        
        standards_data = []
        for product_code in adhesive_product_codes:
            # 外控标准
            standards_data.extend([
                (product_code, 'solid_content', 'external_control', 45.0, 55.0, 50.0),
                (product_code, 'viscosity', 'external_control', 80.0, 120.0, 100.0),
                (product_code, 'acid_value', 'external_control', 60.0, 80.0, 70.0),
                (product_code, 'moisture', 'external_control', 0.1, 0.5, 0.3),
                (product_code, 'residual_monomer', 'external_control', 0.05, 0.15, 0.1),
                (product_code, 'weight_avg_molecular_weight', 'external_control', 70000, 130000, 100000),
                (product_code, 'pdi', 'external_control', 1.7, 2.3, 2.0),
                (product_code, 'color', 'external_control', 0.5, 3.5, 2.0),
                (product_code, 'initial_tack', 'external_control', 7.0, 13.0, 10.0),
                (product_code, 'peel_strength', 'external_control', 12.0, 28.0, 20.0),
                (product_code, 'high_temperature_holding', 'external_control', 15.0, 45.0, 30.0),
                (product_code, 'room_temperature_holding', 'external_control', 45.0, 75.0, 60.0),
                (product_code, 'constant_load_peel', 'external_control', 3.0, 17.0, 10.0),
                
                # 内控标准
                (product_code, 'solid_content', 'internal_control', 48.0, 52.0, 50.0),
                (product_code, 'viscosity', 'internal_control', 90.0, 110.0, 100.0),
                (product_code, 'acid_value', 'internal_control', 65.0, 75.0, 70.0),
                (product_code, 'moisture', 'internal_control', 0.2, 0.4, 0.3),
                (product_code, 'residual_monomer', 'internal_control', 0.08, 0.12, 0.1),
                (product_code, 'weight_avg_molecular_weight', 'internal_control', 80000, 120000, 100000),
                (product_code, 'pdi', 'internal_control', 1.8, 2.2, 2.0),
                (product_code, 'color', 'internal_control', 1.0, 3.0, 2.0),
                (product_code, 'initial_tack', 'internal_control', 8.0, 12.0, 10.0),
                (product_code, 'peel_strength', 'internal_control', 15.0, 25.0, 20.0),
                (product_code, 'high_temperature_holding', 'internal_control', 20.0, 40.0, 30.0),
                (product_code, 'room_temperature_holding', 'internal_control', 50.0, 70.0, 60.0),
                (product_code, 'constant_load_peel', 'internal_control', 5.0, 15.0, 10.0),
            ])

        for product_code, test_item, standard_type, lower, upper, target in standards_data:
            ProductStandard.objects.get_or_create(
                product_code=product_code,
                test_item=test_item,
                standard_type=standard_type,
                defaults={
                    'lower_limit': lower,
                    'upper_limit': upper,
                    'target_value': target
                }
            )

    def create_adhesive_products(self):
        """创建胶粘剂产品数据"""
        # 如果已经有数据，就不重复添加
        if AdhesiveProduct.objects.exists():
            self.stdout.write('已有胶粘剂产品数据，跳过添加示例数据')
            return

        product_codes = ['AD-500', 'AD-600', 'AD-700']
        production_lines = ['A线', 'B线', 'C线']
        physical_inspectors = ['张三', '李四', '王五', '赵六']
        tape_inspectors = ['钱七', '孙八', '周九', '吴十']
        
        # 创建30天的示例数据
        today = datetime.now().date()
        batch_counter = 1  # 全局批次计数器确保唯一性
        
        for i in range(30):
            test_date = today - timedelta(days=29 - i)
            
            for product_code in product_codes:
                for production_line in production_lines:
                    # 每个产品每天每个产线创建1-2个批次
                    for batch_num in range(1, random.randint(2, 3)):
                        # 使用全局计数器确保批次号唯一
                        batch_number = f"AD{batch_counter:06d}"
                        batch_counter += 1
                        
                        # 生成在标准范围内的随机数据
                        solid_content = round(random.uniform(48.0, 52.0), 2)
                        viscosity = round(random.uniform(90.0, 110.0), 1)
                        acid_value = round(random.uniform(65.0, 75.0), 1)
                        moisture = round(random.uniform(0.2, 0.4), 3)
                        residual_monomer = round(random.uniform(0.08, 0.12), 3)
                        
                        # 胶带性能数据
                        initial_tack = round(random.uniform(8.0, 12.0), 1)
                        peel_strength = round(random.uniform(15.0, 25.0), 1)
                        high_temperature_holding = round(random.uniform(20.0, 40.0), 1)
                        room_temperature_holding = round(random.uniform(50.0, 70.0), 1)
                        constant_load_peel = round(random.uniform(5.0, 15.0), 1)
                        
                        # 随机添加一些异常数据
                        if random.random() < 0.1:  # 10%的概率出现异常
                            if random.choice([True, False]):
                                peel_strength = round(random.uniform(10.0, 14.9), 1)
                            else:
                                peel_strength = round(random.uniform(25.1, 30.0), 1)
                        
                        AdhesiveProduct.objects.create(
                            product_code=product_code,
                            batch_number=batch_number,
                            production_line=production_line,
                            physical_inspector=random.choice(physical_inspectors),
                            tape_inspector=random.choice(tape_inspectors),
                            physical_test_date=test_date,
                            tape_test_date=test_date,
                            sample_category='正常样品',
                            remarks='示例数据',
                            appearance='正常',
                            solid_content=solid_content,
                            viscosity=viscosity,
                            acid_value=acid_value,
                            moisture=moisture,
                            residual_monomer=residual_monomer,
                            weight_avg_molecular_weight=round(random.uniform(80000, 120000), 0),
                            pdi=round(random.uniform(1.8, 2.2), 2),
                            color=round(random.uniform(1.0, 3.0), 1),
                            initial_tack=initial_tack,
                            peel_strength=peel_strength,
                            high_temperature_holding=high_temperature_holding,
                            room_temperature_holding=room_temperature_holding,
                            constant_load_peel=constant_load_peel,
                            modified_by='系统',
                            modification_reason='自动生成示例数据'
                        )
