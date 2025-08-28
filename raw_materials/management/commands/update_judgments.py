from django.core.management.base import BaseCommand
from django.db import transaction
from raw_materials.models import RawMaterial
import time

class Command(BaseCommand):
    help = '批量更新原料记录的判定结果'

    def add_arguments(self, parser):
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
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        
        # 获取所有需要更新的原料记录
        materials = RawMaterial.objects.all()
        total_count = materials.count()
        
        self.stdout.write(
            self.style.SUCCESS(f'找到 {total_count} 条原料记录需要更新判定结果')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('试运行模式：不会实际保存更改')
            )
        
        updated_count = 0
        start_time = time.time()
        
        # 使用事务确保数据一致性
        with transaction.atomic():
            for i, material in enumerate(materials):
                # 调用save方法会自动触发calculate_judgment()
                if not dry_run:
                    material.save()
                
                updated_count += 1
                
                # 每处理100条记录输出一次进度
                if (i + 1) % 100 == 0:
                    elapsed_time = time.time() - start_time
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'已处理 {i + 1}/{total_count} 条记录 '
                            f'({(i + 1) / total_count * 100:.1f}%), '
                            f'耗时: {elapsed_time:.2f}秒'
                        )
                    )
        
        elapsed_time = time.time() - start_time
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'试运行完成：将更新 {updated_count} 条记录 '
                    f'(耗时: {elapsed_time:.2f}秒)'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'成功更新 {updated_count} 条原料记录的判定结果 '
                    f'(耗时: {elapsed_time:.2f}秒)'
                )
            )
