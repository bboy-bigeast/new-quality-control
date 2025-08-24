from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='dashboard_index'),
    # 统一的产品API路由
    path('api/products/<str:product_type>/chart-data/', views.get_product_data, name='product_chart_data'),
    path('api/products/<str:product_type>/search/', views.search_products, name='product_search'),
    path('api/products/<str:product_type>/moving-range/', views.get_moving_range_data, name='product_moving_range'),
    path('api/products/<str:product_type>/capability-analysis/', views.get_capability_analysis_data, name='product_capability_analysis'),
]
