from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import json

class DryFilmProduct(models.Model):
    # 产品信息
    product_code = models.CharField(max_length=50, verbose_name="产品牌号", default = 'default')
    batch_number = models.CharField(max_length=50, verbose_name="产品批号", unique=True)
    production_line = models.CharField(max_length=50, verbose_name="产线")
    inspector = models.CharField(max_length=50, verbose_name="检测人")
    test_date = models.DateField(verbose_name="测试日期")
    sample_category = models.CharField(max_length=50, verbose_name="样品类别")
    remarks = models.TextField(blank=True, verbose_name="备注")
    external_final_judgment = models.CharField(max_length=20, verbose_name="外控整体判定", blank=True)
    internal_final_judgment = models.CharField(max_length=20, verbose_name="内控整体判定", blank=True)
    judgment_status = models.CharField(max_length=20, verbose_name="判定状态", default="待判定")
    judgment_details = models.JSONField(verbose_name="判定详情", default=dict, blank=True)
    
    # 产品数据
    appearance = models.CharField(max_length=100, blank=True, verbose_name="外观")
    solid_content = models.FloatField(null=True, blank=True, verbose_name="固含")
    viscosity = models.FloatField(null=True, blank=True, verbose_name="粘度")
    acid_value = models.FloatField(null=True, blank=True, verbose_name="酸值")
    moisture = models.FloatField(null=True, blank=True, verbose_name="水分")
    residual_monomer = models.FloatField(null=True, blank=True, verbose_name="残单")
    weight_avg_molecular_weight = models.FloatField(null=True, blank=True, verbose_name="重均分子量")
    pdi = models.FloatField(null=True, blank=True, verbose_name="PDI")
    color = models.FloatField(null=True, blank=True, verbose_name="色度")
    polymerization_inhibitor = models.FloatField(null=True, blank=True, verbose_name="阻聚剂")
    conversion_rate = models.FloatField(null=True, blank=True, verbose_name="转化率")
    loading_temperature = models.FloatField(null=True, blank=True, verbose_name="装车温度")
    
    # 修改日志
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    modified_by = models.CharField(max_length=50, verbose_name="修改人")
    modification_reason = models.TextField(blank=True, verbose_name="修改原因")
    
    class Meta:
        verbose_name = "干膜产品"
        verbose_name_plural = "干膜产品"
        ordering = ['-test_date', 'batch_number']
    
    def __str__(self):
        return f"{self.product_code} - {self.batch_number}"

    def save(self, *args, **kwargs):
        # 检查是否是更新操作
        is_update = self.pk is not None
        
        # 如果是更新操作，获取原始数据用于比较
        if is_update:
            try:
                original_obj = DryFilmProduct.objects.get(pk=self.pk)
                changed_fields = []
                modified_data = {}
                
                # 检查哪些字段被修改了
                for field in self._meta.fields:
                    field_name = field.name
                    if field_name not in ['created_at', 'updated_at', 'modified_by', 'modification_reason']:
                        original_value = getattr(original_obj, field_name)
                        new_value = getattr(self, field_name)
                        
                        if original_value != new_value:
                            # 格式化字段显示名称
                            field_verbose = field.verbose_name if hasattr(field, 'verbose_name') else field_name
                            changed_fields.append(f"{field_verbose}: {original_value} → {new_value}")
                            modified_data[field_name] = {
                                'old': original_value,
                                'new': new_value
                            }
                
                # 如果有字段被修改，创建历史记录
                if changed_fields:
                    # 自动生成修改描述
                    if not self.modification_reason:
                        self.modification_reason = f"自动检测到修改：{'; '.join(changed_fields)}"
                    
                    # 创建历史记录
                    DryFilmProductHistory.objects.create(
                        dryfilm_product=self,
                        modified_by=self.modified_by if self.modified_by else 'system',
                        modification_reason=self.modification_reason,
                        modified_data=modified_data
                    )
                    
            except DryFilmProduct.DoesNotExist:
                # 如果是新对象，不需要创建历史记录
                pass
        
        # 自动计算整体判定
        self.calculate_final_judgments()
        super().save(*args, **kwargs)

    def calculate_final_judgments(self):
        from products.models import ProductStandard
        
        # 获取标准
        external_standards = ProductStandard.objects.filter(
            product_code=self.product_code, 
            standard_type='external_control'
        )
        internal_standards = ProductStandard.objects.filter(
            product_code=self.product_code, 
            standard_type='internal_control'
        )
        
        judgment_details = {
            'external': {'standards_count': external_standards.count(), 'unfinished_items': [], 'failed_items': []},
            'internal': {'standards_count': internal_standards.count(), 'unfinished_items': [], 'failed_items': []}
        }
        
        # 外控整体判定
        if external_standards.exists():
            has_unfinished = False
            all_qualified = True
            
            for standard in external_standards:
                actual_value = getattr(self, standard.test_item, None)
                
                # 检查数据完整性
                if actual_value is None or (isinstance(actual_value, (int, float)) and actual_value == 0):
                    has_unfinished = True
                    judgment_details['external']['unfinished_items'].append(standard.test_item)
                    continue
                    
                # 检查合格性
                if not (standard.lower_limit <= actual_value <= standard.upper_limit):
                    all_qualified = False
                    judgment_details['external']['failed_items'].append({
                        'item': standard.test_item,
                        'value': actual_value,
                        'lower_limit': standard.lower_limit,
                        'upper_limit': standard.upper_limit
                    })
            
            if has_unfinished:
                self.external_final_judgment = "外控未完成"
                self.judgment_status = "待判定"
            elif all_qualified:
                self.external_final_judgment = "外控合格"
                self.judgment_status = "已完成"
            else:
                self.external_final_judgment = "外控不合格"
                self.judgment_status = "已完成"
        else:
            self.external_final_judgment = "无外控标准"
            self.judgment_status = "已完成"
        
        # 内控整体判定
        if internal_standards.exists():
            has_unfinished = False
            all_qualified = True
            
            for standard in internal_standards:
                actual_value = getattr(self, standard.test_item, None)
                
                # 检查数据完整性
                if actual_value is None or (isinstance(actual_value, (int, float)) and actual_value == 0):
                    has_unfinished = True
                    judgment_details['internal']['unfinished_items'].append(standard.test_item)
                    continue
                    
                # 检查合格性
                if not (standard.lower_limit <= actual_value <= standard.upper_limit):
                    all_qualified = False
                    judgment_details['internal']['failed_items'].append({
                        'item': standard.test_item,
                        'value': actual_value,
                        'lower_limit': standard.lower_limit,
                        'upper_limit': standard.upper_limit
                    })
            
            if has_unfinished:
                self.internal_final_judgment = "内控未完成"
                self.judgment_status = "待判定"
            elif all_qualified:
                self.internal_final_judgment = "内控合格"
                self.judgment_status = "已完成"
            else:
                self.internal_final_judgment = "内控不合格"
                self.judgment_status = "已完成"
        else:
            self.internal_final_judgment = "无内控标准"
            self.judgment_status = "已完成"
        
        self.judgment_details = judgment_details

