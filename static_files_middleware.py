"""
Custom middleware for handling static files and favicon requests
"""
import os
from django.http import HttpResponse
from django.conf import settings
from pathlib import Path

class FaviconMiddleware:
    """
    Middleware to handle favicon.ico requests directly
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Pre-load favicon content
        self.favicon_path = settings.STATIC_ROOT / 'favicon.ico'
        self.favicon_content = None
        if self.favicon_path.exists():
            with open(self.favicon_path, 'rb') as f:
                self.favicon_content = f.read()

    def __call__(self, request):
        # Handle favicon.ico requests
        if request.path == '/favicon.ico':
            if self.favicon_content:
                return HttpResponse(
                    self.favicon_content, 
                    content_type='image/x-icon',
                    status=200
                )
            else:
                return HttpResponse(status=404)
        
        return self.get_response(request)


class StaticFileOptimizationMiddleware:
    """
    Middleware to optimize static file serving and caching
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add caching headers for static files
        if request.path.startswith('/static/'):
            response['Cache-Control'] = 'public, max-age=31536000'  # 1 year
            response['Expires'] = 'Sun, 17 Jan 2038 19:14:07 GMT'
        
        return response
