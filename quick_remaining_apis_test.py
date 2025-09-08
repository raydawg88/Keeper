#!/usr/bin/env python3
"""
QUICK TEST: REMAINING 8+ APIS
- Test all remaining authorized endpoints
- Show basic success/failure status
- Document which APIs work vs don't work
- Save results for final summary
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_remaining_apis():
    """Test all remaining Square API endpoints quickly"""
    
    print("🔬 QUICK TEST: REMAINING 8+ APIS")
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
    
    # TEST REMAINING ENDPOINTS
    test_endpoints = [
        # APPOINTMENTS & BOOKINGS
        ("/v2/bookings", "GET", None, "Bookings"),
        ("/v2/bookings/custom-attributes", "GET", None, "Booking Custom Attributes"),
        
        # INVENTORY & PRODUCTS
        ("/v2/inventory/counts", "GET", None, "Inventory Counts"),
        
        # CASH DRAWERS & TERMINALS
        ("/v2/cash-drawers/shifts", "GET", None, "Cash Drawer Shifts"),
        ("/v2/terminal/checkouts", "GET", None, "Terminal Checkouts"),
        
        # INVOICES
        ("/v2/invoices", "GET", None, "Invoices"),
        
        # GIFT CARDS
        ("/v2/gift-cards", "GET", None, "Gift Cards"),
        
        # SUBSCRIPTIONS
        ("/v2/subscriptions", "GET", None, "Subscriptions"),
        
        # DISPUTES
        ("/v2/disputes", "GET", None, "Disputes"),
        
        # WEBHOOKS
        ("/v2/webhooks/subscriptions", "GET", None, "Webhook Subscriptions"),
        
        # SITES & ONLINE
        ("/v2/sites", "GET", None, "Sites"),
        
        # MERCHANT INFO (already tested but confirming)
        ("/v2/merchants", "GET", None, "Merchants"),
        ("/v2/locations", "GET", None, "Locations"),
    ]
    
    results = {}
    
    print(f"Testing {len(test_endpoints)} endpoints...")
    
    for endpoint, method, body, name in test_endpoints:
        try:
            if method == "POST":
                response = requests.post(f"{api_base_url}{endpoint}", headers=headers, json=body or {})
            else:
                response = requests.get(f"{api_base_url}{endpoint}", headers=headers)
            
            status = response.status_code
            
            if status == 200:
                data = response.json()
                record_count = 0
                
                # Count records quickly
                for key, value in data.items():
                    if isinstance(value, list):
                        record_count = len(value)
                        break
                
                results[name] = {
                    'status': '✅ SUCCESS',
                    'code': status,
                    'records': record_count,
                    'data_keys': list(data.keys()) if data else []
                }
                print(f"✅ {name}: {record_count} records")
                
            elif status == 404:
                results[name] = {'status': '❌ NOT FOUND', 'code': status}
                print(f"❌ {name}: Not Found (404)")
                
            elif status == 403:
                results[name] = {'status': '🔒 FORBIDDEN', 'code': status}
                print(f"🔒 {name}: Permission Denied (403)")
                
            else:
                results[name] = {'status': f'❌ ERROR {status}', 'code': status}
                print(f"❌ {name}: Error {status}")
                
        except Exception as e:
            results[name] = {'status': f'❌ CONNECTION ERROR', 'error': str(e)}
            print(f"❌ {name}: Connection Error")
    
    # SUMMARY RESULTS
    print(f"\n📊 FINAL API TEST RESULTS:")
    print("=" * 60)
    
    working_apis = []
    broken_apis = []
    
    for api_name, result in results.items():
        status = result['status']
        if '✅' in status:
            records = result.get('records', 0)
            working_apis.append(f"{api_name} ({records} records)")
            print(f"✅ {api_name}: WORKING - {records} records")
        else:
            broken_apis.append(f"{api_name} - {status}")
            print(f"{status}: {api_name}")
    
    print(f"\n🎯 SUMMARY:")
    print(f"WORKING APIS: {len(working_apis)}")
    print(f"BROKEN/UNAVAILABLE: {len(broken_apis)}")
    print(f"SUCCESS RATE: {len(working_apis)}/{len(test_endpoints)} ({len(working_apis)/len(test_endpoints)*100:.1f}%)")
    
    # Save complete results
    output_file = f"/tmp/square_api_complete_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'test_info': {
                'test_name': 'Complete Square API Test',
                'timestamp': datetime.now().isoformat(),
                'total_endpoints_tested': len(test_endpoints),
                'working_apis': len(working_apis),
                'broken_apis': len(broken_apis),
                'success_rate_percent': len(working_apis)/len(test_endpoints)*100,
                'api_version': '2025-08-20'
            },
            'results': results,
            'working_apis': working_apis,
            'broken_apis': broken_apis
        }, f, indent=2)
    
    print(f"\n✅ Complete results saved to: {output_file}")
    return results

if __name__ == "__main__":
    results = test_remaining_apis()
    
    print(f"\n" + "=" * 60)
    print("🎉 COMPLETE SQUARE API TESTING FINISHED!")
    print("📋 Ready for final comprehensive summary")
    print("🔄 Next: Address employee data gap and create final report")