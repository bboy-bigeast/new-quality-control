from django.contrib import admin
from .models import DryFilmProduct, ProductStandard

@admin.register(DryFilmProduct)
class DryFilmProductAdmin(admin.ModelAdmin):
    list_display = [
        'product_code', 'batch_number', 'production_line', 'inspector', 
        'test_date', 'factory_judgment', 'internal_control_judgment'
    ]
    list_filter = [
        'production_line', 'test_date', 'factory_judgment', 'internal_control_judgment'
    ]
    search_fields = ['product_code', 'batch_number', 'inspector']
    date_hierarchy = 'test_date'
    ordering = ['-test_date', 'batch_number']
    
    fieldsets = (
        ('产品信息', {
            'fields': (
                'product_code', 'batch_number', 'production_line', 
                'inspector', 'test_date', 'sample_category', 'remarks'
            )
        }),
        ('判定结果', {
            'fields': ('factory_judgment', 'internal_control_judgment')
        }),
        ('产品数据', {
            'fields': (
                'appearance', 'solid_content', 'viscosity', 'acid_value',
                'moisture', 'residual_monomer', 'weight_avg_molecular_weight',
                'pdi', 'color', 'polymerization_inhibitor', 'conversion_rate',
                'loading_temperature'
            ),
            'classes': ('collapse',)
        }),
        ('修改日志', {
            'fields': ('modified_by', 'modification_reason'),
            'classes': ('collapse',)
        })
    )

@admin.register(ProductStandard)
class ProductStandardAdmin(admin.ModelAdmin):
    list_display = [
        'product_code', 'test_item', 'standard_type', 
        'lower_limit', 'upper_limit', 'target_value'
    ]
    list_filter = ['product_code', 'standard_type', 'test_item']
    search_fields = ['product_code', 'test_item']
    ordering = ['product_code', 'test_item', 'standard_type']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('product_code', 'test_item', 'standard_type')
        }),
        ('标准值', {
            'fields': ('lower_limit', 'upper_limit', 'target_value')
        })
    )
