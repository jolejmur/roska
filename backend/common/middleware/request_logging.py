"""
Request logging middleware
"""
import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('apps')


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all requests and responses
    """

    def process_request(self, request):
        """Log request information"""
        request.start_time = time.time()

        logger.info(
            f"Request: {request.method} {request.path}",
            extra={
                'method': request.method,
                'path': request.path,
                'user': getattr(request.user, 'email', 'anonymous'),
            }
        )

    def process_response(self, request, response):
        """Log response information"""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time

            logger.info(
                f"Response: {request.method} {request.path} - {response.status_code} ({duration:.2f}s)",
                extra={
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration': duration,
                    'user': getattr(request.user, 'email', 'anonymous'),
                }
            )

        return response
