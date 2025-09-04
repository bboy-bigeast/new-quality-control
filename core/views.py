from django.shortcuts import render
from django.http import HttpResponse

def clipboard_test(request):
    """测试复制功能的视图"""
    return render(request, 'test_clipboard_demo.html')
