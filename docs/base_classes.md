# Base Classes Documentation

This document describes the base classes used throughout the Flask OOP application.

## Overview

The application uses three main base classes that provide common functionality and follow the DRY (Don't Repeat Yourself) principle:

1. **BaseModel** - Base class for all database models
2. **BaseService** - Base class for all business logic services
3. **BaseController** - Base class for all API controllers

## BaseModel (`app/models/base_model.py`)

The `BaseModel` class provides common database functionality for all models.

### Features:

- **Common Fields**: `id`, `created_at`, `updated_at`
- **CRUD Operations**: `save()`, `delete()`, `update()`
- **Serialization**: `to_dict()` method
- **Automatic Timestamps**: Created and updated timestamps

### Usage:

```python
from app.models.base_model import BaseModel

class MyModel(BaseModel, db.Model):
    __tablename__ = 'my_table'

    name = db.Column(db.String(50), nullable=False)

    def __init__(self, **kwargs):
        super().__init__()
        # Your initialization code
```

### Methods:

- `save()` - Save model to database
- `delete()` - Delete model from database
- `update(**kwargs)` - Update model attributes
- `to_dict()` - Convert model to dictionary

## BaseService (`app/services/base_service.py`)

The `BaseService` class provides common functionality for business logic services.

### Features:

- **Database Access**: Direct access to database session
- **Logging**: Centralized logging for all services
- **Transaction Management**: Safe database commit/rollback

### Usage:

```python
from app.services.base_service import BaseService

class MyService(BaseService):
    def __init__(self):
        super().__init__()
        self.model = MyModel

    def create_item(self, data):
        # Your business logic here
        pass
```

### Properties:

- `self.db` - Database session
- `self.logger` - Logger instance for the service

### Methods:

- `commit_changes()` - Safely commit database changes with error handling

## BaseController (`app/controllers/base_controller.py`)

The `BaseController` class provides common functionality for all API controllers.

### Features:

- **Blueprint Management**: Automatic blueprint creation
- **Response Formatting**: Consistent API responses
- **Input Validation**: Request validation using Marshmallow
- **Logging**: Centralized logging for all controllers

### Usage:

```python
from app.controllers.base_controller import BaseController

class MyController(BaseController):
    def __init__(self):
        super().__init__('my_controller', url_prefix='/api/my')
        self.service = MyService()

    def _register_routes(self):
        self.blueprint.add_url_rule('/', 'list', self.list_items, methods=['GET'])
```

### Properties:

- `self.blueprint` - Flask Blueprint instance
- `self.logger` - Logger instance for the controller

### Methods:

- `success_response(data, message, status_code)` - Create success response
- `error_response(message, status_code, errors)` - Create error response
- `validate_json(schema_class)` - Validate request JSON

## Inheritance Hierarchy

```
BaseModel
├── User
└── (Future models)

BaseService
├── UserService
└── (Future services)

BaseController
├── AuthController
├── UserController
├── MainController
└── (Future controllers)
```

## Benefits of This Architecture

### 1. **Code Reusability**

- Common functionality is written once and reused
- Reduces code duplication across the application

### 2. **Consistency**

- All models, services, and controllers follow the same patterns
- Consistent API responses and error handling

### 3. **Maintainability**

- Changes to base functionality automatically apply to all subclasses
- Easy to add new features to all components

### 4. **Testing**

- Base classes can be tested independently
- Common functionality is tested once

### 5. **Extensibility**

- Easy to add new models, services, and controllers
- Built-in logging and error handling

## Best Practices

### When Creating New Models:

1. Always inherit from `BaseModel`
2. Call `super().__init__()` in your constructor
3. Use the inherited CRUD methods when possible

### When Creating New Services:

1. Always inherit from `BaseService`
2. Initialize the parent class: `super().__init__()`
3. Use `self.logger` for logging
4. Use `self.commit_changes()` for database operations

### When Creating New Controllers:

1. Always inherit from `BaseController`
2. Provide blueprint name and optional URL prefix
3. Implement `_register_routes()` method
4. Use `success_response()` and `error_response()` for consistent responses
5. Use `validate_json()` for input validation

## Example Implementation

### Model Example:

```python
# app/models/product.py
from app.models.base_model import BaseModel
from application import db

class Product(BaseModel, db.Model):
    __tablename__ = 'products'

    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
```

### Service Example:

```python
# app/services/product_service.py
from app.services.base_service import BaseService
from app.models.product import Product

class ProductService(BaseService):
    def __init__(self):
        super().__init__()
        self.model = Product

    def create_product(self, data):
        try:
            product = self.model(**data)
            product.save()
            self.logger.info(f"Product created: {product.name}")
            return product
        except Exception as e:
            self.logger.error(f"Error creating product: {str(e)}")
            raise
```

### Controller Example:

```python
# app/controllers/product_controller.py
from app.controllers.base_controller import BaseController
from app.services.product_service import ProductService

class ProductController(BaseController):
    def __init__(self):
        super().__init__('products', url_prefix='/api/products')
        self.service = ProductService()

    def _register_routes(self):
        self.blueprint.add_url_rule('', 'create', self.create, methods=['POST'])

    def create(self):
        try:
            data = self.validate_json(ProductSchema)
            product = self.service.create_product(data)
            return self.success_response(product.to_dict(), "Product created", 201)
        except Exception as e:
            return self.error_response(str(e), 400)
```

This architecture provides a solid foundation for building scalable and maintainable Flask applications using OOP principles.
