import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from services.template_service import TemplateService, CodingTemplate, ValidationResult

class TestTemplateService(unittest.TestCase):
    """Unit tests for TemplateService"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.service = TemplateService()
        # Override templates directory for testing
        self.service.templates_dir = Path(self.test_dir) / "templates"
        self.service._ensure_templates_directory()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_coding_template_validation(self):
        """Test CodingTemplate validation"""
        # Valid template
        template = CodingTemplate(
            name="Test Template",
            content="Use TypeScript with strict mode. Follow clean architecture patterns. Write unit tests.",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        validation = template.validate()
        self.assertTrue(validation['is_valid'])
        self.assertGreater(validation['character_count'], 50)
        self.assertEqual(len(validation['issues']), 0)
        
        # Invalid template (too short)
        short_template = CodingTemplate(
            name="Short",
            content="Short",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        validation = short_template.validate()
        self.assertFalse(validation['is_valid'])
        self.assertGreater(len(validation['issues']), 0)
    
    def test_template_serialization(self):
        """Test template to_dict and from_dict methods"""
        template = CodingTemplate(
            name="Test Template",
            content="Test content for serialization",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Test serialization
        data = template.to_dict()
        self.assertIn('name', data)
        self.assertIn('content', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
        
        # Test deserialization
        restored_template = CodingTemplate.from_dict(data)
        self.assertEqual(template.name, restored_template.name)
        self.assertEqual(template.content, restored_template.content)
    
    def test_save_template(self):
        """Test saving templates"""
        # Valid template
        result = self.service.save_template(
            "Test Template",
            "Use TypeScript with strict mode. Follow clean architecture patterns. Write comprehensive unit tests."
        )
        self.assertTrue(result)
        
        # Invalid template (too short)
        result = self.service.save_template("Short", "Short")
        self.assertFalse(result)
        
        # Invalid name
        result = self.service.save_template("", "Valid content that is long enough for validation")
        self.assertFalse(result)
    
    def test_load_template(self):
        """Test loading templates"""
        content = "Use TypeScript with strict mode. Follow clean architecture patterns. Write comprehensive unit tests."
        
        # Save template first
        self.service.save_template("Test Template", content)
        
        # Load template
        loaded_content = self.service.load_template("Test Template")
        self.assertEqual(content, loaded_content)
        
        # Load non-existent template
        loaded_content = self.service.load_template("Non-existent")
        self.assertIsNone(loaded_content)
    
    def test_list_templates(self):
        """Test listing templates"""
        # Initially empty
        templates = self.service.list_templates()
        self.assertEqual(len(templates), 0)
        
        # Save some templates
        self.service.save_template("Template 1", "Content 1 with enough characters to pass validation requirements")
        self.service.save_template("Template 2", "Content 2 with enough characters to pass validation requirements")
        
        # List templates
        templates = self.service.list_templates()
        self.assertEqual(len(templates), 2)
        
        # Check template structure
        template = templates[0]
        self.assertIn('name', template)
        self.assertIn('content', template)
        self.assertIn('created_at', template)
        self.assertIn('updated_at', template)
    
    def test_delete_template(self):
        """Test deleting templates"""
        content = "Content with enough characters to pass validation requirements for testing"
        
        # Save template first
        self.service.save_template("Test Template", content)
        
        # Verify it exists
        templates = self.service.list_templates()
        self.assertEqual(len(templates), 1)
        
        # Delete template
        result = self.service.delete_template("Test Template")
        self.assertTrue(result)
        
        # Verify it's gone
        templates = self.service.list_templates()
        self.assertEqual(len(templates), 0)
        
        # Try to delete non-existent template
        result = self.service.delete_template("Non-existent")
        self.assertFalse(result)
    
    def test_validate_template(self):
        """Test template validation service method"""
        # Valid content
        validation = self.service.validate_template(
            "Use TypeScript with strict mode. Follow clean architecture patterns. Write comprehensive unit tests."
        )
        self.assertIsInstance(validation, ValidationResult)
        self.assertTrue(validation.is_valid)
        self.assertEqual(len(validation.issues), 0)
        
        # Invalid content (too short)
        validation = self.service.validate_template("Short")
        self.assertFalse(validation.is_valid)
        self.assertGreater(len(validation.issues), 0)
    
    def test_get_template_preview(self):
        """Test template preview generation"""
        content = "Use TypeScript with strict mode. Follow clean architecture patterns."
        
        preview = self.service.get_template_preview(content)
        self.assertIn("Template Integration Preview", preview)
        self.assertIn(content, preview)
        
        # Empty content
        preview = self.service.get_template_preview("")
        self.assertIn("No template content", preview)

if __name__ == '__main__':
    unittest.main()