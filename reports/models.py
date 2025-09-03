from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import json
from products.models import DryFilmProduct, AdhesiveProduct, ProductStandard

class InspectionReport(models.Model):
    """检测报告模型"""
    REPORT_TYPES = [
        ('dryfilm', '干膜产品检测报告'),
        ('af11', 'AF11产品检测报告'),
        ('bb1', 'BB1产品检测报告'),
        ('adhesive', '胶粘剂产品检测报告'),
    ]
    
    # 报告基本信息
    report_number = models.CharField(max_length=50, verbose_name="报告编号", unique=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, verbose_name="报告类型")
    product_code = models.CharField(max_length=50, verbose_name="产品牌号")
    batch_number = models.CharField(max_length=50, verbose_name="产品批号")
    production_date = models.DateField(verbose_name="生产日期")
    inspector = models.CharField(max_length=50, verbose_name="检验人")
    reviewer = models.CharField(max_length=50, blank=True, verbose_name="审核人")
    report_date = models.DateField(auto_now_add=True, verbose_name="报告日期")
    
    # 检测项目选择
    selected_items = models.JSONField(verbose_name="选择的检测项目", default=list)
    
    # 检测结果和结论
    test_results = models.JSONField(verbose_name="检测结果", default=list)
    conclusion = models.CharField(max_length=100, verbose_name="判定结论", blank=True)
    remarks = models.TextField(blank=True, verbose_name="备注")
    
    # 签名信息
    inspector_signature = models.CharField(max_length=100, blank=True, verbose_name="检验人签名")
    reviewer_signature = models.CharField(max_length=100, blank=True, verbose_name="审核人签名")
    review_date = models.DateField(null=True, blank=True, verbose_name="审核日期")
    
    # 状态管理
    status = models.CharField(max_length=20, default='draft', verbose_name="报告状态", 
                             choices=[('draft', '草稿'), ('published', '已发布')])
    
    class Meta:
        verbose_name = "检测报告"
        verbose_name_plural = "检测报告"
        ordering = ['-report_date', '-report_number']
    
    def __str__(self):
        return f"{self.report_number} - {self.product_code} - {self.batch_number}"
    
    def generate_report_number(self):
        """自动生成报告编号"""
        if not self.report_number:
            from django.conf import settings
            from django.utils import timezone
            import uuid
            
            # 生成唯一报告编号：基础版本 + 时间戳 + 随机后缀
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            random_suffix = str(uuid.uuid4())[:8]  # 取UUID的前8位作为随机后缀
            self.report_number = f"{timestamp}-{random_suffix}"
    
    def save(self, *args, **kwargs):
        # 自动生成报告编号
        if not self.report_number:
            self.generate_report_number()
        
        # 自动填充产品信息
        if self.batch_number and not self.product_code:
            self._fill_product_info()
        
        # 自动生成检测结果（包含产品模型中的所有检测项目）
        if self.batch_number and not self.test_results:
            self._generate_test_results()
        
        super().save(*args, **kwargs)
    
    def _fill_product_info(self):
        """根据批号自动填充产品信息"""
        try:
            if self.report_type in ['dryfilm', 'af11', 'bb1']:
                # AF11和BB1产品也使用DryFilmProduct模型
                product = DryFilmProduct.objects.get(batch_number=self.batch_number)
                self.product_code = product.product_code
                self.production_date = product.test_date
                if not self.inspector:
                    self.inspector = product.inspector
            elif self.report_type == 'adhesive':
                product = AdhesiveProduct.objects.get(batch_number=self.batch_number)
                self.product_code = product.product_code
                self.production_date = product.physical_test_date
                if not self.inspector:
                    self.inspector = product.physical_inspector
        except (DryFilmProduct.DoesNotExist, AdhesiveProduct.DoesNotExist):
            pass
    
    def _generate_test_results(self):
        """根据用户选择的检测项目生成检测结果"""
        results = []
        
        try:
            # 获取产品数据
            if self.report_type in ['dryfilm', 'af11', 'bb1']:
                # AF11和BB1产品也使用DryFilmProduct模型
                product = DryFilmProduct.objects.get(batch_number=self.batch_number)
            elif self.report_type == 'adhesive':
                product = AdhesiveProduct.objects.get(batch_number=self.batch_number)
            else:
                return
            
            # 获取产品标准
            standards = ProductStandard.objects.filter(product_code=self.product_code)
            
            # 遍历用户选择的检测项目
            for selected_item in self.selected_items:
                item_name = selected_item.get('name')
                if not item_name:
                    continue
                
                # 获取检测值
                test_value = getattr(product, item_name, None)
                
                # 获取标准信息
                standard = standards.filter(test_item=item_name).first()
                
                result = {
                    'test_item': item_name,
                    'test_value': test_value,
                    'test_condition': standard.test_condition if standard else selected_item.get('test_condition', ''),
                    'unit': standard.unit if standard else selected_item.get('unit', ''),
                    'lower_limit': standard.lower_limit if standard else selected_item.get('lower_limit'),
                    'upper_limit': standard.upper_limit if standard else selected_item.get('upper_limit'),
                    'analysis_method': standard.analysis_method if standard else selected_item.get('analysis_method', ''),
                    'is_qualified': self._check_qualification(test_value, standard) if standard else None
                }
                results.append(result)
            
            self.test_results = results
            
            # 自动生成结论
            self._generate_conclusion(results)
            
        except (DryFilmProduct.DoesNotExist, AdhesiveProduct.DoesNotExist):
            pass
    
    def _check_qualification(self, test_value, standard):
        """检查检测值是否合格"""
        if test_value is None:
            return None
        
        if standard.lower_limit is not None and standard.upper_limit is not None:
            return standard.lower_limit <= test_value <= standard.upper_limit
        elif standard.lower_limit is not None:
            return test_value >= standard.lower_limit
        elif standard.upper_limit is not None:
            return test_value <= standard.upper_limit
        
        return None
    
    def _generate_conclusion(self, results):
        """根据检测结果生成结论"""
        if not results:
            return
        
        # 检查是否有不合格项
        has_unqualified = any(
            result['is_qualified'] is False 
            for result in results 
            if result['is_qualified'] is not None
        )
        
        # 检查是否有未完成项
        has_unfinished = any(
            result['test_value'] is None 
            for result in results
        )
        
        if has_unqualified:
            self.conclusion = "不合格"
        elif has_unfinished:
            self.conclusion = "待完成"
        else:
            self.conclusion = "合格"
