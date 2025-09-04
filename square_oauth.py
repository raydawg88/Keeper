#!/usr/bin/env python3
"""
Square OAuth Integration for Keeper
Handles business account connection and token management
"""
import os
import json
import uuid
import hashlib
import urllib.parse
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
import requests

# Load environment variables
load_dotenv()

class SquareOAuthManager:
    """Handles Square OAuth flow for business account connection"""
    
    def __init__(self):
        self.client_id = os.getenv('SQUARE_APPLICATION_ID')
        self.client_secret = os.getenv('SQUARE_CLIENT_SECRET')  # We'll need this for production
        self.environment = 'sandbox'  # Change to 'production' when ready
        
        # Supabase setup
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # OAuth endpoints
        if self.environment == 'sandbox':
            self.oauth_base_url = 'https://connect.squareupsandbox.com'
        else:
            self.oauth_base_url = 'https://connect.squareup.com'
    
    def generate_oauth_url(self, redirect_uri, business_name=None):
        """
        Generate Square OAuth authorization URL
        
        Args:
            redirect_uri: Where Square should redirect after authorization
            business_name: Optional business name for tracking
            
        Returns:
            dict: Contains auth_url and state for verification
        """
        # Generate secure state parameter
        state = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:32]
        
        # Store state in database for verification
        session_data = {
            'id': str(uuid.uuid4()),
            'state': state,
            'redirect_uri': redirect_uri,
            'business_name': business_name,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(minutes=10)).isoformat(),
            'status': 'pending'
        }
        
        # Store OAuth session
        try:
            result = self.supabase.table('oauth_sessions').insert(session_data).execute()
            print(f"✅ OAuth session created: {result.data[0]['id']}")
        except Exception as e:
            print(f"❌ Failed to store OAuth session: {e}")
            return None
        
        # Build authorization URL
        params = {
            'client_id': self.client_id,
            'scope': 'CUSTOMERS_READ CUSTOMERS_WRITE PAYMENTS_READ ITEMS_READ',
            'session': 'false',
            'state': state
        }
        
        auth_url = f"{self.oauth_base_url}/oauth2/authorize?" + urllib.parse.urlencode(params)
        
        return {
            'auth_url': auth_url,
            'state': state,
            'session_id': session_data['id']
        }
    
    def handle_oauth_callback(self, authorization_code, state):
        """
        Handle OAuth callback and exchange code for access token
        
        Args:
            authorization_code: Code from Square OAuth callback
            state: State parameter for verification
            
        Returns:
            dict: Account information if successful, None if failed
        """
        # Verify state parameter
        try:
            session_result = self.supabase.table('oauth_sessions')\
                .select("*")\
                .eq('state', state)\
                .eq('status', 'pending')\
                .execute()
            
            if not session_result.data:
                print("❌ Invalid or expired OAuth state")
                return None
                
            session = session_result.data[0]
            
            # Check if session expired
            expires_at = datetime.fromisoformat(session['expires_at'].replace('Z', '+00:00'))
            if datetime.utcnow().replace(tzinfo=expires_at.tzinfo) > expires_at:
                print("❌ OAuth session expired")
                return None
                
        except Exception as e:
            print(f"❌ OAuth state verification failed: {e}")
            return None
        
        # Exchange authorization code for access token
        token_url = f"{self.oauth_base_url}/oauth2/token"
        token_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': authorization_code,
            'grant_type': 'authorization_code'
        }
        
        try:
            response = requests.post(token_url, json=token_data)
            response.raise_for_status()
            token_response = response.json()
            
            print("✅ Access token obtained successfully")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Token exchange failed: {e}")
            # Update session status
            self.supabase.table('oauth_sessions')\
                .update({'status': 'failed', 'error': str(e)})\
                .eq('id', session['id'])\
                .execute()
            return None
        
        # Get merchant information
        access_token = token_response['access_token']
        merchant_info = self.get_merchant_info(access_token)
        
        if not merchant_info:
            print("❌ Failed to get merchant information")
            return None
        
        # Create account in database
        account_data = {
            'id': str(uuid.uuid4()),
            'business_name': merchant_info['business_name'],
            'square_merchant_id': merchant_info['merchant_id'],
            'square_access_token': access_token,  # TODO: Encrypt this in production
            'refresh_token': token_response.get('refresh_token'),
            'token_expires_at': token_response.get('expires_at'),
            'square_locations': json.dumps(merchant_info['locations']),
            'subscription_status': 'trial',
            'created_at': datetime.utcnow().isoformat(),
            'last_sync_at': None
        }
        
        try:
            result = self.supabase.table('accounts').insert(account_data).execute()
            account = result.data[0]
            
            # Update OAuth session status
            self.supabase.table('oauth_sessions')\
                .update({
                    'status': 'completed', 
                    'account_id': account['id'],
                    'completed_at': datetime.utcnow().isoformat()
                })\
                .eq('id', session['id'])\
                .execute()
            
            print(f"✅ Account created successfully: {account['business_name']}")
            print(f"   Account ID: {account['id']}")
            print(f"   Merchant ID: {merchant_info['merchant_id']}")
            print(f"   Locations: {len(merchant_info['locations'])}")
            
            return {
                'account_id': account['id'],
                'business_name': account['business_name'],
                'merchant_id': merchant_info['merchant_id'],
                'locations': merchant_info['locations']
            }
            
        except Exception as e:
            print(f"❌ Failed to create account: {e}")
            return None
    
    def get_merchant_info(self, access_token):
        """
        Get merchant and location information from Square
        
        Args:
            access_token: Square access token
            
        Returns:
            dict: Merchant information or None if failed
        """
        if self.environment == 'sandbox':
            base_url = 'https://connect.squareupsandbox.com'
        else:
            base_url = 'https://connect.squareup.com'
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Square-Version': '2023-10-18'
        }
        
        try:
            # Get merchant info
            merchant_response = requests.get(f"{base_url}/v2/merchants", headers=headers)
            merchant_response.raise_for_status()
            merchant_data = merchant_response.json()
            
            if not merchant_data.get('merchants'):
                print("❌ No merchant data found")
                return None
            
            merchant = merchant_data['merchants'][0]
            
            # Get locations
            locations_response = requests.get(f"{base_url}/v2/locations", headers=headers)
            locations_response.raise_for_status()
            locations_data = locations_response.json()
            
            return {
                'merchant_id': merchant['id'],
                'business_name': merchant.get('business_name', 'Unknown Business'),
                'locations': locations_data.get('locations', [])
            }
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get merchant info: {e}")
            return None
    
    def refresh_access_token(self, account_id):
        """
        Refresh Square access token when it expires
        
        Args:
            account_id: Account ID in our database
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get account info
            account_result = self.supabase.table('accounts')\
                .select("refresh_token")\
                .eq('id', account_id)\
                .execute()
            
            if not account_result.data:
                print("❌ Account not found")
                return False
            
            refresh_token = account_result.data[0]['refresh_token']
            
            if not refresh_token:
                print("❌ No refresh token available")
                return False
            
            # Refresh token
            token_url = f"{self.oauth_base_url}/oauth2/token"
            token_data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
            
            response = requests.post(token_url, json=token_data)
            response.raise_for_status()
            token_response = response.json()
            
            # Update account with new token
            self.supabase.table('accounts')\
                .update({
                    'square_access_token': token_response['access_token'],
                    'refresh_token': token_response.get('refresh_token', refresh_token),
                    'token_expires_at': token_response.get('expires_at'),
                    'updated_at': datetime.utcnow().isoformat()
                })\
                .eq('id', account_id)\
                .execute()
            
            print("✅ Access token refreshed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Token refresh failed: {e}")
            return False

def test_oauth_flow():
    """Test the OAuth flow with a sample redirect URI"""
    oauth_manager = SquareOAuthManager()
    
    print("🔐 Testing Square OAuth Flow")
    print("=" * 40)
    
    # Generate OAuth URL
    redirect_uri = "https://keeper.tools/auth/callback"  # Our future callback URL
    business_name = "Ray's Wife's Spa"  # Test with known business
    
    oauth_result = oauth_manager.generate_oauth_url(redirect_uri, business_name)
    
    if oauth_result:
        print(f"✅ OAuth URL generated successfully")
        print(f"🔗 Authorization URL: {oauth_result['auth_url']}")
        print(f"🔐 State: {oauth_result['state']}")
        print(f"📋 Session ID: {oauth_result['session_id']}")
        print("\n📝 Next steps:")
        print("1. Visit the authorization URL in browser")
        print("2. Authorize the application")
        print("3. Copy the authorization code from callback")
        print("4. Use handle_oauth_callback() with the code and state")
        return oauth_result
    else:
        print("❌ Failed to generate OAuth URL")
        return None

if __name__ == "__main__":
    # Test OAuth URL generation
    test_oauth_flow()