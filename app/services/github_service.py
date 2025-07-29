import requests
from app.services.base_service import BaseService
from typing import List, Dict, Optional
from flask import current_app


class GitHubService(BaseService):
    """Service for interacting with GitHub API."""
    
    def __init__(self):
        super().__init__()
        # Don't access current_app in __init__, defer to when methods are called
        self._base_url = None
        self._timeout = None
        self._per_page = None
    
    @property
    def base_url(self):
        """Get the GitHub API base URL from Flask config."""
        if self._base_url is None:
            self._base_url = current_app.config.get('GITHUB_API_URL', 'https://api.github.com')
        return self._base_url
    
    @property
    def timeout(self):
        """Get the request timeout from Flask config."""
        if self._timeout is None:
            self._timeout = current_app.config.get('GITHUB_API_TIMEOUT', 30)
        return self._timeout
    
    @property
    def per_page(self):
        """Get the per-page limit from Flask config."""
        if self._per_page is None:
            self._per_page = current_app.config.get('GITHUB_API_PER_PAGE', 100)
        return self._per_page
    
    def get_user_repositories(self, github_username: str, repo_name: Optional[str] = None, access_token: Optional[str] = None) -> Dict:
        """
        Get repositories for a GitHub user using GitHub Search API.
        
        Args:
            github_username: The GitHub username
            repo_name: Optional repository name to search for
            access_token: Optional GitHub access token for authenticated requests
            
        Returns:
            Dict containing success status and repositories data or error message
        """
        try:
            url = f"{self.base_url}/search/repositories"
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'doc-generator-app'
            }
            
            # Add authorization header if access_token is provided
            if access_token:
                headers['Authorization'] = f'Bearer {access_token}'
            
            # Add query parameters for search API
            if repo_name:
                search_query = f'{repo_name} user:{github_username} in:name'
                log_message = f"Fetching repositories for user: {github_username} with repo name: {repo_name}"
            else:
                search_query = f'user:{github_username}'
                log_message = f"Fetching repositories for user: {github_username}"

            params = {
                'q': search_query,  # Search query for user repositories with optional repo name
                'sort': 'updated',  # created, updated, pushed, full_name
                'order': 'desc',  # asc, desc
                'per_page': self.per_page  # Max repositories per page
            }
            print(params)  # Debugging line
            self.logger.info(log_message)
            
            response = requests.get(
                url, 
                headers=headers, 
                params=params,
                timeout=self.timeout
            )
            print(response.url)
            if response.status_code == 200:
                search_result = response.json()
                repositories = search_result.get('items', [])
                total_count = search_result.get('total_count', 0)
                
                # Transform the response to include only essential fields
                transformed_repos = []
                for repo in repositories:
                    transformed_repo = {
                        'id': repo.get('id'),
                        'name': repo.get('name'),
                        'full_name': repo.get('full_name'),
                        'description': repo.get('description'),
                        'private': repo.get('private'),
                        'html_url': repo.get('html_url'),
                        'clone_url': repo.get('clone_url'),
                        'ssh_url': repo.get('ssh_url'),
                        'git_url': repo.get('git_url'),
                        'language': repo.get('language'),
                        'size': repo.get('size'),
                        'stargazers_count': repo.get('stargazers_count'),
                        'watchers_count': repo.get('watchers_count'),
                        'forks_count': repo.get('forks_count'),
                        'open_issues_count': repo.get('open_issues_count'),
                        'default_branch': repo.get('default_branch'),
                        'topics': repo.get('topics', []),
                        'visibility': repo.get('visibility'),
                        'archived': repo.get('archived'),
                        'disabled': repo.get('disabled'),
                        'fork': repo.get('fork'),
                        'created_at': repo.get('created_at'),
                        'updated_at': repo.get('updated_at'),
                        'pushed_at': repo.get('pushed_at'),
                        'score': repo.get('score'),  # Search relevance score
                        'owner': {
                            'login': repo.get('owner', {}).get('login'),
                            'id': repo.get('owner', {}).get('id'),
                            'avatar_url': repo.get('owner', {}).get('avatar_url'),
                            'html_url': repo.get('owner', {}).get('html_url'),
                            'type': repo.get('owner', {}).get('type')
                        } if repo.get('owner') else None
                    }
                    transformed_repos.append(transformed_repo)
                
                return {
                    'success': True,
                    'data': transformed_repos,
                    'total_count': total_count,
                    'returned_count': len(transformed_repos),
                    'message': f'Successfully fetched {len(transformed_repos)} repositories out of {total_count} total'
                }
                
            elif response.status_code == 422:
                # Validation failed - likely invalid search query
                return {
                    'success': False,
                    'message': f'Invalid search query for user "{github_username}"',
                    'error_code': 'INVALID_SEARCH_QUERY'
                }
                
            elif response.status_code == 403:
                # Check if it's a rate limit issue
                if 'X-RateLimit-Remaining' in response.headers:
                    return {
                        'success': False,
                        'message': 'GitHub API rate limit exceeded. Please try again later.',
                        'error_code': 'RATE_LIMIT_EXCEEDED'
                    }
                else:
                    return {
                        'success': False,
                        'message': 'Access forbidden. Authentication may be required.',
                        'error_code': 'ACCESS_FORBIDDEN'
                    }
                    
            else:
                response.raise_for_status()
                
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout while fetching repositories for {github_username}")
            return {
                'success': False,
                'message': 'Request timeout while fetching repositories from GitHub',
                'error_code': 'REQUEST_TIMEOUT'
            }
            
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Connection error while fetching repositories for {github_username}")
            return {
                'success': False,
                'message': 'Connection error while contacting GitHub API',
                'error_code': 'CONNECTION_ERROR'
            }
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error while fetching repositories for {github_username}: {str(e)}")
            return {
                'success': False,
                'message': f'Error fetching repositories: {str(e)}',
                'error_code': 'REQUEST_ERROR'
            }
            
        except Exception as e:
            self.logger.error(f"Unexpected error while fetching repositories for {github_username}: {str(e)}")
            return {
                'success': False,
                'message': 'An unexpected error occurred while fetching repositories',
                'error_code': 'UNEXPECTED_ERROR'
            }
    
    def get_repository_details(self, owner: str, repo_name: str, access_token: Optional[str] = None) -> Dict:
        """
        Get detailed information about a specific repository.
        
        Args:
            owner: Repository owner username
            repo_name: Repository name
            access_token: Optional GitHub access token for authenticated requests
            
        Returns:
            Dict containing success status and repository data or error message
        """
        try:
            url = f"{self.base_url}/repos/{owner}/{repo_name}"
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'doc-generator-app'
            }
            
            if access_token:
                headers['Authorization'] = f'token {access_token}'
            
            self.logger.info(f"Fetching repository details for: {owner}/{repo_name}")
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                repo_data = response.json()
                return {
                    'success': True,
                    'data': repo_data,
                    'message': f'Successfully fetched repository details for {owner}/{repo_name}'
                }
            elif response.status_code == 404:
                return {
                    'success': False,
                    'message': f'Repository "{owner}/{repo_name}" not found',
                    'error_code': 'REPOSITORY_NOT_FOUND'
                }
            else:
                response.raise_for_status()
                
        except Exception as e:
            self.logger.error(f"Error fetching repository details for {owner}/{repo_name}: {str(e)}")
            return {
                'success': False,
                'message': f'Error fetching repository details: {str(e)}',
                'error_code': 'REQUEST_ERROR'
            }
