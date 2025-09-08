#!/usr/bin/env python3
"""
TEST SQUARE OAUTH FLOW - Connect Ray's Real Bashful Beauty Account
Fix the product by testing OAuth with actual business account
"""

import os
import requests
import json
from dotenv import load_dotenv
from urllib.parse import urlencode
import uuid

load_dotenv()

class SquareOAuthTest:
    def __init__(self):
        self.client_id = os.getenv('SQUARE_APPLICATION_ID')
        self.client_secret = os.getenv('SQUARE_CLIENT_SECRET')
        self.environment = 'production'  # Using production for real Bashful Beauty
        self.oauth_base_url = 'https://connect.squareup.com'
        self.api_base_url = 'https://connect.squareup.com'
        
        print(f"🔧 SQUARE OAUTH TEST INITIALIZED")
        print(f"   Client ID: {self.client_id}")
        print(f"   Environment: {self.environment}")
        print(f"   OAuth URL: {self.oauth_base_url}")
        
    def step1_generate_auth_url(self):
        """STEP 1: Generate OAuth authorization URL for Bashful Beauty"""
        print(f"\n🚀 STEP 1: GENERATING OAUTH URL")
        print("=" * 60)
        
        # Generate secure state parameter
        state = str(uuid.uuid4())
        
        # Required scopes for Keeper (READ ONLY)
        scopes = [
            'CUSTOMERS_READ',
            'PAYMENTS_READ',
            'ORDERS_READ', 
            'APPOINTMENTS_READ',
            'APPOINTMENTS_ALL_READ',
            'ITEMS_READ',
            'EMPLOYEES_READ',
            'MERCHANT_PROFILE_READ'
        ]
        
        # OAuth parameters
        params = {
            'client_id': self.client_id,
            'scope': ' '.join(scopes),
            'state': state,
            'response_type': 'code'
        }
        
        auth_url = f"{self.oauth_base_url}/oauth2/authorize?" + urlencode(params)
        
        print(f"✅ OAuth URL Generated Successfully!")
        print(f"📋 State: {state}")
        print(f"🔒 Scopes: {', '.join(scopes)}")
        print(f"\n🌐 AUTHORIZATION URL:")
        print("=" * 80)
        print(auth_url)
        print("=" * 80)
        
        print(f"\n📝 NEXT STEPS:")
        print(f"1. Copy the URL above")
        print(f"2. Open in browser")
        print(f"3. Log in to your Bashful Beauty Square account")
        print(f"4. Authorize Keeper to read your data")
        print(f"5. You'll get redirected with an authorization code")
        print(f"6. Bring that code back here for Step 2")
        
        return auth_url, state
    
    def step2_exchange_code_for_token(self, authorization_code, state):
        """STEP 2: Exchange authorization code for access token"""
        print(f"\n🔄 STEP 2: EXCHANGING CODE FOR TOKEN")
        print("=" * 60)
        
        print(f"📥 Authorization Code: {authorization_code[:20]}...")
        print(f"🔒 State: {state}")
        
        # Token exchange request
        token_url = f"{self.api_base_url}/oauth2/token"
        token_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': authorization_code,
            'grant_type': 'authorization_code'
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Square-Version': '2025-08-20'
        }
        
        print(f"🌐 Making token exchange request to: {token_url}")
        
        try:
            response = requests.post(token_url, json=token_data, headers=headers)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                token_result = response.json()
                access_token = token_result.get('access_token')
                
                print(f"✅ TOKEN EXCHANGE SUCCESS!")
                print(f"🔑 Access Token: {access_token[:20]}...")
                print(f"⏰ Expires: {token_result.get('expires_at', 'Never')}")
                
                # Save token for next steps
                with open('/tmp/square_token.json', 'w') as f:
                    json.dump(token_result, f, indent=2)
                
                print(f"💾 Token saved to /tmp/square_token.json")
                return access_token
                
            else:
                error_body = response.text
                print(f"❌ TOKEN EXCHANGE FAILED!")
                print(f"Status: {response.status_code}")
                print(f"Error: {error_body}")
                return None
                
        except Exception as e:
            print(f"❌ TOKEN EXCHANGE ERROR: {e}")
            return None
    
    def step3_test_api_call(self, access_token):
        """STEP 3: Test Square API call with token"""
        print(f"\n🧪 STEP 3: TESTING SQUARE API CALL")
        print("=" * 60)
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Square-Version': '2025-08-20',
            'Content-Type': 'application/json'
        }
        
        # Test with merchants endpoint (basic info)
        test_url = f"{self.api_base_url}/v2/merchants"
        
        print(f"🌐 Testing API call: {test_url}")
        
        try:
            response = requests.get(test_url, headers=headers)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                merchants = response.json()
                
                print(f"✅ API CALL SUCCESS!")
                print(f"📋 Response:")
                print(json.dumps(merchants, indent=2))
                
                return merchants
            else:
                print(f"❌ API CALL FAILED!")
                print(f"Status: {response.status_code}")
                print(f"Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ API CALL ERROR: {e}")
            return None
    
    def step4_get_customers(self, access_token, limit=10):
        """STEP 4: Get actual customers from Bashful Beauty"""
        print(f"\n👥 STEP 4: GETTING REAL CUSTOMERS")
        print("=" * 60)
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Square-Version': '2025-08-20',
            'Content-Type': 'application/json'
        }
        
        # Get customers with limit
        customers_url = f"{self.api_base_url}/v2/customers?limit={limit}"
        
        print(f"🌐 Getting customers: {customers_url}")
        
        try:
            response = requests.get(customers_url, headers=headers)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                customers_data = response.json()
                customers = customers_data.get('customers', [])
                
                print(f"✅ CUSTOMERS RETRIEVED!")
                print(f"📈 Found {len(customers)} customers")
                
                if customers:
                    print(f"\n📋 SAMPLE CUSTOMER:")
                    sample = customers[0]
                    print(f"   ID: {sample.get('id')}")
                    print(f"   Name: {sample.get('given_name', '')} {sample.get('family_name', '')}")
                    print(f"   Email: {sample.get('email_address', 'N/A')}")
                    print(f"   Phone: {sample.get('phone_number', 'N/A')}")
                    print(f"   Created: {sample.get('created_at', 'N/A')}")
                
                # Save customers for database test
                with open('/tmp/square_customers.json', 'w') as f:
                    json.dump(customers_data, f, indent=2)
                
                print(f"💾 Customers saved to /tmp/square_customers.json")
                return customers
                
            else:
                print(f"❌ CUSTOMERS CALL FAILED!")
                print(f"Status: {response.status_code}")
                print(f"Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ CUSTOMERS ERROR: {e}")
            return None

