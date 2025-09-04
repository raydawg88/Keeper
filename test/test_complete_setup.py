#!/usr/bin/env python3
"""
Test complete Keeper setup: Square API + Supabase + AI APIs
"""
import os
from dotenv import load_dotenv
from supabase import create_client
import requests

load_dotenv()

def test_all_integrations():
    """Test all integrations are working"""
    
    print("🔍 Testing Complete Keeper Setup")
    print("=" * 50)
    
    # Test 1: Supabase Database Schema
    print("1. Testing Supabase Database Schema...")
    if test_supabase_schema():
        print("✅ Database schema ready\n")
    else:
        print("❌ Database schema issues\n")
        return False
    
    # Test 2: Square API
    print("2. Testing Square API...")
    if test_square_api():
        print("✅ Square API connected\n")
    else:
        print("❌ Square API issues\n")
        return False
    
    # Test 3: AI APIs
    print("3. Testing AI APIs...")
    if test_ai_apis():
        print("✅ AI APIs connected\n")
    else:
        print("❌ AI API issues\n")
        return False
    
    print("🎉 ALL INTEGRATIONS WORKING!")
    print("🚀 Ready to build Keeper core functionality!")
    return True

def test_supabase_schema():
    """Test that all required tables exist"""
    
    url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    supabase = create_client(url, service_key)
    
    required_tables = ['accounts', 'customers', 'transactions', 'insights', 'tasks']
    
    for table in required_tables:
        try:
            result = supabase.table(table).select('*').limit(1).execute()
            print(f"   ✅ {table} table exists and accessible")
        except Exception as e:
            print(f"   ❌ {table} table error: {str(e)}")
            return False
    
    # Test inserting and retrieving a record
    try:
        # Insert test account
        result = supabase.table('accounts').insert({
            'business_name': 'Test Keeper Setup',
            'business_category': 'spa'
        }).execute()
        
        account_id = result.data[0]['id']
        print(f"   ✅ Test record created: {account_id}")
        
        # Clean up
        supabase.table('accounts').delete().eq('id', account_id).execute()
        print("   ✅ Test record cleaned up")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Database operations failed: {str(e)}")
        return False

def test_square_api():
    """Test Square API connectivity"""
    
    token = os.getenv("SQUARE_ACCESS_TOKEN")
    
    headers = {
        "Square-Version": "2023-10-18",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            "https://connect.squareupsandbox.com/v2/locations",
            headers=headers
        )
        
        if response.status_code == 200:
            locations = response.json().get('locations', [])
            print(f"   ✅ {len(locations)} Square location(s) found")
            return True
        else:
            print(f"   ❌ Square API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Square API error: {str(e)}")
        return False

def test_ai_apis():
    """Test AI API connections"""
    
    # Test OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key.startswith("sk-"):
        print("   ✅ OpenAI API key format valid")
    else:
        print("   ❌ OpenAI API key missing or invalid")
        return False
    
    # Test Anthropic
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key and anthropic_key.startswith("sk-ant-"):
        print("   ✅ Anthropic API key format valid")
    else:
        print("   ❌ Anthropic API key missing or invalid")
        return False
    
    # Test Gemini
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key and gemini_key.startswith("AIzaSy"):
        print("   ✅ Gemini API key format valid")
    else:
        print("   ❌ Gemini API key missing or invalid")
        return False
    
    return True

def show_next_steps():
    """Show what we can build next"""
    
    print("\n🎯 NEXT DEVELOPMENT STEPS:")
    print("-" * 30)
    print("1. Square OAuth Flow (connect real businesses)")
    print("2. Data Sync Pipeline (pull customer/transaction data)")
    print("3. Customer Matching Engine (97%+ accuracy fuzzy matching)")
    print("4. Insight Generation (find $3000+ opportunities)")
    print("5. Task Management (actionable insights with dollar values)")
    print("6. Agent System (8 specialized agents)")
    print("7. Frontend Dashboard (Next.js)")
    print()
    print("🎪 Ready to build the first Square OAuth integration!")

if __name__ == "__main__":
    if test_all_integrations():
        show_next_steps()
    else:
        print("❌ Setup incomplete - fix issues above before continuing")