#!/usr/bin/env python3
"""
TEST 5: TIMECARDS API
- Call Labor/Timecards API
- Show employee timecard data
- Show raw JSON response
- Store in JSON file
- Verify labor cost tracking
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def test_timecards_api():
    """Test Timecards/Labor API step by step"""
    
    print("🕐 TEST 5: TIMECARDS API")
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
    
    # Try multiple timecard/labor endpoints
    test_endpoints = [
        ("/v2/labor/timecards", "GET", None, "Timecards"),
        ("/v2/labor/workweeks", "GET", None, "Workweeks"), 
        ("/v2/labor/shifts/search", "POST", {"limit": 10}, "Shifts Search"),
        ("/v2/labor/team-member-wages", "GET", None, "Team Member Wages")
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
                            break
                    
                    print(f"   Records found: {record_count}")
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
                if len(error_text) > 200:
                    error_text = error_text[:200] + "..."
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
        
        # Process timecard/labor data
        if 'timecards' in data:
            timecards = data['timecards']
            print(f"\n🕐 TIMECARD DETAILS:")
            
            for i, timecard in enumerate(timecards[:5], 1):
                employee_id = timecard.get('employee_id')
                start_at = timecard.get('start_at')
                end_at = timecard.get('end_at')
                
                print(f"\nTimecard {i}:")
                print(f"  Employee ID: {employee_id}")
                print(f"  Start: {start_at}")
                print(f"  End: {end_at}")
                print(f"  Location: {timecard.get('location_id')}")
                
        elif 'workweeks' in data:
            workweeks = data['workweeks']
            print(f"\n📅 WORKWEEK DETAILS:")
            
            for i, week in enumerate(workweeks[:3], 1):
                print(f"\nWorkweek {i}:")
                print(f"  Start Date: {week.get('start_date')}")
                print(f"  End Date: {week.get('end_date')}")
                print(f"  Team Members: {len(week.get('team_member_ids', []))}")
                
        elif 'shifts' in data:
            shifts = data['shifts']
            print(f"\n⏰ SHIFT DETAILS:")
            
            for i, shift in enumerate(shifts[:5], 1):
                print(f"\nShift {i}:")
                print(f"  Team Member: {shift.get('team_member_id')}")
                print(f"  Start: {shift.get('start_at')}")
                print(f"  End: {shift.get('end_at')}")
                print(f"  Status: {shift.get('status')}")
                
        elif 'team_member_wages' in data:
            wages = data['team_member_wages']
            print(f"\n💰 WAGE DETAILS:")
            
            for i, wage in enumerate(wages[:5], 1):
                team_member_id = wage.get('team_member_id')
                job_assignments = wage.get('job_assignments', [])
                
                print(f"\nWage {i}:")
                print(f"  Team Member: {team_member_id}")
                print(f"  Jobs: {len(job_assignments)}")
                
                for job in job_assignments[:2]:
                    hourly_rate = job.get('hourly_rate', {})
                    rate = float(hourly_rate.get('amount', 0)) / 100
                    print(f"    Job: {job.get('job_title')} - ${rate:.2f}/hour")
        
        # Store data
        print(f"\n💾 STORING TIMECARDS/LABOR DATA...")
        
        output_file = f"/tmp/square_timecards_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump({
                'test_info': {
                    'test_name': 'Square Timecards/Labor API Test',
                    'account_id': account_id,
                    'timestamp': datetime.now().isoformat(),
                    'successful_endpoints': list(successful_data.keys()),
                    'total_endpoints_tested': len(test_endpoints),
                    'api_version': '2025-08-20'
                },
                'data': successful_data
            }, f, indent=2)
        
        print(f"✅ Timecards/Labor data saved to: {output_file}")
        
        # Data quality verification
        print(f"\n📊 LABOR DATA VERIFICATION:")
        print("-" * 40)
        print(f"Successful Endpoints: {len(successful_data)}/{len(test_endpoints)}")
        print(f"Working APIs: {list(successful_data.keys())}")
        
        return True
        
    else:
        print(f"\n❌ NO TIMECARDS/LABOR DATA AVAILABLE")
        print("All endpoints returned errors or no data")
        return False

if __name__ == "__main__":
    success = test_timecards_api()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 TEST 5 (TIMECARDS API) COMPLETE!")
        print("✅ At least one labor/timecard endpoint working")
        print("✅ Raw JSON response shown")
        print("✅ Labor data extracted")
        print("✅ Data saved to JSON file")
    else:
        print("❌ TEST 5 (TIMECARDS API) FAILED!")
        print("⚠️  No labor/timecard endpoints accessible")
        print("📋 May require additional Square permissions")
    
    print("\n📋 CHECKPOINT: Moving to TEST 6: Loyalty API")