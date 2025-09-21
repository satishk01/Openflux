"""
AWS Credentials Input UI Components
Provides Streamlit interface for AWS credentials collection and validation
"""
import streamlit as st
from services.credentials_manager import CredentialsManager
from typing import Dict, Optional
import time

class CredentialsUI:
    """Manages the credentials input user interface"""
    
    def __init__(self, credentials_manager: CredentialsManager):
        self.credentials_manager = credentials_manager
    
    def show_welcome_screen(self):
        """Display welcome screen with setup instructions"""
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h1>🤖 Welcome to OpenFlux AI Assistant</h1>
            <h3>Portable Edition</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        ### 🚀 Getting Started
        
        To use OpenFlux AI Assistant, you'll need to provide your AWS credentials to access Bedrock AI models.
        
        **What you'll need:**
        - AWS Access Key ID (20 characters)
        - AWS Secret Access Key (40 characters)
        - AWS account with Bedrock access enabled
        
        **Supported AI Models:**
        - Claude Sonnet 3.5 v2
        - Amazon Nova Pro
        
        **Your credentials are:**
        - ✅ Encrypted in memory only
        - ✅ Never stored on disk
        - ✅ Cleared when you close the app
        - ✅ Used only for AWS API calls
        """)
        
        st.info("💡 **Tip:** Make sure your AWS account has access to Amazon Bedrock and the AI models you want to use.")
    
    def show_credentials_form(self) -> Optional[Dict[str, str]]:
        """Display credentials input form and return credentials if submitted"""
        st.markdown("### 🔐 AWS Credentials Setup")
        
        with st.form("aws_credentials_form"):
            st.markdown("Enter your AWS credentials to connect to Bedrock AI services:")
            
            # Access Key input
            access_key = st.text_input(
                "AWS Access Key ID",
                placeholder="AKIAIOSFODNN7EXAMPLE",
                help="Your 20-character AWS Access Key ID",
                max_chars=20
            )
            
            # Secret Key input
            secret_key = st.text_input(
                "AWS Secret Access Key",
                placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                type="password",
                help="Your 40-character AWS Secret Access Key",
                max_chars=40
            )
            
            # Region selection
            region = st.selectbox(
                "AWS Region",
                options=[
                    "us-east-1",
                    "us-west-2", 
                    "eu-west-1",
                    "ap-southeast-1",
                    "ap-northeast-1"
                ],
                index=0,
                help="Select the AWS region where you have Bedrock access"
            )
            
            # Form submission buttons
            col1, col2 = st.columns([1, 1])
            
            with col1:
                submit_button = st.form_submit_button(
                    "🔗 Connect to AWS",
                    type="primary",
                    use_container_width=True
                )
            
            with col2:
                test_button = st.form_submit_button(
                    "🧪 Test Connection",
                    use_container_width=True
                )
            
            if submit_button or test_button:
                if access_key and secret_key:
                    return {
                        'access_key': access_key.strip(),
                        'secret_key': secret_key.strip(),
                        'region': region,
                        'action': 'connect' if submit_button else 'test'
                    }
                else:
                    st.error("❌ Please enter both Access Key and Secret Access Key")
        
        return None
    
    def validate_and_store_credentials(self, credentials: Dict[str, str]) -> bool:
        """Validate credentials format and store if valid"""
        access_key = credentials['access_key']
        secret_key = credentials['secret_key']
        region = credentials['region']
        
        # Validate format
        format_errors = self.credentials_manager.validate_credential_format(access_key, secret_key)
        
        if format_errors:
            st.error("❌ **Credential Format Errors:**")
            for field, error in format_errors.items():
                st.error(f"• {error}")
            return False
        
        # Test connectivity
        with st.spinner("🔍 Testing AWS connection..."):
            connectivity_result = self.credentials_manager.test_aws_connectivity(
                access_key, secret_key, region
            )
        
        if connectivity_result['success']:
            # Store credentials
            if self.credentials_manager.store_credentials(access_key, secret_key, region):
                st.success("✅ **Successfully connected to AWS!**")
                
                if 'available_models' in connectivity_result:
                    st.info(f"🤖 **Available AI Models:** {len(connectivity_result['available_models'])} models found")
                
                if 'warning' in connectivity_result:
                    st.warning(f"⚠️ {connectivity_result['warning']}")
                
                time.sleep(1)  # Brief pause for user to see success message
                return True
            else:
                st.error("❌ Failed to store credentials securely")
                return False
        else:
            st.error(f"❌ **Connection Failed:** {connectivity_result['message']}")
            
            if 'error' in connectivity_result:
                with st.expander("🔍 Technical Details"):
                    st.code(connectivity_result['error'])
            
            # Provide helpful guidance
            st.markdown("""
            **Troubleshooting Tips:**
            - ✅ Verify your Access Key and Secret Key are correct
            - ✅ Ensure your AWS account has Bedrock access enabled
            - ✅ Check that you have permissions for the selected region
            - ✅ Confirm your AWS account is in good standing
            """)
            
            return False
    
    def test_credentials_only(self, credentials: Dict[str, str]):
        """Test credentials without storing them"""
        access_key = credentials['access_key']
        secret_key = credentials['secret_key']
        region = credentials['region']
        
        # Validate format first
        format_errors = self.credentials_manager.validate_credential_format(access_key, secret_key)
        
        if format_errors:
            st.error("❌ **Credential Format Errors:**")
            for field, error in format_errors.items():
                st.error(f"• {error}")
            return
        
        # Test connectivity
        with st.spinner("🧪 Testing connection (credentials will not be saved)..."):
            connectivity_result = self.credentials_manager.test_aws_connectivity(
                access_key, secret_key, region
            )
        
        if connectivity_result['success']:
            st.success("✅ **Connection test successful!**")
            st.info("🔗 Click 'Connect to AWS' to save credentials and continue")
            
            if 'available_models' in connectivity_result:
                st.success(f"🤖 **Found {len(connectivity_result['available_models'])} AI models**")
                
                with st.expander("📋 Available Models"):
                    for model in connectivity_result['available_models']:
                        st.write(f"• {model}")
            
            if 'warning' in connectivity_result:
                st.warning(f"⚠️ {connectivity_result['warning']}")
        else:
            st.error(f"❌ **Connection test failed:** {connectivity_result['message']}")
            
            if 'error' in connectivity_result:
                with st.expander("🔍 Technical Details"):
                    st.code(connectivity_result['error'])
    
    def show_credentials_status(self):
        """Display current credentials status"""
        status = self.credentials_manager.get_credentials_status()
        
        if status['has_credentials'] and status['validated']:
            st.sidebar.success("🔐 **AWS Connected**")
            st.sidebar.info(f"**Region:** {status['region']}")
            st.sidebar.info(f"**Access Key:** {status['access_key_preview']}")
            
            if st.sidebar.button("🔄 Change Credentials"):
                self.credentials_manager.clear_credentials()
                st.rerun()
        else:
            st.sidebar.warning("🔐 **AWS Not Connected**")
    
    def show_security_notice(self):
        """Display security and privacy notice"""
        with st.expander("🔒 Security & Privacy Information"):
            st.markdown("""
            **How we protect your credentials:**
            
            🔐 **Encryption:** Your credentials are encrypted using AES-256 encryption
            
            💾 **No Storage:** Credentials are never saved to disk or registry
            
            🧠 **Memory Only:** Credentials exist only in encrypted memory during your session
            
            🚪 **Auto-Clear:** All credential data is cleared when you close the application
            
            🌐 **Secure Transmission:** All AWS communications use HTTPS/TLS encryption
            
            📝 **No Logging:** Your actual credentials are never written to log files
            
            **What we use your credentials for:**
            - Connecting to AWS Bedrock AI services
            - Listing available AI models
            - Making AI generation requests
            - Nothing else - no data collection or external sharing
            """)

def show_credentials_setup_page(credentials_manager: CredentialsManager) -> bool:
    """Main credentials setup page - returns True if credentials are ready"""
    ui = CredentialsUI(credentials_manager)
    
    # Show welcome screen
    ui.show_welcome_screen()
    
    # Show security notice
    ui.show_security_notice()
    
    st.markdown("---")
    
    # Show credentials form
    credentials_input = ui.show_credentials_form()
    
    if credentials_input:
        if credentials_input['action'] == 'test':
            ui.test_credentials_only(credentials_input)
        elif credentials_input['action'] == 'connect':
            if ui.validate_and_store_credentials(credentials_input):
                st.balloons()
                st.success("🎉 **Ready to use OpenFlux AI Assistant!**")
                time.sleep(2)
                st.rerun()
    
    # Check if we already have valid credentials
    status = credentials_manager.get_credentials_status()
    return status['has_credentials'] and status['validated']