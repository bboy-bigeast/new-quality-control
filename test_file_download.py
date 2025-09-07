#!/usr/bin/env python
"""测试文件下载功能"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quality_control.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from raw_materials.models import RawMaterial
from raw_materials.admin import RawMaterialAdmin
import io
import csv

def test_csv_download():
    """测试CSV文件下载功能"""
    print("开始测试CSV文件下载功能...")
    
    try:
        # 创建测试用户和请求
        factory = RequestFactory()
        # 检查用户是否已存在，如果存在则获取，否则创建
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'password': 'testpass'}
        )
        request = factory.get('/admin/')
        request.user = user

        # 获取一些测试数据
        queryset = RawMaterial.objects.all()[:3]
        admin = RawMaterialAdmin(RawMaterial, None)

        # 测试CSV导出
        response = admin.export_raw_materials_csv(request, queryset)
        
        print('CSV导出测试结果:')
        print(f'状态码: {response.status_code}')
        print(f'Content-Type: {response["Content-Type"]}')
        print(f'Content-Disposition: {response["Content-Disposition"]}')
        
        # 检查响应头
        assert response.status_code == 200
        assert 'text/csv' in response['Content-Type']
        assert 'attachment' in response['Content-Disposition']
        
        # 读取CSV内容
        content = response.content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))
        rows = list(csv_reader)
        
        print(f'CSV行数: {len(rows)}')
        if rows:
            print('CSV表头:', rows[0])
            if len(rows) > 1:
                print('第一行数据:', rows[1])
        
        print('✓ CSV文件下载功能测试通过！')
        return True
        
    except Exception as e:
        print(f'✗ CSV文件下载测试失败: {e}')
        return False

if __name__ == '__main__':
    success = test_csv_download()
    if success:
        print("\n所有文件下载功能测试通过！")
        print("您可以在Django Admin后台使用导出功能：")
        print("1. 访问 http://127.0.0.1:8000/admin/")
        print("2. 选择任意数据表")
        print("3. 勾选要导出的记录")
        print("4. 在动作下拉菜单中选择导出功能")
        print("5. 点击'执行'按钮下载文件")
    else:
        print("\n文件下载功能测试失败，请检查错误信息")
        sys.exit(1)
