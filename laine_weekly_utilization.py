#!/usr/bin/env python3
"""
EXPANDED UTILIZATION CALCULATION FOR LAINE
- Full week (Sept 1-7, 2025)  
- Examine actual services booked
- Check if durations are correct or missing data
- Compare to 40 hour work week
- Then get monthly data
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def laine_weekly_utilization():
    """Calculate Laine's utilization for full week with service details"""
    
    print("📅 LAINE'S WEEKLY UTILIZATION ANALYSIS")
    print("=" * 60)
    print("Employee: Laine Duttlinger")
    print("Period: September 1-7, 2025 (FULL WEEK)")
    print("Expected: Compare to 40 hour work week")
    
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
    
    # Laine Duttlinger's team member ID (ACTIVE)
    laine_id = "TMZx2T5T5arYJTm7"
    
    # Define full week: September 1-7, 2025
    start_date = datetime(2025, 9, 1)  # Sunday
    end_date = datetime(2025, 9, 7)    # Saturday
    
    start_str = start_date.strftime('%Y-%m-%dT00:00:00Z')
    end_str = (end_date + timedelta(days=1) - timedelta(seconds=1)).strftime('%Y-%m-%dT23:59:59Z')
    
    print(f"Time range: {start_str} to {end_str}")
    
    # ==============================================================
    # GET FULL WEEK OF APPOINTMENTS
    # ==============================================================
    print(f"\n📋 STEP 1: GET LAINE'S APPOINTMENTS FOR FULL WEEK")
    print("=" * 50)
    
    laine_appointments = []
    cursor = None
    
    while True:
        url = f"{api_base_url}/v2/bookings?limit=200&start_at_min={start_str}&start_at_max={end_str}"
        if cursor:
            url += f"&cursor={cursor}"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                bookings = data.get('bookings', [])
                
                # Filter for Laine's appointments
                for apt in bookings:
                    segments = apt.get('appointment_segments', [])
                    for segment in segments:
                        if segment.get('team_member_id') == laine_id:
                            laine_appointments.append({
                                'appointment_id': apt.get('id'),
                                'start_at': apt.get('start_at'),
                                'status': apt.get('status'),
                                'segment': segment,
                                'full_booking': apt
                            })
                
                cursor = data.get('cursor')
                if not cursor:
                    break
            else:
                print(f"❌ API error: {response.status_code}")
                break
        except Exception as e:
            print(f"❌ Error: {e}")
            break
    
    print(f"✅ Found {len(laine_appointments)} appointments for Laine across full week")
    
    # ==============================================================
    # GET SERVICE CATALOG FOR PROPER NAMES
    # ==============================================================
    print(f"\n🛍️  STEP 2: GET SERVICE CATALOG FOR PROPER NAMES")
    print("=" * 45)
    
    # Get catalog items to understand services
    service_catalog = {}
    try:
        catalog_url = f"{api_base_url}/v2/catalog/list?types=ITEM"
        response = requests.get(catalog_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            objects = data.get('objects', [])
            
            for obj in objects:
                if obj.get('type') == 'ITEM':
                    item_id = obj.get('id')
                    item_data = obj.get('item_data', {})
                    name = item_data.get('name', 'Unknown Service')
                    
                    # Also check variations
                    variations = item_data.get('variations', [])
                    for variation in variations:
                        variation_id = variation.get('id')
                        variation_data = variation.get('item_variation_data', {})
                        variation_name = variation_data.get('name', name)
                        service_catalog[variation_id] = {
                            'name': variation_name,
                            'parent_name': name
                        }
            
            print(f"✅ Loaded {len(service_catalog)} service variations")
            
        else:
            print(f"⚠️  Could not load service catalog: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️  Error loading catalog: {e}")
    
    # ==============================================================
    # ANALYZE APPOINTMENTS BY DAY
    # ==============================================================
    print(f"\n📊 STEP 3: WEEKLY APPOINTMENT BREAKDOWN")
    print("=" * 40)
    
    # Group by day
    appointments_by_day = {}
    total_week_minutes = 0
    
    for apt in laine_appointments:
        start_time_str = apt['start_at']
        start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        day_str = start_time.strftime('%Y-%m-%d (%A)')
        
        if day_str not in appointments_by_day:
            appointments_by_day[day_str] = []
        
        appointments_by_day[day_str].append(apt)
    
    print(f"Daily breakdown:")
    print(f"{'DAY':<20} {'APPOINTMENTS':<12} {'DURATION':<10} {'SERVICES'}")
    print("-" * 80)
    
    for day_str in sorted(appointments_by_day.keys()):
        day_appointments = appointments_by_day[day_str]
        day_minutes = 0
        
        service_list = []
        for apt in day_appointments:
            segment = apt['segment']
            duration_minutes = segment.get('duration_minutes', 0)
            day_minutes += duration_minutes
            
            # Get service name
            service_variation_id = segment.get('service_variation_id', '')
            if service_variation_id in service_catalog:
                service_name = service_catalog[service_variation_id]['name']
            else:
                service_name = service_variation_id[:15] + "..." if service_variation_id else "Unknown"
            
            service_list.append(f"{service_name}({duration_minutes}min)")
        
        total_week_minutes += day_minutes
        services_display = ", ".join(service_list)
        
        print(f"{day_str:<20} {len(day_appointments):<12} {day_minutes}min ({day_minutes/60:.1f}h) {services_display}")
    
    total_week_hours = total_week_minutes / 60
    
    print("-" * 80)
    print(f"WEEK TOTALS:")
    print(f"  Total appointments: {len(laine_appointments)}")
    print(f"  Total minutes: {total_week_minutes}")
    print(f"  Total hours: {total_week_hours:.2f}")
    
    # ==============================================================
    # CHECK FOR SUSPICIOUS SHORT DURATIONS
    # ==============================================================
    print(f"\n🔍 STEP 4: DURATION ANALYSIS")
    print("=" * 30)
    
    print("Analyzing appointment durations for accuracy:")
    
    duration_breakdown = {}
    short_appointments = []
    
    for apt in laine_appointments:
        segment = apt['segment']
        duration_minutes = segment.get('duration_minutes', 0)
        
        if duration_minutes not in duration_breakdown:
            duration_breakdown[duration_minutes] = 0
        duration_breakdown[duration_minutes] += 1
        
        if duration_minutes <= 10:  # Flag very short appointments
            service_variation_id = segment.get('service_variation_id', '')
            service_name = service_catalog.get(service_variation_id, {}).get('name', 'Unknown')
            short_appointments.append({
                'duration': duration_minutes,
                'service': service_name,
                'start_time': apt['start_at']
            })
    
    print(f"Duration distribution:")
    for duration in sorted(duration_breakdown.keys()):
        count = duration_breakdown[duration]
        print(f"  {duration} minutes: {count} appointments")
    
    if short_appointments:
        print(f"\n⚠️  SUSPICIOUS SHORT APPOINTMENTS ({len(short_appointments)} found):")
        for short in short_appointments:
            print(f"  • {short['duration']} min - {short['service']} at {short['start_time'][11:16]}")
        
        print(f"\nPOSSIBLE CAUSES:")
        print(f"  - Buffer/prep time between services")
        print(f"  - Quick add-on services")
        print(f"  - Data entry errors")
        print(f"  - Missing actual service duration")
    
    # ==============================================================
    # CALCULATE WEEKLY UTILIZATION
    # ==============================================================
    print(f"\n🎯 STEP 5: WEEKLY UTILIZATION CALCULATION")
    print("=" * 40)
    
    # Standard work week assumptions
    standard_work_week = 40  # hours
    business_days = 5        # Mon-Fri
    hours_per_day = 8        # 8 hours per day
    
    print(f"WEEKLY UTILIZATION:")
    print(f"  Appointment hours: {total_week_hours:.2f}")
    print(f"  Standard work week: {standard_work_week} hours")
    
    if standard_work_week > 0:
        weekly_utilization = (total_week_hours / standard_work_week) * 100
        print(f"  Weekly utilization: ({total_week_hours:.2f} ÷ {standard_work_week}) × 100 = {weekly_utilization:.1f}%")
    
    # Daily average
    working_days_with_appointments = len(appointments_by_day)
    if working_days_with_appointments > 0:
        avg_hours_per_day = total_week_hours / working_days_with_appointments
        daily_utilization = (avg_hours_per_day / hours_per_day) * 100
        
        print(f"\nDAILY AVERAGES:")
        print(f"  Days with appointments: {working_days_with_appointments}")
        print(f"  Average hours per working day: {avg_hours_per_day:.2f}")
        print(f"  Daily utilization: ({avg_hours_per_day:.2f} ÷ {hours_per_day}) × 100 = {daily_utilization:.1f}%")
    
    # ==============================================================
    # REALITY CHECK
    # ==============================================================
    print(f"\n🔍 REALITY CHECK")
    print("=" * 20)
    
    print(f"FINDINGS:")
    if total_week_hours < 10:
        print(f"🔴 VERY LOW hours ({total_week_hours:.2f}) - Possible issues:")
        print(f"    - Incorrect duration data")
        print(f"    - Missing appointments") 
        print(f"    - Part-time schedule")
        print(f"    - Holiday week (Sept 1 was Labor Day)")
    elif total_week_hours < 20:
        print(f"🟡 LOW hours ({total_week_hours:.2f}) - Could be:")
        print(f"    - Part-time employee")
        print(f"    - Slow business week")
        print(f"    - Duration calculation issues")
    else:
        print(f"✅ REASONABLE hours ({total_week_hours:.2f})")
    
    if len(short_appointments) > len(laine_appointments) * 0.3:  # More than 30% short
        print(f"🔴 TOO MANY short appointments ({len(short_appointments)}/{len(laine_appointments)})")
        print(f"    - Likely data quality issue")
        print(f"    - Check if these are buffer times or actual services")
    
    return {
        'employee_name': 'Laine Duttlinger',
        'employee_id': laine_id,
        'week_period': 'September 1-7, 2025',
        'total_appointments': len(laine_appointments),
        'total_hours': total_week_hours,
        'weekly_utilization': weekly_utilization if 'weekly_utilization' in locals() else 0,
        'daily_average_hours': avg_hours_per_day if 'avg_hours_per_day' in locals() else 0,
        'short_appointments': len(short_appointments),
        'appointments_by_day': appointments_by_day
    }

if __name__ == "__main__":
    result = laine_weekly_utilization()
    
    print(f"\n" + "=" * 60)
    print("📅 WEEKLY UTILIZATION COMPLETE")
    
    if result:
        print(f"Employee: {result['employee_name']}")
        print(f"Week: {result['week_period']}")
        print(f"Total appointments: {result['total_appointments']}")
        print(f"Total hours: {result['total_hours']:.2f}")
        print(f"Weekly utilization: {result['weekly_utilization']:.1f}%")
        print(f"Daily average: {result['daily_average_hours']:.2f} hours")
        print(f"Short appointments flagged: {result['short_appointments']}")
        
        print(f"\n🎯 NEXT: Get monthly data and compare to Square's 60% figure")
    else:
        print(f"❌ WEEKLY CALCULATION FAILED")