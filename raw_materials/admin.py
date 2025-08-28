from django.contrib import admin
from django.contrib import messages
from django.utils.safestring import mark_safe
from django import forms
from django.urls import path, reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from .models import RawMaterial, RawMaterialHistory, RawMaterialStandard, RawMaterialStandardHistory


@admin.register(RawMaterial)
class RawMaterialAdmin(admin.ModelAdmin):
    list_display = [
        'material_name', 'material_batch', 'supplier', 'inspector', 
        'test_date', 'final_judgment', 'judgment_status'
    ]
    actions = ['update_judgments_action']
    list_filter = [
        'material_name', 'material_batch', 'supplier', 'test_date', 
        'final_judgment', 'judgment_status'
    ]
    search_fields = ['material_name', 'material_batch', 'supplier', 'inspector']
    date_hierarchy = 'test_date'
    ordering = ['-test_date', 'material_batch']
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
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
        ('原料信息', {
            'fields': (
                'material_name', 'material_batch', 'inspector', 
                'test_date', 'sample_category'
            )
        }),
        ('供应商信息', {
            'fields': (
                'supplier', 'distributor'
            )
        }),
        ('文档信息', {
            'fields': (
                'acceptance_form', 'logistics_form', 'coa_number'
            )
        }),
        ('判定结果', {
            'fields': (
                'final_judgment', 'judgment_status'
            )
        }),
        ('原料质量数据', {
            'fields': (
                'appearance', 'purity', 'peak_position', 'inhibitor_content',
                'moisture_content', 'color', 'ethanol_content', 'acidity'
            ),
            'classes': ('collapse',)
        }),
        ('备注', {
            'fields': ('remarks',),
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
        
        # 原料信息
        material_info = f"原料名称: {obj.material_name}\n原料批号: {obj.material_batch}\n"
        material_info += f"供应商: {obj.supplier}\n检测人: {obj.inspector}\n测试日期: {obj.test_date}\n"
        
        if obj.distributor:
            material_info += f"经销商: {obj.distributor}\n"
        
        # 文档信息
        if obj.acceptance_form:
            material_info += f"验收单号: {obj.acceptance_form}\n"
        if obj.logistics_form:
            material_info += f"物流单号: {obj.logistics_form}\n"
        if obj.coa_number:
            material_info += f"COA编号: {obj.coa_number}\n"
        
        # 原料质量数据（不为空的内容）
        data_fields = [
            ('appearance', '外观'),
            ('purity', '纯度'),
            ('peak_position', '出峰位置'),
            ('inhibitor_content', '阻聚剂含量'),
            ('moisture_content', '水分含量'),
            ('color', '色度'),
            ('ethanol_content', '乙醇含量'),
            ('acidity', '酸度')
        ]
        
        data_lines = []
        for field_name, field_label in data_fields:
            value = getattr(obj, field_name)
            if value is not None and value != "":
                data_lines.append(f"{field_label}: {value}")
        
        if data_lines:
            material_info += "\n质量数据:\n" + "\n".join(data_lines)
        
        # 判定结果
        if obj.final_judgment:
            material_info += f"\n判定结果: {obj.final_judgment}"
        
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
        return mark_safe(f'<div id="copy-text-content" style="white-space: pre-line;">{material_info}</div>{copy_button}')
    
    copy_text.short_description = "复制文本"
    copy_text.allow_tags = True

    def update_judgments_action(self, request, queryset):
        """批量更新选定原料记录的判定结果"""
        from django.db import transaction
        import time
        
        start_time = time.time()
        updated_count = 0
        
        # 使用事务确保数据一致性
        with transaction.atomic():
            for material in queryset:
                # 调用save方法会自动触发calculate_judgment()
                material.save()
                updated_count += 1
        
        elapsed_time = time.time() - start_time
        
        self.message_user(
            request,
            f'成功更新 {updated_count} 条原料记录的判定结果 (耗时: {elapsed_time:.2f}秒)',
            messages.SUCCESS
        )
    
    update_judgments_action.short_description = "更新选定记录的判定结果"
    
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
            RawMaterialHistory.objects.create(
                raw_material=obj,
                modified_by=request.user.username,
                modification_reason=obj.modification_reason,
                modified_data=modified_data
            )
        
        # 自动计算判定结果
        obj.calculate_judgment()
        super().save_model(request, obj, form, change)
    
    def response_add(self, request, obj, post_url_continue=None):
        # 添加成功后显示详细判定结果
        if '_continue' not in request.POST and '_addanother' not in request.POST:
            # 重定向到查看页面
            return HttpResponseRedirect(reverse('admin:raw_materials_rawmaterial_change', args=[obj.pk]))
        return super().response_add(request, obj, post_url_continue)
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/history/', self.admin_site.admin_view(self.history_view), name='raw_materials_rawmaterial_history'),
        ]
        return custom_urls + urls
    
    def history_view(self, request, object_id, extra_context=None):
        """自定义历史记录视图"""
        obj = get_object_or_404(RawMaterial, pk=object_id)
        history_records = RawMaterialHistory.objects.filter(raw_material=obj).order_by('-created_at')
        
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


@admin.register(RawMaterialHistory)
class RawMaterialHistoryAdmin(admin.ModelAdmin):
    list_display = ['raw_material', 'modified_by', 'modification_reason', 'created_at']
    list_filter = ['raw_material__material_name', 'created_at', 'modified_by']
    search_fields = ['raw_material__material_name', 'raw_material__material_batch', 'modified_by', 'modification_reason']
    readonly_fields = ['raw_material', 'modified_by', 'modification_reason', 'modified_data', 'created_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(RawMaterialStandard)
class RawMaterialStandardAdmin(admin.ModelAdmin):
    list_display = [
        'material_name', 'test_item', 'standard_type', 'supplier',
        'lower_limit', 'upper_limit', 'target_value'
    ]
    list_filter = ['material_name', 'standard_type', 'test_item', 'supplier']
    search_fields = ['material_name', 'test_item', 'supplier']
    ordering = ['material_name', 'test_item', 'standard_type', 'supplier']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('material_name', 'test_item', 'standard_type', 'supplier')
        }),
        ('标准值', {
            'fields': ('lower_limit', 'upper_limit', 'target_value')
        }),
        ('修改历史', {
            'fields': ('created_at', 'updated_at', 'modified_by', 'modification_reason'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['created_at', 'updated_at', 'modified_by', 'modification_reason']
    
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
            RawMaterialStandardHistory.objects.create(
                raw_material_standard=obj,
                modified_by=request.user.username if hasattr(request, 'user') and hasattr(request.user, 'username') else 'system',
                modification_reason=obj.modification_reason,
                modified_data=modified_data
            )
        
        super().save_model(request, obj, form, change)
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/history/', self.admin_site.admin_view(self.history_view), name='raw_materials_rawmaterialstandard_history'),
        ]
        return custom_urls + urls
    
    def history_view(self, request, object_id, extra_context=None):
        """自定义历史记录视图"""
        obj = get_object_or_404(RawMaterialStandard, pk=object_id)
        history_records = RawMaterialStandardHistory.objects.filter(raw_material_standard=obj).order_by('-created_at')
        
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


@admin.register(RawMaterialStandardHistory)
class RawMaterialStandardHistoryAdmin(admin.ModelAdmin):
    list_display = ['raw_material_standard', 'modified_by', 'modification_reason', 'created_at']
    list_filter = ['raw_material_standard__material_name', 'created_at', 'modified_by']
    search_fields = ['raw_material_standard__material_name', 'modified_by', 'modification_reason']
    readonly_fields = ['raw_material_standard', 'modified_by', 'modification_reason', 'modified_data', 'created_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
