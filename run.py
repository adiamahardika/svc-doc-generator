"""
Flask OOP Development Server Runner

This script provides an easy way to run the Flask application in development mode
with various options for database management and testing.
"""

import os
import sys
import subprocess
from pathlib import Path


def print_banner():
    """Print application banner."""
    print("=" * 60)
    print("🚀 Flask OOP Backend Development Server")
    print("=" * 60)


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import flask
        import flask_sqlalchemy
        import flask_jwt_extended
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False


def init_database():
    """Initialize database if needed."""
    from init_db import init_database
    print("🗄️  Initializing database...")
    init_database()


def run_tests():
    """Run application tests."""
    from test_app import run_tests
    print("🧪 Running tests...")
    return run_tests()


def start_development_server():
    """Start the development server."""
    print("🌐 Starting development server...")
    print("📍 Server will be available at: http://localhost:5000")
    print("📋 API endpoints:")
    print("   • GET  /              - API information")
    print("   • GET  /health        - Health check")
    print("   • GET  /api/status    - API status")
    print("   • POST /api/auth/login - User login")
    print("   • GET  /api/auth/me   - Current user (requires auth)")
    print("   • POST /api/users     - Create user")
    print("   • GET  /api/users     - Get users (admin only)")
    print("\n🔑 Default admin credentials:")
    print("   Email: admin@example.com")
    print("   Password: admin123")
    print("\n" + "=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Import and run the application
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)


def show_project_info():
    """Show project information."""
    print("\n📁 Project Structure:")
    print("""
    backend/
    ├── app/                     # Main application package
    │   ├── controllers/         # API controllers (MVC)
    │   ├── middleware/          # Error handling & logging
    │   ├── models/             # Database models
    │   ├── services/           # Business logic layer
    │   └── utils/              # Helper functions
    ├── .env                    # Environment variables
    ├── app.py                  # Application entry point
    ├── application.py          # Main Application class
    ├── config.py               # Configuration classes
    ├── init_db.py             # Database initialization
    ├── test_app.py            # Unit tests
    └── requirements.txt        # Dependencies
    """)
    
    print("\n🏗️  Architecture Highlights:")
    print("   • Object-Oriented design with inheritance")
    print("   • Service layer for business logic")
    print("   • Base classes for reusability")
    print("   • JWT authentication with role-based access")
    print("   • Input validation with Marshmallow")
    print("   • Centralized error handling")
    print("   • Security best practices")


def main():
    """Main function."""
    print_banner()
    
    # Check if we're in the right directory
    if not os.path.exists('requirements.txt'):
        print("❌ Please run this script from the backend directory")
        return
    
    while True:
        print("\n🎯 Choose an option:")
        print("1. 🚀 Start development server")
        print("2. 🗄️  Initialize database")
        print("3. 🧪 Run tests")
        print("4. 📦 Install dependencies")
        print("5. 📋 Show project info")
        print("6. 🚪 Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            if not check_dependencies():
                continue
            
            # Check if database needs initialization
            if not os.path.exists('app.db'):
                print("\n📝 Database not found. Initializing...")
                init_database()
            
            start_development_server()
            
        elif choice == '2':
            if not check_dependencies():
                continue
            init_database()
            
        elif choice == '3':
            if not check_dependencies():
                continue
            run_tests()
            
        elif choice == '4':
            print("📦 Installing dependencies...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                             check=True)
                print("✓ Dependencies installed successfully!")
            except subprocess.CalledProcessError:
                print("❌ Failed to install dependencies")
                
        elif choice == '5':
            show_project_info()
            
        elif choice == '6':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print("Please check your configuration and try again.")
