from django.contrib import admin
from django.contrib import messages
from core.utils import export_data
from .models import DryFilmProduct, ProductStandard, ProductStandardHistory, DryFilmProductHistory, AdhesiveProduct, AdhesiveProductHistory, PilotProduct, PilotProductHistory

@admin.register(DryFilmProduct)
class DryFilmProductAdmin(admin.ModelAdmin):
    actions = ['update_judgments_action', 'export_dryfilm_products_csv', 'export_dryfilm_products_excel']
    list_display = [
        'product_code', 'batch_number', 'production_line', 'inspector', 
        'test_date', 'external_final_judgment', 'internal_final_judgment',
        'judgment_status'
    ]
    list_filter = [
        'product_code', 'batch_number', 'production_line', 'test_date', 
        'external_final_judgment', 'internal_final_judgment', 'judgment_status'
    ]
    search_fields = ['product_code', 'batch_number', 'inspector']
    date_hierarchy = 'test_date'
    ordering = ['-test_date', 'batch_number']
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        from django import forms
        
        # 为product_code字段提供下拉选择，数据来自ProductStandard
        if db_field.name == 'product_code':
            from products.models import ProductStandard
            # 获取所有产品标准中的产品名称
            product_codes = ProductStandard.objects.values_list(
                'product_code', flat=True
            ).distinct()
            kwargs['widget'] = forms.Select(choices=[
                (code, code) for code in product_codes
            ])
        
        # 为sample_category字段提供下拉选择
        elif db_field.name == 'sample_category':
            SAMPLE_CATEGORIES = [
                ('单批样', '单批样'),
                ('装车样', '装车样'),
                ('掺桶样', '掺桶样')
            ]
            kwargs['widget'] = forms.Select(choices=SAMPLE_CATEGORIES)
        
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    
    fieldsets = (
        ('产品信息', {
            'fields': (
                'product_code', 'batch_number', 'production_line', 
                'inspector', 'test_date', 'sample_category', 'remarks'
            )
        }),
        ('判定结果', {
            'fields': (
                'external_final_judgment', 'internal_final_judgment', 
                'judgment_status'
            )
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
        ('修改历史', {
            'fields': (
                'created_at', 'updated_at', 'modified_by', 'modification_reason'
            ),
            'classes': ('collapse',)
        }),
        ('复制文本', {
            'fields': ('copy_text',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = [
        'judgment_details', 'created_at', 'updated_at', 'modified_by', 
        'modification_reason', 'copy_text'
    ]
    
    def copy_text(self, obj):
        """生成用于复制的文本内容"""
        if not obj.pk:
            return "请先保存数据以生成复制文本"
        
        # 产品信息
        product_info = f"牌号: {obj.product_code}\n批号: {obj.batch_number}\n"
        
        # 产品数据（不为空的内容）
        data_fields = [
            ('appearance', '外观'),
            ('solid_content', '固含'),
            ('viscosity', '粘度'),
            ('acid_value', '酸值'),
            ('moisture', '水分'),
            ('residual_monomer', '残单'),
            ('weight_avg_molecular_weight', '重均分子量'),
            ('pdi', 'PDI'),
            ('color', '色度'),
            ('polymerization_inhibitor', '阻聚剂'),
            ('conversion_rate', '转化率'),
            ('loading_temperature', '装车温度')
        ]
        
        data_lines = []
        for field_name, field_label in data_fields:
            value = getattr(obj, field_name)
            if value is not None and value != "":
                data_lines.append(f"{field_label}: {value}")
        
        if data_lines:
            product_info += "\n".join(data_lines)
        
        # 添加复制按钮和内联JavaScript
        copy_button = f"""
        <div style="margin-top: 10px;">
            <button type="button" onclick="copyProductText()" 
                    style="background-color: #4CAF50; color: white; border: none; 
                           padding: 5px 10px; border-radius: 3px; cursor: pointer;">
                复制文本
            </button>
        </div>
        <script>
        function copyProductText() {{
            const text = document.getElementById('copy-text-content').textContent;
            copyToClipboard(text, {{
                showError: true,
                successMessage: '已复制到剪贴板！',
                errorMessage: '复制失败，请手动复制文本内容',
                fallbackToPrompt: true
            }});
        }}
        </script>
        """
        
        # 使用mark_safe确保HTML被正确渲染
        from django.utils.safestring import mark_safe
        return mark_safe(f'<div id="copy-text-content" style="white-space: pre-line;">{product_info}</div>{copy_button}')
    
    copy_text.short_description = "复制文本"
    copy_text.allow_tags = True
    
    def save_model(self, request, obj, form, change):
        # 记录修改人信息
        if change:  # 如果是修改操作
            obj.modified_by = request.user.username
            
            # 获取原始对象和当前表单数据的差异
            original_obj = self.model.objects.get(pk=obj.pk)
            changed_fields = []
            modified_data = {}
            
            # 检查哪些字段被修改了
            for field in obj._meta.fields:
                field_name = field.name
                if field_name not in ['created_at', 'updated_at', 'modified_by', 'modification_reason']:
                    original_value = getattr(original_obj, field_name)
                    new_value = getattr(obj, field_name)
                    
                    if original_value != new_value:
                        # 格式化字段显示名称
                        field_verbose = field.verbose_name if hasattr(field, 'verbose_name') else field_name
                        changed_fields.append(f"{field_verbose}: {original_value} → {new_value}")
                        modified_data[field_name] = {
                            'old': original_value,
                            'new': new_value
                        }
            
            # 生成自动修改描述
            if changed_fields:
                obj.modification_reason = f"自动检测到修改：{'; '.join(changed_fields)}"
            else:
                obj.modification_reason = "通过管理界面修改（无数据变更）"
            
            # 创建历史记录（每次修改都创建，无论是否有修改原因）
            DryFilmProductHistory.objects.create(
                dryfilm_product=obj,
                modified_by=request.user.username,
                modification_reason=obj.modification_reason,
                modified_data=modified_data
            )
        
        # 自动计算整体判定
        obj.calculate_final_judgments()
        super().save_model(request, obj, form, change)
    
    def response_add(self, request, obj, post_url_continue=None):
        # 添加成功后显示详细判定结果
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        
        if '_continue' not in request.POST and '_addanother' not in request.POST:
            # 重定向到查看页面
            return HttpResponseRedirect(reverse('admin:products_dryfilmproduct_change', args=[obj.pk]))
        return super().response_add(request, obj, post_url_continue)
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/history/', self.admin_site.admin_view(self.history_view), name='products_dryfilmproduct_history'),
        ]
        return custom_urls + urls
    
    def history_view(self, request, object_id, extra_context=None):
        """自定义历史记录视图"""
        from django.shortcuts import get_object_or_404
        obj = get_object_or_404(DryFilmProduct, pk=object_id)
        history_records = DryFilmProductHistory.objects.filter(dryfilm_product=obj).order_by('-created_at')
        
        context = {
            'title': f'修改历史 - {obj}',
            'object': obj,
            'history_records': history_records,
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
        }
        context.update(extra_context or {})
        
        return super().history_view(request, object_id, context)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save'] = True
        
        # 添加返回列表按钮
        extra_context['show_return_to_list'] = True
        
        return super().change_view(request, object_id, form_url, extra_context)

    def export_pilot_products_csv(self, request, queryset):
        """导出选定的中试产品记录为CSV格式"""
        fields = [
            'product_code', 'batch_number', 'production_line', 'inspector',
            'test_date', 'sample_category', 'appearance', 'solid_content',
            'viscosity', 'acid_value', 'moisture', 'residual_monomer',
            'weight_avg_molecular_weight', 'pdi', 'color', 'polymerization_inhibitor',
            'conversion_rate', 'loading_temperature', 'remarks', 'created_at', 'updated_at'
        ]
        field_names = [
            '产品牌号', '产品批号', '产线', '检测人',
            '测试日期', '样品类别', '外观', '固含',
            '粘度', '酸值', '水分', '残单',
            '重均分子量', 'PDI', '色度', '阻聚剂',
            '转化率', '装车温度', '备注', '创建时间', '更新时间'
        ]
        return export_data(request, queryset, 'PilotProduct', fields, 'csv', field_names)
    
    export_pilot_products_csv.short_description = "导出选定中试产品记录 (CSV)"

    def export_pilot_products_excel(self, request, queryset):
        """导出选定的中试产品记录为Excel格式"""
        fields = [
            'product_code', 'batch_number', 'production_line', 'inspector',
            'test_date', 'sample_category', 'appearance', 'solid_content',
            'viscosity', 'acid_value', 'moisture', 'residual_monomer',
            'weight_avg_molecular_weight', 'pdi', 'color', 'polymerization_inhibitor',
            'conversion_rate', 'loading_temperature', 'remarks', 'created_at', 'updated_at'
        ]
        field_names = [
            '产品牌号', '产品批号', '产线', '检测人',
            '测试日期', '样品类别', '外观', '固含',
            '粘度', '酸值', '水分', '残单',
            '重均分子量', 'PDI', '色度', '阻聚剂',
            '转化率', '装车温度', '备注', '创建时间', '更新时间'
        ]
        return export_data(request, queryset, 'PilotProduct', fields, 'excel', field_names)
    
    export_pilot_products_excel.short_description = "导出选定中试产品记录 (Excel)"

    def update_judgments_action(self, request, queryset):
        """批量更新选定干膜产品记录的判定结果"""
        from django.db import transaction
        import time
        
        start_time = time.time()
        updated_count = 0
        
        # 使用事务确保数据一致性
        with transaction.atomic():
            for product in queryset:
                # 调用save方法会自动触发calculate_final_judgments()
                product.save()
                updated_count += 1
        
        elapsed_time = time.time() - start_time
        
        self.message_user(
            request,
            f'成功更新 {updated_count} 条干膜产品记录的判定结果 (耗时: {elapsed_time:.2f}秒)',
            messages.SUCCESS
        )
    
    update_judgments_action.short_description = "更新选定记录的判定结果"

    def export_dryfilm_products_csv(self, request, queryset):
        """导出选定的干膜产品记录为CSV格式"""
        fields = [
            'product_code', 'batch_number', 'production_line', 'inspector',
            'test_date', 'sample_category', 'appearance', 'solid_content',
            'viscosity', 'acid_value', 'moisture', 'residual_monomer',
            'weight_avg_molecular_weight', 'pdi', 'color', 'polymerization_inhibitor',
            'conversion_rate', 'loading_temperature', 'external_final_judgment',
            'internal_final_judgment', 'judgment_status', 'remarks', 'created_at', 'updated_at'
        ]
        field_names = [
            '牌号', '批号', '生产线', '检测人',
            '测试日期', '样品类别', '外观', '固含',
            '粘度', '酸值', '水分', '残单',
            '重均分子量', 'PDI', '色度', '阻聚剂',
            '转化率', '装车温度', '外部最终判定',
            '内部最终判定', '判定状态', '备注', '创建时间', '更新时间'
        ]
        return export_data(request, queryset, 'DryFilmProduct', fields, 'csv', field_names)
    
    export_dryfilm_products_csv.short_description = "导出选定干膜产品记录 (CSV)"

    def export_dryfilm_products_excel(self, request, queryset):
        """导出选定的干膜产品记录为Excel格式"""
        fields = [
            'product_code', 'batch_number', 'production_line', 'inspector',
            'test_date', 'sample_category', 'appearance', 'solid_content',
            'viscosity', 'acid_value', 'moisture', 'residual_monomer',
            'weight_avg_molecular_weight', 'pdi', 'color', 'polymerization_inhibitor',
            'conversion_rate', 'loading_temperature', 'external_final_judgment',
            'internal_final_judgment', 'judgment_status', 'remarks', 'created_at', 'updated_at'
        ]
        field_names = [
            '牌号', '批号', '生产线', '检测人',
            '测试日期', '样品类别', '外观', '固含',
            '粘度', '酸值', '水分', '残单',
            '重均分子量', 'PDI', '色度', '阻聚剂',
            '转化率', '装车温度', '外部最终判定',
            '内部最终判定', '判定状态', '备注', '创建时间', '更新时间'
        ]
        return export_data(request, queryset, 'DryFilmProduct', fields, 'excel', field_names)
    
    export_dryfilm_products_excel.short_description = "导出选定干膜产品记录 (Excel)"


@admin.register(ProductStandard)
class ProductStandardAdmin(admin.ModelAdmin):
    actions = ['export_product_standards_csv', 'export_product_standards_excel']
    
    def export_product_standards_csv(self, request, queryset):
        """导出选定的产品标准记录为CSV格式"""
        fields = [
            'product_code', 'test_item', 'standard_type', 'lower_limit',
            'upper_limit', 'target_value', 'text_standard', 'test_condition',
            'unit', 'analysis_method', 'created_at', 'updated_at'
        ]
        field_names = [
            '牌号', '测试项目', '标准类型', '下限',
            '上限', '目标值', '文本标准', '测试条件',
            '单位', '分析方法', '创建时间', '更新时间'
        ]
        return export_data(request, queryset, 'ProductStandard', fields, 'csv', field_names)
    
    export_product_standards_csv.short_description = "导出选定产品标准记录 (CSV)"

    def export_product_standards_excel(self, request, queryset):
        """导出选定的产品标准记录为Excel格式"""
        fields = [
            'product_code', 'test_item', 'standard_type', 'lower_limit',
            'upper_limit', 'target_value', 'text_standard', 'test_condition',
            'unit', 'analysis_method', 'created_at', 'updated_at'
        ]
        field_names = [
            '牌号', '测试项目', '标准类型', '下限',
            '上限', '目标值', '文本标准', '测试条件',
            '单位', '分析方法', '创建时间', '更新时间'
        ]
        return export_data(request, queryset, 'ProductStandard', fields, 'excel', field_names)
    
    export_product_standards_excel.short_description = "导出选定产品标准记录 (Excel)"
    list_display = [
        'product_code', 'test_item', 'standard_type', 
        'lower_limit', 'upper_limit', 'target_value', 'text_standard',
        'test_condition', 'unit', 'analysis_method'
    ]
    list_filter = ['product_code', 'standard_type', 'test_item']
    search_fields = ['product_code', 'test_item']
    ordering = ['product_code', 'test_item', 'standard_type']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('product_code', 'test_item', 'standard_type')
        }),
        ('标准值', {
            'fields': ('lower_limit', 'upper_limit', 'target_value', 'text_standard')
        }),
        ('检测信息', {
            'fields': ('test_condition', 'unit', 'analysis_method')
        }),
        ('修改历史', {
            'fields': ('created_at', 'updated_at', 'modified_by', 'modification_reason'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['created_at', 'updated_at', 'modified_by', 'modification_reason']
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/history/', self.admin_site.admin_view(self.history_view), name='products_productstandard_history'),
        ]
        return custom_urls + urls
    
    def save_model(self, request, obj, form, change):
        # 记录修改人信息
        if change:  # 如果是修改操作
            obj.modified_by = request.user.username if hasattr(request, 'user') and hasattr(request.user, 'username') else 'system'
            
            # 获取原始对象和当前表单数据的差异
            original_obj = self.model.objects.get(pk=obj.pk)
            changed_fields = []
            modified_data = {}
            
            # 检查哪些字段被修改了
            for field in obj._meta.fields:
                field_name = field.name
                if field_name not in ['created_at', 'updated_at', 'modified_by', 'modification_reason']:
                    original_value = getattr(original_obj, field_name)
                    new_value = getattr(obj, field_name)
                    
                    if original_value != new_value:
                        # 格式化字段显示名称
                        field_verbose = field.verbose_name if hasattr(field, 'verbose_name') else field_name
                        changed_fields.append(f"{field_verbose}: {original_value} → {new_value}")
                        modified_data[field_name] = {
                            'old': original_value,
                            'new': new_value
                        }
            
            # 生成自动修改描述
            if changed_fields:
                obj.modification_reason = f"自动检测到修改：{'; '.join(changed_fields)}"
            else:
                obj.modification_reason = "通过管理界面修改（无数据变更）"
            
            # 创建历史记录（每次修改都创建，无论是否有修改原因）
            ProductStandardHistory.objects.create(
                product_standard=obj,
                modified_by=request.user.username if hasattr(request, 'user') and hasattr(request.user, 'username') else 'system',
                modification_reason=obj.modification_reason,
                modified_data=modified_data
            )
        
        super().save_model(request, obj, form, change)
    
    def history_view(self, request, object_id, extra_context=None):
        """自定义历史记录视图"""
        from django.shortcuts import get_object_or_404
        obj = get_object_or_404(ProductStandard, pk=object_id)
        history_records = ProductStandardHistory.objects.filter(product_standard=obj).order_by('-created_at')
        
        context = {
            'title': f'修改历史 - {obj}',
            'object': obj,
            'history_records': history_records,
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
        }
        context.update(extra_context or {})
        
        return super().history_view(request, object_id, context)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save'] = True
        
        # 添加返回列表按钮
        extra_context['show_return_to_list'] = True
        
        return super().change_view(request, object_id, form_url, extra_context)


@admin.register(ProductStandardHistory)
class ProductStandardHistoryAdmin(admin.ModelAdmin):
    list_display = ['product_standard', 'modified_by', 'modification_reason', 'created_at']
    list_filter = ['created_at', 'modified_by', 'product_standard__product_code']
    search_fields = ['product_standard__product_code', 'modified_by', 'modification_reason']
    readonly_fields = ['product_standard', 'modified_by', 'modification_reason', 'modified_data', 'created_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DryFilmProductHistory)
class DryFilmProductHistoryAdmin(admin.ModelAdmin):
    list_display = ['dryfilm_product', 'modified_by', 'modification_reason', 'created_at']
    list_filter = ['created_at', 'modified_by', 'dryfilm_product__product_code']
    search_fields = ['dryfilm_product__product_code', 'dryfilm_product__batch_number', 'modified_by', 'modification_reason']
    readonly_fields = ['dryfilm_product', 'modified_by', 'modification_reason', 'modified_data', 'created_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AdhesiveProduct)
class AdhesiveProductAdmin(admin.ModelAdmin):
    actions = ['update_judgments_action', 'export_adhesive_products_csv', 'export_adhesive_products_excel']
    list_display = [
        'product_code', 'batch_number', 'production_line', 
        'physical_inspector', 'tape_inspector', 'physical_test_date',
        'physical_judgment', 'tape_judgment', 'final_judgment', 'judgment_status'
    ]
    list_filter = [
        'product_code', 'batch_number', 'production_line', 'physical_test_date', 'tape_test_date',
        'physical_judgment', 'tape_judgment', 'final_judgment', 'judgment_status'
    ]
    search_fields = ['product_code', 'batch_number', 'physical_inspector', 'tape_inspector']
    date_hierarchy = 'physical_test_date'
    ordering = ['-physical_test_date', 'batch_number']
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        from django import forms
        
        # 为product_code字段提供下拉选择，数据来自ProductStandard
        if db_field.name == 'product_code':
            from products.models import ProductStandard
            # 获取所有产品标准中的产品名称
            product_codes = ProductStandard.objects.values_list(
                'product_code', flat=True
            ).distinct()
            kwargs['widget'] = forms.Select(choices=[
                (code, code) for code in product_codes
            ])
        
        # 为sample_category字段提供下拉选择
        elif db_field.name == 'sample_category':
            SAMPLE_CATEGORIES = [
                ('单批样', '单批样'),
                ('装车样', '装车样'),
                ('掺桶样', '掺桶样')
            ]
            kwargs['widget'] = forms.Select(choices=SAMPLE_CATEGORIES)
        
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    
    fieldsets = (
        ('产品信息', {
            'fields': (
                'product_code', 'batch_number', 'production_line', 
                'physical_inspector', 'tape_inspector', 
                'physical_test_date', 'tape_test_date', 
                'sample_category', 'remarks'
            )
        }),
        ('判定结果', {
            'fields': (
                'physical_judgment', 'tape_judgment', 
                'final_judgment', 'judgment_status'
            )
        }),
        ('理化性能数据', {
            'fields': (
                'appearance', 'solid_content', 'viscosity', 'acid_value',
                'moisture', 'residual_monomer', 'weight_avg_molecular_weight',
                'pdi', 'color'
            ),
            'classes': ('collapse',)
        }),
        ('胶带性能数据', {
            'fields': (
                'initial_tack', 'peel_strength', 'high_temperature_holding',
                'room_temperature_holding', 'constant_load_peel'
            ),
            'classes': ('collapse',)
        }),
        ('修改历史', {
            'fields': (
                'created_at', 'updated_at', 'modified_by', 'modification_reason'
            ),
            'classes': ('collapse',)
        }),
        ('复制文本', {
            'fields': ('copy_text',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = [
        'judgment_details', 'created_at', 'updated_at', 'modified_by', 
        'modification_reason', 'copy_text'
    ]
    
    def copy_text(self, obj):
        """生成用于复制的文本内容"""
        if not obj.pk:
            return "请先保存数据以生成复制文本"
        
        # 产品信息
        product_info = f"牌号: {obj.product_code}\n批号: {obj.batch_number}\n"
        product_info += f"理化检测人: {obj.physical_inspector}\n胶带检测人: {obj.tape_inspector}\n"
        product_info += f"理化测试日期: {obj.physical_test_date}\n胶带测试日期: {obj.tape_test_date}\n"
        
        # 理化性能数据（不为空的内容）
        physical_fields = [
            ('appearance', '外观'),
            ('solid_content', '固含'),
            ('viscosity', '粘度'),
            ('acid_value', '酸值'),
            ('moisture', '水分'),
            ('residual_monomer', '残单'),
            ('weight_avg_molecular_weight', '重均分子量'),
            ('pdi', 'PDI'),
            ('color', '色度')
        ]
        
        physical_lines = []
        for field_name, field_label in physical_fields:
            value = getattr(obj, field_name)
            if value is not None and value != "":
                physical_lines.append(f"{field_label}: {value}")
        
        if physical_lines:
            product_info += "\n理化性能:\n" + "\n".join(physical_lines)
        
        # 胶带性能数据（不为空的内容）
        tape_fields = [
            ('initial_tack', '初粘'),
            ('peel_strength', '剥离'),
            ('high_temperature_holding', '高温持粘'),
            ('room_temperature_holding', '常温持粘'),
            ('constant_load_peel', '定荷重剥离')
        ]
        
        tape_lines = []
        for field_name, field_label in tape_fields:
            value = getattr(obj, field_name)
            if value is not None and value != "":
                tape_lines.append(f"{field_label}: {value}")
        
        if tape_lines:
            product_info += "\n胶带性能:\n" + "\n".join(tape_lines)
        
        # 添加复制按钮和内联JavaScript
        copy_button = f"""
        <div style="margin-top: 10px;">
            <button type="button" onclick="copyAdhesiveText()" 
                    style="background-color: #4CAF50; color: white; border: none; 
                           padding: 5px 10px; border-radius: 3px; cursor: pointer;">
                复制文本
            </button>
        </div>
        <script>
        function copyAdhesiveText() {{
            const text = document.getElementById('copy-text-content').textContent;
            copyToClipboard(text, {{
                showError: true,
                successMessage: '已复制到剪贴板！',
                errorMessage: '复制失败，请手动复制文本内容',
                fallbackToPrompt: true
            }});
        }}
        </script>
        """
        
        # 使用mark_safe确保HTML被正确渲染
        from django.utils.safestring import mark_safe
        return mark_safe(f'<div id="copy-text-content" style="white-space: pre-line;">{product_info}</div>{copy_button}')
    
    copy_text.short_description = "复制文本"
    copy_text.allow_tags = True
    
    def save_model(self, request, obj, form, change):
        # 记录修改人信息
        if change:  # 如果是修改操作
            obj.modified_by = request.user.username
            
            # 获取原始对象和当前表单数据的差异
            original_obj = self.model.objects.get(pk=obj.pk)
            changed_fields = []
            modified_data = {}
            
            # 检查哪些字段被修改了
            for field in obj._meta.fields:
                field_name = field.name
                if field_name not in ['created_at', 'updated_at', 'modified_by', 'modification_reason']:
                    original_value = getattr(original_obj, field_name)
                    new_value = getattr(obj, field_name)
                    
                    if original_value != new_value:
                        # 格式化字段显示名称
                        field_verbose = field.verbose_name if hasattr(field, 'verbose_name') else field_name
                        changed_fields.append(f"{field_verbose}: {original_value} → {new_value}")
                        modified_data[field_name] = {
                            'old': original_value,
                            'new': new_value
                        }
            
            # 生成自动修改描述
            if changed_fields:
                obj.modification_reason = f"自动检测到修改：{'; '.join(changed_fields)}"
            else:
                obj.modification_reason = "通过管理界面修改（无数据变更）"
            
            # 创建历史记录（每次修改都创建，无论是否有修改原因）
            AdhesiveProductHistory.objects.create(
                adhesive_product=obj,
                modified_by=request.user.username,
                modification_reason=obj.modification_reason,
                modified_data=modified_data
            )
        
        # 自动计算判定结果
        obj.calculate_judgments()
        super().save_model(request, obj, form, change)
    
    def response_add(self, request, obj, post_url_continue=None):
        # 添加成功后显示详细判定结果
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        
        if '_continue' not in request.POST and '_addanother' not in request.POST:
            # 重定向到查看页面
            return HttpResponseRedirect(reverse('admin:products_adhesiveproduct_change', args=[obj.pk]))
        return super().response_add(request, obj, post_url_continue)
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/history/', self.admin_site.admin_view(self.history_view), name='products_adhesiveproduct_history'),
        ]
        return custom_urls + urls
    
    def history_view(self, request, object_id, extra_context=None):
        """自定义历史记录视图"""
        from django.shortcuts import get_object_or_404
        obj = get_object_or_404(AdhesiveProduct, pk=object_id)
        history_records = AdhesiveProductHistory.objects.filter(adhesive_product=obj).order_by('-created_at')
        
        context = {
            'title': f'修改历史 - {obj}',
            'object': obj,
            'history_records': history_records,
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
        }
        context.update(extra_context or {})
        
        return super().history_view(request, object_id, context)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save'] = True
        
        # 添加返回列表按钮
        extra_context['show_return_to_list'] = True
        
        return super().change_view(request, object_id, form_url, extra_context)

    def export_adhesive_products_csv(self, request, queryset):
        """导出选定的胶粘剂产品记录为CSV格式"""
        fields = [
            'product_code', 'batch_number', 'production_line', 
            'physical_inspector', 'tape_inspector', 'physical_test_date',
            'tape_test_date', 'sample_category', 'appearance', 'solid_content',
            'viscosity', 'acid_value', 'moisture', 'residual_monomer',
            'weight_avg_molecular_weight', 'pdi', 'color', 'initial_tack',
            'peel_strength', 'high_temperature_holding', 'room_temperature_holding',
            'constant_load_peel', 'physical_judgment', 'tape_judgment',
            'final_judgment', 'judgment_status', 'remarks', 'created_at', 'updated_at'
        ]
        field_names = [
            '牌号', '批号', '生产线', 
            '理化检测人', '胶带检测人', '理化测试日期',
            '胶带测试日期', '样品类别', '外观', '固含',
            '粘度', '酸值', '水分', '残单',
            '重均分子量', 'PDI', '色度', '初粘',
            '剥离', '高温持粘', '常温持粘',
            '定荷重剥离', '理化判定', '胶带判定',
            '最终判定', '判定状态', '备注', '创建时间', '更新时间'
        ]
        return export_data(request, queryset, 'AdhesiveProduct', fields, 'csv', field_names)
    
    export_adhesive_products_csv.short_description = "导出选定胶粘剂产品记录 (CSV)"

    def export_adhesive_products_excel(self, request, queryset):
        """导出选定的胶粘剂产品记录为Excel格式"""
        fields = [
            'product_code', 'batch_number', 'production_line', 
            'physical_inspector', 'tape_inspector', 'physical_test_date',
            'tape_test_date', 'sample_category', 'appearance', 'solid_content',
            'viscosity', 'acid_value', 'moisture', 'residual_monomer',
            'weight_avg_molecular_weight', 'pdi', 'color', 'initial_tack',
            'peel_strength', 'high_temperature_holding', 'room_temperature_holding',
            'constant_load_peel', 'physical_judgment', 'tape_judgment',
            'final_judgment', 'judgment_status', 'remarks', 'created_at', 'updated_at'
        ]
        field_names = [
            '牌号', '批号', '生产线', 
            '理化检测人', '胶带检测人', '理化测试日期',
            '胶带测试日期', '样品类别', '外观', '固含',
            '粘度', '酸值', '水分', '残单',
            '重均分子量', 'PDI', '色度', '初粘',
            '剥离', '高温持粘', '常温持粘',
            '定荷重剥离', '理化判定', '胶带判定',
            '最终判定', '判定状态', '备注', '创建时间', '更新时间'
        ]
        return export_data(request, queryset, 'AdhesiveProduct', fields, 'excel', field_names)
    
    export_adhesive_products_excel.short_description = "导出选定胶粘剂产品记录 (Excel)"

    def update_judgments_action(self, request, queryset):
        """批量更新选定胶粘剂产品记录的判定结果"""
        from django.db import transaction
        import time
        
        start_time = time.time()
        updated_count = 0
        
        # 使用事务确保数据一致性
        with transaction.atomic():
            for product in queryset:
                # 调用save方法会自动触发calculate_judgments()
                product.save()
                updated_count += 1
        
        elapsed_time = time.time() - start_time
        
        self.message_user(
            request,
            f'成功更新 {updated_count} 条胶粘剂产品记录的判定结果 (耗时: {elapsed_time:.2f}秒)',
            messages.SUCCESS
        )
    
    update_judgments_action.short_description = "更新选定记录的判定结果"


@admin.register(AdhesiveProductHistory)
class AdhesiveProductHistoryAdmin(admin.ModelAdmin):
    list_display = ['adhesive_product', 'modified_by', 'modification_reason', 'created_at']
    list_filter = ['created_at', 'modified_by', 'adhesive_product__product_code']
    search_fields = ['adhesive_product__product_code', 'adhesive_product__batch_number', 'modified_by', 'modification_reason']
    readonly_fields = ['adhesive_product', 'modified_by', 'modification_reason', 'modified_data', 'created_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PilotProduct)
class PilotProductAdmin(admin.ModelAdmin):
    actions = ['export_pilot_products_csv', 'export_pilot_products_excel']
    list_display = [
        'product_code', 'batch_number', 'production_line', 'inspector', 
        'test_date', 'sample_category'
    ]
    list_filter = [
        'production_line', 'test_date', 'sample_category'
    ]
    search_fields = ['product_code', 'batch_number', 'inspector']
    date_hierarchy = 'test_date'
    ordering = ['-test_date', 'batch_number']
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        from django import forms
        
        # 为sample_category字段提供下拉选择
        if db_field.name == 'sample_category':
            SAMPLE_CATEGORIES = [
                ('单批样', '单批样'),
                ('装车样', '装车样'),
                ('掺桶样', '掺桶样')
            ]
            kwargs['widget'] = forms.Select(choices=SAMPLE_CATEGORIES)
        
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    
    fieldsets = (
        ('产品信息', {
            'fields': (
                'product_code', 'batch_number', 'production_line', 
                'inspector', 'test_date', 'sample_category', 'remarks'
            )
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
        ('修改历史', {
            'fields': (
                'created_at', 'updated_at', 'modified_by', 'modification_reason'
            ),
            'classes': ('collapse',)
        }),
        ('复制文本', {
            'fields': ('copy_text',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = [
        'created_at', 'updated_at', 'modified_by', 
        'modification_reason', 'copy_text'
    ]
    
    def copy_text(self, obj):
        """生成用于复制的文本内容"""
        if not obj.pk:
            return "请先保存数据以生成复制文本"
        
        # 产品信息
        product_info = f"牌号: {obj.product_code}\n批号: {obj.batch_number}\n"
        
        # 产品数据（不为空的内容）
        data_fields = [
            ('appearance', '外观'),
            ('solid_content', '固含'),
            ('viscosity', '粘度'),
            ('acid_value', '酸值'),
            ('moisture', '水分'),
            ('residual_monomer', '残单'),
            ('weight_avg_molecular_weight', '重均分子量'),
            ('pdi', 'PDI'),
            ('color', '色度'),
            ('polymerization_inhibitor', '阻聚剂'),
            ('conversion_rate', '转化率'),
            ('loading_temperature', '装车温度')
        ]
        
        data_lines = []
        for field_name, field_label in data_fields:
            value = getattr(obj, field_name)
            if value is not None and value != "":
                data_lines.append(f"{field_label}: {value}")
        
        if data_lines:
            product_info += "\n".join(data_lines)
        
        # 添加复制按钮和内联JavaScript
        copy_button = f"""
        <div style="margin-top: 10px;">
            <button type="button" onclick="copyPilotText()" 
                    style="background-color: #4CAF50; color: white; border: none; 
                           padding: 5px 10px; border-radius: 3px; cursor: pointer;">
                复制文本
            </button>
        </div>
        <script>
        function copyPilotText() {{
            const text = document.getElementById('copy-text-content').textContent;
            copyToClipboard(text, {{
                showError: true,
                successMessage: '已复制到剪贴板！',
                errorMessage: '复制失败，请手动复制文本内容',
                fallbackToPrompt: true
            }});
        }}
        </script>
        """
        
        # 使用mark_safe确保HTML被正确渲染
        from django.utils.safestring import mark_safe
        return mark_safe(f'<div id="copy-text-content" style="white-space: pre-line;">{product_info}</div>{copy_button}')
    
    copy_text.short_description = "复制文本"
    copy_text.allow_tags = True
    
    def save_model(self, request, obj, form, change):
        # 记录修改人信息
        if change:  # 如果是修改操作
            obj.modified_by = request.user.username
            
            # 获取原始对象和当前表单数据的差异
            original_obj = self.model.objects.get(pk=obj.pk)
            changed_fields = []
            modified_data = {}
            
            # 检查哪些字段被修改了
            for field in obj._meta.fields:
                field_name = field.name
                if field_name not in ['created_at', 'updated_at', 'modified_by', 'modification_reason']:
                    original_value = getattr(original_obj, field_name)
                    new_value = getattr(obj, field_name)
                    
                    if original_value != new_value:
                        # 格式化字段显示名称
                        field_verbose = field.verbose_name if hasattr(field, 'verbose_name') else field_name
                        changed_fields.append(f"{field_verbose}: {original_value} → {new_value}")
                        modified_data[field_name] = {
                            'old': original_value,
                            'new': new_value
                        }
            
            # 生成自动修改描述
            if changed_fields:
                obj.modification_reason = f"自动检测到修改：{'; '.join(changed_fields)}"
            else:
                obj.modification_reason = "通过管理界面修改（无数据变更）"
            
            # 创建历史记录（每次修改都创建，无论是否有修改原因）
            PilotProductHistory.objects.create(
                pilot_product=obj,
                modified_by=request.user.username,
                modification_reason=obj.modification_reason,
                modified_data=modified_data
            )
        
        super().save_model(request, obj, form, change)
    
    def response_add(self, request, obj, post_url_continue=None):
        # 添加成功后显示详细判定结果
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        
        if '_continue' not in request.POST and '_addanother' not in request.POST:
            # 重定向到查看页面
            return HttpResponseRedirect(reverse('admin:products_pilotproduct_change', args=[obj.pk]))
        return super().response_add(request, obj, post_url_continue)
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/history/', self.admin_site.admin_view(self.history_view), name='products_pilotproduct_history'),
        ]
        return custom_urls + urls
    
    def history_view(self, request, object_id, extra_context=None):
        """自定义历史记录视图"""
        from django.shortcuts import get_object_or_404
        obj = get_object_or_404(PilotProduct, pk=object_id)
        history_records = PilotProductHistory.objects.filter(pilot_product=obj).order_by('-created_at')
        
        context = {
            'title': f'修改历史 - {obj}',
            'object': obj,
            'history_records': history_records,
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
        }
        context.update(extra_context or {})
        
        return super().history_view(request, object_id, context)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save'] = True
        
        # 添加返回列表按钮
        extra_context['show_return_to_list'] = True
        
        return super().change_view(request, object_id, form_url, extra_context)


@admin.register(PilotProductHistory)
class PilotProductHistoryAdmin(admin.ModelAdmin):
    list_display = ['pilot_product', 'modified_by', 'modification_reason', 'created_at']
    list_filter = ['created_at', 'modified_by', 'pilot_product__product_code']
    search_fields = ['pilot_product__product_code', 'pilot_product__batch_number', 'modified_by', 'modification_reason']
    readonly_fields = ['pilot_product', 'modified_by', 'modification_reason', 'modified_data', 'created_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
