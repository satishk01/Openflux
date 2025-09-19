import unittest
from unittest.mock import Mock
from services.ai_service import AIService
from engines.spec_engine import SpecEngine

class TestTemplateFlexibility(unittest.TestCase):
    """Test that the system adapts to different templates and requirements"""
    
    def setUp(self):
        """Set up test environment"""
        self.ai_service = AIService()
        self.spec_engine = SpecEngine(self.ai_service)
        
        # Mock the AI service to capture prompts
        self.captured_prompts = []
        def mock_generate_text(prompt, system_prompt):
            self.captured_prompts.append({"prompt": prompt, "system_prompt": system_prompt})
            return "Mocked AI response"
        
        self.ai_service.generate_text = mock_generate_text
    
    def test_serverless_template_adaptation(self):
        """Test system adapts to serverless template"""
        serverless_template = """
        Use AWS Lambda functions with Node.js
        Use DynamoDB for data persistence
        Implement serverless microservices architecture
        Use API Gateway for REST endpoints
        """
        
        description = "User management system"
        
        # Generate requirements
        requirements = self.ai_service.generate_requirements(description, None, serverless_template)
        
        # Check that template content is included in prompt
        requirements_prompt = self.captured_prompts[-1]["prompt"]
        self.assertIn("AWS Lambda", requirements_prompt)
        self.assertIn("DynamoDB", requirements_prompt)
        self.assertIn("serverless", requirements_prompt)
    
    def test_traditional_web_template_adaptation(self):
        """Test system adapts to traditional web application template"""
        web_template = """
        Use Django framework with Python
        Use PostgreSQL database with SQLAlchemy ORM
        Implement MVC architecture pattern
        Use Redis for caching and session management
        Deploy using Docker containers
        """
        
        description = "E-commerce platform"
        
        # Clear previous prompts
        self.captured_prompts.clear()
        
        # Generate design
        requirements = "Sample requirements"
        design = self.ai_service.create_design(requirements, None, web_template)
        
        # Check that template content is included in prompt
        design_prompt = self.captured_prompts[-1]["prompt"]
        self.assertIn("Django", design_prompt)
        self.assertIn("PostgreSQL", design_prompt)
        self.assertIn("Docker", design_prompt)
    
    def test_mobile_template_adaptation(self):
        """Test system adapts to mobile application template"""
        mobile_template = """
        Use React Native for cross-platform mobile development
        Use Firebase for backend services and real-time database
        Implement Redux for state management
        Use Expo for development and deployment
        Follow mobile-first design principles
        """
        
        description = "Social media mobile app"
        
        # Clear previous prompts
        self.captured_prompts.clear()
        
        # Generate tasks
        design = "Sample design document"
        requirements = "Sample requirements"
        tasks = self.spec_engine.create_task_list(design, requirements, mobile_template)
        
        # Check that template content is included in prompt
        tasks_prompt = self.captured_prompts[-1]["prompt"]
        self.assertIn("React Native", tasks_prompt)
        self.assertIn("Firebase", tasks_prompt)
        self.assertIn("Redux", tasks_prompt)
    
    def test_no_template_fallback(self):
        """Test system works without any template"""
        description = "Project management system"
        
        # Clear previous prompts
        self.captured_prompts.clear()
        
        # Generate requirements without template
        requirements = self.ai_service.generate_requirements(description, None, None)
        
        # Check that fallback message is included
        requirements_prompt = self.captured_prompts[-1]["prompt"]
        self.assertIn("No coding template provided", requirements_prompt)
        self.assertIn("technology-agnostic", requirements_prompt)
    
    def test_empty_template_handling(self):
        """Test system handles empty template gracefully"""
        description = "Inventory management system"
        empty_template = "   "  # Just whitespace
        
        # Clear previous prompts
        self.captured_prompts.clear()
        
        # Generate design with empty template
        requirements = "Sample requirements"
        design = self.ai_service.create_design(requirements, None, empty_template)
        
        # Check that fallback message is used
        design_prompt = self.captured_prompts[-1]["prompt"]
        self.assertIn("No coding template provided", design_prompt)
        self.assertIn("technology-agnostic", design_prompt)
    
    def test_different_architecture_patterns(self):
        """Test system adapts to different architectural patterns"""
        microservices_template = """
        Use microservices architecture with Docker containers
        Implement event-driven communication with Apache Kafka
        Use Spring Boot for Java microservices
        Use MongoDB for document storage
        """
        
        monolith_template = """
        Use monolithic architecture with Ruby on Rails
        Use PostgreSQL with Active Record ORM
        Implement MVC pattern with server-side rendering
        Use Sidekiq for background job processing
        """
        
        description = "Content management system"
        
        # Test microservices template
        self.captured_prompts.clear()
        requirements1 = self.ai_service.generate_requirements(description, None, microservices_template)
        microservices_prompt = self.captured_prompts[-1]["prompt"]
        
        # Test monolith template
        self.captured_prompts.clear()
        requirements2 = self.ai_service.generate_requirements(description, None, monolith_template)
        monolith_prompt = self.captured_prompts[-1]["prompt"]
        
        # Verify different templates produce different prompts
        self.assertIn("microservices", microservices_prompt)
        self.assertIn("Spring Boot", microservices_prompt)
        self.assertIn("Ruby on Rails", monolith_prompt)
        self.assertIn("monolithic", monolith_prompt)
        
        # Verify they don't contain each other's technologies
        self.assertNotIn("Ruby on Rails", microservices_prompt)
        self.assertNotIn("Spring Boot", monolith_prompt)
    
    def test_custom_technology_stack(self):
        """Test system adapts to completely custom technology stack"""
        custom_template = """
        Use Rust programming language with Actix-web framework
        Use CockroachDB for distributed database
        Implement hexagonal architecture pattern
        Use gRPC for service communication
        Deploy on Kubernetes with Helm charts
        Use Prometheus for monitoring and Grafana for visualization
        """
        
        description = "High-performance trading system"
        
        # Clear previous prompts
        self.captured_prompts.clear()
        
        # Generate design
        requirements = "Sample requirements"
        design = self.ai_service.create_design(requirements, None, custom_template)
        
        # Check that all custom technologies are included
        design_prompt = self.captured_prompts[-1]["prompt"]
        self.assertIn("Rust", design_prompt)
        self.assertIn("Actix-web", design_prompt)
        self.assertIn("CockroachDB", design_prompt)
        self.assertIn("hexagonal architecture", design_prompt)
        self.assertIn("gRPC", design_prompt)

if __name__ == '__main__':
    unittest.main()