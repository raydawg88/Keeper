#!/usr/bin/env python3
"""
Test Square OAuth Flow for Keeper
Run this to test the OAuth URL generation
"""
from square_oauth import SquareOAuthManager
import sys

def main():
    """Test OAuth flow with proper error handling"""
    oauth_manager = SquareOAuthManager()
    
    print("🔐 Keeper Square OAuth Flow Test")
    print("=" * 45)
    
    # Test OAuth URL generation
    redirect_uri = "https://keeper.tools/auth/callback"
    business_name = "Test Business"
    
    print(f"📋 Testing OAuth URL generation...")
    print(f"   Redirect URI: {redirect_uri}")
    print(f"   Environment: {oauth_manager.environment}")
    print(f"   Client ID: {oauth_manager.client_id}")
    
    oauth_result = oauth_manager.generate_oauth_url(redirect_uri, business_name)
    
    if oauth_result:
        print(f"\n✅ OAuth URL Generated Successfully!")
        print(f"🔗 Authorization URL:")
        print(f"   {oauth_result['auth_url']}")
        print(f"\n🔐 Security Details:")
        print(f"   State: {oauth_result['state']}")
        print(f"   Session ID: {oauth_result['session_id']}")
        
        print(f"\n📝 OAuth Testing Instructions:")
        print("1. Copy the authorization URL above")
        print("2. Paste it in your browser")
        print("3. Authorize the Keeper application")
        print("4. Copy the 'code' parameter from the callback URL")
        print("5. Run: python test_oauth_callback.py <code> <state>")
        
        print(f"\n🎯 Next Development Steps:")
        print("- Create test_oauth_callback.py for callback handling")
        print("- Set up web server for real OAuth flow")
        print("- Implement token encryption for production")
        
        return True
    else:
        print("❌ OAuth URL generation failed")
        print("Check:")
        print("- .env file has SQUARE_APPLICATION_ID")
        print("- Supabase connection is working")
        print("- Database has oauth_sessions table")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)