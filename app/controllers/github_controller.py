from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers.base_controller import BaseController
from app.services.github_service import GitHubService
from app.services.user_service import UserService
from marshmallow import Schema, fields, ValidationError


class GitHubRepositoryQuerySchema(Schema):
    """Schema for validating GitHub repository query parameters."""
    repo_name = fields.Str(required=False, allow_none=True, validate=lambda x: x is None or len(x.strip()) > 0)
    access_token = fields.Str(required=False, allow_none=True)


class GitHubRepositoryDetailQuerySchema(Schema):
    """Schema for validating GitHub repository detail query parameters."""
    owner = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    repo_name = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    access_token = fields.Str(required=False, allow_none=True)


class GitHubController(BaseController):
    """Controller for GitHub API integration."""
    
    def __init__(self):
        super().__init__('github', url_prefix='/api/github')
        self.github_service = GitHubService()
        self.user_service = UserService()
    
    def _register_routes(self):
        """Register GitHub routes."""
        self.blueprint.add_url_rule(
            '/repositories', 
            'get_user_repositories', 
            self.get_user_repositories, 
            methods=['GET']
        )
        self.blueprint.add_url_rule(
            '/repos/<string:owner>/<string:repo_name>', 
            'get_repository_details', 
            self.get_repository_details, 
            methods=['GET']
        )
    
    @jwt_required()
    def get_user_repositories(self):
        """
        Get repositories for the authenticated user.
        
        Query Parameters:
        - repo_name (optional): Repository name to search for
        - access_token (optional): GitHub access token for authenticated requests
        
        Returns:
        - 200: List of repositories
        - 400: Invalid parameters
        - 401: Authentication required
        - 404: User not found
        - 403: Rate limit exceeded or access forbidden
        - 500: Server error
        """
        try:
            # Get authenticated user ID from JWT token
            current_user_id = int(get_jwt_identity())
            
            # Get user from database to retrieve github_username
            try:
                current_user = self.user_service.get_user_by_id(current_user_id)
                github_username = current_user.github_username
            except ValueError:
                return self.error_response(
                    message="User not found",
                    status_code=404
                )
            
            # Get query parameters
            access_token = request.args.get('access_token')
            repo_name = request.args.get('repo_name')
            
            # Validate input
            schema = GitHubRepositoryQuerySchema()
            try:
                validated_data = schema.load({
                    'repo_name': repo_name,
                    'access_token': access_token
                })
            except ValidationError as e:
                return self.error_response(
                    message="Invalid parameters",
                    errors=e.messages,
                    status_code=400
                )
            
            # Call GitHub service
            result = self.github_service.get_user_repositories(
                github_username=github_username,
                repo_name=validated_data.get('repo_name'),
                access_token=validated_data.get('access_token')
            )
            
            if result['success']:
                return self.success_response(
                    data={
                        'repositories': result['data'],
                        'total_count': result['total_count'],
                        'returned_count': result['returned_count'],
                        'github_username': github_username
                    },
                    message=result['message']
                )
            else:
                # Map error codes to HTTP status codes
                status_code_map = {
                    'USER_NOT_FOUND': 404,
                    'RATE_LIMIT_EXCEEDED': 429,
                    'ACCESS_FORBIDDEN': 403,
                    'REQUEST_TIMEOUT': 408,
                    'CONNECTION_ERROR': 503,
                    'REQUEST_ERROR': 502,
                    'UNEXPECTED_ERROR': 500
                }
                
                status_code = status_code_map.get(result.get('error_code'), 500)
                
                return self.error_response(
                    message=result['message'],
                    status_code=status_code
                )
                
        except Exception as e:
            self.logger.error(f"Unexpected error in get_user_repositories: {str(e)}")
            return self.error_response(
                message="An unexpected error occurred while fetching repositories",
                status_code=500
            )
    
    def get_repository_details(self, owner, repo_name):
        """
        Get detailed information about a specific repository.
        
        Query Parameters:
        - access_token (optional): GitHub access token for authenticated requests
        
        Returns:
        - 200: Repository details
        - 400: Invalid parameters
        - 404: Repository not found
        - 500: Server error
        """
        try:
            # Get access token from query parameters
            access_token = request.args.get('access_token')
            
            # Validate input
            schema = GitHubRepositoryDetailQuerySchema()
            try:
                validated_data = schema.load({
                    'owner': owner,
                    'repo_name': repo_name,
                    'access_token': access_token
                })
            except ValidationError as e:
                return self.error_response(
                    message="Invalid parameters",
                    errors=e.messages,
                    status_code=400
                )
            
            # Call GitHub service
            result = self.github_service.get_repository_details(
                owner=validated_data['owner'],
                repo_name=validated_data['repo_name'],
                access_token=validated_data.get('access_token')
            )
            
            if result['success']:
                return self.success_response(
                    data=result['data'],
                    message=result['message']
                )
            else:
                status_code = 404 if result.get('error_code') == 'REPOSITORY_NOT_FOUND' else 500
                return self.error_response(
                    message=result['message'],
                    status_code=status_code
                )
                
        except Exception as e:
            self.logger.error(f"Unexpected error in get_repository_details: {str(e)}")
            return self.error_response(
                message="An unexpected error occurred while fetching repository details",
                status_code=500
            )
