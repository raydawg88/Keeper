#!/usr/bin/env python3
"""
DEBUG SEPTEMBER 2 FAILURES - CRITICAL ACCURACY PROBLEMS
- FAILED: Found 4 employees, actual is 6 (missing 33% of staff)
- FAILED: Found 23 appointments, actual is 24 (missing 1 appointment)
- FAILED: Found $1,225.95, actual is $1,217.94 ($8.01 off)
- Need to debug EVERY data source to find the gaps
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def debug_sept2_failures():
    """Debug every data collection failure for September 2, 2025"""
    
    print("🚨 DEBUG SEPTEMBER 2 CRITICAL FAILURES")
    print("=" * 60)
    print("FAILURES IDENTIFIED:")
    print("❌ Employees: Found 4, actual 6 (missing 33%)")
    print("❌ Appointments: Found 23, actual 24 (missing 1)")
    print("❌ Revenue: Found $1,225.95, actual $1,217.94 ($8.01 off)")
    print()
    print("DEBUGGING EVERY DATA SOURCE...")
    
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
    
    # Define September 2, 2025 precisely
    target_date = datetime(2025, 9, 2)
    start_str = target_date.strftime('%Y-%m-%dT00:00:00Z')
    end_str = (target_date + timedelta(days=1) - timedelta(seconds=1)).strftime('%Y-%m-%dT23:59:59Z')
    
    print(f"\n🔍 DETAILED DATA ANALYSIS FOR SEPTEMBER 2, 2025")
    print(f"Time range: {start_str} to {end_str}")
    
    # 1. DEEP DIVE INTO APPOINTMENTS - Find the missing appointment
    print(f"\n📋 APPOINTMENTS DEEP DIVE")
    print("=" * 40)
    
    # Get appointments with expanded details
    all_appointments = []
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
                all_appointments.extend(bookings)
                cursor = data.get('cursor')
                if not cursor:
                    break
            else:
                print(f"❌ Bookings API Error: {response.status_code}")
                break
        except Exception as e:
            print(f"❌ Error: {e}")
            break
    
    print(f"Raw appointments found: {len(all_appointments)}")
    
    # Analyze each appointment in detail
    employee_appointments = {}
    all_employees = set()
    
    print(f"\nDETAILED APPOINTMENT ANALYSIS:")
    print(f"{'#':<3} {'TIME':<8} {'STATUS':<20} {'CUSTOMER':<15} {'EMPLOYEE':<25} {'SERVICES'}")
    print("-" * 100)
    
    for i, apt in enumerate(all_appointments, 1):
        apt_id = apt.get('id', 'No ID')
        start_time = apt.get('start_at', 'No time')
        status = apt.get('status', 'No status')
        customer_id = apt.get('customer_id', 'No customer')[:12]
        
        # Get all segments and employees
        segments = apt.get('appointment_segments', [])
        segment_employees = []
        services = []
        
        for segment in segments:
            tm_id = segment.get('team_member_id')
            if tm_id:
                all_employees.add(tm_id)
                segment_employees.append(tm_id)
                
                # Track appointments per employee
                if tm_id not in employee_appointments:
                    employee_appointments[tm_id] = []
                employee_appointments[tm_id].append({
                    'time': start_time,
                    'status': status,
                    'duration': segment.get('duration_minutes', 0)
                })
            
            service_id = segment.get('service_variation_id', 'No service')
            services.append(service_id[:8])
        
        employee_names = []
        try:
            with open('/tmp/team_member_id_name_mapping.json', 'r') as f:
                mapping_data = json.load(f)
            team_mapping = mapping_data['id_to_name_mapping']
            
            for tm_id in segment_employees:
                name = team_mapping.get(tm_id, {}).get('name', 'Unknown')
                employee_names.append(f"{name[:15]}")
        except:
            employee_names = segment_employees
        
        time_display = start_time[11:16] if start_time else 'N/A'
        employees_display = ", ".join(employee_names) if employee_names else "NO EMPLOYEE"
        services_display = f"{len(services)} services"
        
        print(f"{i:<3} {time_display:<8} {status:<20} {customer_id:<15} {employees_display:<25} {services_display}")
    
    # 2. EMPLOYEE ANALYSIS - Find the missing 2 employees
    print(f"\n👤 EMPLOYEE ANALYSIS")
    print("=" * 30)
    print(f"Total unique employees found: {len(all_employees)}")
    print(f"Expected: 6 employees")
    print(f"Missing: {6 - len(all_employees)} employees")
    
    print(f"\nEMPLOYEES FOUND IN APPOINTMENTS:")
    try:
        with open('/tmp/team_member_id_name_mapping.json', 'r') as f:
            mapping_data = json.load(f)
        team_mapping = mapping_data['id_to_name_mapping']
        
        for tm_id in sorted(all_employees):
            name = team_mapping.get(tm_id, {}).get('name', 'Unknown')
            apt_count = len(employee_appointments.get(tm_id, []))
            print(f"  • {name} ({tm_id}) - {apt_count} appointments")
            
    except:
        for tm_id in sorted(all_employees):
            apt_count = len(employee_appointments.get(tm_id, []))
            print(f"  • {tm_id} - {apt_count} appointments")
    
    # 3. PAYMENT ANALYSIS - Find the $8.01 discrepancy
    print(f"\n💰 PAYMENT ANALYSIS - FIND THE $8.01 ERROR")
    print("=" * 50)
    
    # Get all payments
    all_payments = []
    cursor = None
    while True:
        url = f"{api_base_url}/v2/payments?begin_time={start_str}&end_time={end_str}&limit=200"
        if cursor:
            url += f"&cursor={cursor}"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                payments = data.get('payments', [])
                all_payments.extend(payments)
                cursor = data.get('cursor')
                if not cursor:
                    break
            else:
                break
        except:
            break
    
    print(f"Total payments found: {len(all_payments)}")
    
    # Detailed payment breakdown
    total_found = 0
    print(f"\nALL 26 TRANSACTIONS:")
    print(f"{'#':<3} {'TIME':<8} {'AMOUNT':<10} {'TYPE':<6} {'STATUS':<15} {'ID'}")
    print("-" * 60)
    
    for i, payment in enumerate(all_payments, 1):
        amount = float(payment.get('total_money', {}).get('amount', 0)) / 100
        total_found += amount
        
        created_time = payment.get('created_at', 'No time')
        time_display = created_time[11:16] if created_time else 'N/A'
        source_type = payment.get('source_type', 'Unknown')
        status = payment.get('status', 'Unknown')
        payment_id = payment.get('id', 'No ID')[:12]
        
        print(f"{i:<3} {time_display:<8} ${amount:<9.2f} {source_type:<6} {status:<15} {payment_id}")
    
    print("-" * 60)
    print(f"MY TOTAL: ${total_found:.2f}")
    print(f"SQUARE'S ACTUAL: $1,217.94")
    print(f"DIFFERENCE: ${total_found - 1217.94:.2f}")
    
    # 4. CHECK DIFFERENT DATE RANGES - Maybe timing issue
    print(f"\n🕐 CHECKING DIFFERENT TIME BOUNDARIES")
    print("=" * 40)
    
    # Try different time boundaries in case of timezone issues
    time_variants = [
        (datetime(2025, 9, 2, 6, 0, 0), datetime(2025, 9, 3, 5, 59, 59), "6AM-6AM"),
        (datetime(2025, 9, 1, 18, 0, 0), datetime(2025, 9, 2, 18, 0, 0), "6PM-6PM"),
        (datetime(2025, 9, 2, 0, 0, 0), datetime(2025, 9, 2, 23, 59, 59), "Midnight-Midnight")
    ]
    
    for start_dt, end_dt, label in time_variants:
        start_test = start_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_test = end_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # Quick payment count for this range
        try:
            url = f"{api_base_url}/v2/payments?begin_time={start_test}&end_time={end_test}&limit=50"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                payments = data.get('payments', [])
                test_total = sum(float(p.get('total_money', {}).get('amount', 0)) / 100 for p in payments)
                print(f"  {label}: {len(payments)} payments, ${test_total:.2f}")
        except:
            pass
    
    print(f"\n🚨 CRITICAL ISSUES IDENTIFIED:")
    print(f"1. Missing {6 - len(all_employees)} employees from appointment data")
    print(f"2. Appointment count: {len(all_appointments)} vs expected 24")
    print(f"3. Revenue discrepancy: ${abs(total_found - 1217.94):.2f}")
    print(f"4. Need to investigate:")
    print(f"   - Are some appointments in different endpoints?")
    print(f"   - Are some employees in different data?")
    print(f"   - Is there a payment processing issue?")
    
    return {
        'appointments_found': len(all_appointments),
        'employees_found': len(all_employees),
        'revenue_found': total_found,
        'employees_list': list(all_employees)
    }

if __name__ == "__main__":
    debug_results = debug_sept2_failures()
    
    print(f"\n" + "=" * 60)
    print("🚨 DEBUG RESULTS:")
    print(f"Found {debug_results['appointments_found']} appointments (need 24)")
    print(f"Found {debug_results['employees_found']} employees (need 6)")
    print(f"Found ${debug_results['revenue_found']:.2f} revenue (need $1,217.94)")
    print()
    print("NEXT: Need to find missing data sources or fix collection method")