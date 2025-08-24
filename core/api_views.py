"""统一API视图模块 - 用于处理产品数据的API请求"""

from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q
from products.models import DryFilmProduct, AdhesiveProduct
from core.utils import (
    calculate_statistics, get_product_field_value, calculate_moving_range_data,
    calculate_capability_analysis, get_batch_date
)

def get_product_data(request, product_type):
    """获取产品图表数据的统一API"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # 获取筛选参数
        product_code = request.GET.get('product_code')
        production_line = request.GET.get('production_line')
        test_item = request.GET.get('test_item')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # 确定产品模型和字段映射
        if product_type == 'dryfilm':
            model = DryFilmProduct
            date_field = 'test_date'
        elif product_type == 'adhesive':
            model = AdhesiveProduct
            date_field = 'physical_test_date'
        else:
            return JsonResponse({'error': 'Invalid product type'}, status=400)
        
        # 构建查询条件
        filters = {}
        if product_code:
            filters['product_code'] = product_code
        if production_line:
            filters['production_line'] = production_line
        if start_date:
            filters[f'{date_field}__gte'] = start_date
        if end_date:
            filters[f'{date_field}__lte'] = end_date
        
        # 查询数据
        queryset = model.objects.filter(**filters).order_by(date_field, 'batch_number')
        
        # 准备图表数据
        labels = []
        data = []
        
        for product in queryset:
            labels.append(get_batch_date(product, date_field))
            value = get_product_field_value(product, test_item, product_type)
            data.append(value)
        
        # 计算统计信息
        statistics = calculate_statistics(data)
        
        response_data = {
            'labels': labels,
            'data': data,
            'statistics': statistics
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def search_products(request, product_type):
    """产品查询功能的统一API"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # 获取查询参数
        product_code = request.GET.get('product_code')
        batch_number = request.GET.get('batch_number')
        production_line = request.GET.get('production_line')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # 确定产品模型和字段映射
        if product_type == 'dryfilm':
            model = DryFilmProduct
            date_field = 'test_date'
            judgment_fields = ['external_final_judgment', 'internal_final_judgment']
        elif product_type == 'adhesive':
            model = AdhesiveProduct
            date_field = 'physical_test_date'
            judgment_fields = ['physical_judgment', 'tape_judgment', 'final_judgment']
        else:
            return JsonResponse({'error': 'Invalid product type'}, status=400)
        
        # 构建查询条件
        filters = {}
        if product_code:
            filters['product_code__icontains'] = product_code
        if batch_number:
            filters['batch_number__icontains'] = batch_number
        if production_line:
            filters['production_line'] = production_line
        if start_date:
            filters[f'{date_field}__gte'] = start_date
        if end_date:
            filters[f'{date_field}__lte'] = end_date
        
        # 查询数据
        products = model.objects.filter(**filters).order_by(f'-{date_field}', 'batch_number')
        
        # 转换为JSON格式
        product_list = []
        for product in products:
            product_data = {
                'id': product.id,
                'product_code': product.product_code,
                'batch_number': product.batch_number,
                'production_line': product.production_line,
                'test_date': getattr(product, date_field).strftime('%Y-%m-%d'),
                'judgment_status': product.judgment_status,
            }
            
            # 添加判定字段
            for field in judgment_fields:
                if hasattr(product, field):
                    product_data[field] = getattr(product, field)
            
            # 添加检测数据字段
            if product_type == 'dryfilm':
                product_data.update({
                    'inspector': product.inspector,
                    'solid_content': product.solid_content,
                    'viscosity': product.viscosity,
                    'acid_value': product.acid_value,
                })
            elif product_type == 'adhesive':
                product_data.update({
                    'physical_inspector': product.physical_inspector,
                    'tape_inspector': product.tape_inspector,
                    'solid_content': product.solid_content,
                    'viscosity': product.viscosity,
                    'acid_value': product.acid_value,
                })
            
            product_list.append(product_data)
        
        return JsonResponse({'products': product_list})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def get_moving_range_data(request, product_type):
    """获取移动极差图数据的统一API"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # 获取筛选参数
        product_code = request.GET.get('product_code')
        production_line = request.GET.get('production_line')
        test_item = request.GET.get('test_item')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # 确定产品模型和字段映射
        if product_type == 'dryfilm':
            model = DryFilmProduct
            date_field = 'test_date'
        elif product_type == 'adhesive':
            model = AdhesiveProduct
            date_field = 'physical_test_date'
        else:
            return JsonResponse({'error': 'Invalid product type'}, status=400)
        
        # 构建查询条件
        filters = {}
        if product_code:
            filters['product_code'] = product_code
        if production_line:
            filters['production_line'] = production_line
        if start_date:
            filters[f'{date_field}__gte'] = start_date
        if end_date:
            filters[f'{date_field}__lte'] = end_date
        
        # 查询数据并按测试日期排序
        queryset = model.objects.filter(**filters).order_by(date_field, 'batch_number')
        
        # 准备移动极差数据
        labels = []
        data_values = []
        
        for product in queryset:
            labels.append(get_batch_date(product, date_field))
            value = get_product_field_value(product, test_item, product_type)
            data_values.append(value)
        
        # 计算移动极差
        moving_range_result = calculate_moving_range_data(data_values)
        
        response_data = {
            'labels': labels,
            'data_values': data_values,
            'moving_ranges': moving_range_result['moving_ranges'],
            'statistics': moving_range_result['statistics']
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def get_capability_analysis_data(request, product_type):
    """获取能力分析正态分布图数据的统一API"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # 获取筛选参数
        product_code = request.GET.get('product_code')
        production_line = request.GET.get('production_line')
        test_item = request.GET.get('test_item')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # 确定产品模型和字段映射
        if product_type == 'dryfilm':
            model = DryFilmProduct
            date_field = 'test_date'
        elif product_type == 'adhesive':
            model = AdhesiveProduct
            date_field = 'physical_test_date'
        else:
            return JsonResponse({'error': 'Invalid product type'}, status=400)
        
        # 构建查询条件
        filters = {}
        if product_code:
            filters['product_code'] = product_code
        if production_line:
            filters['production_line'] = production_line
        if start_date:
            filters[f'{date_field}__gte'] = start_date
        if end_date:
            filters[f'{date_field}__lte'] = end_date
        
        # 查询数据
        queryset = model.objects.filter(**filters).order_by(date_field, 'batch_number')
        
        # 获取数据值
        data_values = []
        for product in queryset:
            value = get_product_field_value(product, test_item, product_type)
            if value is not None:
                data_values.append(float(value))
        
        # 计算能力分析
        capability_data = calculate_capability_analysis(data_values, product_code, test_item)
        
        return JsonResponse(capability_data)
        
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return JsonResponse({'error': str(e)}, status=400)
