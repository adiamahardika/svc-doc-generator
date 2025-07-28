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
        self.blueprint.add_url_rule('/logout', 'logout', self.logout, methods=['POST'])
        self.blueprint.add_url_rule('/me', 'current_user', self.get_current_user, methods=['GET'])
    
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
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
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
            user = self.user_service.get_user_by_id(current_user_id)
            
            # Create new access token
            access_token = create_access_token(identity=user.id)
            
            return self.success_response({
                'access_token': access_token
            }, "Token refreshed")
            
        except Exception as e:
            self.logger.error(f"Token refresh error: {str(e)}")
            return self.error_response("Token refresh failed", 500)
    
    @jwt_required()
    def logout(self):
        """User logout endpoint."""
        # In a real application, you might want to blacklist the token
        # For now, we'll just return a success message
        return self.success_response(message="Logout successful")
    
    @jwt_required()
    def get_current_user(self):
        """Get current authenticated user."""
        try:
            current_user_id = get_jwt_identity()
            user = self.user_service.get_user_by_id(current_user_id)
            
            return self.success_response({
                'user': user.to_dict()
            })
            
        except Exception as e:
            self.logger.error(f"Get current user error: {str(e)}")
            return self.error_response("Failed to get user info", 500)
