from django.core.management.base import BaseCommand
from django.db import transaction
from products.models import DryFilmProduct, AdhesiveProduct
import time

class Command(BaseCommand):
    help = '批量更新干膜产品和胶粘剂产品的判定结果'

    def add_arguments(self, parser):
        parser.add_argument(
            '--product-type',
            type=str,
            choices=['dryfilm', 'adhesive', 'all'],
            default='all',
            help='要更新的产品类型：dryfilm(干膜产品), adhesive(胶粘剂产品), all(全部)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='每次批量处理的记录数量，默认为100'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='试运行，不实际保存更改'
        )

    def handle(self, *args, **options):
        product_type = options['product_type']
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        
        # 根据产品类型获取相应的记录
        if product_type == 'dryfilm' or product_type == 'all':
            self.update_dryfilm_products(dry_run)
        
        if product_type == 'adhesive' or product_type == 'all':
            self.update_adhesive_products(dry_run)

    def update_dryfilm_products(self, dry_run):
        """更新干膜产品的判定结果"""
        products = DryFilmProduct.objects.all()
        total_count = products.count()
        
        self.stdout.write(
            self.style.SUCCESS(f'找到 {total_count} 条干膜产品记录需要更新判定结果')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('试运行模式：不会实际保存更改')
            )
        
        updated_count = 0
        start_time = time.time()
        
        # 使用事务确保数据一致性
        with transaction.atomic():
            for i, product in enumerate(products):
                # 调用save方法会自动触发calculate_final_judgments()
                if not dry_run:
                    product.save()
                
                updated_count += 1
                
                # 每处理100条记录输出一次进度
                if (i + 1) % 100 == 0:
                    elapsed_time = time.time() - start_time
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'干膜产品 - 已处理 {i + 1}/{total_count} 条记录 '
                            f'({(i + 1) / total_count * 100:.1f}%), '
                            f'耗时: {elapsed_time:.2f}秒'
                        )
                    )
        
        elapsed_time = time.time() - start_time
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'干膜产品试运行完成：将更新 {updated_count} 条记录 '
                    f'(耗时: {elapsed_time:.2f}秒)'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'成功更新 {updated_count} 条干膜产品记录的判定结果 '
                    f'(耗时: {elapsed_time:.2f}秒)'
                )
            )

    def update_adhesive_products(self, dry_run):
        """更新胶粘剂产品的判定结果"""
        products = AdhesiveProduct.objects.all()
        total_count = products.count()
        
        self.stdout.write(
            self.style.SUCCESS(f'找到 {total_count} 条胶粘剂产品记录需要更新判定结果')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('试运行模式：不会实际保存更改')
            )
        
        updated_count = 0
        start_time = time.time()
        
        # 使用事务确保数据一致性
        with transaction.atomic():
            for i, product in enumerate(products):
                # 调用save方法会自动触发calculate_judgments()
                if not dry_run:
                    product.save()
                
                updated_count += 1
                
                # 每处理100条记录输出一次进度
                if (i + 1) % 100 == 0:
                    elapsed_time = time.time() - start_time
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'胶粘剂产品 - 已处理 {i + 1}/{total_count} 条记录 '
                            f'({(i + 1) / total_count * 100:.1f}%), '
                            f'耗时: {elapsed_time:.2f}秒'
                        )
                    )
        
        elapsed_time = time.time() - start_time
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'胶粘剂产品试运行完成：将更新 {updated_count} 条记录 '
                    f'(耗时: {elapsed_time:.2f}秒)'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'成功更新 {updated_count} 条胶粘剂产品记录的判定结果 '
                    f'(耗时: {elapsed_time:.2f}秒)'
                )
            )
