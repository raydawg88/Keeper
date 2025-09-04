#!/usr/bin/env python3
"""
Test Square OAuth Callback Handler
Usage: python test_oauth_callback.py <authorization_code> <state>
"""
from square_oauth import SquareOAuthManager
import sys

def main():
    """Test OAuth callback handling"""
    if len(sys.argv) != 3:
        print("Usage: python test_oauth_callback.py <authorization_code> <state>")
        print("\nGet these from the Square OAuth callback URL:")
        print("https://keeper.tools/auth/callback?code=<code>&state=<state>")
        return False
    
    authorization_code = sys.argv[1]
    state = sys.argv[2]
    
    print("🔐 Testing Square OAuth Callback")
    print("=" * 40)
    print(f"Authorization Code: {authorization_code[:20]}...")
    print(f"State: {state}")
    
    oauth_manager = SquareOAuthManager()
    
    # Handle the callback
    result = oauth_manager.handle_oauth_callback(authorization_code, state)
    
    if result:
        print(f"\n🎉 OAuth Flow Completed Successfully!")
        print(f"✅ Business Connected: {result['business_name']}")
        print(f"📋 Account ID: {result['account_id']}")
        print(f"🏪 Merchant ID: {result['merchant_id']}")
        print(f"📍 Locations: {len(result['locations'])}")
        
        # Show location details
        for i, location in enumerate(result['locations']):
            print(f"   {i+1}. {location.get('name', 'Unnamed Location')}")
            print(f"      ID: {location['id']}")
            if location.get('address'):
                addr = location['address']
                city = addr.get('locality', '')
                state = addr.get('administrative_district_level_1', '')
                print(f"      Address: {city}, {state}")
        
        print(f"\n🚀 Next Steps:")
        print("- Test data sync from Square")
        print("- Import customers and transactions")
        print("- Begin insight generation")
        
        return True
    else:
        print("❌ OAuth callback failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)