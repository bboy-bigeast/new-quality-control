from django.contrib import admin
from .models import DryFilmProduct, ProductStandard, ProductStandardHistory, DryFilmProductHistory, AdhesiveProduct, AdhesiveProductHistory, PilotProduct, PilotProductHistory

@admin.register(DryFilmProduct)
class DryFilmProductAdmin(admin.ModelAdmin):
    list_display = [
        'product_code', 'batch_number', 'production_line', 'inspector', 
        'test_date', 'external_final_judgment', 'internal_final_judgment',
        'judgment_status'
    ]
    list_filter = [
        'production_line', 'test_date', 'external_final_judgment', 
        'internal_final_judgment', 'judgment_status'
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
            <button type="button" onclick="copyToClipboard()" 
                    style="background-color: #4CAF50; color: white; border: none; 
                           padding: 5px 10px; border-radius: 3px; cursor: pointer;">
                复制文本
            </button>
        </div>
        <script>
        function copyToClipboard() {{
            const text = document.getElementById('copy-text-content').textContent;
            navigator.clipboard.writeText(text).then(() => {{
                alert('已复制到剪贴板！');
            }}).catch(err => {{
                console.error('复制失败:', err);
                alert('复制失败，请手动复制文本内容');
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


@admin.register(ProductStandard)
class ProductStandardAdmin(admin.ModelAdmin):
    list_display = [
        'product_code', 'test_item', 'standard_type', 
        'lower_limit', 'upper_limit', 'target_value',
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
            'fields': ('lower_limit', 'upper_limit', 'target_value')
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
    list_filter = ['created_at', 'modified_by']
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
    list_filter = ['created_at', 'modified_by']
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
    list_display = [
        'product_code', 'batch_number', 'production_line', 
        'physical_inspector', 'tape_inspector', 'physical_test_date',
        'physical_judgment', 'tape_judgment', 'final_judgment', 'judgment_status'
    ]
    list_filter = [
        'production_line', 'physical_test_date', 'tape_test_date',
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
            <button type="button" onclick="copyToClipboard()" 
                    style="background-color: #4CAF50; color: white; border: none; 
                           padding: 5px 10px; border-radius: 3px; cursor: pointer;">
                复制文本
            </button>
        </div>
        <script>
        function copyToClipboard() {{
            const text = document.getElementById('copy-text-content').textContent;
            navigator.clipboard.writeText(text).then(() => {{
                alert('已复制到剪贴板！');
            }}).catch(err => {{
                console.error('复制失败:', err);
                alert('复制失败，请手动复制文本内容');
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


@admin.register(AdhesiveProductHistory)
class AdhesiveProductHistoryAdmin(admin.ModelAdmin):
    list_display = ['adhesive_product', 'modified_by', 'modification_reason', 'created_at']
    list_filter = ['created_at', 'modified_by']
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
            <button type="button" onclick="copyToClipboard()" 
                    style="background-color: #4CAF50; color: white; border: none; 
                           padding: 5px 10px; border-radius: 3px; cursor: pointer;">
                复制文本
            </button>
        </div>
        <script>
        function copyToClipboard() {{
            const text = document.getElementById('copy-text-content').textContent;
            navigator.clipboard.writeText(text).then(() => {{
                alert('已复制到剪贴板！');
            }}).catch(err => {{
                console.error('复制失败:', err);
                alert('复制失败，请手动复制文本内容');
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
    list_filter = ['created_at', 'modified_by']
    search_fields = ['pilot_product__product_code', 'pilot_product__batch_number', 'modified_by', 'modification_reason']
    readonly_fields = ['pilot_product', 'modified_by', 'modification_reason', 'modified_data', 'created_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
