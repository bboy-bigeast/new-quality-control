from django.db import models
from django.utils import timezone
import json


class RawMaterialStandard(models.Model):
    """原料标准模型"""
    STANDARD_TYPE_CHOICES = [
        ('external_control', '外控标准'),
        ('internal_control', '内控标准'),
        ('supplier_standard', '供应商标准'),
    ]
    
    TEST_ITEM_CHOICES = [
        ('appearance', '外观'),
        ('purity', '纯度'),
        ('peak_position', '出峰位置'),
        ('inhibitor_content', '阻聚剂含量'),
        ('moisture_content', '水分含量'),
        ('color', '色度'),
        ('ethanol_content', '乙醇含量'),
        ('acidity', '酸度'),
    ]
    
    material_name = models.CharField(max_length=100, verbose_name='原料名称')
    test_item = models.CharField(max_length=50, choices=TEST_ITEM_CHOICES, verbose_name='检测项目')
    standard_type = models.CharField(max_length=20, choices=STANDARD_TYPE_CHOICES, verbose_name='标准类型')
    lower_limit = models.FloatField(null=True, blank=True, verbose_name='下限')
    upper_limit = models.FloatField(null=True, blank=True, verbose_name='上限')
    target_value = models.FloatField(null=True, blank=True, verbose_name='目标值')
    supplier = models.CharField(max_length=100, blank=True, verbose_name='供应商')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    modified_by = models.CharField(max_length=50, blank=True, verbose_name='修改人')
    modification_reason = models.TextField(blank=True, verbose_name='修改原因')
    
    class Meta:
        verbose_name = '原料标准'
        verbose_name_plural = '原料标准'
        unique_together = [('material_name', 'test_item', 'standard_type', 'supplier')]
    
    def __str__(self):
        return f"{self.material_name} - {self.get_test_item_display()} - {self.get_standard_type_display()}"


