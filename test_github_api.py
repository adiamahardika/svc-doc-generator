"""
Test script for GitHub API integration.
Run this script to test the GitHub service functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application import Application
from app.services.github_service import GitHubService


def test_github_service():
    """Test the GitHub service."""
    print("Testing GitHub Service...")
    
    # Create Flask application context
    app_instance = Application()
    app = app_instance.create_app()
    
    with app.app_context():
        service = GitHubService()
        
        # Test with a well-known GitHub user
        test_username = "octocat"
        print(f"\nTesting with GitHub user: {test_username}")
        
        result = service.get_user_repositories(test_username)
        
        if result['success']:
            print(f"Success! Found {result['total_count']} repositories")
            
            # Display first few repositories
            repos = result['data'][:3]  # First 3 repos
            for repo in repos:
                print(f"  - {repo['name']} ({repo['language']}) - {repo['description'][:50] if repo['description'] else 'No description'}...")
        else:
            print(f"Error: {result['message']}")
            print(f"Error Code: {result.get('error_code', 'N/A')}")
        
        # Test repository details
        print(f"\nTesting repository details for {test_username}/Hello-World...")
        detail_result = service.get_repository_details(test_username, "Hello-World")
        
        if detail_result['success']:
            repo_data = detail_result['data']
            print(f"Repository details retrieved successfully")
            print(f"- Name: {repo_data['name']}")
            print(f"- Description: {repo_data['description']}")
            print(f"- Stars: {repo_data['stargazers_count']}")
            print(f"- Language: {repo_data['language']}")
        else:
            print(f"Error: {detail_result['message']}")


if __name__ == "__main__":
    test_github_service()
