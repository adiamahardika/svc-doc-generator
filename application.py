from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_marshmallow import Marshmallow
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
ma = Marshmallow()


class Application:
    """Main Application class following OOP paradigm."""
    
    def __init__(self, config_name=None):
        """Initialize the application."""
        self.app = None
        self.config_name = config_name or os.environ.get('FLASK_ENV', 'development')
        
    def create_app(self):
        """Application factory pattern."""
        self.app = Flask(__name__)
        
        # Configure app
        self._configure_app()
        
        # Initialize extensions
        self._initialize_extensions()
        
        # Register blueprints
        self._register_blueprints()
        
        # Register error handlers
        self._register_error_handlers()
        
        # Register CLI commands
        self._register_cli_commands()
        
        return self.app
    
    def _configure_app(self):
        """Configure the Flask application."""
        from config import config
        self.app.config.from_object(config[self.config_name])
        
        # Create upload folder if it doesn't exist
        upload_folder = self.app.config.get('UPLOAD_FOLDER', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
    
    def _initialize_extensions(self):
        """Initialize Flask extensions."""
        db.init_app(self.app)
        migrate.init_app(self.app, db)
        jwt.init_app(self.app)
        cors.init_app(self.app, origins=self.app.config['CORS_ORIGINS'])
        ma.init_app(self.app)
    
    def _register_blueprints(self):
        """Register application blueprints."""
        from app.controllers.auth_controller import AuthController
        from app.controllers.user_controller import UserController
        from app.controllers.main_controller import MainController
        from app.controllers.registration_controller import RegistrationController
        
        # Register blueprints
        self.app.register_blueprint(MainController().blueprint)
        self.app.register_blueprint(AuthController().blueprint, url_prefix='/api/auth')
        self.app.register_blueprint(UserController().blueprint, url_prefix='/api/users')
        self.app.register_blueprint(RegistrationController().blueprint)
    
    def _register_error_handlers(self):
        """Register global error handlers."""
        from app.middleware.error_handler import ErrorHandler
        error_handler = ErrorHandler()
        
        self.app.register_error_handler(400, error_handler.handle_bad_request)
        self.app.register_error_handler(401, error_handler.handle_unauthorized)
        self.app.register_error_handler(403, error_handler.handle_forbidden)
        self.app.register_error_handler(404, error_handler.handle_not_found)
        self.app.register_error_handler(500, error_handler.handle_internal_error)
    
    def _register_cli_commands(self):
        """Register CLI commands."""
        
        @self.app.cli.command()
        def init_db():
            """Initialize the database."""
            db.create_all()
            print('Database initialized.')
        
        @self.app.cli.command()
        def create_admin():
            """Create admin user."""
            from app.models.user import User
            from app.services.user_service import UserService
            
            user_service = UserService()
            admin_data = {
                'email': 'admin@example.com',
                'password': 'admin123',
                'name': 'Admin User',
                'github_username': 'admin-user'
            }
            
            try:
                user = user_service.create_user(admin_data)
                print(f'Admin user created: {user.email}')
            except Exception as e:
                print(f'Error creating admin user: {str(e)}')
