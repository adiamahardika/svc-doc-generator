from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
import logging


class BaseController:
    """Base controller class with common functionality."""
    
    def __init__(self, blueprint_name, url_prefix=None):
        self.blueprint = Blueprint(blueprint_name, __name__, url_prefix=url_prefix)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._register_routes()
    
    def _register_routes(self):
        """Register routes - to be implemented by subclasses."""
        pass
    
    def success_response(self, data=None, message="Success", status_code=200):
        """Create success response."""
        response = {
            'success': True,
            'message': message
        }
        if data is not None:
            response['data'] = data
        return jsonify(response), status_code
    
    def error_response(self, message="An error occurred", status_code=400, errors=None):
        """Create error response."""
        response = {
            'success': False,
            'message': message
        }
        if errors:
            response['errors'] = errors
        return jsonify(response), status_code
    
    def validate_json(self, schema_class):
        """Validate request JSON against schema."""
        try:
            schema = schema_class()
            return schema.load(request.get_json() or {})
        except ValidationError as e:
            raise ValueError(f"Validation error: {e.messages}")
