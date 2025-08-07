from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from app.controllers.base_controller import BaseController
from app.services.user_service import UserService, UserLoginSchema
from marshmallow import ValidationError
import logging


class AuthController(BaseController):
    """Authentication controller."""
    
    def __init__(self):
        super().__init__('auth')
        self.user_service = UserService()
    
    def _register_routes(self):
        """Register authentication routes."""
        self.blueprint.add_url_rule('/login', 'login', self.login, methods=['POST'])
        self.blueprint.add_url_rule('/refresh', 'refresh', self.refresh_token, methods=['POST'])
    
    def login(self):
        """User login endpoint."""
        try:
            # Validate request data
            data = self.validate_json(UserLoginSchema)
            
            # Authenticate user
            user = self.user_service.authenticate_user(
                data['email'], 
                data['password']
            )
            
            # Create tokens
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            
            self.logger.info(f"User logged in: {user.email}")
            
            return self.success_response({
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }, "Login successful")
            
        except ValueError as e:
            self.logger.warning(f"Login failed: {str(e)}")
            return self.error_response(str(e), 401)
        except Exception as e:
            self.logger.error(f"Login error: {str(e)}")
            return self.error_response("Login failed", 500)
    
    @jwt_required(refresh=True)
    def refresh_token(self):
        """Refresh access token."""
        try:
            current_user_id = get_jwt_identity()
            # Convert string identity back to int for database lookup
            user = self.user_service.get_user_by_id(int(current_user_id))
            
            # Create new access token
            access_token = create_access_token(identity=str(user.id))
            
            return self.success_response({
                'access_token': access_token
            }, "Token refreshed")
            
        except Exception as e:
            self.logger.error(f"Token refresh error: {str(e)}")
            return self.error_response("Token refresh failed", 500)