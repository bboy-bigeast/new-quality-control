"""
Middleware to serve static files in production with Waitress
Add this to your MIDDLEWARE setting
"""

import os
from django.conf import settings
from django.http import HttpResponse
from django.utils.http import http_date
from django.core.exceptions import ImproperlyConfigured
import mimetypes
import time

class StaticFilesMiddleware:
    """
    Middleware to serve static files in production environment
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.static_root = settings.STATIC_ROOT
        
        if not self.static_root:
            raise ImproperlyConfigured(
                "STATIC_ROOT is not set. Run 'python manage.py collectstatic' first."
            )
            
        if not os.path.exists(self.static_root):
            raise ImproperlyConfigured(
                f"STATIC_ROOT directory '{self.static_root}' does not exist. "
                "Run 'python manage.py collectstatic' first."
            )

    def __call__(self, request):
        # Check if this is a static file request
        if request.path.startswith(settings.STATIC_URL):
            return self.serve_static_file(request)
        
        return self.get_response(request)

    def serve_static_file(self, request):
        """Serve static files directly"""
        # Remove the static URL prefix to get the file path
        relative_path = request.path[len(settings.STATIC_URL):]
        file_path = os.path.join(self.static_root, relative_path)
        
        # Security check: prevent directory traversal
        file_path = os.path.normpath(file_path)
        if not file_path.startswith(os.path.abspath(self.static_root)):
            return HttpResponse('Forbidden', status=403)
        
        # Check if file exists
        if not os.path.isfile(file_path):
            return HttpResponse('Not Found', status=404)
        
        # Determine content type
        content_type, encoding = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        # Read file content
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
        except IOError:
            return HttpResponse('Server Error', status=500)
        
        # Create response with proper headers
        response = HttpResponse(content, content_type=content_type)
        
        # Set caching headers (1 day cache)
        response['Cache-Control'] = 'public, max-age=86400'
        response['Last-Modified'] = http_date(os.path.getmtime(file_path))
        response['Expires'] = http_date(time.time() + 86400)
        
        return response
