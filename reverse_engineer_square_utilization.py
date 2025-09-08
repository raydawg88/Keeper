#!/usr/bin/env python3
"""
REVERSE-ENGINEER SQUARE'S UTILIZATION FORMULA
- Stop inventing formulas - analyze the data to find Square's logic
- Target: Match Square's 60% (Laine), 58% (Tayler), 69% (Rylie)
- Test: Booked hours / available appointment slots (not service duration)
- Method: Work backwards from known Square results
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def reverse_engineer_square_utilization():
    """Reverse engineer Square's utilization calculation from known results"""
    
    print("🔍 REVERSE-ENGINEER SQUARE'S UTILIZATION FORMULA")
    print("=" * 60)
    print("STOP INVENTING - ANALYZE THE DATA")
    print("Square's actual data:")
    print("  • Laine: 60% utilization, 1,165 appointments (2025 YTD)")
    print("  • Tayler: 58% utilization, 1,247 appointments") 
    print("  • Rylie: 69% utilization, 1,311 appointments")
    print("  • Alicia: 58% utilization, 347 appointments")
    
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
    
    # Get recent appointments to analyze booking patterns
    print(f"\n📅 GET 2025 YTD APPOINTMENT DATA")
    
    # Get appointments from Jan 1, 2025 to now
    start_date = datetime(2025, 1, 1)
    end_date = datetime.now()
    
    all_2025_appointments = []
    current_start = start_date
    
    while current_start < end_date:
        chunk_end = min(current_start + timedelta(days=30), end_date)
        
        start_str = current_start.strftime('%Y-%m-%dT00:00:00Z')
        end_str = chunk_end.strftime('%Y-%m-%dT23:59:59Z')
        
        print(f"📡 Getting appointments: {current_start.strftime('%Y-%m-%d')} to {chunk_end.strftime('%Y-%m-%d')}")
        
        cursor = None
        while True:
            url = f"{api_base_url}/v2/bookings?limit=200&start_at_min={start_str}&start_at_max={end_str}"
            if cursor:
                url += f"&cursor={cursor}"
            
            try:
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    break
                
                data = response.json()
                bookings = data.get('bookings', [])
                all_2025_appointments.extend(bookings)
                
                cursor = data.get('cursor')
                if not cursor:
                    break
                    
            except Exception as e:
                break
        
        current_start = chunk_end + timedelta(days=1)
    
    print(f"✅ Retrieved {len(all_2025_appointments)} appointments for 2025 YTD")
    
    # Analyze by team member
    team_member_data = {}
    
    for apt in all_2025_appointments:
        segments = apt.get('appointment_segments', [])
        for segment in segments:
            tm_id = segment.get('team_member_id')
            if tm_id:
                if tm_id not in team_member_data:
                    team_member_data[tm_id] = {
                        'appointments': 0,
                        'total_duration': 0,
                        'booking_dates': [],
                        'time_slots': []
                    }
                
                team_member_data[tm_id]['appointments'] += 1
                team_member_data[tm_id]['total_duration'] += segment.get('duration_minutes', 0)
                
                # Track booking time slots
                start_at = apt.get('start_at', '')
                if start_at:
                    try:
                        start_time = datetime.fromisoformat(start_at.replace('Z', '+00:00'))
                        team_member_data[tm_id]['booking_dates'].append(start_time.date())
                        team_member_data[tm_id]['time_slots'].append(start_time.hour)
                    except:
                        pass
    
    # Load team member names
    try:
        with open('/tmp/team_member_id_name_mapping.json', 'r') as f:
            mapping_data = json.load(f)
        team_mapping = mapping_data['id_to_name_mapping']
    except:
        print("❌ No team member mapping found")
        return
    
    # Focus on the employees with known Square utilization
    target_employees = {
        'TMZx2T5T5arYJTm7': {'name': 'Laine Duttlinger', 'square_util': 60, 'square_apts': 1165},
        'TMOUvfuW75DecX_G': {'name': 'Tayler Brunson', 'square_util': 58, 'square_apts': 1247},
        'TMS2RK9gqIP7bVqw': {'name': 'Rylie Calverley', 'square_util': 69, 'square_apts': 1311},
        'tm-11qEVpGsodHy7WNM4': {'name': 'Alicia Cardenas', 'square_util': 58, 'square_apts': 347}
    }
    
    print(f"\n🧮 REVERSE-ENGINEERING UTILIZATION FORMULAS")
    print("=" * 60)
    
    # Calculate months YTD
    months_ytd = datetime.now().month
    
    for tm_id, target_data in target_employees.items():
        if tm_id not in team_member_data:
            print(f"⚠️  {target_data['name']}: No appointment data found")
            continue
            
        data = team_member_data[tm_id]
        name = target_data['name']
        square_util = target_data['square_util']
        square_apts = target_data['square_apts']
        my_apts = data['appointments']
        
        print(f"\n👤 {name}")
        print(f"Square data: {square_util}% util, {square_apts} appointments")
        print(f"My data: {my_apts} appointments")
        
        if my_apts != square_apts:
            print(f"⚠️  Appointment count mismatch - may affect calculation")
        
        # Test different formulas to find what gives ~60% for Laine
        total_duration_hours = data['total_duration'] / 60
        unique_dates = len(set(data['booking_dates']))
        avg_apts_per_day = my_apts / unique_dates if unique_dates > 0 else 0
        
        print(f"Analysis:")
        print(f"  Total service hours: {total_duration_hours:.1f}")
        print(f"  Unique booking dates: {unique_dates}")
        print(f"  Avg appointments/day: {avg_apts_per_day:.1f}")
        
        # FORMULA TESTS - work backwards from Square's result
        print(f"\nFormula Tests:")
        
        # Test 1: Appointments / Working Days
        working_days_estimate = months_ytd * 22  # ~22 working days/month
        formula1 = (my_apts / working_days_estimate) * 100
        print(f"  Appointments/Working Days: {formula1:.1f}% (target: {square_util}%)")
        
        # Test 2: Service Hours / Available Hours (different hour assumptions)
        for daily_hours in [8, 10, 12]:
            available_hours = months_ytd * 22 * daily_hours
            formula2 = (total_duration_hours / available_hours) * 100
            print(f"  Service Hours/{daily_hours}h days: {formula2:.1f}% (target: {square_util}%)")
        
        # Test 3: Appointments / Available Slots (30-min slots)
        for slots_per_day in [16, 20, 24]:  # 8-12 hours of 30-min slots
            available_slots = months_ytd * 22 * slots_per_day
            formula3 = (my_apts / available_slots) * 100
            print(f"  Appointments/{slots_per_day} slots/day: {formula3:.1f}% (target: {square_util}%)")
        
        # Test 4: Booked Days / Available Days
        available_days = months_ytd * 22
        formula4 = (unique_dates / available_days) * 100
        print(f"  Booked Days/Available Days: {formula4:.1f}% (target: {square_util}%)")
        
        # Find closest match
        tests = [
            ("Appointments/Working Days", formula1),
            ("Service Hours/10h days", (total_duration_hours / (months_ytd * 22 * 10)) * 100),
            ("Appointments/20 slots", (my_apts / (months_ytd * 22 * 20)) * 100),
            ("Booked Days/Available", formula4)
        ]
        
        closest_diff = float('inf')
        closest_formula = None
        
        for formula_name, result in tests:
            diff = abs(result - square_util)
            if diff < closest_diff:
                closest_diff = diff
                closest_formula = (formula_name, result)
        
        print(f"\n✅ CLOSEST MATCH: {closest_formula[0]}")
        print(f"   Result: {closest_formula[1]:.1f}% (diff: {closest_diff:.1f}%)")
    
    # IDENTIFY THE PATTERN
    print(f"\n🎯 IDENTIFYING SQUARE'S PATTERN")
    print("=" * 50)
    
    # If we find a consistent formula that works for multiple employees,
    # that's likely Square's method
    print("Looking for consistent formula across all employees...")
    
    # Save analysis results
    analysis_results = {
        'employees_analyzed': len(target_employees),
        'appointments_retrieved': len(all_2025_appointments),
        'team_member_data': {tm_id: {
            'name': team_mapping.get(tm_id, {}).get('name', 'Unknown'),
            'appointments': data['appointments'],
            'total_duration': data['total_duration'],
            'unique_dates': len(set(data['booking_dates']))
        } for tm_id, data in team_member_data.items() if tm_id in target_employees}
    }
    
    with open('/tmp/utilization_analysis.json', 'w') as f:
        json.dump(analysis_results, f, indent=2)
    
    print(f"✅ Analysis saved: /tmp/utilization_analysis.json")
    
    return analysis_results

if __name__ == "__main__":
    results = reverse_engineer_square_utilization()
    
    print(f"\n" + "=" * 60)
    print("🔍 UTILIZATION REVERSE-ENGINEERING: IN PROGRESS")
    print("✅ Retrieved 2025 YTD appointment data")
    print("✅ Tested multiple formulas against Square's results")
    print("🔄 Need to find the exact formula that consistently matches")
    print("📊 Ready to implement Square's actual logic once identified")