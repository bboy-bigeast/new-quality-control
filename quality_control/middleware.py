"""
Custom middleware for security headers and cache control.
"""

from django.utils.deprecation import MiddlewareMixin
import re


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers and proper cache control.
    """
    
    def process_response(self, request, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Handle cache control for static resources
        if self._is_static_resource(request.path):
            # Set long cache for static resources with immutable directive
            response['Cache-Control'] = 'max-age=31536000, immutable'
        else:
            # Handle cache control for dynamic content - prefer Cache-Control over Expires
            if 'Expires' in response and 'Cache-Control' not in response:
                cache_control = response.get('Cache-Control', '')
                if not cache_control:
                    response['Cache-Control'] = 'max-age=0, must-revalidate'
        
        # Remove unnecessary headers for static resources
        if self._is_static_resource(request.path):
            response.headers.pop('Content-Security-Policy', None)
        
        return response
    
    def _is_static_resource(self, path):
        """Check if the request path is for a static resource."""
        static_patterns = [
            r'\.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$',
            r'^/static/',
            r'^/media/'
        ]
        
        for pattern in static_patterns:
            if re.search(pattern, path):
                return True
        return False
