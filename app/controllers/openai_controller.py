from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers.base_controller import BaseController
from app.services.openai_service import OpenAIService
from marshmallow import Schema, fields, ValidationError


class DocumentationGenerationSchema(Schema):
    """Schema for documentation generation request."""
    file_name = fields.Str(required=True)
    base64 = fields.Str(required=True)


class CodeAnalysisSchema(Schema):
    """Schema for direct code analysis request."""
    code = fields.Str(required=True)
    file_path = fields.Str(required=True)
    model = fields.Str(required=False, allow_none=True)


class OpenAIController(BaseController):
    """Controller for OpenAI-related operations."""
    
    def __init__(self):
        super().__init__('openai', '/api/openai')
        self.openai_service = OpenAIService()
        self.documentation_schema = DocumentationGenerationSchema()
        self.code_analysis_schema = CodeAnalysisSchema()
    
    def _register_routes(self):
        """Set up the routes for this controller."""
        
        # Documentation generation routes
        self.blueprint.add_url_rule(
            '/generate-documentation',
            'generate_documentation',
            self.generate_documentation,
            methods=['POST']
        )
        
        # Health check route
        self.blueprint.add_url_rule(
            '/health',
            'health_check',
            self.health_check,
            methods=['GET']
        )
    
    @jwt_required()
    def generate_documentation(self):
        """
        Generate documentation for a file using base64 content.
        
        Expected JSON payload:
        {
            "file_name": "example.py",
            "base64": "base64_encoded_file_content"
        }
        """
        try:
            # Get current user
            current_user_id = get_jwt_identity()
            
            # Validate request data
            json_data = request.get_json()
            if not json_data:
                return self.error_response('No JSON data provided', 400)
            
            try:
                validated_data = self.documentation_schema.load(json_data)
            except ValidationError as e:
                return self.error_response(f'Validation error: {e.messages}', 400)
            
            # Generate documentation
            result = self.openai_service.generate_documentation_from_base64(
                file_name=validated_data['file_name'],
                base64_content=validated_data['base64']
            )
            
            # Add user info to result
            result['generated_by'] = current_user_id
            
            return self.success_response(
                data=result,
                message='Documentation generated successfully'
            )
            
        except Exception as e:
            self.logger.error(f"Error generating documentation: {str(e)}")
            return self.error_response(f'Failed to generate documentation: {str(e)}', 500)
    
    def health_check(self):
        """
        Health check endpoint for OpenAI service.
        """
        try:
            # Check if OpenAI API key is configured
            from flask import current_app
            api_key = current_app.config.get('THESIS_OPENAI_API_KEY')
            
            if not api_key:
                return self.error_response('OpenAI API key not configured', 503)
            
            return self.success_response(
                data={
                    'openai_configured': True,
                    'default_model': current_app.config.get('THESIS_OPENAI_MODEL', 'gpt-3.5-turbo'),
                    'max_tokens': current_app.config.get('THESIS_OPENAI_MAX_TOKENS', 2048),
                    'temperature': current_app.config.get('THESIS_OPENAI_TEMPERATURE', 0.7)
                },
                message='OpenAI service is healthy'
            )
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return self.error_response('OpenAI service health check failed', 503)
