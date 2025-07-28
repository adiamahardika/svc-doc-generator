from application import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates
from app.models.base_model import BaseModel
import re


class User(BaseModel, db.Model):
    """User model."""
    
    __tablename__ = 'users'
    
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime)
    
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
    
    @property
    def full_name(self):
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_admin(self):
        """Check if user is admin."""
        return self.role == 'admin'
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password."""
        return check_password_hash(self.password_hash, password)
    
    def set_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    @validates('email')
    def validate_email(self, key, email):
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError('Invalid email format')
        return email.lower()
    
    @validates('role')
    def validate_role(self, key, role):
        """Validate user role."""
        allowed_roles = ['user', 'admin', 'moderator']
        if role not in allowed_roles:
            raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return role
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email."""
        return cls.query.filter_by(email=email.lower()).first()
    
    @classmethod
    def find_by_id(cls, user_id):
        """Find user by ID."""
        return cls.query.get(user_id)
    
    @classmethod
    def get_all_active(cls):
        """Get all active users."""
        return cls.query.filter_by(is_active=True).all()
    
    def to_dict(self, include_sensitive=False):
        """Convert to dictionary, optionally excluding sensitive data."""
        data = super().to_dict()
        if not include_sensitive:
            data.pop('password_hash', None)
        data['full_name'] = self.full_name
        data['is_admin'] = self.is_admin
        return data
