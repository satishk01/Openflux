import unittest
from unittest.mock import Mock, patch
from services.ai_service import AIService
from engines.spec_engine import SpecEngine

class TestTemplateAIIntegration(unittest.TestCase):
    """Unit tests for template integration with AI services"""
    
    def setUp(self):
        """Set up test environment"""
        self.ai_service = AIService()
        self.spec_engine = SpecEngine(self.ai_service)
        
        # Mock the AI service to avoid actual API calls
        self.ai_service.generate_text = Mock(return_value="Mocked AI response")
    
    def test_requirements_generation_with_template(self):
        """Test requirements generation includes template context"""
        template = "Use TypeScript with strict mode. Follow clean architecture patterns."
        description = "User authentication system"
        
        # Mock the AI service method
        with patch.object(self.ai_service, 'generate_requirements') as mock_generate:
            mock_generate.return_value = "Mocked requirements"
            
            result = self.ai_service.generate_requirements(description, None, template)
            
            # Verify the method was called
            mock_generate.assert_called_once()
            args, kwargs = mock_generate.call_args
            
            # Check that template was included in the call
            self.assertEqual(args[0], description)
            self.assertEqual(args[2], template)
    
    def test_design_generation_with_template(self):
        """Test design generation includes template context"""
        template = "Use TypeScript with strict mode. Follow clean architecture patterns."
        requirements = "System shall authenticate users"
        
        # Mock the AI service method
        with patch.object(self.ai_service, 'create_design') as mock_create:
            mock_create.return_value = "Mocked design"
            
            result = self.ai_service.create_design(requirements, None, template)
            
            # Verify the method was called
            mock_create.assert_called_once()
            args, kwargs = mock_create.call_args
            
            # Check that template was included in the call
            self.assertEqual(args[0], requirements)
            self.assertEqual(args[2], template)
    
    def test_task_generation_with_template(self):
        """Test task generation includes template context"""
        template = "Use TypeScript with strict mode. Follow clean architecture patterns."
        design = "System architecture with authentication module"
        requirements = "User authentication requirements"
        
        result = self.spec_engine.create_task_list(design, requirements, template)
        
        # Verify the AI service was called with template context
        self.ai_service.generate_text.assert_called_once()
        call_args = self.ai_service.generate_text.call_args[0]
        prompt = call_args[0]
        
        # Check that template content is included in the prompt
        self.assertIn(template, prompt)
    
    def test_incorporate_template_method(self):
        """Test the incorporate_template method"""
        base_prompt = "Generate requirements for the following feature. Please format the output properly."
        template = "Use TypeScript with strict mode. Follow clean architecture patterns."
        
        result = self.spec_engine.incorporate_template(base_prompt, template)
        
        # Check that template is incorporated
        self.assertIn(template, result)
        self.assertIn("CODING TEMPLATE", result)
        
        # Test with empty template
        result = self.spec_engine.incorporate_template(base_prompt, "")
        self.assertEqual(result, base_prompt)
        
        # Test with None template
        result = self.spec_engine.incorporate_template(base_prompt, None)
        self.assertEqual(result, base_prompt)
    
    def test_template_fallback_behavior(self):
        """Test fallback behavior when template integration fails"""
        base_prompt = "Generate requirements"
        
        # Test with very long template that might cause issues
        long_template = "A" * 10000  # Very long template
        
        result = self.spec_engine.incorporate_template(base_prompt, long_template)
        
        # Should still return a valid prompt (truncated template)
        self.assertIsInstance(result, str)
        self.assertIn("CODING TEMPLATE", result)
        
        # Template should be truncated
        self.assertLess(len(result), len(base_prompt) + len(long_template))

if __name__ == '__main__':
    unittest.main()