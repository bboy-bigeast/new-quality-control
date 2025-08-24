from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Q, Count, Avg, Max, Min, StdDev
from django.utils import timezone
from datetime import datetime, timedelta
import json
import numpy as np
from scipy import stats

from .models import RawMaterial, RawMaterialStandard


def raw_material_list(request):
    """原料列表视图"""
    materials = RawMaterial.objects.all().order_by('-test_date', 'material_batch')
    
    # 获取筛选参数
    material_name = request.GET.get('material_name', '')
    supplier = request.GET.get('supplier', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    judgment_status = request.GET.get('judgment_status', '')
    
    # 应用筛选
    if material_name:
        materials = materials.filter(material_name__icontains=material_name)
    if supplier:
        materials = materials.filter(supplier__icontains=supplier)
    if start_date:
        materials = materials.filter(test_date__gte=start_date)
    if end_date:
        materials = materials.filter(test_date__lte=end_date)
    if judgment_status:
        materials = materials.filter(judgment_status=judgment_status)
    
    context = {
        'materials': materials,
        'material_name': material_name,
        'supplier': supplier,
        'start_date': start_date,
        'end_date': end_date,
        'judgment_status': judgment_status,
    }
    
    return render(request, 'raw_materials/list.html', context)


def raw_material_detail(request, pk):
    """原料详情视图"""
    material = get_object_or_404(RawMaterial, pk=pk)
    
    # 获取相关标准
    standards = RawMaterialStandard.objects.filter(material_name=material.material_name)
    
    # 获取历史记录
    history = material.rawmaterialhistory_set.all().order_by('-created_at')
    
    context = {
        'material': material,
        'standards': standards,
        'history': history,
    }
    
    return render(request, 'raw_materials/detail.html', context)


def raw_material_dashboard(request):
    """原料数据仪表板"""
    # 统计基本信息
    total_materials = RawMaterial.objects.count()
    qualified_materials = RawMaterial.objects.filter(judgment_status='合格').count()
    unqualified_materials = RawMaterial.objects.filter(judgment_status='不合格').count()
    pending_materials = RawMaterial.objects.filter(judgment_status='待判定').count()
    
    # 按原料名称统计
    material_stats = RawMaterial.objects.values('material_name').annotate(
        total=Count('id'),
        qualified=Count('id', filter=Q(judgment_status='合格')),
        unqualified=Count('id', filter=Q(judgment_status='不合格')),
        pending=Count('id', filter=Q(judgment_status='待判定'))
    ).order_by('material_name')
    
    # 按供应商统计
    supplier_stats = RawMaterial.objects.values('supplier').annotate(
        total=Count('id'),
        qualified=Count('id', filter=Q(judgment_status='合格')),
        unqualified=Count('id', filter=Q(judgment_status='不合格')),
        pending=Count('id', filter=Q(judgment_status='待判定'))
    ).order_by('supplier')
    
    # 最近30天的数据趋势
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    daily_stats = RawMaterial.objects.filter(test_date__gte=thirty_days_ago).values('test_date').annotate(
        total=Count('id'),
        qualified=Count('id', filter=Q(judgment_status='合格')),
        unqualified=Count('id', filter=Q(judgment_status='不合格'))
    ).order_by('test_date')
    
    context = {
        'total_materials': total_materials,
        'qualified_materials': qualified_materials,
        'unqualified_materials': unqualified_materials,
        'pending_materials': pending_materials,
        'material_stats': material_stats,
        'supplier_stats': supplier_stats,
        'daily_stats': list(daily_stats),
    }
    
    return render(request, 'raw_materials/dashboard.html', context)


def raw_material_standards(request):
    """原料标准列表视图"""
    standards = RawMaterialStandard.objects.all().order_by('material_name', 'test_item', 'standard_type')
    
    # 获取筛选参数
    material_name = request.GET.get('material_name', '')
    test_item = request.GET.get('test_item', '')
    standard_type = request.GET.get('standard_type', '')
    
    # 应用筛选
    if material_name:
        standards = standards.filter(material_name__icontains=material_name)
    if test_item:
        standards = standards.filter(test_item=test_item)
    if standard_type:
        standards = standards.filter(standard_type=standard_type)
    
    context = {
        'standards': standards,
        'material_name': material_name,
        'test_item': test_item,
        'standard_type': standard_type,
    }
    
    return render(request, 'raw_materials/standards.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class RawMaterialAPIView(View):
    """原料API视图"""
    
    def get(self, request, pk=None):
        """获取原料数据"""
        if pk:
            # 获取单个原料
            material = get_object_or_404(RawMaterial, pk=pk)
            data = {
                'id': material.id,
                'material_name': material.material_name,
                'material_batch': material.material_batch,
                'supplier': material.supplier,
                'inspector': material.inspector,
                'test_date': material.test_date.isoformat(),
                'judgment_status': material.judgment_status,
                'final_judgment': material.final_judgment,
                'quality_data': {
                    'appearance': material.appearance,
                    'purity': material.purity,
                    'peak_position': material.peak_position,
                    'inhibitor_content': material.inhibitor_content,
                    'moisture_content': material.moisture_content,
                    'color': material.color,
                    'ethanol_content': material.ethanol_content,
                    'acidity': material.acidity,
                }
            }
            return JsonResponse(data)
        else:
            # 获取原料列表
            materials = RawMaterial.objects.all().order_by('-test_date', 'material_batch')
            
            # 分页参数
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            start = (page - 1) * page_size
            end = start + page_size
            
            data = {
                'total': materials.count(),
                'page': page,
                'page_size': page_size,
                'results': [
                    {
                        'id': material.id,
                        'material_name': material.material_name,
                        'material_batch': material.material_batch,
                        'supplier': material.supplier,
                        'inspector': material.inspector,
                        'test_date': material.test_date.isoformat(),
                        'judgment_status': material.judgment_status,
                        'final_judgment': material.final_judgment,
                    }
                    for material in materials[start:end]
                ]
            }
            return JsonResponse(data)
    
    def post(self, request):
        """创建新原料"""
        try:
            data = json.loads(request.body)
            
            # 创建原料对象
            material = RawMaterial.objects.create(
                material_name=data['material_name'],
                material_batch=data['material_batch'],
                supplier=data['supplier'],
                inspector=data['inspector'],
                test_date=datetime.strptime(data['test_date'], '%Y-%m-%d').date(),
                sample_category=data.get('sample_category', '单批样'),
                distributor=data.get('distributor', ''),
                acceptance_form=data.get('acceptance_form', ''),
                logistics_form=data.get('logistics_form', ''),
                coa_number=data.get('coa_number', ''),
                remarks=data.get('remarks', ''),
                appearance=data.get('appearance', ''),
                purity=data.get('purity'),
                peak_position=data.get('peak_position'),
                inhibitor_content=data.get('inhibitor_content'),
                moisture_content=data.get('moisture_content'),
                color=data.get('color'),
                ethanol_content=data.get('ethanol_content'),
                acidity=data.get('acidity'),
                modified_by=data.get('modified_by', 'API'),
                modification_reason=data.get('modification_reason', '通过API创建')
            )
            
            return JsonResponse({
                'id': material.id,
                'message': '原料创建成功',
                'judgment_status': material.judgment_status,
                'final_judgment': material.final_judgment
            }, status=201)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def put(self, request, pk):
        """更新原料"""
        try:
            material = get_object_or_404(RawMaterial, pk=pk)
            data = json.loads(request.body)
            
            # 更新字段
            update_fields = []
            for field in ['material_name', 'supplier', 'inspector', 'sample_category',
                         'distributor', 'acceptance_form', 'logistics_form', 'coa_number',
                         'remarks', 'appearance', 'purity', 'peak_position', 
                         'inhibitor_content', 'moisture_content', 'color', 
                         'ethanol_content', 'acidity']:
                if field in data:
                    setattr(material, field, data[field])
                    update_fields.append(field)
            
            if 'test_date' in data:
                material.test_date = datetime.strptime(data['test_date'], '%Y-%m-%d').date()
                update_fields.append('test_date')
            
            material.modified_by = data.get('modified_by', 'API')
            material.modification_reason = data.get('modification_reason', '通过API更新')
            update_fields.extend(['modified_by', 'modification_reason'])
            
            material.save(update_fields=update_fields)
            
            return JsonResponse({
                'id': material.id,
                'message': '原料更新成功',
                'judgment_status': material.judgment_status,
                'final_judgment': material.final_judgment
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def delete(self, request, pk):
        """删除原料"""
        try:
            material = get_object_or_404(RawMaterial, pk=pk)
            material.delete()
            return JsonResponse({'message': '原料删除成功'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class RawMaterialStandardAPIView(View):
    """原料标准API视图"""
    
    def get(self, request, pk=None):
        """获取原料标准数据"""
        if pk:
            # 获取单个标准
            standard = get_object_or_404(RawMaterialStandard, pk=pk)
            data = {
                'id': standard.id,
                'material_name': standard.material_name,
                'test_item': standard.test_item,
                'standard_type': standard.standard_type,
                'supplier': standard.supplier,
                'lower_limit': standard.lower_limit,
                'upper_limit': standard.upper_limit,
                'target_value': standard.target_value,
            }
            return JsonResponse(data)
        else:
            # 获取标准列表
            standards = RawMaterialStandard.objects.all().order_by('material_name', 'test_item', 'standard_type')
            
            # 筛选参数
            material_name = request.GET.get('material_name', '')
            test_item = request.GET.get('test_item', '')
            standard_type = request.GET.get('standard_type', '')
            
            if material_name:
                standards = standards.filter(material_name__icontains=material_name)
            if test_item:
                standards = standards.filter(test_item=test_item)
            if standard_type:
                standards = standards.filter(standard_type=standard_type)
            
            data = {
                'total': standards.count(),
                'results': [
                    {
                        'id': standard.id,
                        'material_name': standard.material_name,
                        'test_item': standard.test_item,
                        'standard_type': standard.standard_type,
                        'supplier': standard.supplier,
                        'lower_limit': standard.lower_limit,
                        'upper_limit': standard.upper_limit,
                        'target_value': standard.target_value,
                    }
                    for standard in standards
                ]
            }
            return JsonResponse(data)
    
    def post(self, request):
        """创建新标准"""
        try:
            data = json.loads(request.body)
            
            # 创建标准对象
            standard = RawMaterialStandard.objects.create(
                material_name=data['material_name'],
                test_item=data['test_item'],
                standard_type=data['standard_type'],
                supplier=data.get('supplier', ''),
                lower_limit=data.get('lower_limit'),
                upper_limit=data.get('upper_limit'),
                target_value=data.get('target_value'),
                modified_by=data.get('modified_by', 'API'),
                modification_reason=data.get('modification_reason', '通过API创建')
            )
            
            return JsonResponse({
                'id': standard.id,
                'message': '标准创建成功'
            }, status=201)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def put(self, request, pk):
        """更新标准"""
        try:
            standard = get_object_or_404(RawMaterialStandard, pk=pk)
            data = json.loads(request.body)
            
            # 更新字段
            update_fields = []
            for field in ['material_name', 'test_item', 'standard_type', 'supplier',
                         'lower_limit', 'upper_limit', 'target_value']:
                if field in data:
                    setattr(standard, field, data[field])
                    update_fields.append(field)
            
            standard.modified_by = data.get('modified_by', 'API')
            standard.modification_reason = data.get('modification_reason', '通过API更新')
            update_fields.extend(['modified_by', 'modification_reason'])
            
            standard.save(update_fields=update_fields)
            
            return JsonResponse({
                'id': standard.id,
                'message': '标准更新成功'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def delete(self, request, pk):
        """删除标准"""
        try:
            standard = get_object_or_404(RawMaterialStandard, pk=pk)
            standard.delete()
            return JsonResponse({'message': '标准删除成功'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["GET"])
def raw_material_stats(request):
    """原料统计API"""
    # 总体统计
    total_stats = {
        'total': RawMaterial.objects.count(),
        'qualified': RawMaterial.objects.filter(judgment_status='合格').count(),
        'unqualified': RawMaterial.objects.filter(judgment_status='不合格').count(),
        'pending': RawMaterial.objects.filter(judgment_status='待判定').count(),
    }
    
    # 按原料名称统计
    material_stats = RawMaterial.objects.values('material_name').annotate(
        total=Count('id'),
        qualified=Count('id', filter=Q(judgment_status='合格')),
        unqualified=Count('id', filter=Q(judgment_status='不合格')),
        pending=Count('id', filter=Q(judgment_status='待判定'))
    ).order_by('material_name')
    
    # 按供应商统计
    supplier_stats = RawMaterial.objects.values('supplier').annotate(
        total=Count('id'),
        qualified=Count('id', filter=Q(judgment_status='合格')),
        unqualified=Count('id', filter=Q(judgment_status='不合格')),
        pending=Count('id', filter=Q(judgment_status='待判定'))
    ).order_by('supplier')
    
    # 质量数据统计
    quality_stats = {}
    for field in ['purity', 'peak_position', 'inhibitor_content', 
                 'moisture_content', 'color', 'ethanol_content', 'acidity']:
        stats = RawMaterial.objects.filter(**{f'{field}__isnull': False}).aggregate(
            avg=Avg(field),
            max=Max(field),
            min=Min(field),
            count=Count(field)
        )
        quality_stats[field] = stats
    
    return JsonResponse({
        'total_stats': total_stats,
        'material_stats': list(material_stats),
        'supplier_stats': list(supplier_stats),
        'quality_stats': quality_stats,
    })


@require_http_methods(["GET"])
def raw_material_charts(request):
    """原料图表分析API"""
    # 获取查询参数
    material_name = request.GET.get('material_name', '')
    supplier = request.GET.get('supplier', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    test_item = request.GET.get('test_item', 'purity')
    
    # 构建查询条件
    filters = {}
    if material_name:
        filters['material_name__icontains'] = material_name
    if supplier:
        filters['supplier__icontains'] = supplier
    if start_date:
        filters['test_date__gte'] = start_date
    if end_date:
        filters['test_date__lte'] = end_date
    
    # 获取数据
    materials = RawMaterial.objects.filter(**filters).order_by('test_date')
    
    # 时间趋势数据
    time_series_data = []
    for material in materials:
        if getattr(material, test_item) is not None:
            time_series_data.append({
                'date': material.test_date.isoformat(),
                'value': getattr(material, test_item),
                'batch': material.material_batch,
                'status': material.judgment_status
            })
    
    # 质量控制图数据 (X-bar and R chart)
    quality_control_data = []
    if materials.exists() and test_item in ['purity', 'peak_position', 'inhibitor_content', 
                                          'moisture_content', 'color', 'ethanol_content', 'acidity']:
        # 按批次分组计算均值和极差
        batch_groups = {}
        for material in materials:
            value = getattr(material, test_item)
            if value is not None:
                if material.material_batch not in batch_groups:
                    batch_groups[material.material_batch] = []
                batch_groups[material.material_batch].append(value)
        
        for batch, values in batch_groups.items():
            if len(values) >= 3:  # 至少3个数据点才计算控制限
                mean_val = np.mean(values)
                range_val = max(values) - min(values)
                quality_control_data.append({
                    'batch': batch,
                    'mean': mean_val,
                    'range': range_val,
                    'count': len(values)
                })
    
    # 分布分析
    distribution_data = []
    values = [getattr(m, test_item) for m in materials if getattr(m, test_item) is not None]
    if values:
        hist, bin_edges = np.histogram(values, bins=10)
        distribution_data = [{
            'bin_start': float(bin_edges[i]),
            'bin_end': float(bin_edges[i+1]),
            'count': int(hist[i])
        } for i in range(len(hist))]
    
    # 相关性分析（如果选择了数值型检测项目）
    correlation_data = {}
    numeric_fields = ['purity', 'peak_position', 'inhibitor_content', 
                     'moisture_content', 'color', 'ethanol_content', 'acidity']
    if test_item in numeric_fields:
        for other_field in numeric_fields:
            if other_field != test_item:
                x_values = []
                y_values = []
                for material in materials:
                    x_val = getattr(material, test_item)
                    y_val = getattr(material, other_field)
                    if x_val is not None and y_val is not None:
                        x_values.append(x_val)
                        y_values.append(y_val)
                
                if len(x_values) >= 2:
                    correlation, p_value = stats.pearsonr(x_values, y_values)
                    correlation_data[other_field] = {
                        'correlation': float(correlation),
                        'p_value': float(p_value),
                        'sample_size': len(x_values)
                    }
    
    return JsonResponse({
        'time_series': time_series_data,
        'quality_control': quality_control_data,
        'distribution': distribution_data,
        'correlation': correlation_data,
        'metadata': {
            'material_name': material_name,
            'supplier': supplier,
            'start_date': start_date,
            'end_date': end_date,
            'test_item': test_item,
            'total_samples': len(time_series_data)
        }
    })


@require_http_methods(["GET"])
def raw_material_comparison(request):
    """原料对比分析API"""
    # 获取查询参数
    material_names = request.GET.getlist('material_name')
    suppliers = request.GET.getlist('supplier')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    test_item = request.GET.get('test_item', 'purity')
    
    # 构建查询条件
    filters = {}
    if material_names:
        filters['material_name__in'] = material_names
    if suppliers:
        filters['supplier__in'] = suppliers
    if start_date:
        filters['test_date__gte'] = start_date
    if end_date:
        filters['test_date__lte'] = end_date
    
    # 获取数据
    materials = RawMaterial.objects.filter(**filters).order_by('material_name', 'test_date')
    
    # 按原料名称分组
    comparison_data = {}
    for material in materials:
        value = getattr(material, test_item)
        if value is not None:
            if material.material_name not in comparison_data:
                comparison_data[material.material_name] = {
                    'supplier': material.supplier,
                    'data': [],
                    'stats': {}
                }
            comparison_data[material.material_name]['data'].append({
                'date': material.test_date.isoformat(),
                'value': value,
                'batch': material.material_batch,
                'status': material.judgment_status
            })
    
    # 计算统计信息
    for material_name, data_dict in comparison_data.items():
        values = [item['value'] for item in data_dict['data']]
        if values:
            data_dict['stats'] = {
                'count': len(values),
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'min': float(min(values)),
                'max': float(max(values)),
                'median': float(np.median(values)),
                'q1': float(np.percentile(values, 25)),
                'q3': float(np.percentile(values, 75))
            }
    
    # 计算过程能力指数 (Cp, Cpk)
    process_capability = {}
    standards = RawMaterialStandard.objects.filter(
        material_name__in=material_names if material_names else [],
        test_item=test_item
    )
    
    for standard in standards:
        if standard.material_name in comparison_data:
            values = [item['value'] for item in comparison_data[standard.material_name]['data']]
            if values and standard.lower_limit is not None and standard.upper_limit is not None:
                usl = standard.upper_limit
                lsl = standard.lower_limit
                mean_val = np.mean(values)
                std_val = np.std(values)
                
                if std_val > 0:
                    cp = (usl - lsl) / (6 * std_val)
                    cpu = (usl - mean_val) / (3 * std_val)
                    cpl = (mean_val - lsl) / (3 * std_val)
                    cpk = min(cpu, cpl)
                    
                    process_capability[standard.material_name] = {
                        'cp': float(cp),
                        'cpk': float(cpk),
                        'cpu': float(cpu),
                        'cpl': float(cpl),
                        'usl': usl,
                        'lsl': lsl,
                        'mean': float(mean_val),
                        'std': float(std_val)
                    }
    
    return JsonResponse({
        'comparison_data': comparison_data,
        'process_capability': process_capability,
        'metadata': {
            'material_names': material_names,
            'suppliers': suppliers,
            'start_date': start_date,
            'end_date': end_date,
            'test_item': test_item
        }
    })


@require_http_methods(["GET"])
def raw_material_options(request):
    """获取原料名称选项API"""
    # 获取所有不重复的原料名称
    material_names = RawMaterial.objects.values_list('material_name', flat=True).distinct().order_by('material_name')
    
    return JsonResponse({
        'material_names': list(material_names)
    })


@require_http_methods(["GET"])
def supplier_options(request):
    """获取供应商选项API"""
    # 获取所有不重复的供应商
    suppliers = RawMaterial.objects.values_list('supplier', flat=True).distinct().order_by('supplier')
    
    return JsonResponse({
        'suppliers': list(suppliers)
    })
