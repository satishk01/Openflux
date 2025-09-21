#!/usr/bin/env python3
"""
Test script for CredentialsManager functionality
Tests encryption, validation, and AWS connectivity
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from services.credentials_manager import CredentialsManager

class TestCredentialsManager(unittest.TestCase):
    """Test cases for CredentialsManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.credentials_manager = CredentialsManager()
        self.valid_access_key = "AKIAIOSFODNN7EXAMPLE"
        self.valid_secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        self.test_region = "us-east-1"
    
    def tearDown(self):
        """Clean up after tests"""
        self.credentials_manager.clear_credentials()
    
    def test_credential_format_validation_valid(self):
        """Test validation with valid credentials"""
        errors = self.credentials_manager.validate_credential_format(
            self.valid_access_key, 
            self.valid_secret_key
        )
        self.assertEqual(len(errors), 0, "Valid credentials should not have errors")
    
    def test_credential_format_validation_invalid_access_key(self):
        """Test validation with invalid access key"""
        # Test short access key
        errors = self.credentials_manager.validate_credential_format(
            "SHORT", 
            self.valid_secret_key
        )
        self.assertIn('access_key', errors)
        
        # Test lowercase access key
        errors = self.credentials_manager.validate_credential_format(
            "akiaiosfodnn7example", 
            self.valid_secret_key
        )
        self.assertIn('access_key', errors)
        
        # Test non-alphanumeric access key
        errors = self.credentials_manager.validate_credential_format(
            "AKIA-IOSF-ODNN7EXAMPLE", 
            self.valid_secret_key
        )
        self.assertIn('access_key', errors)
    
    def test_credential_format_validation_invalid_secret_key(self):
        """Test validation with invalid secret key"""
        # Test short secret key
        errors = self.credentials_manager.validate_credential_format(
            self.valid_access_key, 
            "SHORT"
        )
        self.assertIn('secret_key', errors)
        
        # Test empty secret key
        errors = self.credentials_manager.validate_credential_format(
            self.valid_access_key, 
            ""
        )
        self.assertIn('secret_key', errors)
    
    def test_encryption_decryption(self):
        """Test credential encryption and decryption"""
        # Store credentials
        success = self.credentials_manager.store_credentials(
            self.valid_access_key,
            self.valid_secret_key,
            self.test_region
        )
        self.assertTrue(success, "Credential storage should succeed")
        
        # Check that credentials are encrypted
        self.assertIsNotNone(self.credentials_manager._encrypted_credentials)
        self.assertIsNotNone(self.credentials_manager._session_key)
        
        # Check that we can get status
        status = self.credentials_manager.get_credentials_status()
        self.assertTrue(status['has_credentials'])
        self.assertTrue(status['validated'])
        self.assertEqual(status['region'], self.test_region)
        
        # Check access key preview
        expected_preview = f"{self.valid_access_key[:4]}...{self.valid_access_key[-4:]}"
        self.assertEqual(status['access_key_preview'], expected_preview)
    
    def test_credential_clearing(self):
        """Test secure credential clearing"""
        # Store credentials first
        self.credentials_manager.store_credentials(
            self.valid_access_key,
            self.valid_secret_key,
            self.test_region
        )
        
        # Verify they're stored
        status = self.credentials_manager.get_credentials_status()
        self.assertTrue(status['has_credentials'])
        
        # Clear credentials
        self.credentials_manager.clear_credentials()
        
        # Verify they're cleared
        status = self.credentials_manager.get_credentials_status()
        self.assertFalse(status['has_credentials'])
        self.assertFalse(status['validated'])
        
        # Check internal state is cleared
        self.assertIsNone(self.credentials_manager._encrypted_credentials)
        self.assertIsNone(self.credentials_manager._session_key)
        self.assertIsNone(self.credentials_manager._aws_session)
    
    @patch('boto3.Session')
    def test_aws_connectivity_success(self, mock_session):
        """Test successful AWS connectivity"""
        # Mock successful AWS response
        mock_bedrock_client = Mock()
        mock_bedrock_client.list_foundation_models.return_value = {
            'modelSummaries': [
                {'modelId': 'anthropic.claude-3-5-sonnet-20241022-v2:0'},
                {'modelId': 'amazon.nova-pro-v1:0'}
            ]
        }
        
        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_bedrock_client
        mock_session.return_value = mock_session_instance
        
        # Test connectivity
        result = self.credentials_manager.test_aws_connectivity(
            self.valid_access_key,
            self.valid_secret_key,
            self.test_region
        )
        
        self.assertTrue(result['success'])
        self.assertIn('available_models', result)
        self.assertEqual(len(result['available_models']), 2)
    
    @patch('boto3.Session')
    def test_aws_connectivity_access_denied(self, mock_session):
        """Test AWS connectivity with access denied"""
        from botocore.exceptions import ClientError
        
        # Mock access denied error for Bedrock, but successful STS
        mock_bedrock_client = Mock()
        mock_bedrock_client.list_foundation_models.side_effect = ClientError(
            error_response={'Error': {'Code': 'AccessDeniedException'}},
            operation_name='ListFoundationModels'
        )
        
        mock_sts_client = Mock()
        mock_sts_client.get_caller_identity.return_value = {'Account': '123456789012'}
        
        mock_session_instance = Mock()
        mock_session_instance.client.side_effect = lambda service, **kwargs: {
            'bedrock': mock_bedrock_client,
            'sts': mock_sts_client
        }[service]
        mock_session.return_value = mock_session_instance
        
        # Test connectivity
        result = self.credentials_manager.test_aws_connectivity(
            self.valid_access_key,
            self.valid_secret_key,
            self.test_region
        )
        
        self.assertTrue(result['success'])
        self.assertIn('warning', result)
    
    @patch('boto3.Session')
    def test_aws_connectivity_invalid_credentials(self, mock_session):
        """Test AWS connectivity with invalid credentials"""
        from botocore.exceptions import ClientError
        
        # Mock invalid credentials error
        mock_bedrock_client = Mock()
        mock_bedrock_client.list_foundation_models.side_effect = ClientError(
            error_response={'Error': {'Code': 'InvalidUserID.NotFound'}},
            operation_name='ListFoundationModels'
        )
        
        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_bedrock_client
        mock_session.return_value = mock_session_instance
        
        # Test connectivity
        result = self.credentials_manager.test_aws_connectivity(
            "INVALID_ACCESS_KEY123",
            "invalid_secret_key_123456789012345678901234",
            self.test_region
        )
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_get_aws_session(self):
        """Test getting AWS session"""
        # Initially no session
        session = self.credentials_manager.get_aws_session()
        self.assertIsNone(session)
        
        # Store credentials
        self.credentials_manager.store_credentials(
            self.valid_access_key,
            self.valid_secret_key,
            self.test_region
        )
        
        # Now should have session
        session = self.credentials_manager.get_aws_session()
        self.assertIsNotNone(session)
    
    def test_memory_security(self):
        """Test that credentials are properly secured in memory"""
        # Store credentials
        self.credentials_manager.store_credentials(
            self.valid_access_key,
            self.valid_secret_key,
            self.test_region
        )
        
        # Check that raw credentials are not stored in plain text
        # This is a basic check - in reality, we'd need more sophisticated testing
        encrypted_data = self.credentials_manager._encrypted_credentials
        self.assertIsInstance(encrypted_data, bytes)
        
        # Verify that the encrypted data doesn't contain plain text credentials
        self.assertNotIn(self.valid_access_key.encode(), encrypted_data)
        self.assertNotIn(self.valid_secret_key.encode(), encrypted_data)


