"""
AWS Credentials Management Service
Handles secure collection, validation, and storage of AWS credentials
"""
import boto3
import streamlit as st
from cryptography.fernet import Fernet
from botocore.exceptions import ClientError, NoCredentialsError
import logging
from typing import Optional, Dict, Tuple
import os
import base64

class CredentialsManager:
    """Manages AWS credentials securely with encryption and validation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._session_key = None
        self._encrypted_credentials = None
        self._aws_session = None
        
    def _generate_session_key(self) -> bytes:
        """Generate a session-specific encryption key"""
        if not self._session_key:
            self._session_key = Fernet.generate_key()
        return self._session_key
    
    def _encrypt_credentials(self, access_key: str, secret_key: str, region: str = "us-east-1") -> bytes:
        """Encrypt credentials using session key"""
        try:
            key = self._generate_session_key()
            fernet = Fernet(key)
            
            credentials_data = f"{access_key}|{secret_key}|{region}"
            encrypted_data = fernet.encrypt(credentials_data.encode())
            
            return encrypted_data
        except Exception as e:
            self.logger.error(f"Failed to encrypt credentials: {e}")
            raise Exception("Failed to encrypt credentials securely")
    
    def _decrypt_credentials(self) -> Tuple[str, str, str]:
        """Decrypt stored credentials"""
        try:
            if not self._encrypted_credentials or not self._session_key:
                raise Exception("No encrypted credentials available")
            
            fernet = Fernet(self._session_key)
            decrypted_data = fernet.decrypt(self._encrypted_credentials).decode()
            
            access_key, secret_key, region = decrypted_data.split('|')
            return access_key, secret_key, region
        except Exception as e:
            self.logger.error(f"Failed to decrypt credentials: {e}")
            raise Exception("Failed to decrypt credentials")
    
    def validate_credential_format(self, access_key: str, secret_key: str) -> Dict[str, str]:
        """Validate AWS credential format"""
        errors = {}
        
        # Validate Access Key format
        if not access_key:
            errors['access_key'] = "Access Key is required"
        elif len(access_key) != 20:
            errors['access_key'] = "Access Key must be exactly 20 characters"
        elif not access_key.isalnum():
            errors['access_key'] = "Access Key must contain only alphanumeric characters"
        elif not access_key.isupper():
            errors['access_key'] = "Access Key must be uppercase"
        
        # Validate Secret Key format
        if not secret_key:
            errors['secret_key'] = "Secret Access Key is required"
        elif len(secret_key) != 40:
            errors['secret_key'] = "Secret Access Key must be exactly 40 characters"
        
        return errors
    
    def test_aws_connectivity(self, access_key: str, secret_key: str, region: str = "us-east-1") -> Dict[str, any]:
        """Test AWS connectivity with provided credentials"""
        try:
            # Create a temporary session for testing
            session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            
            # Test with Bedrock control client
            bedrock_client = session.client('bedrock', region_name=region)
            
            # Try to list foundation models as a connectivity test
            try:
                response = bedrock_client.list_foundation_models()
                available_models = [model['modelId'] for model in response.get('modelSummaries', [])]
                
                return {
                    'success': True,
                    'message': 'Successfully connected to AWS Bedrock',
                    'available_models': available_models,
                    'region': region
                }
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'AccessDeniedException':
                    # Check if we can at least create the client (credentials are valid)
                    try:
                        # Try a simpler operation
                        sts_client = session.client('sts', region_name=region)
                        sts_client.get_caller_identity()
                        
                        return {
                            'success': True,
                            'message': 'Credentials are valid but may lack Bedrock permissions',
                            'warning': 'Limited Bedrock access - some features may not work',
                            'region': region
                        }
                    except ClientError:
                        return {
                            'success': False,
                            'message': 'Invalid AWS credentials or insufficient permissions',
                            'error': str(e)
                        }
                else:
                    return {
                        'success': False,
                        'message': f'AWS connection failed: {error_code}',
                        'error': str(e)
                    }
                    
        except NoCredentialsError:
            return {
                'success': False,
                'message': 'No valid AWS credentials provided',
                'error': 'Credentials not found or invalid format'
            }
        except Exception as e:
            self.logger.error(f"AWS connectivity test failed: {e}")
            return {
                'success': False,
                'message': 'Failed to test AWS connectivity',
                'error': str(e)
            }
    
    def store_credentials(self, access_key: str, secret_key: str, region: str = "us-east-1") -> bool:
        """Store credentials securely in memory"""
        try:
            # Validate format first
            format_errors = self.validate_credential_format(access_key, secret_key)
            if format_errors:
                raise Exception(f"Invalid credential format: {format_errors}")
            
            # Encrypt and store
            self._encrypted_credentials = self._encrypt_credentials(access_key, secret_key, region)
            
            # Create AWS session
            self._aws_session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            
            self.logger.info("Credentials stored successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store credentials: {e}")
            self.clear_credentials()
            return False
    
    def get_aws_session(self) -> Optional[boto3.Session]:
        """Get the configured AWS session"""
        return self._aws_session
    
    def get_credentials_status(self) -> Dict[str, any]:
        """Get current credentials status"""
        if self._aws_session and self._encrypted_credentials:
            try:
                access_key, secret_key, region = self._decrypt_credentials()
                return {
                    'has_credentials': True,
                    'region': region,
                    'access_key_preview': f"{access_key[:4]}...{access_key[-4:]}",
                    'validated': True
                }
            except:
                return {
                    'has_credentials': False,
                    'validated': False,
                    'error': 'Failed to decrypt stored credentials'
                }
        else:
            return {
                'has_credentials': False,
                'validated': False
            }
    
    def clear_credentials(self):
        """Securely clear all stored credentials"""
        try:
            # Clear encrypted data
            if self._encrypted_credentials:
                # Overwrite memory with zeros (best effort)
                self._encrypted_credentials = b'\x00' * len(self._encrypted_credentials)
                self._encrypted_credentials = None
            
            # Clear session key
            if self._session_key:
                self._session_key = b'\x00' * len(self._session_key)
                self._session_key = None
            
            # Clear AWS session
            self._aws_session = None
            
            self.logger.info("Credentials cleared successfully")
            
        except Exception as e:
            self.logger.error(f"Error clearing credentials: {e}")
    
    def __del__(self):
        """Ensure credentials are cleared when object is destroyed"""
        self.clear_credentials()