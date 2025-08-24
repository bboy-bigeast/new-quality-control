import requests
import json

# 测试搜索API
base_url = "http://127.0.0.1:8000"

try:
    # 测试搜索API
    response = requests.get(f"{base_url}/api/search-products/", params={'product_code': 'DF-100'})
    print(f"搜索API状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"找到的产品数量: {len(data.get('products', []))}")
        if data.get('products'):
            for product in data['products'][:3]:
                print(f"批次: {product['batch_number']}, 牌号: {product['product_code']}")
    else:
        print(f"API错误: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("无法连接到服务器，请确保Django开发服务器正在运行")
except Exception as e:
    print(f"测试失败: {e}")
