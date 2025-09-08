#!/usr/bin/env python3
"""
GET TO 50,000 APPOINTMENT CHECKPOINT
- Current: 36,940 appointments
- Target: 50,000 appointments (checkpoint)
- Need: 13,060 more appointments
- Strategy: Focus on one high-activity period at a time
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_to_50k_checkpoint():
    """Get to 50,000 appointment checkpoint efficiently"""
    
    print("🎯 GET TO 50,000 APPOINTMENT CHECKPOINT")
    print("=" * 50)
    print("Current: 36,940 appointments")
    print("Checkpoint: 50,000 appointments") 
    print("Need: 13,060 more appointments")
    print("Focus: One high-activity period")
    
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
    
    # Focus on 2023 - likely high activity year
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    
    print(f"\n📅 FOCUSING ON 2023 (HIGH ACTIVITY YEAR)")
    print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    running_total = 36940
    new_appointments = []
    
    # Process in 2-month chunks for speed
    current_start = start_date
    chunk_count = 1
    
    while current_start <= end_date and running_total < 50000:
        chunk_end = min(current_start + timedelta(days=60), end_date)
        
        print(f"\n📊 CHUNK {chunk_count}: {current_start.strftime('%b %Y')} - {chunk_end.strftime('%b %Y')}")
        
        # Get appointments for this chunk
        chunk_appointments = []
        
        # Break into 31-day sub-chunks for API compliance
        sub_start = current_start
        while sub_start < chunk_end:
            sub_end = min(sub_start + timedelta(days=30), chunk_end)
            
            start_str = sub_start.strftime('%Y-%m-%dT00:00:00Z')
            end_str = sub_end.strftime('%Y-%m-%dT23:59:59Z')
            
            # Get appointments with pagination
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
                    
                    chunk_appointments.extend(bookings)
                    
                    if not cursor or len(bookings) == 0:
                        break
                        
                except Exception as e:
                    print(f"  ❌ Error: {e}")
                    break
            
            sub_start = sub_end + timedelta(days=1)
        
        # Update totals
        new_appointments.extend(chunk_appointments)
        running_total += len(chunk_appointments)
        
        print(f"  ✅ Found: {len(chunk_appointments):,} appointments")
        print(f"  📊 Running total: {running_total:,}")
        print(f"  📈 Progress to 50K: {(running_total / 50000) * 100:.1f}%")
        
        # Check if we hit 50K
        if running_total >= 50000:
            print(f"\n🎯 CHECKPOINT REACHED: {running_total:,} APPOINTMENTS!")
            print(f"✅ 50,000 appointment milestone achieved")
            print(f"✅ Progress to full target: {(running_total / 55236) * 100:.1f}%")
            break
        
        current_start = chunk_end + timedelta(days=1)
        chunk_count += 1
    
    # Save checkpoint progress
    if new_appointments:
        # Analyze team member data
        team_counts = {}
        for apt in new_appointments:
            segments = apt.get('appointment_segments', [])
            for segment in segments:
                tm_id = segment.get('team_member_id')
                if tm_id:
                    team_counts[tm_id] = team_counts.get(tm_id, 0) + 1
        
        # Save checkpoint
        checkpoint_data = {
            'checkpoint_50k': {
                'total_appointments': running_total,
                'checkpoint_achieved': running_total >= 50000,
                'new_appointments_added': len(new_appointments),
                'progress_to_55k': (running_total / 55236) * 100
            },
            'new_team_counts': team_counts,
            'sample_new_appointments': new_appointments[:5]
        }
        
        with open('/tmp/checkpoint_50k.json', 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
        
        print(f"\n💾 CHECKPOINT DATA SAVED: /tmp/checkpoint_50k.json")
        
        # Show top team members from new data
        if team_counts:
            print(f"\n👥 TOP TEAM MEMBERS (from new 2023 data):")
            sorted_members = sorted(team_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            for tm_id, count in sorted_members:
                print(f"  {tm_id}: {count:,} appointments")
    
    return running_total

if __name__ == "__main__":
    total = get_to_50k_checkpoint()
    
    print(f"\n" + "=" * 50)
    if total >= 50000:
        print("🎯 50K CHECKPOINT: ACHIEVED!")
        print(f"Total appointments: {total:,}")
        print(f"Ready to continue to 55,236 target")
    else:
        print(f"📊 Current progress: {total:,} appointments")
        print("Continue data retrieval")