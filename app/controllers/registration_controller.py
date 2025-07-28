from flask import Blueprint, jsonify, request, current_app
from app.controllers.base_controller import BaseController
from app.services.user_service import UserService, UserSchema
from marshmallow import ValidationError
import requests


class RegistrationController(BaseController):
    """Registration controller for user sign-up."""
    
    def __init__(self):
        super().__init__('registration', url_prefix='/api/register')
        self.user_service = UserService()
        self.user_schema = UserSchema()
    
    def _register_routes(self):
        """Register registration routes."""
        self.blueprint.add_url_rule('', 'register', self.register, methods=['POST'])
        self.blueprint.add_url_rule('/validate-github', 'validate_github', self.validate_github_username, methods=['POST'])
    
    def register(self):
        """User registration endpoint."""
        try:
            # Validate request data
            data = self.validate_json(UserSchema)
            
            # Additional validation for confirm password (frontend specific)
            if 'confirmPassword' in request.get_json():
                json_data = request.get_json()
                if data['password'] != json_data.get('confirmPassword'):
                    return self.error_response("Passwords do not match", 400)
            
            # Create user
            user = self.user_service.create_user(data)
            
            self.logger.info(f"User registered: {user.email}")
            
            return self.success_response(
                self.user_schema.dump(user),
                "Registration successful",
                201
            )
            
        except ValueError as e:
            self.logger.warning(f"Registration failed: {str(e)}")
            return self.error_response(str(e), 400)
        except Exception as e:
            self.logger.error(f"Registration error: {str(e)}")
            return self.error_response("Registration failed", 500)
    
    def validate_github_username(self):
        """Validate GitHub username endpoint."""
        try:
            json_data = request.get_json() or {}
            github_username = json_data.get('githubUsername', '').strip()
            
            if not github_username:
                return self.error_response("GitHub username is required", 400)
            
            if len(github_username) < 3:
                return self.error_response("GitHub username must be at least 3 characters", 400)
            
            # Check if username already exists in our database
            from app.models.user import User
            existing_user = User.find_by_github_username(github_username)
            if existing_user:
                return self.error_response("GitHub username is already taken", 400)
            
            # Validate with GitHub API
            try:
                github_api_url = f"{current_app.config['GITHUB_API_URL']}/users/{github_username}"
                response = requests.get(github_api_url, timeout=5)
                
                if response.status_code == 404:
                    return self.error_response("GitHub username does not exist", 400)
                elif response.status_code != 200:
                    return self.error_response("Error validating GitHub username", 500)
                
                # Username exists and is valid
                return self.success_response({
                    'valid': True,
                    'username': github_username
                }, "GitHub username is valid")
                
            except requests.RequestException:
                # If GitHub API is unavailable, just check format
                import re
                if not re.match(r'^[a-zA-Z0-9-]+$', github_username):
                    return self.error_response("Invalid GitHub username format", 400)
                
                return self.success_response({
                    'valid': True,
                    'username': github_username,
                    'note': 'Format validated (GitHub API unavailable)'
                }, "GitHub username format is valid")
            
        except Exception as e:
            self.logger.error(f"GitHub validation error: {str(e)}")
            return self.error_response("Validation failed", 500)
