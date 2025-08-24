from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class DryFilmProduct(models.Model):
    # 产品信息
    product_code = models.CharField(max_length=50, verbose_name="产品牌号", default = 'default')
    batch_number = models.CharField(max_length=50, verbose_name="产品批号")
    production_line = models.CharField(max_length=50, verbose_name="产线")
    inspector = models.CharField(max_length=50, verbose_name="检测人")
    test_date = models.DateField(verbose_name="测试日期")
    sample_category = models.CharField(max_length=50, verbose_name="样品类别")
    remarks = models.TextField(blank=True, verbose_name="备注")
    factory_judgment = models.CharField(max_length=20, verbose_name="出厂判定")
    internal_control_judgment = models.CharField(max_length=20, verbose_name="内控判定")
    
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
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "产品标准"
        verbose_name_plural = "产品标准"
        unique_together = ['product_code', 'test_item', 'standard_type']
    
    def __str__(self):
        return f"{self.product_code} - {self.get_test_item_display()} - {self.get_standard_type_display()}"
