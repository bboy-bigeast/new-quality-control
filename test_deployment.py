#!/usr/bin/env python
"""
Test script to verify Waitress deployment
Run with: python test_deployment.py
"""

import subprocess
import sys
import time
import threading
import requests

def test_waitress_deployment():
    """Test the Waitress deployment"""
    print("🧪 Testing Waitress deployment...")
    
    # Start Waitress server in background
    try:
        process = subprocess.Popen([
            sys.executable, 
            "deploy_waitress_production.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("⏳ Waiting for server to start (5 seconds)...")
        time.sleep(5)
        
        # Test if server is responding
        try:
            response = requests.get("http://localhost:8000", timeout=10)
            if response.status_code == 200:
                print("✅ Server is running and responding correctly!")
                print(f"📋 Status Code: {response.status_code}")
                print(f"📄 Content Length: {len(response.text)} characters")
            else:
                print(f"⚠️  Server responded with unexpected status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Could not connect to server: {e}")
            print("This might be normal if the server is still starting up.")
        
        # Stop the server
        print("🛑 Stopping server...")
        process.terminate()
        process.wait(timeout=10)
        print("✅ Server stopped successfully")
        
    except Exception as e:
        print(f"❌ Error during deployment test: {e}")

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = ['waitress', 'django', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is NOT installed")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All dependencies are installed")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("Quality Control Deployment Test")
    print("=" * 50)
    
    if check_dependencies():
        print("\n" + "=" * 30)
        test_waitress_deployment()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("=" * 50)
