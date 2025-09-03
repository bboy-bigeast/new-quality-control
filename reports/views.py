from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.conf import settings
import json

from .models import InspectionReport
from products.models import DryFilmProduct, AdhesiveProduct, ProductStandard

@login_required
def report_list(request):
    """检测报告列表"""
    reports = InspectionReport.objects.all().order_by('-report_date')
    
    # 分页
    paginator = Paginator(reports, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'reports/report_list.html', {
        'page_obj': page_obj,
        'report_types': InspectionReport.REPORT_TYPES
    })

@login_required
def create_report(request):
    """创建检测报告"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            report = InspectionReport(
                report_type=data.get('report_type'),
                product_code=data.get('product_code', ''),
                batch_number=data.get('batch_number'),
                production_date=data.get('production_date'),
                inspector=data.get('inspector', request.user.get_full_name() or request.user.username),
                reviewer=data.get('reviewer', ''),
                selected_items=data.get('selected_items', []),
                conclusion=data.get('conclusion', ''),
                remarks=data.get('remarks', ''),
                status='draft'
            )
            
            report.save()
            
            return JsonResponse({
                'success': True,
                'report_id': report.id,
                'report_number': report.report_number
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return render(request, 'reports/create_report.html', {
        'report_types': InspectionReport.REPORT_TYPES
    })

@login_required
def get_batch_info(request):
    """根据批号获取产品信息"""
    batch_number = request.GET.get('batch_number')
    report_type = request.GET.get('report_type')
    
    if not batch_number or not report_type:
        return JsonResponse({'error': '批号和报告类型不能为空'})
    
    try:
        if report_type == 'dryfilm':
            product = DryFilmProduct.objects.get(batch_number=batch_number)
            product_info = {
                'product_code': product.product_code,
                'production_date': product.test_date.strftime('%Y-%m-%d') if product.test_date else '',
                'inspector': product.inspector
            }
        elif report_type == 'adhesive':
            product = AdhesiveProduct.objects.get(batch_number=batch_number)
            product_info = {
                'product_code': product.product_code,
                'production_date': product.physical_test_date.strftime('%Y-%m-%d') if product.physical_test_date else '',
                'inspector': product.physical_inspector
            }
        else:
            return JsonResponse({'error': '无效的报告类型'})
        
        # 获取可用的检测项目
        standards = ProductStandard.objects.filter(product_code=product_info['product_code'])
        available_items = [
            {
                'name': standard.test_item,
                'test_condition': standard.test_condition,
                'unit': standard.unit,
                'lower_limit': standard.lower_limit,
                'upper_limit': standard.upper_limit,
                'analysis_method': standard.analysis_method
            }
            for standard in standards
        ]
        
        return JsonResponse({
            'success': True,
            'product_info': product_info,
            'available_items': available_items
        })
        
    except (DryFilmProduct.DoesNotExist, AdhesiveProduct.DoesNotExist):
        return JsonResponse({'error': '未找到对应的产品信息'})
    except Exception as e:
        return JsonResponse({'error': str(e)})

@login_required
def report_detail(request, report_id):
    """检测报告详情"""
    report = get_object_or_404(InspectionReport, id=report_id)
    
    # 处理检测结果，将英文项目名称转换为中文
    processed_results = []
    for result in report.test_results:
        processed_result = result.copy()
        test_item = result.get('test_item', '')
        # 转换项目名称为中文
        processed_result['test_item_chinese'] = TEST_ITEM_MAPPING.get(test_item, test_item)
        processed_results.append(processed_result)
    
    return render(request, 'reports/report_detail.html', {
        'report': report,
        'processed_results': processed_results  # 传递处理后的结果
    })

# 检测项目中英文映射
TEST_ITEM_MAPPING = {
    # 产品检测项目
    'appearance': '外观',
    'solid_content': '固含',
    'viscosity': '粘度',
    'acid_value': '酸值',
    'moisture': '水分',
    'residual_monomer': '残单',
    'weight_avg_molecular_weight': '重均分子量',
    'pdi': 'PDI',
    'color': '色度',
    'initial_tack': '初粘力',
    'peel_strength': '剥离力',
    'high_temperature_holding': '高温持粘',
    'room_temperature_holding': '常温持粘',
    'constant_load_peel': '定荷重剥离',
}

@login_required
def generate_pdf(request, report_id):
    """生成PDF报告"""
    report = get_object_or_404(InspectionReport, id=report_id)
    
    # 获取模板参数，默认为原始模板
    template_name = request.GET.get('template', 'reports/report_template.html')
    
    # 验证模板名称，防止路径遍历攻击
    valid_templates = [
        'reports/report_template.html',
        'reports/report_template_v2.html'
    ]
    
    if template_name not in valid_templates:
        template_name = 'reports/report_template.html'
    
    # 处理检测结果，将英文项目名称转换为中文
    processed_results = []
    for result in report.test_results:
        processed_result = result.copy()
        test_item = result.get('test_item', '')
        # 转换项目名称为中文
        processed_result['test_item_chinese'] = TEST_ITEM_MAPPING.get(test_item, test_item)
        processed_results.append(processed_result)
    
    # 生成HTML内容
    html_content = render_to_string(template_name, {
        'report': report,
        'company_name': settings.COMPANY_NAME,
        'report_version': settings.REPORT_VERSION,
        'processed_results': processed_results  # 传递处理后的结果
    })
    
    response = HttpResponse(html_content, content_type='text/html')
    response['Content-Disposition'] = f'attachment; filename="{report.report_number}.html"'
    return response

@login_required
def update_report(request, report_id):
    """更新检测报告"""
    report = get_object_or_404(InspectionReport, id=report_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # 更新基本信息
            report.inspector = data.get('inspector', report.inspector)
            report.reviewer = data.get('reviewer', report.reviewer)
            report.conclusion = data.get('conclusion', report.conclusion)
            report.remarks = data.get('remarks', report.remarks)
            report.status = data.get('status', report.status)
            
            # 更新签名信息
            if data.get('inspector_signature'):
                report.inspector_signature = data['inspector_signature']
            if data.get('reviewer_signature'):
                report.reviewer_signature = data['reviewer_signature']
            if data.get('review_date'):
                report.review_date = data['review_date']
            
            report.save()
            
            return JsonResponse({
                'success': True,
                'message': '报告更新成功'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'error': '无效的请求方法'})

@login_required
def delete_report(request, report_id):
    """删除检测报告"""
    report = get_object_or_404(InspectionReport, id=report_id)
    
    if request.method == 'POST':
        report.delete()
        return JsonResponse({'success': True, 'message': '报告删除成功'})
    
    return JsonResponse({'error': '无效的请求方法'})

@login_required
def get_report_data(request, report_id):
    """获取报告数据（API接口）"""
    report = get_object_or_404(InspectionReport, id=report_id)
    
    data = {
        'report_number': report.report_number,
        'report_type': report.report_type,
        'product_code': report.product_code,
        'batch_number': report.batch_number,
        'production_date': report.production_date.strftime('%Y-%m-%d') if report.production_date else '',
        'inspector': report.inspector,
        'reviewer': report.reviewer,
        'report_date': report.report_date.strftime('%Y-%m-%d'),
        'selected_items': report.selected_items,
        'test_results': report.test_results,
        'conclusion': report.conclusion,
        'remarks': report.remarks,
        'inspector_signature': report.inspector_signature,
        'reviewer_signature': report.reviewer_signature,
        'review_date': report.review_date.strftime('%Y-%m-%d') if report.review_date else '',
        'status': report.status
    }
    
    return JsonResponse(data)
