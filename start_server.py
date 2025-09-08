#!/usr/bin/env python
"""
Simple startup script for testing Waitress deployment
Run with: python start_server.py
"""

import os
import sys
import subprocess
import time

def start_waitress():
    """Start Waitress server in a subprocess"""
    print("🚀 Starting Quality Control application with Waitress...")
    print("📊 Server will be available at: http://localhost:8000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Start the waitress server
        process = subprocess.Popen([sys.executable, "deploy_waitress.py"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            import requests
            response = requests.get("http://localhost:8000", timeout=5)
            if response.status_code == 200:
                print("✅ Server started successfully!")
                print(f"📋 Status: {response.status_code}")
            else:
                print(f"⚠️  Server responded with status: {response.status_code}")
        except ImportError:
            print("ℹ️  requests module not available, skipping status check")
        except Exception as e:
            print(f"ℹ️  Could not connect to server: {e}")
        
        print("\nServer is running in background...")
        print("To stop the server, use: Ctrl+C")
        
        # Wait for process to complete
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        if process:
            process.terminate()
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    start_waitress()
