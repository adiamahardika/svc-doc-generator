# Flask OOP Backend

A well-structured Flask application following Object-Oriented Programming (OOP) principles.

## Project Structure

```
backend/
├── app/                          # Main application package
│   ├── controllers/              # Controllers (MVC pattern)
│   │   ├── __init__.py
│   │   ├── base_controller.py    # Base controller class
│   │   ├── auth_controller.py    # Authentication endpoints
│   │   ├── main_controller.py    # Main application endpoints
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
│   │   └── user_service.py      # User service with business logic
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       └── helpers.py           # Helper functions and classes
├── docs/                        # Documentation
│   └── base_classes.md          # Base classes documentation
├── logs/                        # Log files (created automatically)
├── uploads/                     # File uploads (created automatically)
├── .env                         # Environment variables
├── app.py                       # Application entry point
├── application.py               # Main Application class
├── config.py                    # Configuration classes
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
- Role-based access control (User, Admin)
- Secure password hashing with bcrypt
- Token refresh mechanism

### 📊 **Database Management**

- SQLAlchemy ORM with base model class
- Database migrations with Flask-Migrate
- Model validation and relationships
- Query optimization methods

### 🌐 **RESTful API Design**

- Consistent response formatting
- Proper HTTP status codes
- Input validation with Marshmallow
- CORS support for frontend integration

### 🛡️ **Security Features**

- Input sanitization
- SQL injection prevention
- XSS protection headers
- File upload security

### 📝 **Logging & Error Handling**

- Centralized logging system
- Rotating log files
- Global error handlers
- Request/response logging

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Environment

Copy `.env` file and update the values:

```bash
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///app.db
CORS_ORIGINS=http://localhost:3000
```

### 3. Initialize Database

```bash
flask init-db
```

### 4. Create Admin User

```bash
flask create-admin
```

### 5. Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication (`/api/auth`)

- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user info

### Users (`/api/users`)

- `GET /api/users` - Get all users (Admin only)
- `POST /api/users` - Create new user
- `GET /api/users/<id>` - Get user by ID
- `PUT /api/users/<id>` - Update user
- `DELETE /api/users/<id>` - Delete user (Admin only)
- `GET /api/users/search?q=<query>` - Search users (Admin only)
- `PUT /api/users/<id>/promote` - Promote user to admin (Admin only)

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
└── (Future services inherit from BaseService)

BaseController (controllers/base_controller.py)
├── AuthController
├── UserController
└── MainController
```

## Environment Configuration

The application supports multiple environments through configuration classes:

- **Development**: Debug enabled, verbose logging
- **Production**: Optimized for performance and security
- **Testing**: In-memory database, simplified settings

## Security Best Practices

1. **Password Security**: Bcrypt hashing with salt
2. **Input Validation**: Marshmallow schemas
3. **SQL Injection Prevention**: SQLAlchemy ORM
4. **XSS Protection**: Security headers
5. **CORS Configuration**: Controlled origins
6. **File Upload Security**: Extension validation and secure filenames

## Testing

The OOP structure makes testing easier:

```python
# Example test structure
class TestUserService(unittest.TestCase):
    def setUp(self):
        self.user_service = UserService()

    def test_create_user(self):
        # Test user creation logic
```

## Extending the Application

### Adding New Models

1. Create model class inheriting from `BaseModel`
2. Add to migrations
3. Create corresponding service class

### Adding New Controllers

1. Create controller class inheriting from `BaseController`
2. Register routes in `_register_routes` method
3. Add to application blueprint registration

### Adding New Services

1. Create service class inheriting from `BaseService`
2. Implement business logic methods
3. Add corresponding schemas for validation

## Deployment

### Development

```bash
python app.py
```

### Production

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Contributing

1. Follow OOP principles
2. Add proper docstrings
3. Include input validation
4. Add appropriate logging
5. Write unit tests

## License

MIT License
