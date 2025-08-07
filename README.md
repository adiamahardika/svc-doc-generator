# Doc Generator Backend

A well-structured Flask application for document generation following Object-Oriented Programming (OOP) principles, with GitHub integration and OpenAI-powered documentation generation.

## Project Structure

```
backend/
├── app/                          # Main application package
│   ├── controllers/              # Controllers (MVC pattern)
│   │   ├── __init__.py
│   │   ├── base_controller.py    # Base controller class
│   │   ├── auth_controller.py    # Authentication endpoints
│   │   ├── github_controller.py  # GitHub API integration
│   │   ├── main_controller.py    # Main application endpoints
│   │   ├── openai_controller.py  # OpenAI documentation generation
│   │   ├── registration_controller.py # User registration
│   │   └── user_controller.py    # User management endpoints
│   ├── middleware/               # Middleware classes
│   │   ├── __init__.py
│   │   └── error_handler.py      # Error handling and logging
│   ├── models/                   # Database models
│   │   ├── __init__.py
│   │   ├── base_model.py         # Base model class
│   │   └── user.py              # User model
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   ├── base_service.py       # Base service class
│   │   ├── github_service.py     # GitHub API service
│   │   ├── openai_service.py     # OpenAI API service
│   │   └── user_service.py      # User service with business logic
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       └── helpers.py           # Helper functions and classes
├── uploads/                     # File uploads (created automatically)
├── app.py                       # Application entry point
├── application.py               # Main Application class
├── config.py                    # Configuration classes
├── init_db.py                   # Database initialization script
├── run.py                       # Development server runner
└── requirements.txt             # Python dependencies
```

## Features

### 🏗️ **Object-Oriented Architecture**

- **Application Class**: Main application factory following OOP principles
- **Base Classes**: Reusable base classes for controllers, services, and models
- **Service Layer**: Separated business logic from controllers
- **Model Classes**: SQLAlchemy models with OOP methods

### 🔐 **Authentication & Authorization**

- JWT-based authentication
- User registration with GitHub username validation
- Secure password hashing with Werkzeug
- Token refresh mechanism

### � **GitHub Integration**

- GitHub API integration for repository access
- Repository browsing and file management
- Branch selection and navigation
- GitHub username validation

### 🤖 **AI-Powered Documentation**

- OpenAI integration for automatic documentation generation
- Support for multiple programming languages
- Base64 file content processing
- Batch documentation generation

### �📊 **Database Management**

- SQLAlchemy ORM with base model class
- Database migrations with Flask-Migrate
- Model validation and relationships
- User management system

### 🌐 **RESTful API Design**

- Consistent response formatting
- Proper HTTP status codes
- Input validation with Marshmallow
- CORS support for frontend integration

### 🛡️ **Security Features**

- Input sanitization and validation
- GitHub API token security
- Secure file handling
- Error handling and logging

### 📝 **Development Tools**

- Interactive development server runner
- Database initialization utilities
- Comprehensive logging system
- Development environment management

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Environment

Create a `.env` file and update the values:

```bash
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///app.db
CORS_ORIGINS=http://localhost:3000
GITHUB_API_URL=https://api.github.com
GITHUB_API_TIMEOUT=30
THESIS_OPENAI_API_KEY=your-openai-api-key-here
THESIS_OPENAI_MODEL=gpt-3.5-turbo
THESIS_OPENAI_TEMPERATURE=0.3
```

### 3. Initialize Database

Using the interactive runner:

```bash
python run.py
# Choose option 2 to initialize database
```

Or using Flask CLI:

```bash
python -c "from init_db import init_database; init_database()"
```

### 4. Run the Application

Using the interactive runner (recommended):

```bash
python run.py
# Choose option 1 to start development server
```

Or directly:

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication (`/api/auth`)

- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token

### Registration (`/api/register`)

- `POST /api/register` - User registration
- `POST /api/register/validate-github` - Validate GitHub username

### Users (`/api/users`)

- `GET /api/users/<id>` - Get user by ID (requires auth)
- `PUT /api/users/<id>` - Update user (requires auth)
- `PUT /api/users/<id>/change-password` - Change user password (requires auth)

### GitHub Integration (`/api/github`)

- `GET /api/github/repositories` - Get user repositories (requires auth)
- `GET /api/github/repository/<repo_name>` - Get repository details (requires auth)
- `GET /api/github/repository/<repo_name>/branches` - Get repository branches (requires auth)

### OpenAI Documentation (`/api/openai`)

- `POST /api/openai/generate-documentation` - Generate documentation from files (requires auth)
- `GET /api/openai/health` - OpenAI service health check

