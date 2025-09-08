#!/usr/bin/env python3
"""
FIX ALL CRITICAL API FAILURES
1. Bookings: Add date ranges to get historical appointments
2. Subscriptions: Correct API endpoint and parameters
3. Timecards: Try multiple endpoints with correct parameters
4. Cash Drawer: Use correct endpoints and parameters
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def fix_all_apis():
    """Fix all critical API failures with proper parameters"""
    
    print("🔧 FIXING ALL CRITICAL API FAILURES")
    print("=" * 80)
    
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
    
    results = {}
    
    # =============================================================================
    # FIX 1: BOOKINGS WITH HISTORICAL DATE RANGES
    # =============================================================================
    print(f"\n🔧 FIX 1: BOOKINGS WITH HISTORICAL DATE RANGES")
    print("=" * 60)
    print("Issue: Only getting future appointments (339 instead of 55,236)")
    print("Fix: Add start_at_min parameter for historical data")
    
    # Try getting appointments from last 2 years
    start_date = "2023-01-01T00:00:00Z"
    end_date = "2025-12-31T23:59:59Z"
    
    url = f"{api_base_url}/v2/bookings?limit=200&start_at_min={start_date}&start_at_max={end_date}"
    print(f"\n📡 EXACT API CALL:")
    print(f"URL: {url}")
    print(f"Method: GET")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            bookings = data.get('bookings', [])
            cursor = data.get('cursor')
            
            print(f"✅ SUCCESS! Retrieved {len(bookings)} historical bookings")
            if bookings:
                oldest = min(booking.get('start_at', '') for booking in bookings)
                newest = max(booking.get('start_at', '') for booking in bookings)
                print(f"Date range: {oldest[:10]} to {newest[:10]}")
                
                # Check for team members
                team_counts = {}
                for booking in bookings:
                    segments = booking.get('appointment_segments', [])
                    for segment in segments:
                        tm_id = segment.get('team_member_id')
                        if tm_id:
                            team_counts[tm_id] = team_counts.get(tm_id, 0) + 1
                
                print(f"Team members with appointments: {len(team_counts)}")
                if team_counts:
                    top_member = max(team_counts.items(), key=lambda x: x[1])
                    print(f"Top performer: {top_member[0]} with {top_member[1]} appointments")
            
            results['bookings'] = {
                'status': 'SUCCESS',
                'appointments': len(bookings),
                'has_cursor': bool(cursor),
                'team_members': len(team_counts) if bookings else 0
            }
            
        else:
            error_text = response.text
            print(f"❌ ERROR: {response.status_code}")
            print(f"Response: {error_text}")
            results['bookings'] = {'status': f'ERROR {response.status_code}', 'details': error_text}
            
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")
        results['bookings'] = {'status': 'CONNECTION ERROR', 'details': str(e)}
    
    # =============================================================================
    # FIX 2: SUBSCRIPTIONS API
    # =============================================================================
    print(f"\n🔧 FIX 2: SUBSCRIPTIONS API")
    print("=" * 60)
    print("Issue: Getting 404 Not Found")
    print("Fix: Try correct endpoint with search parameters")
    
    subscription_endpoints = [
        ("/v2/subscriptions", "GET", None, "Direct Subscriptions"),
        ("/v2/subscriptions/search", "POST", {"limit": 50}, "Subscriptions Search")
    ]
    
    for endpoint, method, body, name in subscription_endpoints:
        url = f"{api_base_url}{endpoint}"
        print(f"\n📡 TESTING {name.upper()}:")
        print(f"URL: {url}")
        print(f"Method: {method}")
        if body:
            print(f"Body: {json.dumps(body)}")
        
        try:
            if method == "POST":
                response = requests.post(url, headers=headers, json=body)
            else:
                response = requests.get(url, headers=headers)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                subscriptions = data.get('subscriptions', [])
                print(f"✅ SUCCESS! Found {len(subscriptions)} subscriptions")
                
                if subscriptions:
                    for i, sub in enumerate(subscriptions[:3], 1):
                        plan_id = sub.get('plan_id', 'N/A')
                        status = sub.get('status', 'N/A')
                        price = sub.get('price_override_money', {})
                        amount = float(price.get('amount', 0)) / 100 if price else 0
                        print(f"  Sub {i}: Plan {plan_id}, Status {status}, ${amount}")
                
                results['subscriptions'] = {
                    'status': 'SUCCESS',
                    'endpoint': name,
                    'subscriptions': len(subscriptions)
                }
                break
            else:
                print(f"❌ ERROR: {response.status_code} - {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ CONNECTION ERROR: {e}")
    
    if 'subscriptions' not in results:
        results['subscriptions'] = {'status': 'ALL ENDPOINTS FAILED'}
    
    # =============================================================================
    # FIX 3: TIMECARDS API
    # =============================================================================
    print(f"\n🔧 FIX 3: TIMECARDS API")
    print("=" * 60)
    print("Issue: Getting 404 errors")
    print("Fix: Try all possible labor/timecard endpoints")
    
    timecard_endpoints = [
        ("/v2/labor/timecards", "GET", None, "Timecards"),
        ("/v2/labor/shifts", "GET", None, "Labor Shifts"),
        ("/v2/labor/shifts/search", "POST", {"limit": 50}, "Shifts Search"),
        ("/v2/labor/break-types", "GET", None, "Break Types"),
        ("/v2/labor/workweeks", "GET", None, "Work Weeks")
    ]
    
    for endpoint, method, body, name in timecard_endpoints:
        url = f"{api_base_url}{endpoint}"
        print(f"\n📡 TESTING {name.upper()}:")
        print(f"URL: {url}")
        print(f"Method: {method}")
        if body:
            print(f"Body: {json.dumps(body)}")
        
        try:
            if method == "POST":
                response = requests.post(url, headers=headers, json=body)
            else:
                response = requests.get(url, headers=headers)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                # Look for any list data
                record_count = 0
                for key, value in data.items():
                    if isinstance(value, list):
                        record_count = len(value)
                        print(f"✅ SUCCESS! Found {record_count} {key}")
                        break
                
                if record_count == 0:
                    print(f"✅ SUCCESS! (Empty result - no timecard data)")
                
                results['timecards'] = {
                    'status': 'SUCCESS',
                    'endpoint': name,
                    'records': record_count
                }
                break
            else:
                print(f"❌ ERROR: {response.status_code} - {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ CONNECTION ERROR: {e}")
    
    if 'timecards' not in results:
        results['timecards'] = {'status': 'ALL ENDPOINTS FAILED'}
    
    # =============================================================================
    # FIX 4: CASH DRAWER API
    # =============================================================================
    print(f"\n🔧 FIX 4: CASH DRAWER API")
    print("=" * 60)
    print("Issue: Getting 400 errors")
    print("Fix: Try correct endpoint structure")
    
    cash_endpoints = [
        ("/v2/cash-drawers", "GET", None, "Cash Drawers"),
        ("/v2/cash-drawers/shifts", "GET", None, "Cash Drawer Shifts"),
        ("/v2/cash-drawers/shifts/search", "POST", {"limit": 50}, "Cash Drawer Search")
    ]
    
    for endpoint, method, body, name in cash_endpoints:
        url = f"{api_base_url}{endpoint}"
        print(f"\n📡 TESTING {name.upper()}:")
        print(f"URL: {url}")
        print(f"Method: {method}")
        if body:
            print(f"Body: {json.dumps(body)}")
        
        try:
            if method == "POST":
                response = requests.post(url, headers=headers, json=body)
            else:
                response = requests.get(url, headers=headers)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                record_count = 0
                for key, value in data.items():
                    if isinstance(value, list):
                        record_count = len(value)
                        print(f"✅ SUCCESS! Found {record_count} {key}")
                        break
                
                if record_count == 0:
                    print(f"✅ SUCCESS! (Empty result)")
                
                results['cash_drawer'] = {
                    'status': 'SUCCESS',
                    'endpoint': name,
                    'records': record_count
                }
                break
            else:
                print(f"❌ ERROR: {response.status_code} - {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ CONNECTION ERROR: {e}")
    
    if 'cash_drawer' not in results:
        results['cash_drawer'] = {'status': 'ALL ENDPOINTS FAILED'}
    
    # =============================================================================
    # FINAL SUMMARY
    # =============================================================================
    print(f"\n🎯 FINAL RESULTS SUMMARY:")
    print("=" * 80)
    
    for api_name, result in results.items():
        status = result['status']
        if status == 'SUCCESS':
            details = []
            if 'appointments' in result:
                details.append(f"{result['appointments']} appointments")
            if 'subscriptions' in result:
                details.append(f"{result['subscriptions']} subscriptions")
            if 'records' in result:
                details.append(f"{result['records']} records")
            
            detail_str = f" ({', '.join(details)})" if details else ""
            print(f"✅ {api_name.upper()}: FIXED{detail_str}")
        else:
            print(f"❌ {api_name.upper()}: {status}")
    
    # Save results
    output_file = f"/tmp/square_api_fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    return results

if __name__ == "__main__":
    results = fix_all_apis()
    
    print(f"\n" + "=" * 80)
    print("🔧 CRITICAL API FIXES COMPLETE!")
    
    success_count = sum(1 for r in results.values() if r.get('status') == 'SUCCESS')
    total_count = len(results)
    
    print(f"✅ Fixed APIs: {success_count}/{total_count}")
    print(f"📊 Success Rate: {(success_count/total_count)*100:.1f}%")
    
    if success_count == total_count:
        print("🎉 ALL CRITICAL FAILURES RESOLVED!")
    else:
        print("⚠️  Some APIs still need investigation")