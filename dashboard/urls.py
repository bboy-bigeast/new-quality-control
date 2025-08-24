from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='dashboard_index'),
    path('api/chart-data/', views.get_chart_data, name='chart_data'),
    path('api/search-products/', views.search_products, name='search_products'),
    path('api/moving-range-data/', views.get_moving_range_data, name='moving_range_data'),
    path('api/capability-analysis/', views.get_capability_analysis_data, name='capability_analysis'),
    # 胶粘剂产品API
    path('api/adhesive/chart-data/', views.get_adhesive_chart_data, name='adhesive_chart_data'),
    path('api/adhesive/search-products/', views.search_adhesive_products, name='adhesive_search_products'),
    path('api/adhesive/moving-range-data/', views.get_adhesive_moving_range_data, name='adhesive_moving_range_data'),
    path('api/adhesive/capability-analysis/', views.get_adhesive_capability_analysis_data, name='adhesive_capability_analysis'),
]
