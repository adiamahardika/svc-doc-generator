import os
from datetime import timedelta


class Config:
    """Base configuration class."""
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # GitHub API settings
    GITHUB_API_URL = os.environ.get('GITHUB_API_URL') or 'https://api.github.com'
    GITHUB_API_TIMEOUT = int(os.environ.get('GITHUB_API_TIMEOUT', '30'))
    GITHUB_API_PER_PAGE = int(os.environ.get('GITHUB_API_PER_PAGE', '100'))
    
    # OpenAI API settings
    THESIS_OPENAI_API_KEY = os.environ.get('THESIS_OPENAI_API_KEY')
    OPENAI_API_URL = os.environ.get('OPENAI_API_URL') or 'https://api.openai.com/v1'
    THESIS_OPENAI_MODEL = os.environ.get('THESIS_OPENAI_MODEL') or 'gpt-3.5-turbo'
    THESIS_OPENAI_MAX_TOKENS = int(os.environ.get('THESIS_OPENAI_MAX_TOKENS', '2048'))
    THESIS_OPENAI_TEMPERATURE = float(os.environ.get('THESIS_OPENAI_TEMPERATURE', '0.7'))
    THESIS_OPENAI_TIMEOUT = int(os.environ.get('THESIS_OPENAI_TIMEOUT', '30'))
    
    # Pagination
    POSTS_PER_PAGE = 20
    
    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
