#!/usr/bin/env python3
"""
Integration testing script for OpenFlux AI Assistant
Tests end-to-end workflows and component integration
"""

import unittest
import sys
import os
import time
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class TestApplicationIntegration(unittest.TestCase):
    """Integration tests for the complete application workflow"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        from services.credentials_manager import CredentialsManager
        from services.ai_service import AIService
        
        self.credentials_manager = CredentialsManager()
        self.ai_service = AIService(self.credentials_manager)
        
        # Test credentials
        self.test_access_key = "AKIAIOSFODNN7EXAMPLE"
        self.test_secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        self.test_region = "us-east-1"
    
    def tearDown(self):
        """Clean up after integration tests"""
        self.credentials_manager.clear_credentials()
    
    def test_credentials_to_ai_service_integration(self):
        """Test integration between credentials manager and AI service"""
        # Initially AI service should not have credentials
        session = self.ai_service.credentials_manager.get_aws_session()
        self.assertIsNone(session)
        
        # Store credentials
        success = self.credentials_manager.store_credentials(
            self.test_access_key,
            self.test_secret_key,
            self.test_region
        )
        self.assertTrue(success)
        
        # AI service should now have access to credentials
        session = self.ai_service.credentials_manager.get_aws_session()
        self.assertIsNotNone(session)
        
        # Verify session configuration
        self.assertEqual(session.region_name, self.test_region)
    
    @patch('boto3.Session')
    def test_full_ai_workflow_with_credentials(self, mock_session):
        """Test complete AI workflow with credential authentication"""
        # Mock AWS responses
        mock_bedrock_client = Mock()
        mock_bedrock_client.list_foundation_models.return_value = {
            'modelSummaries': [
                {'modelId': 'anthropic.claude-3-5-sonnet-20241022-v2:0'},
                {'modelId': 'amazon.nova-pro-v1:0'}
            ]
        }
        
        mock_runtime_client = Mock()
        mock_runtime_client.invoke_model.return_value = {
            'body': Mock(read=lambda: '{"content": [{"text": "Test response"}]}')
        }
        
        mock_session_instance = Mock()
        mock_session_instance.client.side_effect = lambda service, **kwargs: {
            'bedrock': mock_bedrock_client,
            'bedrock-runtime': mock_runtime_client
        }[service]
        mock_session_instance.region_name = self.test_region
        mock_session.return_value = mock_session_instance
        
        # Store credentials
        self.credentials_manager.store_credentials(
            self.test_access_key,
            self.test_secret_key,
            self.test_region
        )
        
        # Initialize Bedrock client
        success = self.ai_service.initialize_bedrock_client()
        self.assertTrue(success)
        
        # Select model
        success = self.ai_service.select_model("Claude Sonnet 3.5 v2")
        self.assertTrue(success)
        
        # Generate text
        response = self.ai_service.generate_text("Test prompt")
        self.assertEqual(response, "Test response")
    
    def test_credential_lifecycle_integration(self):
        """Test complete credential lifecycle with all components"""
        # Start with no credentials
        status = self.credentials_manager.get_credentials_status()
        self.assertFalse(status['has_credentials'])
        
        # Store credentials
        success = self.credentials_manager.store_credentials(
            self.test_access_key,
            self.test_secret_key,
            self.test_region
        )
        self.assertTrue(success)
        
        # Verify credentials are available
        status = self.credentials_manager.get_credentials_status()
        self.assertTrue(status['has_credentials'])
        self.assertTrue(status['validated'])
        
        # AI service should be able to use credentials
        session = self.ai_service.credentials_manager.get_aws_session()
        self.assertIsNotNone(session)
        
        # Clear credentials
        self.credentials_manager.clear_credentials()
        
        # Verify everything is cleared
        status = self.credentials_manager.get_credentials_status()
        self.assertFalse(status['has_credentials'])
        
        session = self.ai_service.credentials_manager.get_aws_session()
        self.assertIsNone(session)
    
    def test_error_handling_integration(self):
        """Test error handling across components"""
        # Test AI service without credentials
        with self.assertRaises(Exception):
            self.ai_service.generate_text("Test prompt")
        
        # Test with invalid credentials format
        errors = self.credentials_manager.validate_credential_format("invalid", "invalid")
        self.assertGreater(len(errors), 0)
        
        # Test AI service initialization without valid credentials
        success = self.ai_service.initialize_bedrock_client()
        self.assertFalse(success)
    
    def test_memory_cleanup_integration(self):
        """Test that memory is properly cleaned up across components"""
        # Store and clear credentials multiple times
        for i in range(10):
            self.credentials_manager.store_credentials(
                self.test_access_key,
                self.test_secret_key,
                self.test_region
            )
            
            # Verify storage
            status = self.credentials_manager.get_credentials_status()
            self.assertTrue(status['has_credentials'])
            
            # Clear
            self.credentials_manager.clear_credentials()
            
            # Verify cleanup
            status = self.credentials_manager.get_credentials_status()
            self.assertFalse(status['has_credentials'])
        
        # Final verification that everything is clean
        self.assertIsNone(self.credentials_manager._encrypted_credentials)
        self.assertIsNone(self.credentials_manager._session_key)
        self.assertIsNone(self.credentials_manager._aws_session)


class TestUIIntegration(unittest.TestCase):
    """Integration tests for UI components"""
    
    def setUp(self):
        """Set up UI integration test fixtures"""
        from services.credentials_manager import CredentialsManager
        from components.credentials_ui import CredentialsUI
        
        self.credentials_manager = CredentialsManager()
        self.credentials_ui = CredentialsUI(self.credentials_manager)
    
    def tearDown(self):
        """Clean up after UI integration tests"""
        self.credentials_manager.clear_credentials()
    
    def test_ui_credentials_manager_integration(self):
        """Test integration between UI and credentials manager"""
        # Test credentials validation through UI
        test_credentials = {
            'access_key': 'AKIAIOSFODNN7EXAMPLE',
            'secret_key': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
            'region': 'us-east-1',
            'action': 'connect'
        }
        
        # Mock the AWS connectivity test
        with patch.object(self.credentials_manager, 'test_aws_connectivity') as mock_test:
            mock_test.return_value = {
                'success': True,
                'message': 'Connection successful',
                'available_models': ['claude-3-5-sonnet', 'nova-pro']
            }
            
            # This would normally be called by Streamlit, but we can test the logic
            result = self.credentials_ui.validate_and_store_credentials(test_credentials)
            
            # Should succeed with mocked response
            self.assertTrue(result)
            
            # Verify credentials were stored
            status = self.credentials_manager.get_credentials_status()
            self.assertTrue(status['has_credentials'])


class TestStartupIntegration(unittest.TestCase):
    """Integration tests for application startup"""
    
    def test_startup_imports(self):
        """Test that all required modules can be imported"""
        try:
            # Test core service imports
            from services.credentials_manager import CredentialsManager
            from services.ai_service import AIService
            from components.credentials_ui import CredentialsUI, show_credentials_setup_page
            
            # Test that classes can be instantiated
            credentials_manager = CredentialsManager()
            ai_service = AIService(credentials_manager)
            credentials_ui = CredentialsUI(credentials_manager)
            
            self.assertIsNotNone(credentials_manager)
            self.assertIsNotNone(ai_service)
            self.assertIsNotNone(credentials_ui)
            
        except ImportError as e:
            self.fail(f"Failed to import required modules: {e}")
    
    def test_service_initialization_order(self):
        """Test that services initialize in the correct order"""
        from services.credentials_manager import CredentialsManager
        from services.ai_service import AIService
        
        # Credentials manager should initialize first
        credentials_manager = CredentialsManager()
        self.assertIsNotNone(credentials_manager)
        
        # AI service should initialize with credentials manager
        ai_service = AIService(credentials_manager)
        self.assertIsNotNone(ai_service)
        self.assertEqual(ai_service.credentials_manager, credentials_manager)
    
    def test_executable_environment_detection(self):
        """Test detection of executable vs script environment"""
        import sys
        
        # In normal testing, we're not frozen
        is_frozen = getattr(sys, 'frozen', False)
        self.assertFalse(is_frozen)
        
        # Test path handling for both environments
        from pathlib import Path
        
        if is_frozen:
            # Would use sys._MEIPASS in executable
            base_path = Path(sys._MEIPASS)
        else:
            # Use script directory
            base_path = Path(__file__).parent
        
        self.assertTrue(base_path.exists())


def run_integration_tests():
    """Run all integration tests"""
    print("🔗 Running Integration Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all integration test classes
    suite.addTests(loader.loadTestsFromTestCase(TestApplicationIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestUIIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestStartupIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All integration tests passed!")
        print("🔗 Component integration is working correctly")
        return True
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        print("🔧 Check component integration and dependencies")
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)