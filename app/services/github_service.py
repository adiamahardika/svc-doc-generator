import requests
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
    
    def get_user_repositories(self, github_username: str, search: Optional[str] = None, access_token: Optional[str] = None, page: int = 1, per_page: int = 30, sort: str = 'updated_at', order: str = 'desc') -> Dict:
        """
        Get repositories for a GitHub user using GitHub Search API.
        
        Args:
            github_username: The GitHub username
            search: Optional search term for repositories (searches in name and description)
            access_token: Optional GitHub access token for authenticated requests
            page: Page number (1-based)
            per_page: Number of results per page (1-100)
            sort: Sort field (updated_at, name)
            order: Sort order (asc, desc)
            
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
            if search:
                search_query = f'{search} user:{github_username}'
                log_message = f"Fetching repositories for user: {github_username} with search term: {search} (page {page}, per_page {per_page}, sort {sort} {order})"
            else:
                search_query = f'user:{github_username}'
                log_message = f"Fetching repositories for user: {github_username} (page {page}, per_page {per_page}, sort {sort} {order})"

            # Map sort parameter for GitHub API
            github_sort = sort
            if sort == 'name':
                github_sort = 'name'  # GitHub API uses 'name' for name sorting
            elif sort == 'updated_at':
                github_sort = 'updated'  # GitHub API uses 'updated' for updated_at sorting
            else:
                github_sort = sort

            params = {
                'q': search_query,  # Search query for user repositories with optional repo name
                'sort': github_sort,  # GitHub API sort parameter
                'order': order,  # asc, desc
                'page': page,  # Page number
                'per_page': min(per_page, 100)  # Max repositories per page (GitHub limit is 100)
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
                
                # Calculate pagination metadata
                total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
                has_next_page = page < total_pages
                has_prev_page = page > 1
                
                return {
                    'success': True,
                    'data': transformed_repos,
                    'total_count': total_count,
                    'returned_count': len(transformed_repos),
                    'total_pages': total_pages,
                    'has_next_page': has_next_page,
                    'has_prev_page': has_prev_page,
                    'message': f'Successfully fetched {len(transformed_repos)} repositories out of {total_count} total (page {page} of {total_pages})'
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
    
    def get_repository_details(self, owner: str, repo_name: str, path: str = "", access_token: Optional[str] = None) -> Dict:
        """
        Get contents of a file or directory in a repository.
        
        Args:
            owner: Repository owner username
            repo_name: Repository name
            path: Path to file or directory (empty string for root)
            access_token: Optional GitHub access token for authenticated requests
            
        Returns:
            Dict containing success status and repository contents data or error message
        """
        try:
            # Build URL for contents API
            if path:
                url = f"{self.base_url}/repos/{owner}/{repo_name}/contents/{path}"
            else:
                url = f"{self.base_url}/repos/{owner}/{repo_name}/contents"
                
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'doc-generator-app'
            }
            
            if access_token:
                headers['Authorization'] = f'Bearer {access_token}'
            
            self.logger.info(f"Fetching repository contents for: {owner}/{repo_name}/{path}")
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                contents_data = response.json()
                
                # Transform the response based on whether it's a file or directory
                if isinstance(contents_data, list):
                    # Directory contents
                    transformed_contents = []
                    for item in contents_data:
                        transformed_item = {
                            'name': item.get('name'),
                            'path': item.get('path'),
                            'type': item.get('type'),  # file, dir, symlink, submodule
                            'size': item.get('size'),
                            'sha': item.get('sha'),
                            'url': item.get('url'),
                            'html_url': item.get('html_url'),
                            'git_url': item.get('git_url'),
                            'download_url': item.get('download_url'),
                            '_links': item.get('_links')
                        }
                        transformed_contents.append(transformed_item)
                    
                    return {
                        'success': True,
                        'data': {
                            'type': 'directory',
                            'contents': transformed_contents,
                            'path': path,
                            'repository': f"{owner}/{repo_name}"
                        },
                        'message': f'Successfully fetched directory contents for {owner}/{repo_name}/{path}'
                    }
                else:
                    # Single file
                    transformed_file = {
                        'name': contents_data.get('name'),
                        'path': contents_data.get('path'),
                        'type': contents_data.get('type'),
                        'size': contents_data.get('size'),
                        'sha': contents_data.get('sha'),
                        'url': contents_data.get('url'),
                        'html_url': contents_data.get('html_url'),
                        'git_url': contents_data.get('git_url'),
                        'download_url': contents_data.get('download_url'),
                        'content': contents_data.get('content'),  # Base64 encoded content
                        'encoding': contents_data.get('encoding'),
                        '_links': contents_data.get('_links')
                    }
                    
                    return {
                        'success': True,
                        'data': {
                            'type': 'file',
                            'file': transformed_file,
                            'path': path,
                            'repository': f"{owner}/{repo_name}"
                        },
                        'message': f'Successfully fetched file contents for {owner}/{repo_name}/{path}'
                    }
                    
            elif response.status_code == 404:
                return {
                    'success': False,
                    'message': f'Path "{path}" not found in repository "{owner}/{repo_name}"',
                    'error_code': 'PATH_NOT_FOUND'
                }
            elif response.status_code == 403:
                return {
                    'success': False,
                    'message': 'Access forbidden. The repository may be private or you may not have permission.',
                    'error_code': 'ACCESS_FORBIDDEN'
                }
            else:
                response.raise_for_status()
                
        except Exception as e:
            self.logger.error(f"Error fetching repository contents for {owner}/{repo_name}/{path}: {str(e)}")
            return {
                'success': False,
                'message': f'Error fetching repository contents: {str(e)}',
                'error_code': 'REQUEST_ERROR'
            }
