from django.shortcuts import render
from django.http import JsonResponse
from products.models import DryFilmProduct, AdhesiveProduct
from core.api_views import (
    get_product_data, search_products, get_moving_range_data, get_capability_analysis_data
)
from django.views.decorators.csrf import csrf_exempt

def index(request):
    """首页 - 查询和图表展示"""
    # 获取干膜产品筛选条件 - 使用set去重
    product_codes = list(set(DryFilmProduct.objects.values_list('product_code', flat=True)))
    production_lines = list(set(DryFilmProduct.objects.values_list('production_line', flat=True)))
    
    # 获取胶粘剂产品筛选条件 - 使用set去重
    adhesive_product_codes = list(set(AdhesiveProduct.objects.values_list('product_code', flat=True)))
    adhesive_production_lines = list(set(AdhesiveProduct.objects.values_list('production_line', flat=True)))
    
    context = {
        'product_codes': product_codes,
        'production_lines': production_lines,
        'adhesive_product_codes': adhesive_product_codes,
        'adhesive_production_lines': adhesive_production_lines,
    }
    return render(request, 'dashboard/index.html', context)

@csrf_exempt
def mobile_test(request):
    """移动端测试页面"""
    return render(request, 'mobile_test.html')

# API视图函数 - 直接使用core.api_views中的函数
get_product_data = get_product_data
search_products = search_products
get_moving_range_data = get_moving_range_data
get_capability_analysis_data = get_capability_analysis_data
