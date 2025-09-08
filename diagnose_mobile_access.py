#!/usr/bin/env python
"""
诊断手机访问问题的脚本
检查网络连接、防火墙和静态文件服务
"""

import requests
import socket
import subprocess
import platform

def check_local_access():
    """检查本地访问"""
    print("🔍 检查本地访问:")
    print("=" * 50)
    
    test_urls = [
        "http://localhost:8000/",
        "http://localhost:8000/admin/login/",
        "http://localhost:8000/static/admin/css/base.css"
    ]
    
    for url in test_urls:
        try:
            response = requests.head(url, timeout=5)
            print(f"{url}: {response.status_code} ✅")
        except requests.exceptions.RequestException as e:
            print(f"{url}: 错误 ❌ - {e}")

def get_local_ip():
    """获取本机IP地址"""
    try:
        # 创建一个UDP socket来获取本机IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "无法获取IP"

def check_firewall():
    """检查防火墙设置"""
    print("\n🔥 检查防火墙:")
    print("=" * 50)
    
    local_ip = get_local_ip()
    print(f"本机IP地址: {local_ip}")
    
    # 检查Windows防火墙
    if platform.system() == "Windows":
        try:
            result = subprocess.run(
                ['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=all'],
                capture_output=True, text=True, timeout=10
            )
            if "8000" in result.stdout:
                print("✅ 端口8000可能在防火墙规则中")
            else:
                print("⚠️  未找到端口8000的防火墙规则")
        except:
            print("⚠️  无法检查防火墙设置")
    else:
        print("⚠️  非Windows系统，跳过防火墙检查")

def check_network_connectivity():
    """检查网络连通性"""
    print("\n🌐 检查网络连通性:")
    print("=" * 50)
    
    local_ip = get_local_ip()
    if local_ip != "无法获取IP":
        print(f"请确保手机和电脑连接到同一个WiFi网络")
        print(f"手机应该访问: http://{local_ip}:8000")
        print(f"而不是: http://localhost:8000")
    else:
        print("无法确定本机IP地址")

def provide_troubleshooting_steps():
    """提供故障排除步骤"""
    print("\n🔧 故障排除步骤:")
    print("=" * 50)
    print("1. ✅ 确保手机和电脑连接到同一个WiFi网络")
    print("2. ✅ 在手机浏览器中访问正确的IP地址（不是localhost）")
    print("3. 🔄 清除手机浏览器缓存")
    print("4. 📱 尝试使用不同的手机浏览器")
    print("5. 🔍 检查手机浏览器开发者工具中的网络请求")
    print("6. 🌐 确保电脑防火墙允许端口8000的入站连接")

if __name__ == "__main__":
    print("📱 手机访问问题诊断工具")
    print("=" * 60)
    
    check_local_access()
    check_firewall()
    check_network_connectivity()
    provide_troubleshooting_steps()
    
    local_ip = get_local_ip()
    if local_ip != "无法获取IP":
        print(f"\n🎯 手机访问地址: http://{local_ip}:8000")
    else:
        print("\n❌ 无法确定本机IP地址，请手动检查网络设置")
