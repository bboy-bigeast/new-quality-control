from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # 报告列表
    path('', views.report_list, name='report_list'),
    
    # 创建报告
    path('create/', views.create_report, name='create_report'),
    
    # 获取批号信息
    path('get-batch-info/', views.get_batch_info, name='get_batch_info'),
    
    # 报告详情
    path('<int:report_id>/', views.report_detail, name='report_detail'),
    
    # 生成PDF
    path('<int:report_id>/pdf/', views.generate_pdf, name='generate_pdf'),
    
    # 更新报告
    path('<int:report_id>/update/', views.update_report, name='update_report'),
    
    # 删除报告
    path('<int:report_id>/delete/', views.delete_report, name='delete_report'),
    
    # 获取报告数据（API）
    path('<int:report_id>/data/', views.get_report_data, name='get_report_data'),
]
