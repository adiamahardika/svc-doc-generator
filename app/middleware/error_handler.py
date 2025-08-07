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