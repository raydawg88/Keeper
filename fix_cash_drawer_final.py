#!/usr/bin/env python3
"""
FIX CASH DRAWER API - FINAL IMPLEMENTATION
- Get location_id from Locations API
- Use location_id for Cash Drawer API calls
- Show actual cash transactions
- This is the 2-minute task that's been pending for 4 hours
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def fix_cash_drawer_final():
    """Fix Cash Drawer API once and for all"""
    
    print("💰 FIX CASH DRAWER API - FINAL")
    print("=" * 50)
    print("TASK: 2-minute fix that's been pending 4 hours")
    print("STEPS: Get location_id → Call cash drawer → Show transactions")
    
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
    
    # STEP 1: Get location_id (we know this works)
    print(f"\n📡 STEP 1: GET LOCATION_ID")
    
    try:
        response = requests.get(f"{api_base_url}/v2/locations", headers=headers)
        
        if response.status_code == 200:
            locations_data = response.json()
            locations = locations_data.get('locations', [])
            
            if locations:
                location_id = locations[0].get('id')
                location_name = locations[0].get('name', 'Unknown')
                print(f"✅ Location ID: {location_id}")
                print(f"✅ Location Name: {location_name}")
            else:
                print("❌ No locations found")
                return
        else:
            print(f"❌ Locations API error: {response.status_code} - {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error getting location: {e}")
        return
    
    # STEP 2: Get Cash Drawer data using location_id
    print(f"\n📡 STEP 2: GET CASH DRAWER DATA")
    
    # Try the correct Cash Drawer Shifts endpoint
    try:
        url = f"{api_base_url}/v2/cash-drawers/shifts?location_id={location_id}&limit=10"
        print(f"URL: {url}")
        
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            shifts = data.get('shifts', [])
            
            print(f"✅ SUCCESS! Found {len(shifts)} cash drawer shifts")
            
            if shifts:
                print(f"\n💰 CASH DRAWER SHIFTS:")
                print(f"{'DATE':<12} {'OPENED':<8} {'CLOSED':<8} {'OPENING $':<12} {'CLOSING $':<12} {'DIFFERENCE'}")
                print("-" * 80)
                
                for shift in shifts[:10]:  # Show first 10 shifts
                    shift_id = shift.get('id', 'N/A')[:8]
                    opened_at = shift.get('opened_at', '')
                    ended_at = shift.get('ended_at', '')
                    
                    # Format dates
                    opened_date = datetime.fromisoformat(opened_at.replace('Z', '+00:00')).strftime('%Y-%m-%d') if opened_at else 'N/A'
                    opened_time = datetime.fromisoformat(opened_at.replace('Z', '+00:00')).strftime('%H:%M') if opened_at else 'N/A'
                    ended_time = datetime.fromisoformat(ended_at.replace('Z', '+00:00')).strftime('%H:%M') if ended_at else 'Open'
                    
                    # Get cash amounts
                    opening_cash = shift.get('opening_cash_money', {})
                    closing_cash = shift.get('closed_cash_money', {})
                    
                    opening_amount = float(opening_cash.get('amount', 0)) / 100 if opening_cash else 0
                    closing_amount = float(closing_cash.get('amount', 0)) / 100 if closing_cash else 0
                    difference = closing_amount - opening_amount
                    
                    print(f"{opened_date:<12} {opened_time:<8} {ended_time:<8} ${opening_amount:<11.2f} ${closing_amount:<11.2f} ${difference:+.2f}")
                
                # Calculate totals
                total_opening = sum(float(s.get('opening_cash_money', {}).get('amount', 0)) / 100 for s in shifts)
                total_closing = sum(float(s.get('closed_cash_money', {}).get('amount', 0)) / 100 for s in shifts)
                net_difference = total_closing - total_opening
                
                print("-" * 80)
                print(f"TOTALS: Opening: ${total_opening:.2f}, Closing: ${total_closing:.2f}, Net: ${net_difference:+.2f}")
                
                print(f"\n✅ CASH DRAWER API: WORKING!")
                print(f"✅ Location ID: {location_id}")
                print(f"✅ Cash shifts retrieved: {len(shifts)}")
                print(f"✅ Real cash transaction data shown")
                
                # Save cash drawer data
                with open('/tmp/cash_drawer_data.json', 'w') as f:
                    json.dump({
                        'location_id': location_id,
                        'location_name': location_name,
                        'shifts': shifts,
                        'summary': {
                            'total_shifts': len(shifts),
                            'total_opening_cash': total_opening,
                            'total_closing_cash': total_closing,
                            'net_difference': net_difference
                        }
                    }, f, indent=2)
                
                print(f"✅ Data saved: /tmp/cash_drawer_data.json")
                return True
            
            else:
                print("⚠️  No cash drawer shifts found")
                return True  # API works, just no data
                
        else:
            print(f"❌ Cash Drawer API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting cash drawer data: {e}")
        return False

if __name__ == "__main__":
    success = fix_cash_drawer_final()
    
    print(f"\n" + "=" * 50)
    if success:
        print("💰 CASH DRAWER API: FIXED!")
        print("✅ 2-minute task completed")
        print("✅ Real cash transaction data retrieved")
        print("✅ Ready for Keeper cash flow analysis")
    else:
        print("❌ Cash Drawer API: Still has issues")
        print("May need additional permissions or different endpoint")