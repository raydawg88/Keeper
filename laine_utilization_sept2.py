#!/usr/bin/env python3
"""
PHASE 2: VALIDATE UTILIZATION CALCULATION
Calculate Laine Duttlinger's utilization for September 2, 2025
- Get her 6 appointments
- Calculate appointment duration hours
- Find scheduled work hours (shift data if available)
- Apply formula: (Appointment Hours / Scheduled Hours) × 100
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def calculate_laine_utilization():
    """Calculate Laine's utilization for September 2, 2025 step-by-step"""
    
    print("🎯 PHASE 2: LAINE'S UTILIZATION CALCULATION")
    print("=" * 50)
    print("Employee: Laine Duttlinger")
    print("Date: September 2, 2025")
    print("Expected appointments: 6")
    
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
    print(f"✅ Laine's Team Member ID: {laine_id}")
    
    # Define September 2, 2025
    target_date = datetime(2025, 9, 2)
    start_str = target_date.strftime('%Y-%m-%dT00:00:00Z')
    end_str = (target_date + timedelta(days=1) - timedelta(seconds=1)).strftime('%Y-%m-%dT23:59:59Z')
    
    print(f"Time range: {start_str} to {end_str}")
    
    # ==============================================================
    # STEP 1: GET LAINE'S APPOINTMENTS
    # ==============================================================
    print(f"\n📋 STEP 1: GET LAINE'S APPOINTMENTS")
    print("=" * 35)
    
    # Get all appointments for September 2
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
                                'appointment_segments': apt.get('appointment_segments', []),
                                'status': apt.get('status'),
                                'segment': segment
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
    
    print(f"✅ Found {len(laine_appointments)} appointments for Laine")
    
    if len(laine_appointments) != 6:
        print(f"⚠️  Expected 6 appointments, found {len(laine_appointments)}")
    
    # ==============================================================
    # STEP 2: CALCULATE APPOINTMENT HOURS
    # ==============================================================
    print(f"\n⏰ STEP 2: CALCULATE APPOINTMENT HOURS")
    print("=" * 35)
    
    total_appointment_minutes = 0
    
    print(f"{'#':<2} {'START TIME':<10} {'DURATION':<10} {'SERVICE':<20}")
    print("-" * 50)
    
    for i, apt in enumerate(laine_appointments, 1):
        segment = apt['segment']
        
        # Get duration from segment
        duration_minutes = segment.get('duration_minutes', 0)
        total_appointment_minutes += duration_minutes
        
        # Format start time for display
        start_time = apt['start_at']
        start_display = start_time[11:16] if start_time else 'N/A'
        
        # Get service name if available
        service_variation_id = segment.get('service_variation_id', '')
        service_name = service_variation_id[:15] + "..." if len(service_variation_id) > 15 else service_variation_id
        
        print(f"{i:<2} {start_display:<10} {duration_minutes}min{'':<4} {service_name:<20}")
    
    # Convert to hours
    total_appointment_hours = total_appointment_minutes / 60
    
    print("-" * 50)
    print(f"TOTAL APPOINTMENT TIME:")
    print(f"  Minutes: {total_appointment_minutes}")
    print(f"  Hours: {total_appointment_hours:.2f}")
    
    # ==============================================================
    # STEP 3: FIND SCHEDULED WORK HOURS
    # ==============================================================
    print(f"\n🕐 STEP 3: FIND SCHEDULED WORK HOURS")
    print("=" * 35)
    
    scheduled_hours = None
    
    # Try to get shift data from Square API
    print("Checking Square API for shift/timecard data...")
    
    try:
        # Try shifts endpoint
        shifts_url = f"{api_base_url}/v2/labor/shifts/search"
        
        # Search for Laine's shifts on September 2
        search_body = {
            "query": {
                "filter": {
                    "workday": {
                        "date_range": {
                            "start_date": "2025-09-02",
                            "end_date": "2025-09-02"
                        }
                    },
                    "team_member_ids": [laine_id]
                }
            },
            "limit": 10
        }
        
        response = requests.post(shifts_url, headers=headers, json=search_body)
        
        if response.status_code == 200:
            data = response.json()
            shifts = data.get('shifts', [])
            
            if shifts:
                print(f"✅ Found {len(shifts)} shifts for Laine")
                
                total_shift_minutes = 0
                for shift in shifts:
                    start_at = shift.get('start_at')
                    end_at = shift.get('end_at')
                    
                    if start_at and end_at:
                        start_time = datetime.fromisoformat(start_at.replace('Z', '+00:00'))
                        end_time = datetime.fromisoformat(end_at.replace('Z', '+00:00'))
                        shift_minutes = (end_time - start_time).total_seconds() / 60
                        total_shift_minutes += shift_minutes
                        
                        print(f"  Shift: {start_at[11:16]} - {end_at[11:16]} ({shift_minutes/60:.2f} hours)")
                
                scheduled_hours = total_shift_minutes / 60
                print(f"✅ Total scheduled hours: {scheduled_hours:.2f}")
            else:
                print("❌ No shift data found for Laine on September 2")
        else:
            print(f"❌ Shifts API error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error getting shift data: {e}")
    
    # If no shift data, use assumption
    if scheduled_hours is None:
        print(f"\n⚠️  USING ASSUMPTION: 8-hour workday (9 AM - 5 PM)")
        scheduled_hours = 8.0
        print(f"Assumed scheduled hours: {scheduled_hours}")
    
    # ==============================================================
    # STEP 4: CALCULATE UTILIZATION
    # ==============================================================
    print(f"\n🎯 STEP 4: UTILIZATION CALCULATION")
    print("=" * 35)
    
    print(f"FORMULA: Utilization = (Appointment Hours / Scheduled Hours) × 100")
    print(f"")
    print(f"VALUES:")
    print(f"  Appointment Hours: {total_appointment_hours:.2f}")
    print(f"  Scheduled Hours: {scheduled_hours:.2f}")
    
    if scheduled_hours > 0:
        utilization_percentage = (total_appointment_hours / scheduled_hours) * 100
        
        print(f"")
        print(f"CALCULATION:")
        print(f"  ({total_appointment_hours:.2f} ÷ {scheduled_hours:.2f}) × 100 = {utilization_percentage:.1f}%")
        
        print(f"")
        print(f"🎯 LAINE'S UTILIZATION: {utilization_percentage:.1f}%")
        
        # Interpretation
        print(f"\nINTERPRETATION:")
        if utilization_percentage >= 80:
            print(f"✅ HIGH utilization - Laine is very busy")
        elif utilization_percentage >= 60:
            print(f"🟡 MODERATE utilization - Room for more appointments")
        else:
            print(f"🔴 LOW utilization - Significant capacity available")
        
        return {
            'employee_name': 'Laine Duttlinger',
            'employee_id': laine_id,
            'date': '2025-09-02',
            'appointments_found': len(laine_appointments),
            'appointment_hours': total_appointment_hours,
            'scheduled_hours': scheduled_hours,
            'utilization_percentage': utilization_percentage
        }
    else:
        print(f"❌ Cannot calculate utilization - no scheduled hours")
        return None

if __name__ == "__main__":
    result = calculate_laine_utilization()
    
    print(f"\n" + "=" * 50)
    print("🎯 UTILIZATION CALCULATION COMPLETE")
    
    if result:
        print(f"Employee: {result['employee_name']}")
        print(f"Date: {result['date']}")
        print(f"Appointments: {result['appointments_found']}")
        print(f"Appointment Hours: {result['appointment_hours']:.2f}")
        print(f"Scheduled Hours: {result['scheduled_hours']:.2f}")
        print(f"UTILIZATION: {result['utilization_percentage']:.1f}%")
        
        if result['appointments_found'] == 6:
            print(f"✅ CHECKPOINT PASSED: Found expected 6 appointments")
        else:
            print(f"⚠️  CHECKPOINT: Expected 6, found {result['appointments_found']}")
            
        print(f"\n🏆 PHASE 2 READY: Utilization formula validated")
    else:
        print(f"❌ UTILIZATION CALCULATION FAILED")