from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='dashboard_index'),
    path('api/chart-data/', views.get_chart_data, name='chart_data'),
    path('api/search-products/', views.search_products, name='search_products'),
    path('api/moving-range-data/', views.get_moving_range_data, name='moving_range_data'),
    path('api/capability-analysis/', views.get_capability_analysis_data, name='capability_analysis'),
]
