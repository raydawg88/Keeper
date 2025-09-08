#!/usr/bin/env python3
"""
STEP 2: Exchange authorization code for access token
STEP 3: Test Square API with real Bashful Beauty data
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def exchange_code_for_token():
    """Exchange the authorization code for access token"""
    
    client_id = os.getenv('SQUARE_APPLICATION_ID')
    client_secret = os.getenv('SQUARE_CLIENT_SECRET')
    api_base_url = 'https://connect.squareup.com'
    
    # The authorization code from the redirect
    authorization_code = "sq0cgp-qs_D4y-RDlsOrszFxdVoKw"
    state = "d69e957f-feea-4956-8c9f-0a30c53ddce8"
    
    print("🔄 STEP 2: EXCHANGING AUTHORIZATION CODE FOR ACCESS TOKEN")
    print("=" * 70)
    print(f"Auth Code: {authorization_code}")
    print(f"State: {state}")
    
    # Token exchange request
    token_url = f"{api_base_url}/oauth2/token"
    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': authorization_code,
        'grant_type': 'authorization_code'
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Square-Version': '2025-08-20'
    }
    
    print(f"🌐 Making token exchange request...")
    
    try:
        response = requests.post(token_url, json=token_data, headers=headers)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            token_result = response.json()
            access_token = token_result.get('access_token')
            
            print(f"✅ TOKEN EXCHANGE SUCCESS!")
            print(f"🔑 Access Token: {access_token[:30]}...")
            print(f"⏰ Expires: {token_result.get('expires_at', 'Never')}")
            print(f"🔒 Token Type: {token_result.get('token_type', 'Bearer')}")
            
            # Save token
            with open('/tmp/bashful_beauty_token.json', 'w') as f:
                json.dump(token_result, f, indent=2)
            
            print(f"💾 Token saved to /tmp/bashful_beauty_token.json")
            return access_token
            
        else:
            print(f"❌ TOKEN EXCHANGE FAILED!")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ TOKEN EXCHANGE ERROR: {e}")
        return None

def test_square_api(access_token):
    """Test Square API calls with the access token"""
    
    print(f"\n🧪 STEP 3: TESTING SQUARE API WITH BASHFUL BEAUTY")
    print("=" * 70)
    
    api_base_url = 'https://connect.squareup.com'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Square-Version': '2025-08-20',
        'Content-Type': 'application/json'
    }
    
    # Test 1: Get merchant info
    print(f"📋 Test 1: Getting merchant information...")
    try:
        merchant_response = requests.get(f"{api_base_url}/v2/merchants", headers=headers)
        
        if merchant_response.status_code == 200:
            merchants = merchant_response.json()
            merchant = merchants.get('merchant', [{}])[0] if merchants.get('merchant') else {}
            
            print(f"✅ Merchant API Success!")
            print(f"   Business: {merchant.get('business_name', 'Unknown')}")
            print(f"   ID: {merchant.get('id', 'Unknown')}")
            print(f"   Country: {merchant.get('country', 'Unknown')}")
        else:
            print(f"❌ Merchant API Failed: {merchant_response.status_code}")
            print(f"Error: {merchant_response.text}")
            
    except Exception as e:
        print(f"❌ Merchant API Error: {e}")
    
    # Test 2: Get locations
    print(f"\n📍 Test 2: Getting location information...")
    try:
        locations_response = requests.get(f"{api_base_url}/v2/locations", headers=headers)
        
        if locations_response.status_code == 200:
            locations_data = locations_response.json()
            locations = locations_data.get('locations', [])
            
            print(f"✅ Locations API Success!")
            print(f"   Found {len(locations)} location(s)")
            
            for i, location in enumerate(locations, 1):
                print(f"   {i}. {location.get('name', 'Unnamed Location')}")
                print(f"      ID: {location.get('id')}")
                print(f"      Address: {location.get('address', {}).get('address_line_1', 'N/A')}")
        else:
            print(f"❌ Locations API Failed: {locations_response.status_code}")
            print(f"Error: {locations_response.text}")
            
    except Exception as e:
        print(f"❌ Locations API Error: {e}")
    
    # Test 3: Get first 10 customers (THE BIG TEST)
    print(f"\n👥 Test 3: Getting REAL Bashful Beauty customers...")
    try:
        customers_response = requests.get(f"{api_base_url}/v2/customers?limit=10", headers=headers)
        
        if customers_response.status_code == 200:
            customers_data = customers_response.json()
            customers = customers_data.get('customers', [])
            
            print(f"✅ CUSTOMERS API SUCCESS!")
            print(f"🎉 Retrieved {len(customers)} REAL customers from Bashful Beauty!")
            
            if customers:
                print(f"\n📋 REAL CUSTOMER SAMPLES:")
                for i, customer in enumerate(customers[:5], 1):
                    name = f"{customer.get('given_name', '')} {customer.get('family_name', '')}".strip()
                    print(f"   {i}. {name or 'No name'}")
                    print(f"      ID: {customer.get('id')}")
                    print(f"      Email: {customer.get('email_address', 'No email')}")
                    print(f"      Phone: {customer.get('phone_number', 'No phone')}")
                    print(f"      Created: {customer.get('created_at', 'Unknown')}")
                    print()
                
                # Save customers
                with open('/tmp/bashful_beauty_customers.json', 'w') as f:
                    json.dump(customers_data, f, indent=2)
                
                print(f"💾 Customers saved to /tmp/bashful_beauty_customers.json")
                
                return customers
            else:
                print(f"⚠️  No customers found (empty response)")
                
        else:
            print(f"❌ CUSTOMERS API FAILED!")
            print(f"Status: {customers_response.status_code}")
            print(f"Error: {customers_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Customers API Error: {e}")
        return None

def main():
    print("🏆 TESTING SQUARE INTEGRATION WITH BASHFUL BEAUTY")
    print("🎯 Goal: Prove OAuth → API calls → Real data works")
    print("=" * 80)
    
    # Step 2: Exchange code for token
    access_token = exchange_code_for_token()
    
    if not access_token:
        print("❌ Cannot continue without access token")
        return
    
    # Step 3: Test API calls
    customers = test_square_api(access_token)
    
    if customers and len(customers) > 0:
        print(f"\n🎉 SUCCESS! SQUARE INTEGRATION IS WORKING!")
        print(f"✅ OAuth flow: WORKING")
        print(f"✅ Token exchange: WORKING")
        print(f"✅ Square API calls: WORKING")
        print(f"✅ Real Bashful Beauty data: RETRIEVED")
        print(f"📊 Found {len(customers)} real customers")
        print(f"\n🚀 READY FOR STEP 4: Full sync to database!")
    else:
        print(f"\n❌ INTEGRATION STILL HAS ISSUES")
        print(f"Check the error messages above")

if __name__ == "__main__":
    main()