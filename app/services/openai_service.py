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
            # Use lower temperature for more consistent, less creative responses
            temperature = current_app.config.get('THESIS_OPENAI_TEMPERATURE', 0.3)
            
            # Create system prompt based on file type
            system_prompt = self._get_system_prompt(file_extension)
            
            # Create structured user prompt with file-specific guidance
            user_prompt = self._create_structured_prompt(code, file_path, file_extension)
            
            # Call OpenAI API using v0.28.1 interface
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature
            )
            
            response_content = response.choices[0].message.content
            
            # Validate the response format
            validated_content = self._validate_documentation_format(response_content, file_path)
            
            return validated_content
            
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
            'py': "You are an expert Python developer and technical writer. Generate clear, comprehensive documentation for Python code. ALWAYS follow the exact 7-section template structure provided in the user prompt. Maintain consistency in formatting, headings, and section organization.",
            'js': "You are an expert JavaScript developer and technical writer. Generate clear, comprehensive documentation for JavaScript code. ALWAYS follow the exact 7-section template structure provided in the user prompt. Maintain consistency in formatting, headings, and section organization.",
            'ts': "You are an expert TypeScript developer and technical writer. Generate clear, comprehensive documentation for TypeScript code. ALWAYS follow the exact 7-section template structure provided in the user prompt. Maintain consistency in formatting, headings, and section organization.",
            'java': "You are an expert Java developer and technical writer. Generate clear, comprehensive documentation for Java code. ALWAYS follow the exact 7-section template structure provided in the user prompt. Maintain consistency in formatting, headings, and section organization.",
            'cpp': "You are an expert C++ developer and technical writer. Generate clear, comprehensive documentation for C++ code. ALWAYS follow the exact 7-section template structure provided in the user prompt. Maintain consistency in formatting, headings, and section organization.",
            'c': "You are an expert C developer and technical writer. Generate clear, comprehensive documentation for C code. ALWAYS follow the exact 7-section template structure provided in the user prompt. Maintain consistency in formatting, headings, and section organization.",
            'go': "You are an expert Go developer and technical writer. Generate clear, comprehensive documentation for Go code. ALWAYS follow the exact 7-section template structure provided in the user prompt. Maintain consistency in formatting, headings, and section organization.",
            'rs': "You are an expert Rust developer and technical writer. Generate clear, comprehensive documentation for Rust code. ALWAYS follow the exact 7-section template structure provided in the user prompt. Maintain consistency in formatting, headings, and section organization.",
            'php': "You are an expert PHP developer and technical writer. Generate clear, comprehensive documentation for PHP code. ALWAYS follow the exact 7-section template structure provided in the user prompt. Maintain consistency in formatting, headings, and section organization.",
            'rb': "You are an expert Ruby developer and technical writer. Generate clear, comprehensive documentation for Ruby code. ALWAYS follow the exact 7-section template structure provided in the user prompt. Maintain consistency in formatting, headings, and section organization.",
            'html': "You are an expert web developer and technical writer. Generate clear, comprehensive documentation for HTML code. ALWAYS follow the exact 7-section template structure provided in the user prompt. Maintain consistency in formatting, headings, and section organization.",
            'css': "You are an expert web developer and technical writer. Generate clear, comprehensive documentation for CSS code. ALWAYS follow the exact 7-section template structure provided in the user prompt. Maintain consistency in formatting, headings, and section organization.",
            'sql': "You are an expert database developer and technical writer. Generate clear, comprehensive documentation for SQL code. ALWAYS follow the exact 7-section template structure provided in the user prompt. Maintain consistency in formatting, headings, and section organization.",
            'sh': "You are an expert system administrator and technical writer. Generate clear, comprehensive documentation for shell scripts. ALWAYS follow the exact 7-section template structure provided in the user prompt. Maintain consistency in formatting, headings, and section organization.",
            'md': "You are an expert technical writer. Generate clear, comprehensive documentation for Markdown content. ALWAYS follow the exact 7-section template structure provided in the user prompt. Maintain consistency in formatting, headings, and section organization.",
            'json': "You are an expert developer and technical writer. Generate clear, comprehensive documentation for JSON configuration files. ALWAYS follow the exact 7-section template structure provided in the user prompt. Maintain consistency in formatting, headings, and section organization.",
            'yaml': "You are an expert developer and technical writer. Generate clear, comprehensive documentation for YAML configuration files. ALWAYS follow the exact 7-section template structure provided in the user prompt. Maintain consistency in formatting, headings, and section organization.",
            'yml': "You are an expert developer and technical writer. Generate clear, comprehensive documentation for YAML configuration files. ALWAYS follow the exact 7-section template structure provided in the user prompt. Maintain consistency in formatting, headings, and section organization.",
            'mod': "You are an expert Go developer and technical writer. Generate clear, comprehensive documentation for Go module files. ALWAYS follow the exact 7-section template structure provided in the user prompt. Maintain consistency in formatting, headings, and section organization.",
            'sum': "You are an expert Go developer and technical writer. Generate clear, comprehensive documentation for Go dependency files. ALWAYS follow the exact 7-section template structure provided in the user prompt. Maintain consistency in formatting, headings, and section organization.",
        }
        
        return language_prompts.get(
            file_extension, 
            "You are an expert software developer and technical writer. Generate clear, comprehensive documentation for the provided code. ALWAYS follow the exact 7-section template structure provided in the user prompt. Maintain consistency in formatting, headings, and section organization."
        )
    
    def _validate_documentation_format(self, content: str, file_path: str) -> str:
        """
        Validate and fix the documentation format to ensure consistency.
        
        Args:
            content: Generated documentation content
            file_path: Original file path for context
            
        Returns:
            Validated and potentially corrected documentation
        """
        required_sections = [
            "## 1. Overview",
            "## 2. Key Components", 
            "## 3. Parameters/Arguments",
            "## 4. Return Values",
            "## 5. Dependencies",
            "## 6. Usage Examples",
            "## 7. Best Practices"
        ]
        
        # Check if content starts with proper title format
        if not content.startswith(f"# Documentation: `{file_path}`"):
            # Fix the title if it's incorrect
            lines = content.split('\n')
            # Find the first heading and replace it
            for i, line in enumerate(lines):
                if line.startswith('# '):
                    lines[i] = f"# Documentation: `{file_path}`"
                    break
            else:
                # Add title if missing
                lines.insert(0, f"# Documentation: `{file_path}`")
                lines.insert(1, "")
            content = '\n'.join(lines)
        
        # Ensure all required sections are present
        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        if missing_sections:
            self.logger.warning(f"Missing sections in documentation: {missing_sections}")
            # Note: In production, you might want to call OpenAI again or add placeholder sections
        
        # Ensure proper section separators
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            fixed_lines.append(line)
            # Add separator after each main section (except the last one)
            if any(line.startswith(section) for section in required_sections[:-1]):
                # Look ahead to see if there's already a separator
                next_non_empty = None
                for j in range(i + 1, min(i + 5, len(lines))):
                    if lines[j].strip():
                        next_non_empty = lines[j].strip()
                        break
                
                # Add separator if not present
                if next_non_empty != "---":
                    # Find the end of this section's content
                    section_end = i + 1
                    while section_end < len(lines) and not any(lines[section_end].startswith(s) for s in required_sections):
                        section_end += 1
                    
                    # Add separator before the next section
                    if section_end < len(lines):
                        fixed_lines.append("")
                        fixed_lines.append("---")
                        fixed_lines.append("")
        
        return '\n'.join(fixed_lines)
    
    def _create_structured_prompt(self, code: str, file_path: str, file_extension: str) -> str:
        """
        Create a structured prompt with file-type specific guidance.
        
        Args:
            code: The source code content
            file_path: Path/name of the file
            file_extension: File extension
            
        Returns:
            Structured prompt string
        """
        # File-specific guidance for different types
        file_type_guidance = {
            'mod': {
                'overview_guide': 'This `go.mod` file defines the Go module configuration for the project. Describe the module name, Go version, and purpose of the service/application.',
                'components_guide': 'As a `go.mod` file, describe the key dependency categories (web framework, database, CLI tools, etc.) rather than classes or functions.',
                'params_guide': '_Not applicable to `go.mod` files_, as they specify dependencies and versions rather than function parameters.',
                'returns_guide': '_Not applicable._ The `go.mod` file does not define functions or return values.',
                'examples': 'Include commands like `go mod tidy`, `go build`, `go get`, and project initialization examples.'
            },
            'sum': {
                'overview_guide': 'The `go.sum` file is part of the Go modules system providing cryptographic verification for dependencies.',
                'components_guide': 'Describe the structure of checksum entries (module path, version, hash) rather than code components.',
                'params_guide': '_Not applicable to `go.sum` files_, as they are automatically generated dependency checksums.',
                'returns_guide': '_Not applicable._ The `go.sum` file does not define functions or return values.',
                'examples': 'Include Go commands that interact with go.sum like `go mod verify`, `go build`, `go mod tidy`.'
            },
            'py': {
                'overview_guide': 'This Python file/module [describe main purpose]. Focus on the primary functionality and role within the application.',
                'components_guide': 'List and describe classes, functions, constants, and key variables. Include class inheritance and method signatures.',
                'params_guide': 'Document function parameters, their types, default values, and validation requirements.',
                'returns_guide': 'Document return types, possible return values, and any exceptions that may be raised.',
                'examples': 'Provide practical code examples showing how to import, instantiate, and use the main components.'
            },
            'go': {
                'overview_guide': 'This Go file/package [describe main purpose]. Focus on the package functionality and exported types.',
                'components_guide': 'List and describe structs, interfaces, functions, constants, and exported variables.',
                'params_guide': 'Document function parameters, struct fields, their types, and any validation rules.',
                'returns_guide': 'Document return types, error conditions, and any side effects.',
                'examples': 'Show package import, struct initialization, method calls, and error handling patterns.'
            },
            'js': {
                'overview_guide': 'This JavaScript file/module [describe main purpose]. Focus on the primary functionality and exports.',
                'components_guide': 'List and describe functions, classes, objects, constants, and exported variables.',
                'params_guide': 'Document function parameters, their types, default values, and validation requirements.',
                'returns_guide': 'Document return types, possible return values, and any thrown exceptions.',
                'examples': 'Provide practical code examples showing imports, instantiation, and usage patterns.'
            },
            'ts': {
                'overview_guide': 'This TypeScript file/module [describe main purpose]. Focus on the primary functionality and type definitions.',
                'components_guide': 'List and describe interfaces, classes, types, functions, and exported members.',
                'params_guide': 'Document function parameters, their TypeScript types, default values, and constraints.',
                'returns_guide': 'Document return types, possible return values, and any thrown exceptions.',
                'examples': 'Show import statements, type usage, class instantiation, and method calls.'
            },
            'json': {
                'overview_guide': 'This JSON file serves as a configuration/data file. Describe its purpose and how it\'s used in the application.',
                'components_guide': 'Describe the main configuration sections, data structures, and key-value pairs.',
                'params_guide': '_Not applicable to JSON files_, as they contain data structures rather than function parameters.',
                'returns_guide': '_Not applicable._ JSON files define data structures and configuration values.',
                'examples': 'Show how the configuration is loaded and used in the application, including environment-specific variations.'
            },
            'yaml': {
                'overview_guide': 'This YAML file serves as a configuration file. Describe its purpose and role in the application or deployment.',
                'components_guide': 'Describe the main configuration sections, hierarchical structure, and key settings.',
                'params_guide': '_Not applicable to YAML files_, as they contain configuration data rather than function parameters.',
                'returns_guide': '_Not applicable._ YAML files define configuration structures and values.',
                'examples': 'Show how the configuration is loaded, validated, and applied in the application or deployment process.'
            }
        }
        
        guidance = file_type_guidance.get(file_extension, {
            'overview_guide': 'This file/module [describe main purpose]. Focus on the primary functionality and role within the application.',
            'components_guide': 'List and describe the main components, functions, classes, or configuration elements.',
            'params_guide': 'Document parameters, arguments, or configuration options if applicable.',
            'returns_guide': 'Document return values, outputs, or results if applicable.',
            'examples': 'Provide practical usage examples and common operations.'
        })
        
        return f"""
Please generate comprehensive documentation for the following {file_extension} file: {file_path}

```{file_extension}
{code}
```

IMPORTANT: Follow this EXACT format and structure for consistency. Use this precise template:

# Documentation: `{file_path}`

## 1. Overview

{guidance['overview_guide']}

---

## 2. Key Components

{guidance['components_guide']}

---

## 3. Parameters/Arguments

{guidance['params_guide']}

---

## 4. Return Values

{guidance['returns_guide']}

---

## 5. Dependencies

List external dependencies, imports, or required modules. For config files, categorize dependencies by purpose. Use tables when appropriate with columns: Package/Module | Purpose/Description

---

## 6. Usage Examples

{guidance['examples']}

---

## 7. Best Practices

List recommendations, security considerations, maintenance tips, and common pitfalls to avoid. Use bullet points starting with action verbs.

---

FORMATTING REQUIREMENTS:
- Use exactly the heading structure shown above (## 1. Overview, ## 2. Key Components, etc.)
- Always include horizontal separators (---) between sections
- Use **bold** for important terms and concepts
- Use `backticks` for code elements, file names, and technical terms
- Use bullet points for lists (start with -)
- Use tables for dependency lists when appropriate
- Keep consistent spacing and indentation
- End with a summary note if the file is foundational/skeletal

Format the documentation in clear, well-structured Markdown following this exact template.
"""