class RawMaterial(models.Model):
    """原料模型"""
    SAMPLE_CATEGORY_CHOICES = [
        ('单批样', '单批样'),
        ('装车样', '装车样'),
        ('掺桶样', '掺桶样'),
    ]
    
    JUDGMENT_STATUS_CHOICES = [
        ('待判定', '待判定'),
        ('合格', '合格'),
        ('不合格', '不合格'),
        ('待复检', '待复检'),
    ]
    
    material_name = models.CharField(max_length=100, verbose_name='原料名称')
    material_batch = models.CharField(max_length=50, unique=True, verbose_name='原料批号')
    inspector = models.CharField(max_length=50, verbose_name='检测人')
    sample_category = models.CharField(max_length=50, choices=SAMPLE_CATEGORY_CHOICES, verbose_name='样品类别')
    test_date = models.DateField(verbose_name='测试日期')
    
    supplier = models.CharField(max_length=100, verbose_name='供应商')
    distributor = models.CharField(max_length=100, blank=True, verbose_name='经销商')
    
    acceptance_form = models.CharField(max_length=100, blank=True, verbose_name='验收单号')
    logistics_form = models.CharField(max_length=100, blank=True, verbose_name='物流单号')
    coa_number = models.CharField(max_length=100, blank=True, verbose_name='COA编号')
    
    final_judgment = models.CharField(max_length=20, blank=True, verbose_name='判定结果')
    judgment_status = models.CharField(max_length=20, choices=JUDGMENT_STATUS_CHOICES, default='待判定', verbose_name='判定状态')
    judgment_details = models.JSONField(default=dict, blank=True, verbose_name='判定详情')
    
    remarks = models.TextField(blank=True, verbose_name='备注')
    
    # 原料质量数据
    appearance = models.CharField(max_length=100, blank=True, verbose_name='外观')
    purity = models.FloatField(null=True, blank=True, verbose_name='纯度')
    peak_position = models.FloatField(null=True, blank=True, verbose_name='出峰位置')
    inhibitor_content = models.FloatField(null=True, blank=True, verbose_name='阻聚剂含量')
    moisture_content = models.FloatField(null=True, blank=True, verbose_name='水分含量')
    color = models.FloatField(null=True, blank=True, verbose_name='色度')
    ethanol_content = models.FloatField(null=True, blank=True, verbose_name='乙醇含量')
    acidity = models.FloatField(null=True, blank=True, verbose_name='酸度')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    modified_by = models.CharField(max_length=50, verbose_name='修改人')
    modification_reason = models.TextField(blank=True, verbose_name='修改原因')
    
    class Meta:
        verbose_name = '原料'
        verbose_name_plural = '原料'
        ordering = ['-test_date', 'material_batch']
    
    def __str__(self):
        return f"{self.material_name} - {self.material_batch}"
    
    def calculate_judgment(self):
        """自动计算原料判定结果"""
        if not self.material_name:
            return
        
        # 获取该原料的所有标准
        standards = RawMaterialStandard.objects.filter(material_name=self.material_name)
        if not standards:
            self.judgment_status = '待判定'
            self.final_judgment = '无标准数据'
            self.judgment_details = {'error': '未找到相关标准'}
            return
        
        judgment_results = []
        all_passed = True
        has_judgment = False
        
        # 检查每个检测项目
        test_fields = [
            ('appearance', '外观'),
            ('purity', '纯度'),
            ('peak_position', '出峰位置'),
            ('inhibitor_content', '阻聚剂含量'),
            ('moisture_content', '水分含量'),
            ('color', '色度'),
            ('ethanol_content', '乙醇含量'),
            ('acidity', '酸度'),
        ]
        
        for field_name, field_label in test_fields:
            value = getattr(self, field_name)
            if value is not None and value != "":
                has_judgment = True
                # 查找对应的标准
                field_standards = standards.filter(test_item=field_name)
                if field_standards.exists():
                    passed = True
                    reasons = []
                    
                    for standard in field_standards:
                        if standard.lower_limit is not None and value < standard.lower_limit:
                            passed = False
                            reasons.append(f"低于{standard.get_standard_type_display()}下限({standard.lower_limit})")
                        if standard.upper_limit is not None and value > standard.upper_limit:
                            passed = False
                            reasons.append(f"高于{standard.get_standard_type_display()}上限({standard.upper_limit})")
                    
                    judgment_results.append({
                        'field': field_name,
                        'label': field_label,
                        'value': value,
                        'passed': passed,
                        'reasons': reasons
                    })
                    
                    if not passed:
                        all_passed = False
        
        if not has_judgment:
            self.judgment_status = '待判定'
            self.final_judgment = '无检测数据'
            self.judgment_details = {'info': '未填写检测数据'}
        elif all_passed:
            self.judgment_status = '合格'
            self.final_judgment = '合格'
            self.judgment_details = {
                'results': judgment_results,
                'summary': '所有检测项目均符合标准'
            }
        else:
            self.judgment_status = '不合格'
            self.final_judgment = '不合格'
            failed_items = [result for result in judgment_results if not result['passed']]
            self.judgment_details = {
                'results': judgment_results,
                'failed_items': failed_items,
                'summary': f'{len(failed_items)}个检测项目不符合标准'
            }
    
    def save(self, *args, **kwargs):
        # 自动计算判定结果
        self.calculate_judgment()
        super().save(*args, **kwargs)


class RawMaterialHistory(models.Model):
    """原料修改历史模型"""
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, verbose_name='原料')
    modified_by = models.CharField(max_length=50, verbose_name='修改人')
    modification_reason = models.TextField(verbose_name='修改原因')
    modified_data = models.JSONField(default=dict, verbose_name='修改数据')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='修改时间')
    
    class Meta:
        verbose_name = '原料修改历史'
        verbose_name_plural = '原料修改历史'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.raw_material} - {self.modified_by} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class RawMaterialStandardHistory(models.Model):
    """原料标准修改历史模型"""
    raw_material_standard = models.ForeignKey(RawMaterialStandard, on_delete=models.CASCADE, verbose_name='原料标准')
    modified_by = models.CharField(max_length=50, verbose_name='修改人')
    modification_reason = models.TextField(verbose_name='修改原因')
    modified_data = models.JSONField(default=dict, verbose_name='修改数据')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='修改时间')
    
    class Meta:
        verbose_name = '原料标准修改历史'
        verbose_name_plural = '原料标准修改历史'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.raw_material_standard} - {self.modified_by} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
