import os
import logging
from logging.handlers import RotatingFileHandler


class Logger:
    """Centralized logging configuration."""
    
    @staticmethod
    def setup_logging(app):
        """Setup application logging."""
        
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Setup file handler
        file_handler = RotatingFileHandler(
            'logs/flask_app.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        # Setup console handler for development
        if app.debug:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s'
            ))
            console_handler.setLevel(logging.DEBUG)
            app.logger.addHandler(console_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Flask OOP application startup')


class FileUploadHelper:
    """Helper class for file uploads."""
    
    @staticmethod
    def allowed_file(filename, allowed_extensions):
        """Check if file extension is allowed."""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    @staticmethod
    def secure_filename(filename):
        """Generate secure filename."""
        import re
        import uuid
        
        # Remove unsafe characters
        filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
        
        # Add unique identifier to prevent conflicts
        name, ext = os.path.splitext(filename)
        unique_id = str(uuid.uuid4())[:8]
        return f"{name}_{unique_id}{ext}"
    
    @staticmethod
    def save_file(file, upload_folder, allowed_extensions=None):
        """Save uploaded file securely."""
        if allowed_extensions is None:
            allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
        
        if file and FileUploadHelper.allowed_file(file.filename, allowed_extensions):
            filename = FileUploadHelper.secure_filename(file.filename)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            return filename
        return None


class ResponseFormatter:
    """Helper class for consistent API responses."""
    
    @staticmethod
    def success(data=None, message="Success", status_code=200):
        """Format success response."""
        response = {
            'success': True,
            'message': message,
            'status_code': status_code
        }
        if data is not None:
            response['data'] = data
        return response
    
    @staticmethod
    def error(message="An error occurred", status_code=400, errors=None):
        """Format error response."""
        response = {
            'success': False,
            'message': message,
            'status_code': status_code
        }
        if errors:
            response['errors'] = errors
        return response
    
    @staticmethod
    def paginated_response(items, pagination_info, message="Success"):
        """Format paginated response."""
        return ResponseFormatter.success({
            'items': items,
            'pagination': pagination_info
        }, message)


class DatabaseHelper:
    """Helper class for database operations."""
    
    @staticmethod
    def create_tables():
        """Create all database tables."""
        from application import db
        db.create_all()
    
    @staticmethod
    def drop_tables():
        """Drop all database tables."""
        from application import db
        db.drop_all()
    
    @staticmethod
    def reset_database():
        """Reset database (drop and create)."""
        DatabaseHelper.drop_tables()
        DatabaseHelper.create_tables()


class ValidationHelper:
    """Helper class for common validations."""
    
    @staticmethod
    def validate_email(email):
        """Validate email format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password):
        """Validate password strength."""
        import re
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        
        if not re.search(r'[A-Za-z]', password):
            return False, "Password must contain at least one letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        return True, "Password is valid"
    
    @staticmethod
    def sanitize_input(input_string):
        """Sanitize user input."""
        if not input_string:
            return ""
        
        # Remove potentially dangerous characters
        import re
        sanitized = re.sub(r'[<>"\']', '', str(input_string))
        return sanitized.strip()
