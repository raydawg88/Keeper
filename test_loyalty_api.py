#!/usr/bin/env python3
"""
TEST 6: LOYALTY API
- Call Loyalty API endpoints
- Show loyalty program and customer data
- Show raw JSON response
- Store in JSON file
- Verify customer retention programs
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_loyalty_api():
    """Test Loyalty API step by step"""
    
    print("🎗️ TEST 6: LOYALTY API")
    print("=" * 60)
    
    # Load comprehensive access token
    try:
        with open('/tmp/comprehensive_square_token.json', 'r') as f:
            token_data = json.load(f)
        access_token = token_data['access_token']
    except:
        print("❌ No comprehensive token found")
        return

    # Set up API call
    api_base_url = 'https://connect.squareup.com'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Square-Version': '2025-08-20',
        'Content-Type': 'application/json'
    }
    
    account_id = "b491de6e-7d5b-4e0e-b1cd-625c6c4f7d81"
    
    # Try multiple loyalty endpoints
    test_endpoints = [
        ("/v2/loyalty/programs", "GET", None, "Loyalty Programs"),
        ("/v2/loyalty/accounts", "GET", None, "Loyalty Accounts"),
        ("/v2/loyalty/rewards", "GET", None, "Loyalty Rewards"),
        ("/v2/loyalty/accounts/search", "POST", {"limit": 10}, "Loyalty Accounts Search"),
    ]
    
    successful_data = {}
    
    for endpoint, method, body, name in test_endpoints:
        print(f"\n🌐 TESTING {name.upper()}...")
        print(f"URL: {api_base_url}{endpoint}")
        print(f"Method: {method}")
        
        try:
            if method == "POST":
                response = requests.post(f"{api_base_url}{endpoint}", headers=headers, json=body or {})
            else:
                response = requests.get(f"{api_base_url}{endpoint}", headers=headers)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS! {name} API working")
                
                # Show basic data structure
                if data:
                    keys = list(data.keys())
                    print(f"   Response keys: {keys}")
                    
                    # Check if we got any records
                    record_count = 0
                    for key in keys:
                        if isinstance(data[key], list):
                            record_count = len(data[key])
                            print(f"   {key}: {record_count} records")
                            break
                    
                    if record_count == 0 and data:
                        print(f"   Response has data but no arrays")
                        
                    successful_data[name] = data
                else:
                    print(f"   Empty response")
                    
            elif response.status_code == 404:
                print(f"❌ {name}: Endpoint not found (404)")
                
            elif response.status_code == 403:
                print(f"🔒 {name}: Permission denied (403)")
                
            else:
                print(f"❌ {name}: Error {response.status_code}")
                error_text = response.text
                if len(error_text) > 300:
                    error_text = error_text[:300] + "..."
                print(f"   Error: {error_text}")
                
        except Exception as e:
            print(f"❌ {name}: Connection error - {e}")
    
    # If we got successful data, process the best one
    if successful_data:
        # Pick the endpoint with the most data
        best_endpoint = max(successful_data.items(), key=lambda x: len(str(x[1])))
        endpoint_name, data = best_endpoint
        
        print(f"\n📋 DETAILED RESULTS FROM {endpoint_name.upper()}:")
        print("-" * 60)
        print(json.dumps(data, indent=2))
        print("-" * 60)
        
        # Process loyalty data
        if 'programs' in data:
            programs = data['programs']
            print(f"\n🎗️ LOYALTY PROGRAM DETAILS:")
            
            for i, program in enumerate(programs, 1):
                program_id = program.get('id')
                status = program.get('status')
                terminology = program.get('terminology', {})
                
                print(f"\nProgram {i}:")
                print(f"  ID: {program_id}")
                print(f"  Status: {status}")
                print(f"  Points Name: {terminology.get('one', 'Point')}")
                print(f"  Reward Tiers: {len(program.get('reward_tiers', []))}")
                
                # Show reward tiers
                for j, tier in enumerate(program.get('reward_tiers', [])[:3], 1):
                    points = tier.get('points')
                    name = tier.get('name', 'Unnamed Reward')
                    print(f"    Tier {j}: {name} ({points} points)")
                
        elif 'loyalty_accounts' in data:
            accounts = data['loyalty_accounts']
            print(f"\n👤 LOYALTY ACCOUNT DETAILS:")
            
            for i, account in enumerate(accounts[:5], 1):
                account_id = account.get('id')
                customer_id = account.get('customer_id')
                balance = account.get('balance')
                lifetime_balance = account.get('lifetime_balance')
                
                print(f"\nAccount {i}:")
                print(f"  Account ID: {account_id}")
                print(f"  Customer: {customer_id}")
                print(f"  Current Balance: {balance} points")
                print(f"  Lifetime Balance: {lifetime_balance} points")
                
        elif 'rewards' in data:
            rewards = data['rewards']
            print(f"\n🎁 LOYALTY REWARDS DETAILS:")
            
            for i, reward in enumerate(rewards[:5], 1):
                reward_id = reward.get('id')
                status = reward.get('status')
                points = reward.get('points')
                
                print(f"\nReward {i}:")
                print(f"  Reward ID: {reward_id}")
                print(f"  Status: {status}")
                print(f"  Points: {points}")
        
        # Store data
        print(f"\n💾 STORING LOYALTY DATA...")
        
        output_file = f"/tmp/square_loyalty_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump({
                'test_info': {
                    'test_name': 'Square Loyalty API Test',
                    'account_id': account_id,
                    'timestamp': datetime.now().isoformat(),
                    'successful_endpoints': list(successful_data.keys()),
                    'total_endpoints_tested': len(test_endpoints),
                    'api_version': '2025-08-20'
                },
                'data': successful_data
            }, f, indent=2)
        
        print(f"✅ Loyalty data saved to: {output_file}")
        
        # Data quality verification
        print(f"\n📊 LOYALTY DATA VERIFICATION:")
        print("-" * 40)
        print(f"Successful Endpoints: {len(successful_data)}/{len(test_endpoints)}")
        print(f"Working APIs: {list(successful_data.keys())}")
        
        # Check for active programs
        if 'programs' in data and data['programs']:
            active_programs = [p for p in data['programs'] if p.get('status') == 'ACTIVE']
            print(f"Active Loyalty Programs: {len(active_programs)}")
            
        return True
        
    else:
        print(f"\n❌ NO LOYALTY DATA AVAILABLE")
        print("All loyalty endpoints returned errors or no data")
        return False

if __name__ == "__main__":
    success = test_loyalty_api()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 TEST 6 (LOYALTY API) COMPLETE!")
        print("✅ At least one loyalty endpoint working")
        print("✅ Raw JSON response shown")
        print("✅ Loyalty program data extracted")
        print("✅ Data saved to JSON file")
    else:
        print("❌ TEST 6 (LOYALTY API) FAILED!")
        print("⚠️  No loyalty endpoints accessible")
        print("📋 Business may not have active loyalty programs")
    
    print("\n📋 CHECKPOINT: Moving to TEST 7: Refunds API")