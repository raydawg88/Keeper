#!/usr/bin/env python3
"""
SYSTEMATIC FIXES FOR SEPTEMBER 2 DATA - CHECKPOINT AFTER EACH FIX
FIX 1: Revenue - exclude FAILED transactions
FIX 2: Missing employees - find Alexa, Audrey, Doan, Joley  
FIX 3: Remove phantom employees
FIX 4: Get ALL appointments
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def fix_sept2_systematic():
    """Fix September 2 data issues systematically with checkpoints"""
    
    print("🔧 SYSTEMATIC FIXES FOR SEPTEMBER 2, 2025")
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
    
    # Define September 2, 2025 precisely
    target_date = datetime(2025, 9, 2)
    start_str = target_date.strftime('%Y-%m-%dT00:00:00Z')
    end_str = (target_date + timedelta(days=1) - timedelta(seconds=1)).strftime('%Y-%m-%dT23:59:59Z')
    
    print(f"Target: September 2, 2025")
    print(f"Time range: {start_str} to {end_str}")
    
    # ==============================================================
    # FIX 1: REVENUE CALCULATION - EXCLUDE FAILED TRANSACTIONS
    # ==============================================================
    print(f"\n🔧 FIX 1: REVENUE CALCULATION")
    print("=" * 30)
    print("Goal: Filter to COMPLETED transactions only = $1,217.94")
    
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
    
    # Filter to COMPLETED only and calculate
    completed_payments = []
    failed_payments = []
    completed_total = 0
    
    for payment in all_payments:
        status = payment.get('status', 'Unknown')
        amount = float(payment.get('total_money', {}).get('amount', 0)) / 100
        
        if status == 'COMPLETED':
            completed_payments.append(payment)
            completed_total += amount
        else:
            failed_payments.append(payment)
    
    print(f"Total payments found: {len(all_payments)}")
    print(f"COMPLETED payments: {len(completed_payments)} = ${completed_total:.2f}")
    print(f"FAILED/OTHER payments: {len(failed_payments)}")
    
    if failed_payments:
        print(f"FAILED transactions excluded:")
        for payment in failed_payments:
            amount = float(payment.get('total_money', {}).get('amount', 0)) / 100
            status = payment.get('status', 'Unknown')
            print(f"  ${amount:.2f} ({status})")
    
    # CHECKPOINT 1
    print(f"\n📊 CHECKPOINT 1 - REVENUE:")
    if abs(completed_total - 1217.94) < 0.01:
        print(f"✅ SUCCESS: ${completed_total:.2f} matches Square's $1,217.94")
    else:
        print(f"❌ STILL OFF: ${completed_total:.2f} vs Square's $1,217.94 (diff: ${abs(completed_total - 1217.94):.2f})")
    
    # ==============================================================
    # FIX 2: MISSING EMPLOYEES INVESTIGATION
    # ==============================================================
    print(f"\n🔧 FIX 2: MISSING EMPLOYEES INVESTIGATION")
    print("=" * 40)
    print("Goal: Find Alexa, Audrey, Doan, Joley (missing from API)")
    
    print(f"\nFIX 2a: Check ALL team members (no filters)")
    
    # Get ALL team members without filters
    try:
        search_body = {"limit": 100}  # Get more members
        response = requests.post(f"{api_base_url}/v2/team-members/search", 
                               headers=headers, 
                               json=search_body)
        
        if response.status_code == 200:
            data = response.json()
            all_team_members = data.get('team_members', [])
            
            print(f"✅ Found {len(all_team_members)} total team members")
            
            # Look for missing names
            missing_names = ['alexa', 'audrey', 'doan', 'joley']
            found_missing = {}
            
            print(f"\nSearching for missing employees:")
            for member in all_team_members:
                given_name = member.get('given_name', '').lower()
                family_name = member.get('family_name', '').lower()
                full_name = f"{given_name} {family_name}".strip()
                member_id = member.get('id')
                status = member.get('status', 'Unknown')
                
                for missing_name in missing_names:
                    if missing_name in given_name or missing_name in family_name:
                        found_missing[missing_name] = {
                            'id': member_id,
                            'name': f"{member.get('given_name', '')} {member.get('family_name', '')}".strip(),
                            'status': status
                        }
                        print(f"  ✅ FOUND {missing_name.upper()}: {found_missing[missing_name]['name']} ({member_id}) - {status}")
            
            # Report what we didn't find
            for missing_name in missing_names:
                if missing_name not in found_missing:
                    print(f"  ❌ NOT FOUND: {missing_name}")
            
        else:
            print(f"❌ Team Members API error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting team members: {e}")
    
    # CHECKPOINT 2a
    print(f"\n📊 CHECKPOINT 2a - TEAM MEMBERS:")
    print(f"Found {len(found_missing)} of 4 missing employees: {list(found_missing.keys())}")
    
    print(f"\nFIX 2b: Check appointments with newly found employee IDs")
    
    # Now check appointments for these newly found employees
    if found_missing:
        # Get appointments again but look for these specific employee IDs
        appointments_by_employee = {}
        
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
                    
                    for apt in bookings:
                        segments = apt.get('appointment_segments', [])
                        for segment in segments:
                            tm_id = segment.get('team_member_id')
                            if tm_id:
                                if tm_id not in appointments_by_employee:
                                    appointments_by_employee[tm_id] = 0
                                appointments_by_employee[tm_id] += 1
                    
                    cursor = data.get('cursor')
                    if not cursor:
                        break
                else:
                    break
            except:
                break
        
        print(f"\nEmployees found in appointments:")
        # Load names for display
        try:
            with open('/tmp/team_member_id_name_mapping.json', 'r') as f:
                mapping_data = json.load(f)
            team_mapping = mapping_data['id_to_name_mapping']
        except:
            team_mapping = {}
        
        for tm_id, count in sorted(appointments_by_employee.items(), key=lambda x: x[1], reverse=True):
            name = team_mapping.get(tm_id, {}).get('name', 'Unknown')
            # Check if this is one of our newly found employees
            is_missing_employee = False
            for missing_name, info in found_missing.items():
                if tm_id == info['id']:
                    print(f"  ✅ {name} ({tm_id}): {count} appointments - WAS MISSING!")
                    is_missing_employee = True
                    break
            
            if not is_missing_employee:
                print(f"  • {name} ({tm_id}): {count} appointments")
    
    # CHECKPOINT 2b
    print(f"\n📊 CHECKPOINT 2b - APPOINTMENTS BY EMPLOYEE:")
    total_employees_in_appointments = len(appointments_by_employee) if 'appointments_by_employee' in locals() else 0
    print(f"Total employees found in appointments: {total_employees_in_appointments}")
    print(f"Target: 6 employees")
    
    if total_employees_in_appointments == 6:
        print("✅ SUCCESS: Found all 6 employees!")
    else:
        print(f"❌ STILL MISSING: {6 - total_employees_in_appointments} employees")
    
    # ==============================================================
    # FIX 3: REMOVE PHANTOM EMPLOYEES
    # ==============================================================
    print(f"\n🔧 FIX 3: REMOVE PHANTOM EMPLOYEES")
    print("=" * 35)
    print("Goal: Remove Sarah Lehmann if she didn't actually work Sept 2")
    
    if 'appointments_by_employee' in locals():
        print(f"Checking if Sarah Lehmann (TMeNAvKXJPvMSEQi) had appointments:")
        sarah_id = "TMeNAvKXJPvMSEQi"
        if sarah_id in appointments_by_employee:
            print(f"✅ Sarah Lehmann: {appointments_by_employee[sarah_id]} appointments - REAL")
        else:
            print(f"❌ Sarah Lehmann: 0 appointments - PHANTOM")
    
    # ==============================================================
    # FINAL SUMMARY
    # ==============================================================
    print(f"\n📋 FINAL SUMMARY AFTER ALL FIXES")
    print("=" * 40)
    
    if 'completed_total' in locals():
        print(f"Revenue: ${completed_total:.2f} (target: $1,217.94)")
        revenue_accurate = abs(completed_total - 1217.94) < 0.01
    else:
        revenue_accurate = False
    
    if 'appointments_by_employee' in locals():
        print(f"Employees with appointments: {len(appointments_by_employee)}")
        print(f"Employee list:")
        for tm_id, count in sorted(appointments_by_employee.items(), key=lambda x: x[1], reverse=True):
            name = team_mapping.get(tm_id, {}).get('name', 'Unknown')
            print(f"  • {name}: {count} appointments")
        
        employees_accurate = len(appointments_by_employee) == 6
    else:
        employees_accurate = False
    
    print(f"\n🎯 ACCURACY CHECK:")
    print(f"Revenue accurate: {'✅' if revenue_accurate else '❌'}")
    print(f"Employee count accurate: {'✅' if employees_accurate else '❌'}")
    
    if revenue_accurate and employees_accurate:
        print(f"\n🏆 GROUND TRUTH ACHIEVED!")
        print(f"✅ Ready for Phase 2: Utilization calculations")
    else:
        print(f"\n⚠️  STILL NEED FIXES:")
        if not revenue_accurate:
            print(f"  - Revenue calculation still off")
        if not employees_accurate:
            print(f"  - Missing employees in appointment data")
    
    return revenue_accurate and employees_accurate

if __name__ == "__main__":
    success = fix_sept2_systematic()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🏆 SEPTEMBER 2 DATA: 100% ACCURATE!")
        print("Ready to proceed to Phase 2")
    else:
        print("⚠️  SEPTEMBER 2 DATA: STILL NEEDS FIXES")
        print("Continue debugging before Phase 2")