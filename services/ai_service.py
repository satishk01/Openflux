import boto3
import json
import logging
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError, NoCredentialsError
import streamlit as st

class AIService:
    """AI Service for AWS Bedrock integration with Claude and Nova models"""
    
    def __init__(self, credentials_manager=None):
        self.bedrock_client = None
        self.bedrock_control_client = None
        self.current_model = None
        self.credentials_manager = credentials_manager
        self.model_configs = {
            "Claude Sonnet 3.5 v2": {
                "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                "max_tokens": 4096,
                "temperature": 0.7
            },
            "Amazon Nova Pro": {
                "model_id": "amazon.nova-pro-v1:0",
                "max_tokens": 4096,
                "temperature": 0.7
            }
        }
        self.logger = logging.getLogger(__name__)
        
    def initialize_bedrock_client(self) -> bool:
        """Initialize AWS Bedrock client using credentials manager"""
        try:
            # Get AWS session from credentials manager
            if self.credentials_manager:
                session = self.credentials_manager.get_aws_session()
                if not session:
                    self.logger.error("No valid AWS session available from credentials manager")
                    st.error("🚨 No valid AWS credentials. Please configure your credentials first.")
                    return False
            else:
                # Fallback to default credentials (for backward compatibility)
                session = boto3.Session()
            
            # Get region from session or use default
            region = session.region_name or 'us-east-1'
            
            # Initialize both clients - bedrock for listing models, bedrock-runtime for inference
            self.bedrock_client = session.client(
                service_name='bedrock-runtime',
                region_name=region
            )
            
            self.bedrock_control_client = session.client(
                service_name='bedrock',
                region_name=region
            )
            
            # Test connection
            self._test_connection()
            return True
            
        except NoCredentialsError:
            self.logger.error("No AWS credentials found. Please provide valid credentials.")
            st.error("🚨 AWS credentials not found. Please configure your AWS Access Key and Secret Key.")
            return False
        except ClientError as e:
            self.logger.error(f"AWS Bedrock client initialization failed: {e}")
            st.error(f"🚨 Failed to connect to AWS Bedrock: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error initializing Bedrock client: {e}")
            st.error(f"🚨 Unexpected error: {e}")
            return False
    
    def _test_connection(self):
        """Test Bedrock connection"""
        try:
            # Try to list models first (requires bedrock:ListFoundationModels permission)
            try:
                response = self.bedrock_control_client.list_foundation_models()
                self.logger.info("Successfully connected to AWS Bedrock")
                
                # Verify our target models are available
                available_models = [model['modelId'] for model in response.get('modelSummaries', [])]
                
                # Check if our configured models are available
                for model_name, config in self.model_configs.items():
                    model_id = config['model_id']
                    if model_id not in available_models:
                        self.logger.warning(f"Model {model_id} not found in available models")
                        
            except ClientError as e:
                if e.response['Error']['Code'] == 'AccessDeniedException':
                    # If we can't list models, just log a warning and continue
                    self.logger.warning("Cannot list foundation models (permission denied), but clients are initialized")
                else:
                    raise e
            
        except Exception as e:
            raise ClientError(
                error_response={'Error': {'Code': 'ConnectionTest', 'Message': str(e)}},
                operation_name='TestConnection'
            )
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        if not self.bedrock_control_client:
            if not self.initialize_bedrock_client():
                return []
        
        try:
            response = self.bedrock_control_client.list_foundation_models()
            available_models = [model['modelId'] for model in response.get('modelSummaries', [])]
            
            # Filter to only our configured models that are available
            configured_available = []
            for model_name, config in self.model_configs.items():
                if config['model_id'] in available_models:
                    configured_available.append(model_name)
            
            return configured_available
        except Exception as e:
            self.logger.error(f"Failed to get available models: {e}")
            return list(self.model_configs.keys())  # Return all configured models as fallback
    
    def select_model(self, model_name: str) -> bool:
        """Select and validate AI model"""
        if model_name not in self.model_configs:
            st.error(f"🚨 Unknown model: {model_name}")
            return False
        
        # Check if we have valid credentials first
        if self.credentials_manager:
            status = self.credentials_manager.get_credentials_status()
            if not (status['has_credentials'] and status['validated']):
                st.error("🚨 Please configure your AWS credentials first")
                return False
        
        if not self.bedrock_client:
            if not self.initialize_bedrock_client():
                return False
        
        self.current_model = model_name
        st.success(f"✅ Selected model: {model_name}")
        return True
    
    def _prepare_claude_payload(self, prompt: str, system_prompt: str = None) -> Dict:
        """Prepare payload for Claude models"""
        config = self.model_configs[self.current_model]
        
        messages = [{"role": "user", "content": prompt}]
        
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": config["max_tokens"],
            "temperature": config["temperature"],
            "messages": messages
        }
        
        if system_prompt:
            payload["system"] = system_prompt
            
        return payload
    
    def _prepare_nova_payload(self, prompt: str, system_prompt: str = None) -> Dict:
        """Prepare payload for Nova models"""
        config = self.model_configs[self.current_model]
        
        # Nova Pro expects content to be an array of content objects
        messages = [{"role": "user", "content": [{"text": prompt}]}]
        
        payload = {
            "messages": messages,
            "inferenceConfig": {
                "max_new_tokens": config["max_tokens"],
                "temperature": config["temperature"]
            }
        }
        
        if system_prompt:
            payload["system"] = [{"text": system_prompt}]
            
        return payload
    
    def _invoke_model(self, payload: Dict) -> str:
        """Invoke the selected model with payload"""
        try:
            config = self.model_configs[self.current_model]
            
            response = self.bedrock_client.invoke_model(
                modelId=config["model_id"],
                body=json.dumps(payload),
                contentType="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            
            # Parse response based on model type
            if "claude" in config["model_id"].lower():
                return response_body['content'][0]['text']
            elif "nova" in config["model_id"].lower():
                return response_body['output']['message']['content'][0]['text']
            else:
                raise ValueError(f"Unknown model type: {config['model_id']}")
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ValidationException':
                raise Exception(f"Model validation error: {e}")
            elif error_code == 'ThrottlingException':
                raise Exception("Request throttled. Please try again later.")
            else:
                raise Exception(f"AWS Bedrock error: {e}")
        except Exception as e:
            raise Exception(f"Model invocation failed: {e}")
    
    def generate_text(self, prompt: str, system_prompt: str = None) -> str:
        """Generate text using the selected model"""
        if not self.current_model:
            raise Exception("No model selected. Please select a model first.")
        
        # Verify credentials are still valid
        if self.credentials_manager:
            status = self.credentials_manager.get_credentials_status()
            if not (status['has_credentials'] and status['validated']):
                raise Exception("AWS credentials are not available. Please reconfigure your credentials.")
        
        if not self.bedrock_client:
            if not self.initialize_bedrock_client():
                raise Exception("Failed to initialize Bedrock client")
        
        try:
            # Prepare payload based on model type
            if "claude" in self.current_model.lower():
                payload = self._prepare_claude_payload(prompt, system_prompt)
            elif "nova" in self.current_model.lower():
                payload = self._prepare_nova_payload(prompt, system_prompt)
            else:
                raise Exception(f"Unsupported model: {self.current_model}")
            
            return self._invoke_model(payload)
            
        except Exception as e:
            self.logger.error(f"Text generation failed: {e}")
            # Don't expose credential details in error messages
            if "credential" in str(e).lower() or "access" in str(e).lower():
                raise Exception("Authentication failed. Please check your AWS credentials.")
            raise e
    
    def generate_requirements(self, description: str, context: Dict = None, coding_template: str = None) -> str:
        """Generate EARS-format requirements from description"""
        system_prompt = """You are an expert business analyst and requirements engineer. Generate comprehensive, detailed business requirements in EARS format that match the quality and depth of professional specification documents.

        CRITICAL INSTRUCTIONS:
        1. Generate BUSINESS REQUIREMENTS ONLY - no technical implementation details
        2. Create 6-8 comprehensive requirements covering all major functional areas
        3. Each requirement should have 4-6 detailed acceptance criteria
        4. Use precise, professional language with specific business terminology
        5. Include edge cases, error scenarios, and business rules
        6. Consider different user roles and their specific needs
        7. Address security, compliance, and audit requirements from business perspective

        DOCUMENT STRUCTURE:

        # Requirements Document

        ## Introduction
        Write a comprehensive 2-3 paragraph introduction that:
        - Clearly describes the business purpose and scope
        - Identifies the target users and stakeholders  
        - Explains the business value and objectives
        - References the technical approach (from template) without implementation details

        ## Requirements

        ### Requirement 1: [Core Business Function]
        **User Story:** As a [specific role], I want [detailed business capability], so that [clear business benefit and value]

        #### Acceptance Criteria
        1. WHEN [specific business event/trigger] THEN [system] SHALL [detailed business response with specific outcomes]
        2. WHEN [user action with context] THEN [system] SHALL [comprehensive behavior including data returned]
        3. IF [business condition or constraint] THEN [system] SHALL [appropriate business behavior]
        4. WHEN [edge case or error scenario] THEN [system] SHALL [error handling from business perspective]
        5. WHEN [integration or workflow scenario] THEN [system] SHALL [cross-functional behavior]
        6. WHEN [security or compliance scenario] THEN [system] SHALL [business-level security requirements]

        [Continue with 5-7 more requirements covering all major business functions]

        QUALITY STANDARDS:
        - Each acceptance criterion should be testable and measurable
        - Use specific business terminology and domain language
        - Include quantitative measures where appropriate (response times, limits, etc.)
        - Address both happy path and error scenarios
        - Consider different user roles and permissions
        - Include audit, compliance, and reporting requirements
        - Address data validation and business rules
        - Consider integration points and external dependencies

        BUSINESS FOCUS AREAS:
        - Core business functionality and workflows
        - User management and authentication (business perspective)
        - Data management and business rules
        - Integration requirements (what systems, not how)
        - Security and compliance (business requirements)
        - Reporting and analytics needs
        - Performance expectations (business impact)
        - Error handling and business continuity"""
        
        context_str = ""
        if context:
            context_str = f"\n\nAdditional context:\n{json.dumps(context, indent=2)}"
        
        template_str = ""
        if coding_template and coding_template.strip():
            template_str = f"\n\nCoding Template & Standards:\n{coding_template[:1000]}{'...' if len(coding_template) > 1000 else ''}\n\nIMPORTANT: Use this template to understand the technical context and constraints, but generate BUSINESS requirements only. Adapt your requirements to align with the architectural approach and technology choices mentioned in the template, while keeping requirements focused on business functionality."
        else:
            template_str = "\n\nNote: No coding template provided. Generate technology-agnostic business requirements that can be implemented with any suitable technology stack."
        
        prompt = f"Generate business requirements document for: {description}{context_str}{template_str}"
        
        return self.generate_text(prompt, system_prompt)
    
    def create_design(self, requirements: str, codebase: Dict = None, coding_template: str = None) -> str:
        """Create design document from requirements"""
        system_prompt = """You are an expert software architect and technical lead. Create a comprehensive, professional-grade technical design document that matches the quality and depth of enterprise-level system designs.

        CRITICAL INSTRUCTIONS:
        1. Follow the coding template's architectural patterns and technology choices precisely
        2. Create detailed technical specifications with specific implementation approaches
        3. Include comprehensive Mermaid diagrams showing system architecture
        4. Provide specific data models with field definitions and types
        5. Address all technical aspects: security, performance, scalability, testing
        6. Use professional technical language and industry best practices
        7. Include specific technology stack details from the template

        DOCUMENT STRUCTURE:

        # Design Document

        ## Overview
        Write a comprehensive 2-3 paragraph technical overview that:
        - Describes the overall architecture approach and style (from template)
        - Identifies key technology choices and their rationale
        - Explains how the design addresses the business requirements
        - Highlights scalability, security, and performance considerations
        - References specific patterns and frameworks from the coding template

        ## Architecture

        ### High-Level Architecture
        Create a detailed Mermaid diagram showing:
        - All major system components and services
        - Data flow between components
        - External integrations and dependencies
        - Technology stack elements (databases, APIs, services)
        - Security boundaries and access patterns

        ```mermaid
        graph TB
            [Create comprehensive architecture diagram with 15-25 nodes showing complete system]
        ```

        ### Service Architecture
        Provide detailed breakdown of each service/component:
        - Specific responsibilities and business logic
        - Technology implementation approach
        - Integration patterns and communication methods
        - Data access and persistence strategies

        ## Components and Interfaces

        For each major component (create 5-8 components):

        ### 1. [Component Name] Service
        **Endpoints/APIs:**
        - List 4-6 specific endpoints with HTTP methods and paths
        - Include request/response formats and parameters
        
        **Implementation Components:**
        - List specific implementation units (functions, classes, modules, services) based on the architecture
        - Include implementation approach and business logic
        
        **Responsibilities:**
        - Detailed list of what this component handles
        - Integration points with other components

        ## Data Models

        Provide comprehensive data structures for each entity:
        ```javascript
        {
          // Detailed field definitions with types, constraints, and relationships
          // Include 8-12 fields per model with proper data types
          // Add comments explaining business purpose of fields
        }
        ```

        Include:
        - Primary entities (5-8 main data models)
        - Relationships and foreign keys
        - Indexes and query optimization considerations
        - Data validation rules and constraints

        ## Error Handling
        - Standardized error response formats with examples
        - Error categorization and HTTP status codes
        - Retry logic and circuit breaker patterns
        - Logging and monitoring strategies

        ## Testing Strategy
        - Unit testing approach with specific frameworks
        - Integration testing scenarios and tools
        - End-to-end testing workflows
        - Performance and load testing strategies
        - Security testing requirements

        ## Deployment and Configuration
        - Infrastructure as Code approach
        - Environment configuration management
        - CI/CD pipeline requirements
        - Monitoring and observability setup

        ## Security Considerations
        - Authentication and authorization mechanisms
        - Data encryption at rest and in transit
        - Input validation and sanitization
        - Security headers and CORS configuration
        - Compliance requirements (PCI, GDPR, etc.)

        QUALITY STANDARDS:
        - Use specific technology names and versions from template
        - Include actual code patterns and architectural decisions
        - Provide measurable performance and scalability targets
        - Address enterprise-level concerns (monitoring, logging, security)
        - Include specific implementation details and best practices
        - Reference industry standards and proven patterns"""
        
        codebase_str = ""
        if codebase:
            codebase_str = f"\n\nExisting codebase context:\n{json.dumps(codebase, indent=2)}"
        
        template_str = ""
        if coding_template and coding_template.strip():
            template_str = f"\n\nCoding Template & Standards:\n{coding_template[:1000]}{'...' if len(coding_template) > 1000 else ''}\n\nCRITICAL: Adapt the design to follow the specific architectural patterns, technologies, frameworks, coding standards, and technical approaches specified in this template. Use the template as your primary guide for all technical decisions, technology choices, and implementation approaches. If the template specifies different technologies than mentioned in examples above, use the template's specifications instead."
        else:
            template_str = "\n\nNote: No coding template provided. Create a flexible, technology-agnostic design that follows modern software architecture best practices. Choose appropriate technologies and patterns based on the requirements and industry standards."
        
        prompt = f"Create technical design document for these requirements:\n{requirements}{codebase_str}{template_str}"
        
        return self.generate_text(prompt, system_prompt)
    

    def analyze_codebase(self, files: Dict) -> Dict:
        """Analyze codebase structure and patterns"""
        system_prompt = """You are OpenFlux, an AI assistant and IDE built to assist developers.
        Analyze the provided codebase and return insights about:
        - Architecture patterns
        - Technology stack
        - Data models and relationships
        - Potential improvements
        - Security considerations
        
        Provide actionable insights for development planning."""
        
        # Limit file content for analysis to avoid token limits
        limited_files = {}
        for path, content in files.items():
            if len(content) > 2000:  # Truncate large files
                limited_files[path] = content[:2000] + "... [truncated]"
            else:
                limited_files[path] = content
        
        prompt = f"Analyze this codebase:\n{json.dumps(limited_files, indent=2)}"
        
        response = self.generate_text(prompt, system_prompt)
        
        return {
            "analysis": response,
            "file_count": len(files),
            "total_size": sum(len(content) for content in files.values()),
            "languages": self._detect_languages(files)
        }
    
    def _detect_languages(self, files: Dict) -> List[str]:
        """Detect programming languages from file extensions"""
        extensions = set()
        for file_path in files.keys():
            if '.' in file_path:
                ext = file_path.split('.')[-1].lower()
                extensions.add(ext)
        
        # Map extensions to languages
        lang_map = {
            'py': 'Python', 'js': 'JavaScript', 'ts': 'TypeScript',
            'java': 'Java', 'cpp': 'C++', 'c': 'C', 'cs': 'C#',
            'go': 'Go', 'rs': 'Rust', 'php': 'PHP', 'rb': 'Ruby',
            'html': 'HTML', 'css': 'CSS', 'sql': 'SQL', 'json': 'JSON',
            'yaml': 'YAML', 'yml': 'YAML', 'xml': 'XML', 'md': 'Markdown'
        }
        
        return [lang_map.get(ext, ext.upper()) for ext in extensions if ext in lang_map]