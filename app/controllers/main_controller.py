from flask import Blueprint, jsonify
from app.controllers.base_controller import BaseController


class MainController(BaseController):
    """Main application controller."""
    
    def __init__(self):
        super().__init__('main')
    
    def _register_routes(self):
        """Register main routes."""
        self.blueprint.add_url_rule('/', 'index', self.index, methods=['GET'])
        self.blueprint.add_url_rule('/health', 'health_check', self.health_check, methods=['GET'])
        self.blueprint.add_url_rule('/api/status', 'api_status', self.api_status, methods=['GET'])
    
    def index(self):
        """Root endpoint."""
        return self.success_response({
            'message': 'Flask OOP API is running',
            'version': '1.0.0'
        })
    
    def health_check(self):
        """Health check endpoint."""
        return self.success_response({
            'status': 'healthy',
            'timestamp': '2025-01-28T00:00:00Z'
        })
    
    def api_status(self):
        """API status endpoint."""
        return self.success_response({
            'api': 'Flask OOP Backend',
            'version': '1.0.0',
            'status': 'active',
            'endpoints': {
                'auth': '/api/auth',
                'users': '/api/users',
                'github': '/api/github',
                'health': '/health'
            }
        })
