from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers.base_controller import BaseController
from app.services.user_service import UserService, UserSchema, UserUpdateSchema
from marshmallow import ValidationError


class UserController(BaseController):
    """User management controller."""
    
    def __init__(self):
        super().__init__('users')
        self.user_service = UserService()
        self.user_schema = UserSchema()
        self.users_schema = UserSchema(many=True)
        self.update_schema = UserUpdateSchema()
    
    def _register_routes(self):
        """Register user routes."""
        self.blueprint.add_url_rule('', 'get_users', self.get_users, methods=['GET'])
        self.blueprint.add_url_rule('/<int:user_id>', 'get_user', self.get_user, methods=['GET'])
        self.blueprint.add_url_rule('/<int:user_id>', 'update_user', self.update_user, methods=['PUT'])
        self.blueprint.add_url_rule('/<int:user_id>', 'delete_user', self.delete_user, methods=['DELETE'])
    
    @jwt_required()
    def get_users(self):
        """Get all users or search users with optional query parameter."""
        try:
            # Get query parameters
            query = request.args.get('q', '').strip()
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            
            # If query is provided, search users; otherwise get all users
            if query:
                result = self.user_service.search_users(query, page, per_page)
                return self.success_response({
                    'users': self.users_schema.dump(result.items),
                    'pagination': {
                        'page': result.page,
                        'pages': result.pages,
                        'per_page': result.per_page,
                        'total': result.total,
                        'has_next': result.has_next,
                        'has_prev': result.has_prev
                    }
                })
            else:
                # Get all users (could add pagination here too if needed)
                users = self.user_service.get_all_users()
                return self.success_response(
                    self.users_schema.dump(users)
                )
            
        except Exception as e:
            self.logger.error(f"Get users error: {str(e)}")
            return self.error_response("Failed to get users", 500)
    
    @jwt_required()
    def get_user(self, user_id):
        """Get user by ID."""
        try:
            # Check permissions (user can only get their own info)
            current_user_id = get_jwt_identity()
            
            if current_user_id != user_id:
                return self.error_response("Access denied", 403)
            
            user = self.user_service.get_user_by_id(user_id)
            
            return self.success_response(
                self.user_schema.dump(user)
            )
            
        except ValueError as e:
            return self.error_response(str(e), 404)
        except Exception as e:
            self.logger.error(f"Get user error: {str(e)}")
            return self.error_response("Failed to get user", 500)
    
    @jwt_required()
    def update_user(self, user_id):
        """Update user information."""
        try:
            # Check permissions (users can only update their own info)
            current_user_id = get_jwt_identity()
            
            if current_user_id != user_id:
                return self.error_response("Access denied", 403)
            
            # Validate request data
            data = self.validate_json(UserUpdateSchema)
            
            user = self.user_service.update_user(user_id, data)
            
            return self.success_response(
                self.user_schema.dump(user),
                "User updated successfully"
            )
            
        except ValueError as e:
            return self.error_response(str(e), 400)
        except Exception as e:
            self.logger.error(f"Update user error: {str(e)}")
            return self.error_response("Failed to update user", 500)
    
    @jwt_required()
    def delete_user(self, user_id):
        """Delete user."""
        try:
            # Users can only delete their own account
            current_user_id = get_jwt_identity()
            
            if current_user_id != user_id:
                return self.error_response("Access denied", 403)
            
            self.user_service.delete_user(user_id)
            
            return self.success_response(
                message="User deleted successfully"
            )
            
        except ValueError as e:
            return self.error_response(str(e), 404)
        except Exception as e:
            self.logger.error(f"Delete user error: {str(e)}")
            return self.error_response("Failed to delete user", 500)
