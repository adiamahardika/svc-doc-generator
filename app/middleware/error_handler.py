from flask import jsonify
import logging


class ErrorHandler:
    """Global error handler class."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def handle_bad_request(self, error):
        """Handle 400 Bad Request errors."""
        self.logger.warning(f"Bad request: {str(error)}")
        return jsonify({
            'success': False,
            'message': 'Bad request',
            'error': str(error)
        }), 400
    
    def handle_unauthorized(self, error):
        """Handle 401 Unauthorized errors."""
        self.logger.warning(f"Unauthorized access: {str(error)}")
        return jsonify({
            'success': False,
            'message': 'Unauthorized access',
            'error': 'Authentication required'
        }), 401
    
    def handle_forbidden(self, error):
        """Handle 403 Forbidden errors."""
        self.logger.warning(f"Forbidden access: {str(error)}")
        return jsonify({
            'success': False,
            'message': 'Forbidden',
            'error': 'Insufficient permissions'
        }), 403
    
    def handle_not_found(self, error):
        """Handle 404 Not Found errors."""
        self.logger.warning(f"Resource not found: {str(error)}")
        return jsonify({
            'success': False,
            'message': 'Resource not found',
            'error': 'The requested resource was not found'
        }), 404
    
    def handle_internal_error(self, error):
        """Handle 500 Internal Server errors."""
        self.logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': 'Something went wrong on our end'
        }), 500


class SecurityMiddleware:
    """Security middleware for additional security measures."""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security middleware."""
        app.after_request(self.add_security_headers)
    
    def add_security_headers(self, response):
        """Add security headers to responses."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response


class LoggingMiddleware:
    """Logging middleware for request/response logging."""
    
    def __init__(self, app=None):
        self.app = app
        self.logger = logging.getLogger(self.__class__.__name__)
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize logging middleware."""
        app.before_request(self.log_request)
        app.after_request(self.log_response)
    
    def log_request(self):
        """Log incoming requests."""
        from flask import request
        self.logger.info(f"{request.method} {request.url} - {request.remote_addr}")
    
    def log_response(self, response):
        """Log outgoing responses."""
        from flask import request
        self.logger.info(f"{request.method} {request.url} - {response.status_code}")
        return response
