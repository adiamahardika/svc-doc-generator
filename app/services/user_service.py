from app.models.user import User
from application import db
from app.services.base_service import BaseService
from marshmallow import Schema, fields, validate, post_load
from datetime import datetime


class UserService(BaseService):
    """User service class for business logic."""
    
    def __init__(self):
        super().__init__()
        self.model = User
    
    def create_user(self, user_data):
        """Create a new user."""
        try:
            # Check if user already exists
            existing_user = self.model.find_by_email(user_data['email'])
            if existing_user:
                raise ValueError('User with this email already exists')
            
            # Create new user
            user = self.model(**user_data)
            user.save()
            
            self.logger.info(f"User created: {user.email}")
            return user
            
        except Exception as e:
            self.logger.error(f"Error creating user: {str(e)}")
            raise
    
    def get_user_by_id(self, user_id):
        """Get user by ID."""
        user = self.model.find_by_id(user_id)
        if not user:
            raise ValueError('User not found')
        return user
    
    def get_user_by_email(self, email):
        """Get user by email."""
        user = self.model.find_by_email(email)
        if not user:
            raise ValueError('User not found')
        return user
    
    def authenticate_user(self, email, password):
        """Authenticate user login."""
        try:
            user = self.get_user_by_email(email)
            
            if not user.is_active:
                raise ValueError('User account is inactive')
            
            if not user.check_password(password):
                raise ValueError('Invalid credentials')
            
            user.set_last_login()
            self.logger.info(f"User authenticated: {user.email}")
            return user
            
        except Exception as e:
            self.logger.error(f"Authentication failed for {email}: {str(e)}")
            raise
    
    def update_user(self, user_id, update_data):
        """Update user information."""
        try:
            user = self.get_user_by_id(user_id)
            
            # Handle password update separately
            if 'password' in update_data:
                user.set_password(update_data.pop('password'))
            
            # Update other fields
            user.update(**update_data)
            
            self.logger.info(f"User updated: {user.email}")
            return user
            
        except Exception as e:
            self.logger.error(f"Error updating user {user_id}: {str(e)}")
            raise
    
    def delete_user(self, user_id):
        """Soft delete user (deactivate)."""
        try:
            user = self.get_user_by_id(user_id)
            user.update(is_active=False)
            
            self.logger.info(f"User deactivated: {user.email}")
            return user
            
        except Exception as e:
            self.logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise
    
    def get_all_users(self, include_inactive=False):
        """Get all users."""
        if include_inactive:
            return self.model.query.all()
        return self.model.get_all_active()
    
    def search_users(self, query, page=1, per_page=20):
        """Search users by name or email."""
        search_term = f"%{query}%"
        users = self.model.query.filter(
            db.or_(
                self.model.email.like(search_term),
                self.model.first_name.like(search_term),
                self.model.last_name.like(search_term)
            )
        ).filter_by(is_active=True).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return users
    
    def promote_to_admin(self, user_id):
        """Promote user to admin role."""
        try:
            user = self.get_user_by_id(user_id)
            user.update(role='admin')
            
            self.logger.info(f"User promoted to admin: {user.email}")
            return user
            
        except Exception as e:
            self.logger.error(f"Error promoting user {user_id}: {str(e)}")
            raise


# Marshmallow Schemas for validation and serialization
class UserSchema(Schema):
    """User schema for validation and serialization."""
    
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(required=True, validate=validate.Length(min=6), load_only=True)
    first_name = fields.Str(required=True, validate=validate.Length(max=50))
    last_name = fields.Str(required=True, validate=validate.Length(max=50))
    role = fields.Str(validate=validate.OneOf(['user', 'admin', 'moderator']), missing='user')
    is_active = fields.Bool(missing=True)
    full_name = fields.Str(dump_only=True)
    is_admin = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    last_login = fields.DateTime(dump_only=True)
    
    @post_load
    def make_user(self, data, **kwargs):
        """Create user instance from validated data."""
        return data


class UserLoginSchema(Schema):
    """Schema for user login."""
    
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class UserUpdateSchema(Schema):
    """Schema for user updates."""
    
    email = fields.Email(validate=validate.Length(max=120))
    password = fields.Str(validate=validate.Length(min=6))
    first_name = fields.Str(validate=validate.Length(max=50))
    last_name = fields.Str(validate=validate.Length(max=50))
    role = fields.Str(validate=validate.OneOf(['user', 'admin', 'moderator']))
    is_active = fields.Bool()
