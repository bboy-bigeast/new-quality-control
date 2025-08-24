from django.urls import path
from . import views

app_name = 'raw_materials'

urlpatterns = [
    # 网页视图
    path('', views.raw_material_list, name='raw_material_list'),
    path('dashboard/', views.raw_material_dashboard, name='raw_material_dashboard'),
    path('standards/', views.raw_material_standards, name='raw_material_standards'),
    path('<int:pk>/', views.raw_material_detail, name='raw_material_detail'),
    
    # API接口
    path('api/materials/', views.RawMaterialAPIView.as_view(), name='raw_material_api'),
    path('api/materials/<int:pk>/', views.RawMaterialAPIView.as_view(), name='raw_material_detail_api'),
    path('api/standards/', views.RawMaterialStandardAPIView.as_view(), name='raw_material_standard_api'),
    path('api/standards/<int:pk>/', views.RawMaterialStandardAPIView.as_view(), name='raw_material_standard_detail_api'),
    path('api/stats/', views.raw_material_stats, name='raw_material_stats'),
    path('api/charts/', views.raw_material_charts, name='raw_material_charts'),
    path('api/comparison/', views.raw_material_comparison, name='raw_material_comparison'),
]