### Main

- `GET /` - API information
- `GET /health` - Health check
- `GET /api/status` - API status

## Object-Oriented Design Patterns Used

### 1. **Factory Pattern**

```python
# Application factory in application.py
class Application:
    def create_app(self):
        # Creates and configures Flask app
```

### 2. **Service Layer Pattern**

```python
# Business logic separated from controllers
class UserService(BaseService):
    def create_user(self, user_data):
        # Business logic for user creation

class GitHubService(BaseService):
    def get_user_repositories(self, username):
        # GitHub API integration logic

class OpenAIService(BaseService):
    def generate_documentation_from_base64(self, file_name, content):
        # OpenAI documentation generation logic
```

### 3. **Repository Pattern**

```python
# Model methods for data access
class User(BaseModel):
    @classmethod
    def find_by_email(cls, email):
        # Data access method
```

### 4. **Strategy Pattern**

```python
# Different configurations for different environments
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
```

## Class Hierarchy

```
BaseModel (models/base_model.py)
├── User
└── (Future models inherit from BaseModel)

BaseService (services/base_service.py)
├── UserService
├── GitHubService
├── OpenAIService
└── (Future services inherit from BaseService)

BaseController (controllers/base_controller.py)
├── AuthController
├── UserController
├── MainController
├── RegistrationController
├── GitHubController
└── OpenAIController
```

## Environment Configuration

The application supports multiple environments through configuration classes:

- **Development**: Debug enabled, verbose logging
- **Production**: Optimized for performance and security
- **Testing**: In-memory database, simplified settings

## Security Best Practices

1. **Password Security**: Werkzeug password hashing with salt
2. **Input Validation**: Marshmallow schemas for all endpoints
3. **SQL Injection Prevention**: SQLAlchemy ORM usage
4. **API Security**: JWT token-based authentication
5. **GitHub Integration**: Secure token handling for API calls
6. **File Processing**: Secure base64 content handling

## Development Tools

The application includes a comprehensive development runner (`run.py`) with the following features:

- Interactive menu for common tasks
- Database initialization and management
- Dependency checking
- Development server with auto-reload
- Project information display

Run `python run.py` to access the development menu.

## Testing

The OOP structure makes testing easier:

```python
# Example test structure
class TestUserService(unittest.TestCase):
    def setUp(self):
        self.user_service = UserService()

    def test_create_user(self):
        # Test user creation logic

class TestGitHubService(unittest.TestCase):
    def setUp(self):
        self.github_service = GitHubService()

    def test_get_repositories(self):
        # Test GitHub API integration
```

## Key Features in Detail

### GitHub Integration

The application provides comprehensive GitHub integration:

- **Repository Management**: Browse and access user repositories
- **Branch Navigation**: Switch between different branches
- **File Access**: Read repository contents and file structures
- **Username Validation**: Real-time GitHub username verification

### AI Documentation Generation

- **Multi-file Support**: Process up to 5 files simultaneously
- **Language Detection**: Automatic programming language detection
- **Structured Output**: Consistent documentation format
- **Error Handling**: Robust error handling for API failures

### User Management

- **Registration Flow**: Complete user registration with GitHub integration
- **Profile Management**: Update user information and preferences
- **Password Security**: Secure password management and updates

## Extending the Application

### Adding New Models

1. Create model class inheriting from `BaseModel`
2. Add database migrations
3. Create corresponding service class

### Adding New Controllers

1. Create controller class inheriting from `BaseController`
2. Register routes in `_register_routes` method
3. Add to application blueprint registration in `application.py`

### Adding New Services

1. Create service class inheriting from `BaseService`
2. Implement business logic methods
3. Add corresponding Marshmallow schemas for validation

### Adding New API Integrations

1. Create service class for external API
2. Add configuration variables
3. Implement error handling and validation
4. Create corresponding controller endpoints

## Deployment

### Development

Using the interactive runner:

```bash
python run.py
```

Or directly:

```bash
python app.py
```

### Production

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Configuration

The application supports multiple configuration environments:

- **Development**: Debug enabled, verbose logging
- **Production**: Optimized for performance and security
- **Testing**: In-memory database, simplified settings

Configuration is managed through the `config.py` file with environment-specific classes.

## Contributing

1. Follow OOP principles and existing patterns
2. Add proper docstrings to all methods
3. Include input validation using Marshmallow schemas
4. Add appropriate logging for debugging
5. Handle errors gracefully with meaningful messages
6. Update documentation when adding new features

## License

MIT License
