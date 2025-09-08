#!/usr/bin/env python3
"""
GET LOCATION_ID AND USE FOR CASH DRAWER API
- Get location_id from Locations API (we already called this successfully)
- Use that location_id for Cash Drawer API calls
- Show actual cash drawer data
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def get_location_and_cash_drawer():
    """Get location_id and use it for Cash Drawer API"""
    
    print("💰 GET LOCATION_ID AND CASH DRAWER DATA")
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
    
    # STEP 1: Get location_id from Locations API
    print(f"\n📡 STEP 1: GET LOCATION_ID")
    print(f"URL: {api_base_url}/v2/locations")
    print(f"Method: GET")
    
    try:
        response = requests.get(f"{api_base_url}/v2/locations", headers=headers)
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ ERROR: {response.text}")
            return
        
        locations_data = response.json()
        locations = locations_data.get('locations', [])
        
        print(f"✅ SUCCESS! Found {len(locations)} locations")
        
        if not locations:
            print("❌ No locations found")
            return
        
        # Show location details
        for i, location in enumerate(locations, 1):
            location_id = location.get('id')
            name = location.get('name', 'Unknown')
            status = location.get('status', 'Unknown')
            print(f"  Location {i}:")
            print(f"    ID: {location_id}")
            print(f"    Name: {name}")
            print(f"    Status: {status}")
        
        # Use first location for cash drawer
        location_id = locations[0].get('id')
        print(f"\n🎯 USING LOCATION_ID: {location_id}")
        
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")
        return
    
    # STEP 2: Use location_id for Cash Drawer API
    print(f"\n📡 STEP 2: GET CASH DRAWER DATA")
    
    # Try multiple cash drawer endpoints with location_id
    cash_endpoints = [
        (f"/v2/cash-drawers/{location_id}", "GET", None, "Cash Drawer Direct"),
        (f"/v2/cash-drawers/shifts?location_id={location_id}", "GET", None, "Cash Drawer Shifts with Param"),
        (f"/v2/cash-drawers/shifts/{location_id}", "GET", None, "Cash Drawer Shifts Direct")
    ]
    
    for endpoint, method, body, name in cash_endpoints:
        url = f"{api_base_url}{endpoint}"
        print(f"\n📞 TESTING {name.upper()}:")
        print(f"URL: {url}")
        print(f"Method: {method}")
        print(f"Location ID: {location_id}")
        
        try:
            if method == "POST":
                response = requests.post(url, headers=headers, json=body or {})
            else:
                response = requests.get(url, headers=headers)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS! Cash drawer data retrieved")
                
                # Show data structure
                print(f"Response keys: {list(data.keys())}")
                
                # Look for cash drawer shifts or data
                if 'shifts' in data:
                    shifts = data['shifts']
                    print(f"Found {len(shifts)} cash drawer shifts")
                    
                    for i, shift in enumerate(shifts[:3], 1):
                        shift_id = shift.get('id', 'N/A')
                        opened_at = shift.get('opened_at', 'N/A')
                        ended_at = shift.get('ended_at', 'N/A')
                        opening_cash = shift.get('opening_cash_money', {})
                        closing_cash = shift.get('closed_cash_money', {})
                        
                        opening_amount = float(opening_cash.get('amount', 0)) / 100 if opening_cash else 0
                        closing_amount = float(closing_cash.get('amount', 0)) / 100 if closing_cash else 0
                        
                        print(f"  Shift {i}:")
                        print(f"    ID: {shift_id}")
                        print(f"    Opened: {opened_at}")
                        print(f"    Closed: {ended_at}")
                        print(f"    Opening Cash: ${opening_amount:.2f}")
                        print(f"    Closing Cash: ${closing_amount:.2f}")
                
                elif 'cash_drawer' in data:
                    drawer = data['cash_drawer']
                    print(f"Cash drawer info: {drawer}")
                
                else:
                    print(f"Raw data: {json.dumps(data, indent=2)}")
                
                print(f"\n🎉 CASH DRAWER API: WORKING!")
                print(f"✅ Location ID: {location_id}")
                print(f"✅ Endpoint: {name}")
                print(f"✅ Real cash drawer data retrieved")
                
                return True
                
            elif response.status_code == 404:
                print(f"❌ NOT FOUND: {response.text}")
                
            elif response.status_code == 400:
                print(f"❌ BAD REQUEST: {response.text}")
                
            else:
                print(f"❌ ERROR {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ CONNECTION ERROR: {e}")
    
    print(f"\n❌ ALL CASH DRAWER ENDPOINTS FAILED")
    return False

if __name__ == "__main__":
    success = get_location_and_cash_drawer()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 LOCATION_ID AND CASH DRAWER: SUCCESS!")
        print("✅ Retrieved location_id from Locations API")
        print("✅ Used location_id for Cash Drawer API")
        print("✅ Cash drawer data retrieved")
    else:
        print("❌ CASH DRAWER API: STILL BLOCKED")
        print("⚠️  May require additional parameters or permissions")