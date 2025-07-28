from app.models.user import User
from application import db
from app.services.base_service import BaseService
from marshmallow import Schema, fields, validate


class UserService(BaseService):
    """User service class for business logic."""
    
    def __init__(self):
        super().__init__()
        self.model = User
    
    def create_user(self, user_data):
        """Create a new user."""
        try:
            # Check if user already exists by email
            existing_user = self.model.find_by_email(user_data['email'])
            if existing_user:
                raise ValueError('User with this email already exists')
            
            # Check if GitHub username already exists
            existing_github_user = self.model.find_by_github_username(user_data.get('github_username', ''))
            if existing_github_user:
                raise ValueError('User with this GitHub username already exists')
            
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
            
            if not user.check_password(password):
                raise ValueError('Invalid credentials')
            
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
        """Delete user."""
        try:
            user = self.get_user_by_id(user_id)
            user.delete()
            
            self.logger.info(f"User deleted: {user.email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise
    
    def get_all_users(self):
        """Get all users."""
        return self.model.get_all_users()
    
    def search_users(self, query, page=1, per_page=20):
        """Search users by name, email, or GitHub username."""
        search_term = f"%{query}%"
        users = self.model.query.filter(
            db.or_(
                self.model.email.like(search_term),
                self.model.name.like(search_term),
                self.model.github_username.like(search_term)
            )
        ).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return users


# Marshmallow Schemas for validation and serialization
class UserSchema(Schema):
    """User schema for validation and serialization."""
    
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True, validate=validate.Length(max=120))
    github_username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    password = fields.Str(required=True, validate=validate.Length(min=8), load_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class UserLoginSchema(Schema):
    """Schema for user login."""
    
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class UserUpdateSchema(Schema):
    """Schema for user updates."""
    
    name = fields.Str(validate=validate.Length(min=1, max=100))
    email = fields.Email(validate=validate.Length(max=120))
    github_username = fields.Str(validate=validate.Length(min=3, max=50))
    password = fields.Str(validate=validate.Length(min=8))
