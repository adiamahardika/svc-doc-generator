import base64
import openai
from app.services.base_service import BaseService
from app.services.github_service import GitHubService
from typing import Optional, Dict, Any
from flask import current_app


class OpenAIService(BaseService):
    """Service for interacting with OpenAI API."""
    
    def __init__(self):
        super().__init__()
        self.github_service = GitHubService()
    
    def _configure_openai(self):
        """Configure OpenAI with API key."""
        api_key = current_app.config.get('THESIS_OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not configured")
        openai.api_key = api_key
    
    def generate_documentation_from_base64(self, file_name: str, base64_content: str, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate documentation for a file from base64 content using OpenAI.
        
        Args:
            file_name: Name of the file (e.g., 'example.py')
            base64_content: Base64 encoded file content
            model: Optional OpenAI model to use (defaults to config)
            
        Returns:
            Dict containing file info and generated documentation
        """
        try:
            # Decode base64 content
            file_content = base64.b64decode(base64_content).decode('utf-8')
            
            # Generate documentation using OpenAI
            documentation = self._generate_documentation_with_openai(file_content, file_name, model)
            
            return {
                "file": file_name,
                "model_used": model or current_app.config.get('THESIS_OPENAI_MODEL', 'gpt-3.5-turbo'),
                "documentation": documentation,
                "status": "success"
            }
            
        except Exception as e:
            self.logger.error(f"Error generating documentation from base64: {str(e)}")
            raise Exception(f"Failed to generate documentation: {str(e)}")
    
    def generate_documentation(self, repo_name: str, file_path: str, access_token: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate documentation for a file from GitHub repository using OpenAI.
        
        Args:
            repo_name: GitHub repository name (e.g., 'username/repo')
            file_path: Path to the file in the repository
            access_token: Optional GitHub access token for private repos
            model: Optional OpenAI model to use (defaults to config)
            
        Returns:
            Dict containing repository info, file info, and generated documentation
        """
        try:
            # Get file content from GitHub
            file_content = self._get_file_content_from_github(repo_name, file_path, access_token)
            
            # Generate documentation using OpenAI
            documentation = self._generate_documentation_with_openai(file_content, file_path, model)
            
            return {
                "repository": repo_name,
                "file": file_path,
                "model_used": model or current_app.config.get('THESIS_OPENAI_MODEL', 'gpt-3.5-turbo'),
                "documentation": documentation,
                "status": "success"
            }
            
        except Exception as e:
            self.logger.error(f"Error generating documentation: {str(e)}")
            raise Exception(f"Failed to generate documentation: {str(e)}")
    
    def _get_file_content_from_github(self, repo_name: str, file_path: str, access_token: Optional[str] = None) -> str:
        """
        Get file content from GitHub repository.
        
        Args:
            repo_name: GitHub repository name
            file_path: Path to the file
            access_token: Optional GitHub access token
            
        Returns:
            File content as string
        """
        try:
            # Parse repository name
            if '/' not in repo_name:
                raise ValueError("Repository name must be in format 'owner/repo'")
                
            owner, repo = repo_name.split('/', 1)
            
            # Use the existing get_repository_details method
            file_info = self.github_service.get_repository_details(owner, repo, file_path, access_token=access_token)
            
            if not file_info.get('success'):
                raise Exception(file_info.get('message', 'Failed to get file from GitHub'))
            
            # Extract file data
            file_data = file_info.get('data')
            if not file_data:
                raise Exception('No file data returned from GitHub')
            
            # Check if it's a file (not a directory)
            if file_data.get('type') != 'file':
                raise Exception(f'Path "{file_path}" is not a file, it is a {file_data.get("type")}')
            
            # Decode base64 content
            content = file_data.get('content', '')
            encoding = file_data.get('encoding', 'base64')
            
            if encoding == 'base64':
                content = base64.b64decode(content).decode('utf-8')
                
            return content
            
        except Exception as e:
            self.logger.error(f"Error getting file from GitHub: {str(e)}")
            raise Exception(f"Failed to get file from GitHub: {str(e)}")
    
    def _generate_documentation_with_openai(self, code: str, file_path: str, model: Optional[str] = None) -> str:
        """
        Generate documentation for code using OpenAI.
        
        Args:
            code: The source code
            file_path: Path/name of the file for context
            model: Optional OpenAI model to use
            
        Returns:
            Generated documentation as string
        """
        try:
            # Configure OpenAI
            self._configure_openai()
            
            # Determine file type from extension
            file_extension = file_path.split('.')[-1].lower() if '.' in file_path else 'unknown'
            
            # Configure model and parameters
            model_name = model or current_app.config.get('THESIS_OPENAI_MODEL', 'gpt-3.5-turbo')
            max_tokens = current_app.config.get('THESIS_OPENAI_MAX_TOKENS', 2048)
            temperature = current_app.config.get('THESIS_OPENAI_TEMPERATURE', 0.7)
            
            # Create system prompt based on file type
            system_prompt = self._get_system_prompt(file_extension)
            
            # Create user prompt
            user_prompt = f"""
Please generate comprehensive documentation for the following {file_extension} file: {file_path}

```{file_extension}
{code}
```

Please provide:
1. **Overview**: Brief description of what this file/module does
2. **Key Components**: Main classes, functions, or components
3. **Parameters/Arguments**: If applicable, document function parameters
4. **Return Values**: If applicable, document return values
5. **Dependencies**: List any external dependencies or imports
6. **Usage Examples**: Provide practical usage examples if possible
7. **Best Practices**: Any recommendations for using this code

Format the documentation in clear, well-structured Markdown.
"""
            
            # Call OpenAI API using v0.28.1 interface
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Error calling OpenAI API: {str(e)}")
            raise Exception(f"Failed to generate documentation with OpenAI: {str(e)}")
    
    def _get_system_prompt(self, file_extension: str) -> str:
        """
        Get appropriate system prompt based on file type.
        
        Args:
            file_extension: File extension to determine language/type
            
        Returns:
            System prompt string
        """
        language_prompts = {
            'py': "You are an expert Python developer and technical writer. Generate clear, comprehensive documentation for Python code.",
            'js': "You are an expert JavaScript developer and technical writer. Generate clear, comprehensive documentation for JavaScript code.",
            'ts': "You are an expert TypeScript developer and technical writer. Generate clear, comprehensive documentation for TypeScript code.",
            'java': "You are an expert Java developer and technical writer. Generate clear, comprehensive documentation for Java code.",
            'cpp': "You are an expert C++ developer and technical writer. Generate clear, comprehensive documentation for C++ code.",
            'c': "You are an expert C developer and technical writer. Generate clear, comprehensive documentation for C code.",
            'go': "You are an expert Go developer and technical writer. Generate clear, comprehensive documentation for Go code.",
            'rs': "You are an expert Rust developer and technical writer. Generate clear, comprehensive documentation for Rust code.",
            'php': "You are an expert PHP developer and technical writer. Generate clear, comprehensive documentation for PHP code.",
            'rb': "You are an expert Ruby developer and technical writer. Generate clear, comprehensive documentation for Ruby code.",
            'html': "You are an expert web developer and technical writer. Generate clear, comprehensive documentation for HTML code.",
            'css': "You are an expert web developer and technical writer. Generate clear, comprehensive documentation for CSS code.",
            'sql': "You are an expert database developer and technical writer. Generate clear, comprehensive documentation for SQL code.",
            'sh': "You are an expert system administrator and technical writer. Generate clear, comprehensive documentation for shell scripts.",
            'md': "You are an expert technical writer. Generate clear, comprehensive documentation for Markdown content.",
            'json': "You are an expert developer and technical writer. Generate clear, comprehensive documentation for JSON configuration files.",
            'yaml': "You are an expert developer and technical writer. Generate clear, comprehensive documentation for YAML configuration files.",
            'yml': "You are an expert developer and technical writer. Generate clear, comprehensive documentation for YAML configuration files.",
        }
        
        return language_prompts.get(
            file_extension, 
            "You are an expert software developer and technical writer. Generate clear, comprehensive documentation for the provided code."
        )
