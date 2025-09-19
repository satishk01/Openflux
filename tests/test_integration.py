import unittest
import tempfile
import shutil
from pathlib import Path
from services.template_service import TemplateService
from services.ai_service import AIService
from engines.spec_engine import SpecEngine

class TestTemplateIntegration(unittest.TestCase):
    """Integration tests for template functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.template_service = TemplateService()
        self.template_service.templates_dir = Path(self.test_dir) / "templates"
        self.template_service._ensure_templates_directory()
        
        self.ai_service = AIService()
        self.spec_engine = SpecEngine(self.ai_service)
        
        # Mock AI service to avoid actual API calls
        self.ai_service.generate_text = lambda prompt, system_prompt: f"AI Response for: {prompt[:100]}..."
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_end_to_end_template_workflow(self):
        """Test complete template workflow from creation to spec generation"""
        # 1. Create and save a template
        template_content = """
        Use TypeScript with strict mode enabled
        Follow clean architecture patterns with separate layers
        Implement repository pattern for data access
        Use dependency injection for service management
        Write comprehensive unit tests using Jest framework
        """
        
        result = self.template_service.save_template("Test Template", template_content)
        self.assertTrue(result)
        
        # 2. Load the template
        loaded_content = self.template_service.load_template("Test Template")
        self.assertEqual(template_content.strip(), loaded_content.strip())
        
        # 3. Use template in requirements generation
        feature_description = "User authentication system with login and registration"
        
        requirements = self.spec_engine.create_requirements(
            feature_description, 
            None, 
            template_content
        )
        
        # Verify template influence
        self.assertIsInstance(requirements, str)
        self.assertGreater(len(requirements), 0)
        
        # 4. Use template in design generation
        design = self.spec_engine.generate_design(
            requirements,
            None,
            template_content
        )
        
        self.assertIsInstance(design, str)
        self.assertGreater(len(design), 0)
        
        # 5. Use template in task generation
        tasks = self.spec_engine.create_task_list(
            design,
            requirements,
            template_content
        )
        
        self.assertIsInstance(tasks, str)
        self.assertGreater(len(tasks), 0)
    
    def test_template_management_workflow(self):
        """Test template CRUD operations workflow"""
        template_content = "Test template content with sufficient length for validation"
        
        # Create
        result = self.template_service.save_template("CRUD Test", template_content)
        self.assertTrue(result)
        
        # Read
        templates = self.template_service.list_templates()
        self.assertEqual(len(templates), 1)
        self.assertEqual(templates[0]['name'], "CRUD Test")
        
        loaded = self.template_service.load_template("CRUD Test")
        self.assertEqual(loaded, template_content)
        
        # Update (save with same name)
        updated_content = "Updated template content with sufficient length for validation"
        result = self.template_service.save_template("CRUD Test", updated_content)
        self.assertTrue(result)
        
        loaded = self.template_service.load_template("CRUD Test")
        self.assertEqual(loaded, updated_content)
        
        # Delete
        result = self.template_service.delete_template("CRUD Test")
        self.assertTrue(result)
        
        templates = self.template_service.list_templates()
        self.assertEqual(len(templates), 0)
    
    def test_template_validation_workflow(self):
        """Test template validation in workflow context"""
        # Valid template
        valid_template = "Use TypeScript with strict mode. Follow clean architecture patterns. Write comprehensive tests."
        validation = self.template_service.validate_template(valid_template)
        
        self.assertTrue(validation.is_valid)
        self.assertEqual(len(validation.issues), 0)
        self.assertGreater(validation.score, 60)
        
        # Invalid template
        invalid_template = "Short"
        validation = self.template_service.validate_template(invalid_template)
        
        self.assertFalse(validation.is_valid)
        self.assertGreater(len(validation.issues), 0)
        self.assertLess(validation.score, 60)
    
    def test_template_preview_functionality(self):
        """Test template preview generation"""
        template_content = "Use TypeScript with strict mode. Follow clean architecture patterns."
        
        preview = self.template_service.get_template_preview(template_content)
        
        self.assertIn("Template Integration Preview", preview)
        self.assertIn(template_content, preview)
        self.assertIn("Requirements generation", preview)
        self.assertIn("Design document creation", preview)
        self.assertIn("Implementation tasks", preview)
    
    def test_error_handling_workflow(self):
        """Test error handling in various scenarios"""
        # Invalid template name
        result = self.template_service.save_template("", "Valid content")
        self.assertFalse(result)
        
        # Invalid template content
        result = self.template_service.save_template("Valid Name", "")
        self.assertFalse(result)
        
        # Load non-existent template
        content = self.template_service.load_template("Non-existent")
        self.assertIsNone(content)
        
        # Delete non-existent template
        result = self.template_service.delete_template("Non-existent")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()