def run_oauth_test():
    """Run the complete OAuth test"""
    print("🏆 SQUARE OAUTH INTEGRATION TEST")
    print("🎯 Goal: Connect Ray's Bashful Beauty Account")
    print("🔧 Fix: Make Square OAuth actually work")
    print("=" * 80)
    
    oauth_test = SquareOAuthTest()
    
    # Step 1: Generate authorization URL
    auth_url, state = oauth_test.step1_generate_auth_url()
    
    print(f"\n⏸️  PAUSED - WAITING FOR YOUR AUTHORIZATION")
    print(f"Copy this URL and authorize in browser:")
    print(f"{auth_url}")
    print(f"\nAfter authorization, you'll get a redirect URL like:")
    print(f"http://localhost:3000/auth/callback?code=ABC123&state={state}")
    print(f"\nExtract the 'code' parameter and paste it below:")
    
    # Get authorization code from user
    auth_code = input("\n📥 Enter authorization code: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided. Test aborted.")
        return
    
    # Step 2: Exchange code for token
    access_token = oauth_test.step2_exchange_code_for_token(auth_code, state)
    
    if not access_token:
        print("❌ Token exchange failed. Cannot continue.")
        return
    
    # Step 3: Test basic API call
    merchant_data = oauth_test.step3_test_api_call(access_token)
    
    if not merchant_data:
        print("❌ API test failed. Cannot continue.")
        return
    
    # Step 4: Get real customers
    customers = oauth_test.step4_get_customers(access_token, limit=10)
    
    if customers:
        print(f"\n🎉 SUCCESS! Square OAuth integration working!")
        print(f"✅ Connected to Bashful Beauty")
        print(f"✅ Retrieved {len(customers)} real customers")
        print(f"✅ Ready for full sync")
    else:
        print(f"\n❌ Customer retrieval failed")

if __name__ == "__main__":
    run_oauth_test()