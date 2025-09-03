from django.contrib import admin
from django.contrib import messages
from django import forms
from django.utils.safestring import mark_safe
from .models import InspectionReport

@admin.register(InspectionReport)
class InspectionReportAdmin(admin.ModelAdmin):
    list_display = [
        'report_number', 'report_type', 'product_code', 'batch_number',
        'production_date', 'inspector', 'reviewer', 'report_date',
        'conclusion', 'status'
    ]
    list_filter = [
        'report_type', 'production_date', 'report_date', 'status',
        'conclusion', 'inspector', 'reviewer'
    ]
    search_fields = [
        'report_number', 'product_code', 'batch_number', 'inspector',
        'reviewer'
    ]
    date_hierarchy = 'report_date'
    ordering = ['-report_date', '-report_number']
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        # 为report_type字段提供下拉选择
        if db_field.name == 'report_type':
            REPORT_TYPES = [
                ('dryfilm', '干膜产品检测报告'),
                ('adhesive', '胶粘剂产品检测报告'),
            ]
            kwargs['widget'] = forms.Select(choices=REPORT_TYPES)
        
        # 为status字段提供下拉选择
        elif db_field.name == 'status':
            STATUS_CHOICES = [
                ('draft', '草稿'),
                ('published', '已发布'),
            ]
            kwargs['widget'] = forms.Select(choices=STATUS_CHOICES)
        
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    
    fieldsets = (
        ('报告基本信息', {
            'fields': (
                'report_number', 'report_type', 'product_code', 'batch_number',
                'production_date', 'inspector', 'reviewer', 'report_date'
            )
        }),
        ('检测项目', {
            'fields': ('selected_items',),
            'classes': ('collapse',)
        }),
        ('检测结果', {
            'fields': ('test_results', 'conclusion'),
            'classes': ('collapse',)
        }),
        ('签名信息', {
            'fields': (
                'inspector_signature', 'reviewer_signature', 'review_date'
            ),
            'classes': ('collapse',)
        }),
        ('状态管理', {
            'fields': ('status', 'remarks')
        }),
        ('JSON数据预览', {
            'fields': ('selected_items_preview', 'test_results_preview'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = [
        'report_number', 'report_date', 'selected_items_preview',
        'test_results_preview'
    ]
    
    def selected_items_preview(self, obj):
        """预览选择的检测项目"""
        if not obj.selected_items:
            return "暂无选择的检测项目"
        
        preview = "<ul>"
        for item in obj.selected_items:
            if isinstance(item, str):
                preview += f"<li>{item}</li>"
            elif isinstance(item, dict) and 'name' in item:
                preview += f"<li>{item['name']}</li>"
        preview += "</ul>"
        
        return mark_safe(preview)
    
    selected_items_preview.short_description = "选择的检测项目预览"
    
    def test_results_preview(self, obj):
        """预览检测结果"""
        if not obj.test_results:
            return "暂无检测结果"
        
        preview = "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        preview += "<tr><th>检测项目</th><th>检测值</th><th>单位</th><th>下限</th><th>上限</th><th>是否合格</th></tr>"
        
        for result in obj.test_results:
            test_item = result.get('test_item', '')
            test_value = result.get('test_value', '')
            unit = result.get('unit', '')
            lower_limit = result.get('lower_limit', '')
            upper_limit = result.get('upper_limit', '')
            is_qualified = result.get('is_qualified', '')
            
            # 格式化合格状态显示
            qualified_display = ""
            if is_qualified is True:
                qualified_display = "<span style='color: green;'>✓ 合格</span>"
            elif is_qualified is False:
                qualified_display = "<span style='color: red;'>✗ 不合格</span>"
            elif is_qualified is None:
                qualified_display = "<span style='color: gray;'>- 未判定</span>"
            
            preview += f"<tr>"
            preview += f"<td>{test_item}</td>"
            preview += f"<td>{test_value}</td>"
            preview += f"<td>{unit}</td>"
            preview += f"<td>{lower_limit}</td>"
            preview += f"<td>{upper_limit}</td>"
            preview += f"<td>{qualified_display}</td>"
            preview += f"</tr>"
        
        preview += "</table>"
        
        return mark_safe(preview)
    
    test_results_preview.short_description = "检测结果预览"
    
    def save_model(self, request, obj, form, change):
        # 自动生成报告编号（如果为空）
        if not obj.report_number:
            obj.generate_report_number()
        
        # 自动填充产品信息（如果批号存在但产品代码为空）
        if obj.batch_number and not obj.product_code:
            obj._fill_product_info()
        
        # 自动生成检测结果（如果选择了检测项目但结果为空）
        if obj.batch_number and obj.selected_items and not obj.test_results:
            obj._generate_test_results()
        
        super().save_model(request, obj, form, change)
    
    def response_add(self, request, obj, post_url_continue=None):
        # 添加成功后显示详细检测结果
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        
        if '_continue' not in request.POST and '_addanother' not in request.POST:
            # 重定向到查看页面
            return HttpResponseRedirect(reverse('admin:reports_inspectionreport_change', args=[obj.pk]))
        return super().response_add(request, obj, post_url_continue)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save'] = True
        
        # 添加返回列表按钮
        extra_context['show_return_to_list'] = True
        
        return super().change_view(request, object_id, form_url, extra_context)
