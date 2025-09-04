#!/usr/bin/env python3
"""
Test Square API connection with Ray's sandbox credentials
"""
import requests
import json
from datetime import datetime

# Ray's Square sandbox credentials
SQUARE_APPLICATION_ID = "sandbox-sq0idb-Cw1weGGBPFe_rd5n88AN4w"
SQUARE_ACCESS_TOKEN = "EAAAly9qBw1tIof19JwYlbSe_lKVJWgQI97qLn8hhSa3NMZyWzq8_tgoio_sz1Ac"
SQUARE_BASE_URL = "https://connect.squareupsandbox.com"

def test_square_connection():
    """Test basic Square API connectivity"""
    
    headers = {
        "Square-Version": "2023-10-18",
        "Authorization": f"Bearer {SQUARE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("🔄 Testing Square API connection...")
    print(f"Application ID: {SQUARE_APPLICATION_ID}")
    print(f"Environment: Sandbox")
    print("-" * 50)
    
    # Test 1: Get locations
    try:
        response = requests.get(f"{SQUARE_BASE_URL}/v2/locations", headers=headers)
        
        if response.status_code == 200:
            locations = response.json().get('locations', [])
            print(f"✅ Locations API: SUCCESS ({len(locations)} locations found)")
            
            for loc in locations:
                print(f"   📍 {loc.get('name', 'Unnamed')} - {loc.get('id')}")
                print(f"      Status: {loc.get('status', 'unknown')}")
                print(f"      Country: {loc.get('country', 'unknown')}")
                
        else:
            print(f"❌ Locations API: FAILED ({response.status_code})")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Locations API: ERROR - {str(e)}")
        return False
    
    # Test 2: Get customers
    try:
        response = requests.post(f"{SQUARE_BASE_URL}/v2/customers/search", 
                               headers=headers,
                               json={"limit": 10})
        
        if response.status_code == 200:
            customers = response.json().get('customers', [])
            print(f"✅ Customers API: SUCCESS ({len(customers)} customers found)")
            
            for customer in customers[:3]:  # Show first 3
                name = f"{customer.get('given_name', '')} {customer.get('family_name', '')}".strip()
                print(f"   👤 {name or 'Unnamed'} - {customer.get('id')}")
                
        else:
            print(f"❌ Customers API: FAILED ({response.status_code})")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Customers API: ERROR - {str(e)}")
    
    # Test 3: Get recent payments
    try:
        response = requests.post(f"{SQUARE_BASE_URL}/v2/payments/search",
                               headers=headers, 
                               json={"limit": 5, "sort_order": "DESC"})
        
        if response.status_code == 200:
            payments = response.json().get('payments', [])
            print(f"✅ Payments API: SUCCESS ({len(payments)} recent payments)")
            
            for payment in payments[:3]:  # Show first 3
                amount = payment.get('amount_money', {})
                total = amount.get('amount', 0) / 100  # Convert cents to dollars
                currency = amount.get('currency', 'USD')
                status = payment.get('status', 'unknown')
                print(f"   💰 ${total:.2f} {currency} - Status: {status}")
                
        else:
            print(f"❌ Payments API: FAILED ({response.status_code})")  
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Payments API: ERROR - {str(e)}")
    
    print("-" * 50)
    print("✅ Square API connection test complete!")
    print("🎯 Ready to build Keeper data pipeline")
    return True

if __name__ == "__main__":
    test_square_connection()