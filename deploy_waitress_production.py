#!/usr/bin/env python
"""
Waitress deployment script for quality_control Django project with static file serving
Run with: python deploy_waitress_production.py
"""

import os
import sys
from waitress import serve
from django.core.wsgi import get_wsgi_application
from django.conf import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quality_control.settings')

# Get WSGI application
application = get_wsgi_application()

# Use StaticFilesHandler to serve static files in production
if not settings.DEBUG:
    application = StaticFilesHandler(application)

if __name__ == '__main__':
    print("🚀 Starting Waitress server for quality_control application...")
    print("📊 Server will be available at: http://localhost:8000")
    print("📁 Static files will be served automatically")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 60)
    
    # Serve the application using Waitress
    serve(
        application,
        host='0.0.0.0',  # Listen on all interfaces
        port=8000,       # Default port
        threads=4,       # Number of threads
        url_scheme='http'
    )