class TestCredentialsManagerIntegration(unittest.TestCase):
    """Integration tests for CredentialsManager with real AWS (if credentials available)"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.credentials_manager = CredentialsManager()
        
        # Check if real AWS credentials are available for integration testing
        self.real_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        self.real_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.real_region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        
        self.has_real_credentials = bool(self.real_access_key and self.real_secret_key)
    
    def tearDown(self):
        """Clean up after integration tests"""
        self.credentials_manager.clear_credentials()
    
    def test_real_aws_connectivity(self):
        """Test connectivity with real AWS credentials (if available)"""
        if not self.has_real_credentials:
            self.skipTest("No real AWS credentials available for integration testing")
        
        # Test with real credentials
        result = self.credentials_manager.test_aws_connectivity(
            self.real_access_key,
            self.real_secret_key,
            self.real_region
        )
        
        # Should succeed or fail gracefully
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        self.assertIn('message', result)
        
        if result['success']:
            print(f"✅ Real AWS connectivity test passed: {result['message']}")
            if 'available_models' in result:
                print(f"📋 Available models: {len(result['available_models'])}")
        else:
            print(f"⚠️ Real AWS connectivity test failed: {result['message']}")


def run_tests():
    """Run all tests and return results"""
    print("🧪 Running CredentialsManager Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add unit tests
    suite.addTests(loader.loadTestsFromTestCase(TestCredentialsManager))
    
    # Add integration tests if credentials available
    if os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'):
        print("🔗 Real AWS credentials detected - including integration tests")
        suite.addTests(loader.loadTestsFromTestCase(TestCredentialsManagerIntegration))
    else:
        print("ℹ️ No real AWS credentials - skipping integration tests")
        print("   Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to run integration tests")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
        return True
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)