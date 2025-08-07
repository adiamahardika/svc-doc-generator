from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers.base_controller import BaseController
from app.services.openai_service import OpenAIService
from marshmallow import Schema, fields, ValidationError


class FileItemSchema(Schema):
    """Schema for individual file item."""
    file_name = fields.Str(required=True)
    base64 = fields.Str(required=True)


class DocumentationGenerationSchema(Schema):
    """Schema for documentation generation request."""
    files = fields.List(fields.Nested(FileItemSchema), required=True, validate=lambda x: 1 <= len(x) <= 5)


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
        Generate documentation for multiple files using base64 content.
        
        Expected JSON payload:
        {
            "files": [
                {
                    "file_name": "example1.py",
                    "base64": "base64_encoded_file_content1"
                },
                {
                    "file_name": "example2.js",
                    "base64": "base64_encoded_file_content2"
                }
            ]
        }
        
        Maximum 5 files per request.
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
            
            # Process multiple files
            results = []
            errors = []
            
            for file_item in validated_data['files']:
                try:
                    # Generate documentation for each file
                    result = self.openai_service.generate_documentation_from_base64(
                        file_name=file_item['file_name'],
                        base64_content=file_item['base64']
                    )
                    results.append(result)
                    
                except Exception as e:
                    error_info = {
                        'file_name': file_item['file_name'],
                        'error': str(e)
                    }
                    errors.append(error_info)
                    self.logger.error(f"Error processing file {file_item['file_name']}: {str(e)}")
            
            # Prepare response
            response_data = {
                'total_files': len(validated_data['files']),
                'successful': len(results),
                'failed': len(errors),
                'results': results,
                'errors': errors if errors else None,
                'generated_by': current_user_id
            }
            
            # Determine response status based on results
            if results and not errors:
                # All files processed successfully
                return self.success_response(
                    data=response_data,
                    message=f'Documentation generated successfully for {len(results)} files'
                )
            elif results and errors:
                # Some files processed successfully, some failed
                return self.success_response(
                    data=response_data,
                    message=f'Documentation generated for {len(results)} files, {len(errors)} files failed'
                )
            else:
                # All files failed
                return self.error_response(
                    'Failed to generate documentation for all files',
                    500,
                    data=response_data
                )
            
        except Exception as e:
            self.logger.error(f"Error in batch documentation generation: {str(e)}")
            return self.error_response(f'Failed to process documentation request: {str(e)}', 500)
    
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
