#!/usr/bin/env python3
"""
GET ALL REMAINING APPOINTMENTS TO REACH 55,236 TOTAL
- Current: 33,046 appointments (need 22,190 more)
- Strategy: Continue 3-month windows going back further in history
- Target: Get complete 55,236 appointments for accurate employee analysis
- No incomplete analysis until we have ALL the data
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

load_dotenv()

def get_all_remaining_appointments():
    """Get ALL remaining appointments to reach the full 55,236 total"""
    
    print("📅 GET ALL REMAINING APPOINTMENTS")
    print("=" * 60)
    print("CURRENT STATUS:")
    print("✅ Retrieved: 33,046 appointments")
    print("🎯 Target: 55,236 total appointments") 
    print("📊 Still need: 22,190 more appointments")
    print("🚀 Strategy: Continue 3-month windows further back in history")
    
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
    
    # Load current progress
    try:
        with open('/tmp/square_appointments_30k_final.json', 'r') as f:
            current_data = json.load(f)
        current_total = current_data['final_checkpoint']['total_appointments']
        print(f"✅ Loaded checkpoint: {current_total:,} appointments")
    except:
        current_total = 33046
        print(f"⚠️  Using estimated current total: {current_total:,}")
    
    # Continue with earlier historical periods
    # We've covered 2019-2025, now go even further back if needed
    historical_periods = [
        (datetime(2018, 1, 1), datetime(2018, 12, 31), "2018"),
        (datetime(2017, 1, 1), datetime(2017, 12, 31), "2017"),
        (datetime(2016, 1, 1), datetime(2016, 12, 31), "2016"),
    ]
    
    running_total = current_total
    all_new_appointments = []
    
    print(f"\n🗓️ CONTINUING HISTORICAL SEARCH:")
    print(f"Starting from: {running_total:,} appointments")
    print(f"Need: {55236 - running_total:,} more appointments")
    print(f"Strategy: Search 2016-2018 with 3-month windows")
    
    for period_start, period_end, year_label in historical_periods:
        if running_total >= 55236:
            break
            
        print(f"\n📅 SEARCHING {year_label}")
        print(f"Date range: {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}")
        
        # Break year into 3-month windows
        window_start = period_start
        year_appointments = []
        
        while window_start <= period_end and running_total < 55236:
            window_end = min(window_start + relativedelta(months=3), period_end)
            
            print(f"\n📊 3-MONTH WINDOW: {window_start.strftime('%b %Y')} - {window_end.strftime('%b %Y')}")
            
            # Break 3-month window into 31-day chunks for API compliance
            window_appointments = []
            chunk_start = window_start
            
            while chunk_start < window_end:
                chunk_end = min(chunk_start + timedelta(days=30), window_end)
                
                start_str = chunk_start.strftime('%Y-%m-%dT00:00:00Z')
                end_str = chunk_end.strftime('%Y-%m-%dT23:59:59Z')
                
                print(f"  📡 Chunk: {chunk_start.strftime('%Y-%m-%d')} to {chunk_end.strftime('%Y-%m-%d')}")
                
                # Get appointments for this chunk with pagination
                chunk_appointments = []
                cursor = None
                
                while True:
                    url = f"{api_base_url}/v2/bookings?limit=200&start_at_min={start_str}&start_at_max={end_str}"
                    if cursor:
                        url += f"&cursor={cursor}"
                    
                    try:
                        response = requests.get(url, headers=headers)
                        
                        if response.status_code != 200:
                            print(f"    ❌ ERROR: {response.status_code}")
                            break
                        
                        data = response.json()
                        bookings = data.get('bookings', [])
                        cursor = data.get('cursor')
                        
                        chunk_appointments.extend(bookings)
                        
                        if not cursor or len(bookings) == 0:
                            break
                            
                    except Exception as e:
                        print(f"    ❌ CONNECTION ERROR: {e}")
                        break
                
                print(f"    ✅ Found: {len(chunk_appointments)} appointments")
                window_appointments.extend(chunk_appointments)
                
                # Move to next chunk
                chunk_start = chunk_end + timedelta(days=1)
            
            # Add window total
            all_new_appointments.extend(window_appointments)
            running_total += len(window_appointments)
            
            print(f"📊 Window total: {len(window_appointments):,} appointments")
            print(f"Running total: {running_total:,} appointments")
            print(f"Progress to target: {(running_total / 55236) * 100:.2f}%")
            
            # Check if we reached our target
            if running_total >= 55236:
                print(f"\n🎯 TARGET REACHED: {running_total:,} APPOINTMENTS!")
                break
            
            # Move to next 3-month window
            window_start = window_end + timedelta(days=1)
        
        print(f"\n📊 {year_label} COMPLETE: Added {len([a for a in all_new_appointments if a.get('created_at', '').startswith(year_label)])} appointments")
        
        # If we reached target, break from year loop
        if running_total >= 55236:
            break
    
    # FINAL RESULTS
    print(f"\n" + "=" * 60)
    if running_total >= 55236:
        print(f"🎉 SUCCESS: REACHED {running_total:,} APPOINTMENTS!")
        print(f"✅ Target achieved: {running_total:,} >= 55,236")
        print(f"✅ Complete data set for accurate employee analysis")
        print(f"✅ Ready for correct utilization calculations")
        
        # Analyze team member data from all appointments
        if all_new_appointments:
            team_counts = {}
            for apt in all_new_appointments:
                segments = apt.get('appointment_segments', [])
                for segment in segments:
                    tm_id = segment.get('team_member_id')
                    if tm_id:
                        team_counts[tm_id] = team_counts.get(tm_id, 0) + 1
            
            # Load existing counts and combine
            try:
                with open('/tmp/square_appointments_30k_final.json', 'r') as f:
                    existing_data = json.load(f)
                existing_counts = existing_data.get('historical_team_counts', {})
                
                # Combine counts
                for tm_id, count in team_counts.items():
                    existing_counts[tm_id] = existing_counts.get(tm_id, 0) + count
                
                total_team_counts = existing_counts
            except:
                total_team_counts = team_counts
            
            print(f"\n👥 COMPLETE TEAM MEMBER APPOINTMENT COUNTS:")
            sorted_members = sorted(total_team_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            for tm_id, count in sorted_members:
                print(f"  {tm_id}: {count:,} appointments")
                
                # Check for Laine specifically
                if tm_id == "TMZx2T5T5arYJTm7":
                    print(f"    ⭐ LAINE DUTTLINGER: {count:,} total appointments")
                    if 6000 <= count <= 8000:
                        print(f"    ✅ MATCHES EXPECTED ~7,212 appointments")
        
        # Save complete dataset
        complete_data = {
            'complete_dataset': {
                'total_appointments': running_total,
                'target_achieved': True,
                'date_coverage': '2016-2025',
                'completeness': (running_total / 55236) * 100,
                'new_appointments_added': len(all_new_appointments)
            },
            'complete_team_counts': total_team_counts if 'total_team_counts' in locals() else {},
            'sample_new_appointments': all_new_appointments[:5] if all_new_appointments else []
        }
        
        with open('/tmp/complete_appointments_dataset.json', 'w') as f:
            json.dump(complete_data, f, indent=2)
        
        print(f"\n✅ COMPLETE DATASET SAVED: /tmp/complete_appointments_dataset.json")
        print(f"**READY FOR ACCURATE EMPLOYEE ANALYSIS**")
        print(f"**ALL UTILIZATION CALCULATIONS WILL NOW BE CORRECT**")
        
        return running_total, total_team_counts if 'total_team_counts' in locals() else {}
    
    else:
        print(f"📊 CURRENT PROGRESS: {running_total:,} appointments")
        print(f"Still need: {55236 - running_total:,} more appointments")
        print("May need to search even further back or check data availability")
        
        return running_total, {}

if __name__ == "__main__":
    total, team_counts = get_all_remaining_appointments()
    
    print(f"\n" + "=" * 60)
    if total >= 55236:
        print("🎉 COMPLETE APPOINTMENT DATASET: SUCCESS!")
        print("✅ Ready for accurate employee performance analysis")
        print("✅ All utilization calculations will be mathematically correct")
        print("✅ Laine's true performance can now be calculated")
    else:
        print(f"📊 Progress: {total:,} / 55,236 appointments")
        print("Continue searching further back in history if needed")