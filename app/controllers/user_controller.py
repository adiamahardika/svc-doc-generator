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
        self.blueprint.add_url_rule('', 'create_user', self.create_user, methods=['POST'])
        self.blueprint.add_url_rule('', 'get_users', self.get_users, methods=['GET'])
        self.blueprint.add_url_rule('/<int:user_id>', 'get_user', self.get_user, methods=['GET'])
        self.blueprint.add_url_rule('/<int:user_id>', 'update_user', self.update_user, methods=['PUT'])
        self.blueprint.add_url_rule('/<int:user_id>', 'delete_user', self.delete_user, methods=['DELETE'])
        self.blueprint.add_url_rule('/search', 'search_users', self.search_users, methods=['GET'])
        self.blueprint.add_url_rule('/<int:user_id>/promote', 'promote_user', self.promote_user, methods=['PUT'])
    
    def create_user(self):
        """Create a new user."""
        try:
            # Validate request data
            data = self.validate_json(UserSchema)
            
            # Create user
            user = self.user_service.create_user(data)
            
            return self.success_response(
                self.user_schema.dump(user),
                "User created successfully",
                201
            )
            
        except ValueError as e:
            return self.error_response(str(e), 400)
        except Exception as e:
            self.logger.error(f"Create user error: {str(e)}")
            return self.error_response("Failed to create user", 500)
    
    @jwt_required()
    def get_users(self):
        """Get all users (admin only)."""
        try:
            # Check if current user is admin
            current_user_id = get_jwt_identity()
            current_user = self.user_service.get_user_by_id(current_user_id)
            
            if not current_user.is_admin:
                return self.error_response("Admin access required", 403)
            
            # Get query parameters
            include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
            
            users = self.user_service.get_all_users(include_inactive)
            
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
            # Check permissions (user can get their own info, admin can get any)
            current_user_id = get_jwt_identity()
            current_user = self.user_service.get_user_by_id(current_user_id)
            
            if current_user_id != user_id and not current_user.is_admin:
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
            # Check permissions
            current_user_id = get_jwt_identity()
            current_user = self.user_service.get_user_by_id(current_user_id)
            
            if current_user_id != user_id and not current_user.is_admin:
                return self.error_response("Access denied", 403)
            
            # Validate request data
            data = self.validate_json(UserUpdateSchema)
            
            # Regular users can't change their role
            if current_user_id == user_id and not current_user.is_admin:
                data.pop('role', None)
                data.pop('is_active', None)
            
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
        """Delete (deactivate) user."""
        try:
            # Check if current user is admin
            current_user_id = get_jwt_identity()
            current_user = self.user_service.get_user_by_id(current_user_id)
            
            if not current_user.is_admin:
                return self.error_response("Admin access required", 403)
            
            # Prevent admin from deleting themselves
            if current_user_id == user_id:
                return self.error_response("Cannot delete your own account", 400)
            
            user = self.user_service.delete_user(user_id)
            
            return self.success_response(
                message="User deleted successfully"
            )
            
        except ValueError as e:
            return self.error_response(str(e), 404)
        except Exception as e:
            self.logger.error(f"Delete user error: {str(e)}")
            return self.error_response("Failed to delete user", 500)
    
    @jwt_required()
    def search_users(self):
        """Search users."""
        try:
            # Check if current user is admin
            current_user_id = get_jwt_identity()
            current_user = self.user_service.get_user_by_id(current_user_id)
            
            if not current_user.is_admin:
                return self.error_response("Admin access required", 403)
            
            # Get query parameters
            query = request.args.get('q', '')
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            
            if not query:
                return self.error_response("Search query is required", 400)
            
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
            
        except Exception as e:
            self.logger.error(f"Search users error: {str(e)}")
            return self.error_response("Failed to search users", 500)
    
    @jwt_required()
    def promote_user(self, user_id):
        """Promote user to admin."""
        try:
            # Check if current user is admin
            current_user_id = get_jwt_identity()
            current_user = self.user_service.get_user_by_id(current_user_id)
            
            if not current_user.is_admin:
                return self.error_response("Admin access required", 403)
            
            user = self.user_service.promote_to_admin(user_id)
            
            return self.success_response(
                self.user_schema.dump(user),
                "User promoted to admin successfully"
            )
            
        except ValueError as e:
            return self.error_response(str(e), 404)
        except Exception as e:
            self.logger.error(f"Promote user error: {str(e)}")
            return self.error_response("Failed to promote user", 500)
