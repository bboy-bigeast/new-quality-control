from django.urls import path
from . import views

urlpatterns = [
    path('clipboard-test/', views.clipboard_test, name='clipboard_test'),
]
