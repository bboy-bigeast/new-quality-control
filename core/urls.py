from django.urls import path
from . import views
from .api_views import get_product_data, search_products, get_moving_range_data, get_capability_analysis_data

urlpatterns = [
    path('clipboard-test/', views.clipboard_test, name='clipboard_test'),
    # API endpoints
    path('api/products/<str:product_type>/chart-data/', get_product_data, name='product_chart_data'),
    path('api/products/<str:product_type>/search/', search_products, name='product_search'),
    path('api/products/<str:product_type>/moving-range/', get_moving_range_data, name='moving_range_data'),
    path('api/products/<str:product_type>/capability-analysis/', get_capability_analysis_data, name='capability_analysis'),
]
