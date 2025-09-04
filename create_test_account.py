#!/usr/bin/env python3
"""
Create Keeper account using Square test account token
"""
import os
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import requests

def create_keeper_test_account():
    """Create a Keeper account using Square's test account token"""
    load_dotenv()
    
    print("🏗️  Creating Keeper Test Account")
    print("=" * 40)
    
    # Supabase setup
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Square test token (from your developer dashboard)
    test_token = "EAAAly9qBw1tIof19JwYlbSe_lKVJWgQI97qLn8hhSa3NMZyWzq8_tgoio_sz1Ac"
    
    # Get merchant and location info from Square
    headers = {
        'Authorization': f'Bearer {test_token}',
        'Square-Version': '2023-10-18',
        'Content-Type': 'application/json'
    }
    
    try:
        # Get locations
        locations_response = requests.get(
            'https://connect.squareupsandbox.com/v2/locations', 
            headers=headers
        )
        locations_response.raise_for_status()
        locations_data = locations_response.json()
        
        if not locations_data.get('locations'):
            print("❌ No locations found")
            return None
            
        location = locations_data['locations'][0]  # Use first location
        
        print(f"📍 Found location: {location.get('name', 'Default Test Account')}")
        print(f"   Location ID: {location['id']}")
        
        # Create account in Keeper database
        account_data = {
            'id': str(uuid.uuid4()),
            'business_name': location.get('name', 'Default Test Account'),
            'square_merchant_id': location.get('merchant_id', 'test-merchant'),
            'square_access_token': test_token,  # Store for API calls
            'refresh_token': None,  # Test tokens don't have refresh tokens
            'token_expires_at': None,  # Test tokens don't expire
            'square_locations': json.dumps(locations_data['locations']),
            'subscription_status': 'trial',
            'created_at': datetime.utcnow().isoformat(),
            'last_sync_at': None
        }
        
        # Insert into accounts table
        result = supabase.table('accounts').insert(account_data).execute()
        account = result.data[0]
        
        print(f"\n✅ Keeper Account Created Successfully!")
        print(f"🏢 Business Name: {account['business_name']}")
        print(f"📋 Account ID: {account['id']}")
        print(f"🔑 Square Merchant ID: {account['square_merchant_id']}")
        print(f"📍 Locations: {len(locations_data['locations'])}")
        
        # Test getting some customers (even though there are none)
        customers_response = requests.get(
            'https://connect.squareupsandbox.com/v2/customers',
            headers=headers
        )
        customers_response.raise_for_status()
        customers_data = customers_response.json()
        
        print(f"👥 Square Customers Available: {len(customers_data.get('customers', []))}")
        
        print(f"\n🚀 Ready for Next Steps:")
        print("- Data sync pipeline development")
        print("- Customer import functionality") 
        print("- Insight generation system")
        print("- Task management features")
        
        return {
            'account_id': account['id'],
            'business_name': account['business_name'],
            'merchant_id': account['square_merchant_id'],
            'access_token': test_token
        }
        
    except Exception as e:
        print(f"❌ Failed to create Keeper account: {e}")
        return None

if __name__ == "__main__":
    result = create_keeper_test_account()
    
    if result:
        print(f"\n🎯 Test Account Ready!")
        print(f"Use Account ID: {result['account_id']} for development")
    else:
        print("\n❌ Account creation failed")