class ProductStandard(models.Model):
    TEST_ITEMS = [
        ('appearance', '外观'),
        ('solid_content', '固含'),
        ('viscosity', '粘度'),
        ('acid_value', '酸值'),
        ('moisture', '水分'),
        ('residual_monomer', '残单'),
        ('weight_avg_molecular_weight', '重均分子量'),
        ('pdi', 'PDI'),
        ('color', '色度'),
    ]
    
    STANDARD_TYPES = [
        ('external_control', '外控标准'),
        ('internal_control', '内控标准'),
    ]
    
    product_code = models.CharField(max_length=50, verbose_name="产品牌号", default="DF-100")
    test_item = models.CharField(max_length=50, choices=TEST_ITEMS, verbose_name="检测项目")
    standard_type = models.CharField(max_length=20, choices=STANDARD_TYPES, verbose_name="标准类型")
    lower_limit = models.FloatField(null=True, blank=True, verbose_name="下限")
    upper_limit = models.FloatField(null=True, blank=True, verbose_name="上限")
    target_value = models.FloatField(null=True, blank=True, verbose_name="目标值")
    
    # 修改日志
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    modified_by = models.CharField(max_length=50, verbose_name="修改人", blank=True)
    modification_reason = models.TextField(blank=True, verbose_name="修改原因")
    
    class Meta:
        verbose_name = "产品标准"
        verbose_name_plural = "产品标准"
        unique_together = ['product_code', 'test_item', 'standard_type']
    
    def __str__(self):
        return f"{self.product_code} - {self.get_test_item_display()} - {self.get_standard_type_display()}"

class ProductStandardHistory(models.Model):
    """产品标准修改历史记录"""
    product_standard = models.ForeignKey(ProductStandard, on_delete=models.CASCADE, verbose_name="产品标准")
    modified_by = models.CharField(max_length=50, verbose_name="修改人")
    modification_reason = models.TextField(verbose_name="修改原因")
    modified_data = models.JSONField(verbose_name="修改数据", default=dict)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="修改时间")
    
    class Meta:
        verbose_name = "产品标准修改历史"
        verbose_name_plural = "产品标准修改历史"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product_standard} - {self.modified_by} - {self.created_at}"


class DryFilmProductHistory(models.Model):
    """干膜产品修改历史记录"""
    dryfilm_product = models.ForeignKey(DryFilmProduct, on_delete=models.CASCADE, verbose_name="干膜产品")
    modified_by = models.CharField(max_length=50, verbose_name="修改人")
    modification_reason = models.TextField(verbose_name="修改原因")
    modified_data = models.JSONField(verbose_name="修改数据", default=dict)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="修改时间")
    
    class Meta:
        verbose_name = "干膜产品修改历史"
        verbose_name_plural = "干膜产品修改历史"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.dryfilm_product} - {self.modified_by} - {self.created_at}"
