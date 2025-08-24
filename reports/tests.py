from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
import json
from .models import InspectionReport
from products.models import DryFilmProduct, ProductStandard

class InspectionReportTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # 创建测试产品
        self.product = DryFilmProduct.objects.create(
            product_code='TEST001',
            batch_number='BATCH001',
            production_line='Test Line',
            inspector='Test Inspector',
            test_date=timezone.now().date(),
            sample_category='Test Category',
            modified_by='Test User',
            solid_content=50.0,
            viscosity=100.0,
            acid_value=5.0
        )
        
        # 创建产品标准
        self.standard1 = ProductStandard.objects.create(
            product_code='TEST001',
            test_item='solid_content',
            test_condition='室温',
            unit='%',
            lower_limit=45.0,
            upper_limit=55.0,
            analysis_method='GB/T 6672'
        )
        
        self.standard2 = ProductStandard.objects.create(
            product_code='TEST001',
            test_item='viscosity',
            test_condition='室温',
            unit='mPa·s',
            lower_limit=80.0,
            upper_limit=120.0,
            analysis_method='GB/T 1040'
        )
    
    def test_create_report_with_selected_items(self):
        """测试创建报告时selected_items字段正确处理对象数组"""
        self.client.login(username='testuser', password='testpass123')
        
        # 模拟前端发送的数据格式
        report_data = {
            'report_type': 'dryfilm',
            'product_code': 'TEST001',
            'batch_number': 'BATCH001',
            'production_date': str(timezone.now().date()),
            'inspector': 'Test Inspector',
            'reviewer': 'Test Reviewer',
            'selected_items': [
                {
                    'name': 'solid_content',
                    'test_condition': '室温',
                    'unit': '%',
                    'lower_limit': 45.0,
                    'upper_limit': 55.0,
                    'analysis_method': 'GB/T 6672'
                },
                {
                    'name': 'viscosity',
                    'test_condition': '室温',
                    'unit': 'mPa·s',
                    'lower_limit': 80.0,
                    'upper_limit': 120.0,
                    'analysis_method': 'GB/T 1040'
                }
            ],
            'remarks': 'Test remarks'
        }
        
        response = self.client.post(
            '/reports/create/',
            data=json.dumps(report_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        
        # 验证报告已创建
        report = InspectionReport.objects.get(id=response_data['report_id'])
        self.assertEqual(report.report_type, 'dryfilm')
        self.assertEqual(report.batch_number, 'BATCH001')
        
        # 验证selected_items字段正确保存
        self.assertEqual(len(report.selected_items), 2)
        self.assertEqual(report.selected_items[0]['name'], 'solid_content')
        self.assertEqual(report.selected_items[1]['name'], 'viscosity')
        
        # 验证test_results字段自动生成
        self.assertEqual(len(report.test_results), 2)
        self.assertEqual(report.test_results[0]['test_item'], 'solid_content')
        self.assertEqual(report.test_results[1]['test_item'], 'viscosity')
        self.assertEqual(report.test_results[0]['test_value'], 50.0)
        self.assertEqual(report.test_results[1]['test_value'], 100.0)
    
    def test_create_report_with_string_selected_items_should_succeed(self):
        """测试使用字符串数组的selected_items应该成功（验证修复后的行为）"""
        self.client.login(username='testuser', password='testpass123')
        
        # 模拟前端发送的字符串数组格式
        report_data = {
            'report_type': 'dryfilm',
            'product_code': 'TEST001',
            'batch_number': 'BATCH001',
            'production_date': str(timezone.now().date()),
            'inspector': 'Test Inspector',
            'selected_items': ['solid_content', 'viscosity'],  # 这是字符串数组
            'remarks': 'Test remarks'
        }
        
        response = self.client.post(
            '/reports/create/',
            data=json.dumps(report_data),
            content_type='application/json'
        )
        
        # 这个测试应该成功，因为修复后后端可以处理字符串数组
        response_data = response.json()
        self.assertTrue(response_data['success'])
        
        # 验证报告已创建
        report = InspectionReport.objects.get(id=response_data['report_id'])
        self.assertEqual(report.report_type, 'dryfilm')
        self.assertEqual(report.batch_number, 'BATCH001')
        
        # 验证selected_items字段正确保存为字符串数组
        self.assertEqual(len(report.selected_items), 2)
        self.assertEqual(report.selected_items[0], 'solid_content')
        self.assertEqual(report.selected_items[1], 'viscosity')
        
        # 验证test_results字段自动生成
        self.assertEqual(len(report.test_results), 2)
        self.assertEqual(report.test_results[0]['test_item'], 'solid_content')
        self.assertEqual(report.test_results[1]['test_item'], 'viscosity')
        self.assertEqual(report.test_results[0]['test_value'], 50.0)
        self.assertEqual(report.test_results[1]['test_value'], 100.0)
    
    def test_get_batch_info(self):
        """测试获取批号信息功能"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(
            '/reports/get-batch-info/',
            {'report_type': 'dryfilm', 'batch_number': 'BATCH001'}
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        
        # 验证返回的产品信息
        self.assertEqual(response_data['product_info']['product_code'], 'TEST001')
        
        # 验证返回的可用检测项目
        self.assertEqual(len(response_data['available_items']), 2)
        self.assertEqual(response_data['available_items'][0]['name'], 'solid_content')
        self.assertEqual(response_data['available_items'][1]['name'], 'viscosity')
