from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Avg, StdDev
from products.models import DryFilmProduct, ProductStandard
import json
from datetime import datetime, timedelta

def index(request):
    """首页 - 查询和图表展示"""
    # 获取筛选条件
    product_codes = DryFilmProduct.objects.values_list('product_code', flat=True).distinct()
    production_lines = DryFilmProduct.objects.values_list('production_line', flat=True).distinct()
    
    context = {
        'product_codes': product_codes,
        'production_lines': production_lines,
    }
    return render(request, 'dashboard/index.html', context)

def get_chart_data(request):
    """获取图表数据的API"""
    if request.method == 'GET':
        try:
            # 获取筛选参数
            product_code = request.GET.get('product_code')
            production_line = request.GET.get('production_line')
            test_item = request.GET.get('test_item')
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            
            # 构建查询条件
            filters = {}
            if product_code:
                filters['product_code'] = product_code
            if production_line:
                filters['production_line'] = production_line
            if start_date:
                filters['test_date__gte'] = start_date
            if end_date:
                filters['test_date__lte'] = end_date
            
            # 查询数据
            queryset = DryFilmProduct.objects.filter(**filters).order_by('test_date', 'batch_number')
            
            # 准备图表数据
            labels = []
            data = []
            
            for product in queryset:
                # 使用批次号前8位作为日期（格式：YYYYMMDD）
                batch_date = product.batch_number[:8] if len(product.batch_number) >= 8 else product.test_date.strftime('%Y%m%d')
                labels.append(batch_date)
                
                # 根据选择的测试项目获取数据
                if test_item == 'solid_content':
                    data.append(product.solid_content)
                elif test_item == 'viscosity':
                    data.append(product.viscosity)
                elif test_item == 'acid_value':
                    data.append(product.acid_value)
                elif test_item == 'moisture':
                    data.append(product.moisture)
                elif test_item == 'residual_monomer':
                    data.append(product.residual_monomer)
                elif test_item == 'weight_avg_molecular_weight':
                    data.append(product.weight_avg_molecular_weight)
                elif test_item == 'pdi':
                    data.append(product.pdi)
                elif test_item == 'color':
                    data.append(product.color)
                else:
                    data.append(None)
            
            # 计算统计信息
            valid_data = [x for x in data if x is not None]
            if valid_data:
                avg = sum(valid_data) / len(valid_data)
                std_dev = (sum((x - avg) ** 2 for x in valid_data) / len(valid_data)) ** 0.5
            else:
                avg = 0
                std_dev = 0
            
            response_data = {
                'labels': labels,
                'data': data,
                'statistics': {
                    'average': avg,
                    'std_dev': std_dev,
                    'std_dev_lines': {
                        'plus_1sigma': avg + std_dev,
                        'minus_1sigma': avg - std_dev,
                        'plus_2sigma': avg + 2 * std_dev,
                        'minus_2sigma': avg - 2 * std_dev,
                        'plus_3sigma': avg + 3 * std_dev,
                        'minus_3sigma': avg - 3 * std_dev,
                        'plus_4sigma': avg + 4 * std_dev,
                        'minus_4sigma': avg - 4 * std_dev,
                        'plus_5sigma': avg + 5 * std_dev,
                        'minus_5sigma': avg - 5 * std_dev,
                    }
                }
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def search_products(request):
    """产品查询功能"""
    if request.method == 'GET':
        try:
            # 获取查询参数
            product_code = request.GET.get('product_code')
            batch_number = request.GET.get('batch_number')
            production_line = request.GET.get('production_line')
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            
            # 构建查询条件
            filters = {}
            if product_code:
                filters['product_code__icontains'] = product_code
            if batch_number:
                filters['batch_number__icontains'] = batch_number
            if production_line:
                filters['production_line'] = production_line
            if start_date:
                filters['test_date__gte'] = start_date
            if end_date:
                filters['test_date__lte'] = end_date
            
            # 查询数据
            products = DryFilmProduct.objects.filter(**filters).order_by('-test_date', 'batch_number')
            
            # 转换为JSON格式
            product_list = []
            for product in products:
                product_list.append({
                    'id': product.id,
                    'product_code': product.product_code,
                    'batch_number': product.batch_number,
                    'production_line': product.production_line,
                    'inspector': product.inspector,
                    'test_date': product.test_date.strftime('%Y-%m-%d'),
                    'factory_judgment': product.factory_judgment,
                    'internal_control_judgment': product.internal_control_judgment,
                    'solid_content': product.solid_content,
                    'viscosity': product.viscosity,
                    'acid_value': product.acid_value,
                })
            
            return JsonResponse({'products': product_list})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def get_moving_range_data(request):
    """获取移动极差图数据"""
    if request.method == 'GET':
        try:
            # 获取筛选参数
            product_code = request.GET.get('product_code')
            production_line = request.GET.get('production_line')
            test_item = request.GET.get('test_item')
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            
            # 构建查询条件
            filters = {}
            if product_code:
                filters['product_code'] = product_code
            if production_line:
                filters['production_line'] = production_line
            if start_date:
                filters['test_date__gte'] = start_date
            if end_date:
                filters['test_date__lte'] = end_date
            
            # 查询数据并按测试日期排序
            queryset = DryFilmProduct.objects.filter(**filters).order_by('test_date', 'batch_number')
            
            # 准备移动极差数据
            labels = []
            data_values = []
            moving_ranges = []
            
            previous_value = None
            for product in queryset:
                # 使用批次号前8位作为日期
                batch_date = product.batch_number[:8] if len(product.batch_number) >= 8 else product.test_date.strftime('%Y%m%d')
                labels.append(batch_date)
                
                # 获取当前值
                current_value = None
                if test_item == 'solid_content':
                    current_value = product.solid_content
                elif test_item == 'viscosity':
                    current_value = product.viscosity
                elif test_item == 'acid_value':
                    current_value = product.acid_value
                elif test_item == 'moisture':
                    current_value = product.moisture
                elif test_item == 'residual_monomer':
                    current_value = product.residual_monomer
                elif test_item == 'weight_avg_molecular_weight':
                    current_value = product.weight_avg_molecular_weight
                elif test_item == 'pdi':
                    current_value = product.pdi
                elif test_item == 'color':
                    current_value = product.color
                
                data_values.append(current_value)
                
                # 计算移动极差
                if previous_value is not None and current_value is not None:
                    moving_range = abs(current_value - previous_value)
                    moving_ranges.append(moving_range)
                else:
                    moving_ranges.append(None)
                
                previous_value = current_value
            
            # 计算移动极差统计
            valid_moving_ranges = [x for x in moving_ranges if x is not None]
            if valid_moving_ranges:
                mr_avg = sum(valid_moving_ranges) / len(valid_moving_ranges)
                # 移动极差控制图参数
                ucl_mr = 3.267 * mr_avg  # 移动极差图上控制限
            else:
                mr_avg = 0
                ucl_mr = 0
            
            response_data = {
                'labels': labels,
                'data_values': data_values,
                'moving_ranges': moving_ranges,
                'statistics': {
                    'mr_average': mr_avg,
                    'ucl_mr': ucl_mr,
                }
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def get_capability_analysis_data(request):
    """获取能力分析正态分布图数据"""
    if request.method == 'GET':
        try:
            # 获取筛选参数
            product_code = request.GET.get('product_code')
            production_line = request.GET.get('production_line')
            test_item = request.GET.get('test_item')
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            
            print(f"Debug: product_code={product_code}, test_item={test_item}")
            
            # 构建查询条件
            filters = {}
            if product_code:
                filters['product_code'] = product_code
            if production_line:
                filters['production_line'] = production_line
            if start_date:
                filters['test_date__gte'] = start_date
            if end_date:
                filters['test_date__lte'] = end_date
            
            # 查询数据
            queryset = DryFilmProduct.objects.filter(**filters).order_by('test_date', 'batch_number')
            print(f"Debug: Found {queryset.count()} records")
            
            # 获取数据值
            data_values = []
            for product in queryset:
                if test_item == 'solid_content':
                    value = product.solid_content
                elif test_item == 'viscosity':
                    value = product.viscosity
                elif test_item == 'acid_value':
                    value = product.acid_value
                elif test_item == 'moisture':
                    value = product.moisture
                elif test_item == 'residual_monomer':
                    value = product.residual_monomer
                elif test_item == 'weight_avg_molecular_weight':
                    value = product.weight_avg_molecular_weight
                elif test_item == 'pdi':
                    value = product.pdi
                elif test_item == 'color':
                    value = product.color
                else:
                    value = None
                
                if value is not None:
                    data_values.append(float(value))
            
            print(f"Debug: data_values length = {len(data_values)}")
            
            # 计算过程能力指标
            if data_values and len(data_values) > 1:
                import numpy as np
                from scipy import stats
                
                data_array = np.array(data_values)
                mean = float(np.mean(data_array))
                std_dev = float(np.std(data_array, ddof=1))  # 样本标准差
                
                print(f"Debug: mean={mean}, std_dev={std_dev}")
                
                # 获取产品标准
                usl = None
                lsl = None
                target = mean
                
                if product_code:
                    try:
                        standard = ProductStandard.objects.get(
                            product_code=product_code,
                            test_item=test_item,  # 直接使用英文的test_item
                            standard_type='internal_control'
                        )
                        usl = float(standard.upper_limit) if standard.upper_limit else None
                        lsl = float(standard.lower_limit) if standard.lower_limit else None
                        target = float(standard.target_value) if standard.target_value else mean
                        print(f"Debug: Found standard - USL={usl}, LSL={lsl}, target={target}")
                    except ProductStandard.DoesNotExist:
                        print(f"Debug: No standard found for {product_code}-{test_item}")
                    except Exception as e:
                        print(f"Debug: Error getting standard: {e}")
                
                # 计算过程能力指数
                cp = None
                cpk = None
                if usl is not None and lsl is not None and std_dev > 0:
                    cp = float((usl - lsl) / (6 * std_dev))  # 过程能力指数
                    cpk = float(min((usl - mean) / (3 * std_dev), (mean - lsl) / (3 * std_dev)))  # 实际过程能力指数
                    print(f"Debug: CP={cp}, CPK={cpk}")
                
                # 生成正态分布曲线数据
                x_min = float(min(data_values) - 3 * std_dev) if data_values else 0
                x_max = float(max(data_values) + 3 * std_dev) if data_values else 1
                x = np.linspace(x_min, x_max, 100)
                y = stats.norm.pdf(x, mean, std_dev)
                
                # 计算直方图数据
                hist, bin_edges = np.histogram(data_values, bins=min(10, len(data_values)), density=True)
                
                response_data = {
                    'histogram': {
                        'values': [float(v) for v in hist.tolist()],
                        'bins': [float(b) for b in bin_edges.tolist()]
                    },
                    'normal_distribution': {
                        'x': [float(v) for v in x.tolist()],
                        'y': [float(v) for v in y.tolist()]
                    },
                    'statistics': {
                        'mean': mean,
                        'std_dev': std_dev,
                        'usl': usl,
                        'lsl': lsl,
                        'target': target,
                        'cp': cp,
                        'cpk': cpk,
                        'sample_size': len(data_values)
                    }
                }
            else:
                response_data = {
                    'histogram': {'values': [], 'bins': []},
                    'normal_distribution': {'x': [], 'y': []},
                    'statistics': {
                        'mean': 0,
                        'std_dev': 0,
                        'usl': None,
                        'lsl': None,
                        'target': 0,
                        'cp': None,
                        'cpk': None,
                        'sample_size': len(data_values) if data_values else 0
                    }
                }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            import traceback
            error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
