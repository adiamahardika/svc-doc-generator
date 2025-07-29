#!/usr/bin/env python3
"""
Quick test script to verify the application starts without errors.
"""

import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

try:
    from application import Application
    
    print("Starting application test...")
    
    # Create application instance
    app_instance = Application()
    app = app_instance.create_app()
    
    print("Application created successfully!")
    
    # Test that we can access the configuration
    with app.app_context():
        github_api_url = app.config.get('GITHUB_API_URL')
        print(f"GitHub API URL: {github_api_url}")
        
        # Test GitHub service instantiation
        from app.services.github_service import GitHubService
        github_service = GitHubService()
        print(f"GitHub service base URL: {github_service.base_url}")
        print(f"GitHub service timeout: {github_service.timeout}")
        print(f"GitHub service per_page: {github_service.per_page}")
    
    print("\nAll tests passed! The application is ready to run.")
    print("To start the server, run: python app.py")
    
except ImportError as e:
    print(f"Import Error: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
except Exception as e:
    print(f"Error: {e}")
    print("There was an issue starting the application.")
    import traceback
    traceback.print_exc()
