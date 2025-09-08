#!/usr/bin/env python3
"""
CONTINUE TO 50K CHECKPOINT
- Current: 46,014 appointments
- Target: 50,000 appointments
- Need: 3,986 more appointments
- Strategy: Focus on 2024 data (recent high activity)
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def continue_to_50k():
    """Continue to 50K checkpoint with 2024 data"""
    
    print("🎯 CONTINUE TO 50K CHECKPOINT")
    print("=" * 40)
    print("Current: 46,014 appointments")
    print("Target: 50,000 appointments")
    print("Need: 3,986 more appointments")
    print("Strategy: 2024 data (recent high activity)")
    
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
    
    # Focus on first half of 2024
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 6, 30)
    
    print(f"\n📅 FOCUSING ON EARLY 2024")
    print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    running_total = 46014
    new_appointments = []
    
    # Process in monthly chunks
    current_start = start_date
    month_count = 1
    
    while current_start <= end_date and running_total < 50000:
        # Monthly chunk
        if current_start.month == 12:
            chunk_end = datetime(current_start.year + 1, 1, 31)
        else:
            next_month = current_start.month + 1
            chunk_end = datetime(current_start.year, next_month, min(28, 31))
        
        chunk_end = min(chunk_end, end_date)
        
        print(f"\n📊 MONTH {month_count}: {current_start.strftime('%b %Y')}")
        
        # Get appointments for this month
        start_str = current_start.strftime('%Y-%m-%dT00:00:00Z')
        end_str = chunk_end.strftime('%Y-%m-%dT23:59:59Z')
        
        month_appointments = []
        cursor = None
        
        while True:
            url = f"{api_base_url}/v2/bookings?limit=200&start_at_min={start_str}&start_at_max={end_str}"
            if cursor:
                url += f"&cursor={cursor}"
            
            try:
                response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    print(f"  ❌ API Error: {response.status_code}")
                    break
                
                data = response.json()
                bookings = data.get('bookings', [])
                cursor = data.get('cursor')
                
                month_appointments.extend(bookings)
                
                if not cursor or len(bookings) == 0:
                    break
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
                break
        
        # Update totals
        new_appointments.extend(month_appointments)
        running_total += len(month_appointments)
        
        print(f"  ✅ Found: {len(month_appointments):,} appointments")
        print(f"  📊 Running total: {running_total:,}")
        print(f"  🎯 Progress to 50K: {(running_total / 50000) * 100:.1f}%")
        print(f"  📈 Still need: {50000 - running_total:,} appointments")
        
        # Check if we hit 50K
        if running_total >= 50000:
            print(f"\n🏆 50K CHECKPOINT REACHED!")
            print(f"✅ Total appointments: {running_total:,}")
            print(f"✅ Milestone achieved!")
            print(f"✅ Progress to 55,236 target: {(running_total / 55236) * 100:.1f}%")
            break
        
        # Move to next month
        if current_start.month == 12:
            current_start = datetime(current_start.year + 1, 1, 1)
        else:
            current_start = datetime(current_start.year, current_start.month + 1, 1)
        month_count += 1
    
    # Save 50K checkpoint
    if running_total >= 50000:
        # Analyze team member data from all new appointments
        team_counts = {}
        for apt in new_appointments:
            segments = apt.get('appointment_segments', [])
            for segment in segments:
                tm_id = segment.get('team_member_id')
                if tm_id:
                    team_counts[tm_id] = team_counts.get(tm_id, 0) + 1
        
        checkpoint_data = {
            'checkpoint_50k_achieved': {
                'total_appointments': running_total,
                'milestone_reached': True,
                'progress_to_full_target': (running_total / 55236) * 100,
                'appointments_added_today': len(new_appointments)
            },
            'team_counts_2024': team_counts,
            'ready_for_next_phase': True
        }
        
        with open('/tmp/50k_checkpoint_achieved.json', 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
        
        print(f"\n💾 50K CHECKPOINT SAVED: /tmp/50k_checkpoint_achieved.json")
        
        # Show team performance from new data
        if team_counts:
            print(f"\n👥 TOP PERFORMERS (2024 data added):")
            sorted_members = sorted(team_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            for tm_id, count in sorted_members:
                print(f"  {tm_id}: {count:,} appointments")
        
        print(f"\n🚀 READY FOR NEXT PHASE:")
        print(f"✅ 50,000 appointment checkpoint achieved")
        print(f"✅ {(running_total / 55236) * 100:.1f}% progress to full target")
        print(f"✅ {55236 - running_total:,} appointments remaining to 100%")
        print(f"✅ Can now proceed with more targeted data collection")
        
        return running_total, True
    
    else:
        print(f"\n📊 Current progress: {running_total:,} appointments")
        print(f"Still need: {50000 - running_total:,} for 50K checkpoint")
        return running_total, False

if __name__ == "__main__":
    total, reached_50k = continue_to_50k()
    
    print(f"\n" + "=" * 40)
    if reached_50k:
        print("🏆 50K CHECKPOINT: ACHIEVED!")
        print("Ready to continue to full 55,236 target")
    else:
        print(f"📊 Progress: {total:,} / 50,000 appointments")
        print("Continue data collection")