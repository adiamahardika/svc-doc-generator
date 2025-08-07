from application import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates
from app.models.base_model import BaseModel
import re


class User(BaseModel, db.Model):
    """User model."""
    
    __tablename__ = 'users'
    
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    github_username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    def __init__(self, **kwargs):
        """Initialize user."""
        super().__init__()
        for key, value in kwargs.items():
            if key == 'password':
                self.set_password(value)
            elif hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password."""
        return check_password_hash(self.password_hash, password)
    
    @validates('email')
    def validate_email(self, key, email):
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError('Invalid email format')
        return email.lower()
    
    @validates('github_username')
    def validate_github_username(self, key, github_username):
        """Validate GitHub username format."""
        if not github_username or len(github_username.strip()) < 3:
            raise ValueError('GitHub username must be at least 3 characters')
        # GitHub username can only contain alphanumeric characters and hyphens
        if not re.match(r'^[a-zA-Z0-9-]+$', github_username):
            raise ValueError('GitHub username can only contain letters, numbers, and hyphens')
        return github_username.strip()
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email."""
        return cls.query.filter_by(email=email.lower()).first()
    
    @classmethod
    def find_by_github_username(cls, github_username):
        """Find user by GitHub username."""
        return cls.query.filter_by(github_username=github_username).first()
    
    @classmethod
    def find_by_id(cls, user_id):
        """Find user by ID."""
        return cls.query.get(user_id)
    
    def to_dict(self, include_sensitive=False):
        """Convert to dictionary, optionally excluding sensitive data."""
        data = super().to_dict()
        if not include_sensitive:
            data.pop('password_hash', None)
        return data
