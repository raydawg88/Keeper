#!/usr/bin/env python3
"""
Test using Square's built-in test account authorization
This bypasses the OAuth flow and uses the direct test account access token
"""
import os
from dotenv import load_dotenv
import requests

def test_with_square_test_token():
    """Test Square API with the test account token from developer dashboard"""
    load_dotenv()
    
    print("🔐 Testing Square API with Test Account Token")
    print("=" * 50)
    
    # You'll need to get this token from the "Test account authorizations" section
    # in your Square Developer Dashboard after clicking "Authorize test account"
    test_token = input("Enter the test account access token from Square Dashboard: ").strip()
    
    if not test_token:
        print("❌ No test token provided")
        return False
    
    # Test with Square API
    headers = {
        'Authorization': f'Bearer {test_token}',
        'Square-Version': '2023-10-18',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test locations endpoint
        locations_response = requests.get(
            'https://connect.squareupsandbox.com/v2/locations', 
            headers=headers
        )
        locations_response.raise_for_status()
        locations_data = locations_response.json()
        
        print("✅ Square API Connection Successful!")
        print(f"📍 Found {len(locations_data.get('locations', []))} location(s)")
        
        for loc in locations_data.get('locations', []):
            print(f"   - {loc.get('name', 'Unnamed Location')} ({loc['id']})")
        
        # Test customers endpoint
        customers_response = requests.get(
            'https://connect.squareupsandbox.com/v2/customers',
            headers=headers
        )
        customers_response.raise_for_status()
        customers_data = customers_response.json()
        
        print(f"👥 Found {len(customers_data.get('customers', []))} customer(s)")
        
        # If successful, we can use this token for testing
        print("\n🎉 Test Account Authorization Working!")
        print("💡 You can use this access token for testing Keeper functionality")
        print(f"🔑 Token: {test_token[:20]}...")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Square API test failed: {e}")
        return False

if __name__ == "__main__":
    test_with_square_test_token()