from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers.base_controller import BaseController
from app.services.github_service import GitHubService
from app.services.user_service import UserService
from marshmallow import Schema, fields, ValidationError


class GitHubRepositoryQuerySchema(Schema):
    """Schema for validating GitHub repository query parameters."""
    search = fields.Str(required=False, allow_none=True, validate=lambda x: x is None or len(x.strip()) > 0)
    access_token = fields.Str(required=False, allow_none=True)
    page = fields.Int(required=False, missing=1, validate=lambda x: x >= 1)
    per_page = fields.Int(required=False, missing=30, validate=lambda x: 1 <= x <= 100)
    sort = fields.Str(required=False, missing='updated_at', validate=lambda x: x in ['updated_at', 'name'])
    order = fields.Str(required=False, missing='desc', validate=lambda x: x in ['asc', 'desc'])


class GitHubRepositoryDetailQuerySchema(Schema):
    """Schema for validating GitHub repository detail query parameters."""
    repo_name = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    path = fields.Str(required=False, allow_none=True, missing="")
    access_token = fields.Str(required=False, allow_none=True)


class GitHubRepositoryBranchesQuerySchema(Schema):
    """Schema for validating GitHub repository branches query parameters."""
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
            '/repository/<string:repo_name>', 
            'get_repository_details', 
            self.get_repository_details, 
            methods=['GET']
        )
        self.blueprint.add_url_rule(
            '/repository/<string:repo_name>/branches', 
            'get_repository_branches', 
            self.get_repository_branches, 
            methods=['GET']
        )
    
    @jwt_required()
    def get_user_repositories(self):
        """
        Get repositories for the authenticated user.
        
        Query Parameters:
        - search (optional): Search term for repositories (name, description, etc.)
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
            search = request.args.get('search')
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 30, type=int)
            sort = request.args.get('sort', 'updated_at')
            order = request.args.get('order', 'desc')
            
            # Validate input
            schema = GitHubRepositoryQuerySchema()
            try:
                validated_data = schema.load({
                    'search': search,
                    'access_token': access_token,
                    'page': page,
                    'per_page': per_page,
                    'sort': sort,
                    'order': order
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
                search=validated_data.get('search'),
                access_token=validated_data.get('access_token'),
                page=validated_data.get('page', 1),
                per_page=validated_data.get('per_page', 30),
                sort=validated_data.get('sort', 'updated_at'),
                order=validated_data.get('order', 'desc')
            )
            
            if result['success']:
                return self.success_response(
                    data={
                        'repositories': result['data'],
                        'total_count': result['total_count'],
                        'returned_count': result['returned_count'],
                        'github_username': github_username,
                        'pagination': {
                            'page': validated_data.get('page', 1),
                            'per_page': validated_data.get('per_page', 30),
                            'total_pages': result.get('total_pages', 1),
                            'has_next_page': result.get('has_next_page', False),
                            'has_prev_page': result.get('has_prev_page', False)
                        },
                        'sort': {
                            'sort_by': validated_data.get('sort', 'updated_at'),
                            'order': validated_data.get('order', 'desc')
                        }
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
    
    @jwt_required()
    def get_repository_details(self, repo_name):
        """
        Get contents of a file or directory in a repository for the authenticated user.
        
        Query Parameters:
        - path (optional): Path to file or directory (empty for root directory)
        - access_token (optional): GitHub access token for authenticated requests
        
        Returns:
        - 200: Repository contents (file or directory listing)
        - 400: Invalid parameters
        - 401: Authentication required
        - 404: User, repository, or path not found
        - 403: Access forbidden
        - 500: Server error
        """
        try:
            # Get authenticated user ID from JWT token
            current_user_id = int(get_jwt_identity())
            
            # Get user from database to retrieve github_username (owner)
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
            path = request.args.get('path', "")
            branch = request.args.get('branch', 'main')
            
            # Validate input
            schema = GitHubRepositoryDetailQuerySchema()
            try:
                validated_data = schema.load({
                    'repo_name': repo_name,
                    'path': path,
                    'access_token': access_token
                })
            except ValidationError as e:
                return self.error_response(
                    message="Invalid parameters",
                    errors=e.messages,
                    status_code=400
                )
            
            # Call GitHub service with authenticated user's github_username as owner
            result = self.github_service.get_repository_details(
                owner=github_username,
                repo_name=validated_data['repo_name'],
                path=validated_data.get('path', ""),
                branch=branch,
                access_token=validated_data.get('access_token')
            )
            
            if result['success']:
                return self.success_response(
                    data=result['data'],
                    message=result['message']
                )
            else:
                # Map error codes to HTTP status codes
                status_code_map = {
                    'PATH_NOT_FOUND': 404,
                    'REPOSITORY_NOT_FOUND': 404,
                    'ACCESS_FORBIDDEN': 403,
                    'REQUEST_ERROR': 500
                }
                
                status_code = status_code_map.get(result.get('error_code'), 500)
                return self.error_response(
                    message=result['message'],
                    status_code=status_code
                )
                
        except Exception as e:
            self.logger.error(f"Unexpected error in get_repository_details: {str(e)}")
            return self.error_response(
                message="An unexpected error occurred while fetching repository contents",
                status_code=500
            )
    
    @jwt_required()
    def get_repository_branches(self, repo_name):
        """
        Get branches for a repository of the authenticated user.
        
        Query Parameters:
        - access_token (optional): GitHub access token for authenticated requests
        
        Returns:
        - 200: List of repository branches
        - 400: Invalid parameters
        - 401: Authentication required
        - 404: User or repository not found
        - 403: Access forbidden
        - 500: Server error
        """
        try:
            # Get authenticated user ID from JWT token
            current_user_id = int(get_jwt_identity())
            
            # Get user from database to retrieve github_username (owner)
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
            
            # Validate input
            schema = GitHubRepositoryBranchesQuerySchema()
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
            
            # Call GitHub service with authenticated user's github_username as owner
            result = self.github_service.get_repository_branches(
                owner=github_username,
                repo_name=validated_data['repo_name'],
                access_token=validated_data.get('access_token')
            )
            
            if result['success']:
                return self.success_response(
                    data={
                        'branches': result['data'],
                        'total_count': result['total_count'],
                        'repository': result['repository']
                    },
                    message=result['message']
                )
            else:
                # Map error codes to HTTP status codes
                status_code_map = {
                    'REPOSITORY_NOT_FOUND': 404,
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
            self.logger.error(f"Unexpected error in get_repository_branches: {str(e)}")
            return self.error_response(
                message="An unexpected error occurred while fetching repository branches",
                status_code=500
            )
