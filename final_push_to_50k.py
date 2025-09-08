#!/usr/bin/env python3
"""
FINAL PUSH TO 50K CHECKPOINT
- Current: 46,766 appointments
- Target: 50,000 appointments
- Need: 3,234 more appointments
- Strategy: Try 2022 data (should be stable)
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def final_push_to_50k():
    """Final push to reach 50K checkpoint"""
    
    print("🏁 FINAL PUSH TO 50K CHECKPOINT")
    print("=" * 40)
    print("Current: 46,766 appointments")
    print("Target: 50,000 appointments")
    print("Need: 3,234 more appointments")
    print("Strategy: 2022 data (stable period)")
    
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
    
    # Try 2022 data in quarters
    quarters_2022 = [
        (datetime(2022, 1, 1), datetime(2022, 3, 31), "Q1 2022"),
        (datetime(2022, 4, 1), datetime(2022, 6, 30), "Q2 2022"),
        (datetime(2022, 7, 1), datetime(2022, 9, 30), "Q3 2022"),
        (datetime(2022, 10, 1), datetime(2022, 12, 31), "Q4 2022")
    ]
    
    running_total = 46766
    new_appointments = []
    
    for start_date, end_date, quarter_name in quarters_2022:
        if running_total >= 50000:
            break
            
        print(f"\n📅 PROCESSING {quarter_name}")
        print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        # Process quarter in monthly chunks
        current_start = start_date
        quarter_appointments = []
        
        while current_start <= end_date and running_total < 50000:
            # Monthly chunk within quarter
            month_end = datetime(current_start.year, current_start.month + 1, 1) - timedelta(days=1) if current_start.month < 12 else datetime(current_start.year, 12, 31)
            month_end = min(month_end, end_date)
            
            start_str = current_start.strftime('%Y-%m-%dT00:00:00Z')
            end_str = month_end.strftime('%Y-%m-%dT23:59:59Z')
            
            print(f"  📊 Month: {current_start.strftime('%b %Y')}")
            
            # Get appointments for this month
            month_appointments = []
            cursor = None
            
            while True:
                url = f"{api_base_url}/v2/bookings?limit=200&start_at_min={start_str}&start_at_max={end_str}"
                if cursor:
                    url += f"&cursor={cursor}"
                
                try:
                    response = requests.get(url, headers=headers)
                    
                    if response.status_code != 200:
                        print(f"    ❌ API Error: {response.status_code}")
                        break
                    
                    data = response.json()
                    bookings = data.get('bookings', [])
                    cursor = data.get('cursor')
                    
                    month_appointments.extend(bookings)
                    
                    if not cursor or len(bookings) == 0:
                        break
                        
                except Exception as e:
                    print(f"    ❌ Error: {e}")
                    break
            
            quarter_appointments.extend(month_appointments)
            print(f"    ✅ Found: {len(month_appointments):,} appointments")
            
            # Move to next month
            if current_start.month == 12:
                current_start = datetime(current_start.year + 1, 1, 1)
            else:
                current_start = datetime(current_start.year, current_start.month + 1, 1)
        
        # Update totals for quarter
        new_appointments.extend(quarter_appointments)
        running_total += len(quarter_appointments)
        
        print(f"  📊 {quarter_name} total: {len(quarter_appointments):,} appointments")
        print(f"  📊 Running total: {running_total:,}")
        print(f"  🎯 Progress to 50K: {(running_total / 50000) * 100:.1f}%")
        
        if running_total >= 50000:
            print(f"\n🏆 50K CHECKPOINT ACHIEVED!")
            print(f"✅ Final total: {running_total:,} appointments")
            break
        else:
            print(f"  📈 Still need: {50000 - running_total:,} appointments")
    
    # Final checkpoint save
    if running_total >= 50000:
        checkpoint_data = {
            'milestone_50k': {
                'total_appointments': running_total,
                'checkpoint_achieved': True,
                'target_progress': (running_total / 55236) * 100,
                'final_push_added': len(new_appointments),
                'ready_for_utilization_fix': True
            }
        }
        
        with open('/tmp/milestone_50k_achieved.json', 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
        
        print(f"\n🎯 MILESTONE ACHIEVED!")
        print(f"Total appointments: {running_total:,}")
        print(f"Progress to 55,236: {(running_total / 55236) * 100:.1f}%")
        print(f"Remaining to full target: {55236 - running_total:,}")
        print(f"✅ Ready to proceed with utilization calculations")
        
        return running_total, True
    
    else:
        print(f"\n📊 Current total: {running_total:,}")
        print(f"Still {50000 - running_total:,} short of 50K checkpoint")
        return running_total, False

if __name__ == "__main__":
    total, achieved = final_push_to_50k()
    
    print(f"\n" + "=" * 40)
    if achieved:
        print("🏆 50K MILESTONE: ACHIEVED!")
        print("Ready to continue data collection or fix utilization")
    else:
        print(f"📊 Current: {total:,} appointments")
        print("Continue working toward 50K checkpoint")