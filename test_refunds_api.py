#!/usr/bin/env python3
"""
TEST 7: REFUNDS API
- Call Refunds API
- Show refund transaction data
- Show raw JSON response
- Store in JSON file
- Verify customer satisfaction issues
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_refunds_api():
    """Test Refunds API step by step"""
    
    print("💸 TEST 7: REFUNDS API")
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
    
    # Try multiple refunds endpoints
    test_endpoints = [
        ("/v2/refunds", "GET", None, "Refunds"),
        ("/v2/refunds?begin_time=2023-01-01T00:00:00Z&end_time=2025-12-31T23:59:59Z", "GET", None, "Refunds with Date Range"),
        ("/v2/payments/refunds", "GET", None, "Payment Refunds")
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
                    
                    if record_count == 0:
                        print(f"   No refunds found (good for business!)")
                        
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
    
    # If we got successful data, process it
    if successful_data:
        # Pick the endpoint with the most data
        best_endpoint = max(successful_data.items(), key=lambda x: len(str(x[1])))
        endpoint_name, data = best_endpoint
        
        print(f"\n📋 DETAILED RESULTS FROM {endpoint_name.upper()}:")
        print("-" * 60)
        print(json.dumps(data, indent=2))
        print("-" * 60)
        
        # Process refunds data
        if 'refunds' in data and data['refunds']:
            refunds = data['refunds']
            print(f"\n💸 REFUND DETAILS:")
            
            total_refund_amount = 0
            for i, refund in enumerate(refunds[:10], 1):
                refund_id = refund.get('id')
                payment_id = refund.get('payment_id')
                amount_money = refund.get('amount_money', {})
                refund_amount = float(amount_money.get('amount', 0)) / 100
                total_refund_amount += refund_amount
                reason = refund.get('reason', 'No reason given')
                status = refund.get('status')
                
                print(f"\nRefund {i}:")
                print(f"  Refund ID: {refund_id}")
                print(f"  Payment ID: {payment_id}")
                print(f"  Amount: ${refund_amount:.2f}")
                print(f"  Reason: {reason}")
                print(f"  Status: {status}")
                print(f"  Created: {refund.get('created_at')}")
                
            print(f"\n📊 REFUNDS SUMMARY:")
            print(f"Total Refunds: {len(refunds)}")
            print(f"Total Refund Amount: ${total_refund_amount:.2f}")
            
        elif 'refunds' in data and not data['refunds']:
            print(f"\n✅ NO REFUNDS FOUND!")
            print("This is excellent for business - no customer refund issues!")
        
        # Store data
        print(f"\n💾 STORING REFUNDS DATA...")
        
        output_file = f"/tmp/square_refunds_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump({
                'test_info': {
                    'test_name': 'Square Refunds API Test',
                    'account_id': account_id,
                    'timestamp': datetime.now().isoformat(),
                    'successful_endpoints': list(successful_data.keys()),
                    'total_endpoints_tested': len(test_endpoints),
                    'refunds_count': len(data.get('refunds', [])) if 'refunds' in data else 0,
                    'api_version': '2025-08-20'
                },
                'data': successful_data
            }, f, indent=2)
        
        print(f"✅ Refunds data saved to: {output_file}")
        
        # Data quality verification
        print(f"\n📊 REFUNDS DATA VERIFICATION:")
        print("-" * 40)
        print(f"Successful Endpoints: {len(successful_data)}/{len(test_endpoints)}")
        print(f"Working APIs: {list(successful_data.keys())}")
        
        # Check refund rate
        if 'refunds' in data:
            refund_count = len(data['refunds'])
            if refund_count == 0:
                print(f"✅ Refund Rate: 0% (Excellent customer satisfaction)")
            else:
                print(f"⚠️  Refund Count: {refund_count} (Monitor for satisfaction issues)")
        
        return True
        
    else:
        print(f"\n❌ NO REFUNDS DATA AVAILABLE")
        print("All refunds endpoints returned errors")
        return False

if __name__ == "__main__":
    success = test_refunds_api()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 TEST 7 (REFUNDS API) COMPLETE!")
        print("✅ Refunds endpoint working")
        print("✅ Raw JSON response shown")
        print("✅ Refund analysis completed")
        print("✅ Data saved to JSON file")
    else:
        print("❌ TEST 7 (REFUNDS API) FAILED!")
        print("⚠️  No refunds endpoints accessible")
        print("📋 May require additional permissions")
    
    print("\n📋 CHECKPOINT: Continue testing remaining APIs")