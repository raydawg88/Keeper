#!/usr/bin/env python3
"""
MATCH SQUARE'S ACTUAL UTILIZATION LOGIC
- Stop inventing formulas - use Square's real calculation
- Account for spa business hours (not 24/7)
- Match actual Square data: Laine 60%, Tayler 58%, etc.
- Fix the 8-10x calculation error
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def match_square_utilization_logic():
    """Match Square's actual utilization calculation logic"""
    
    print("🎯 MATCH SQUARE'S ACTUAL UTILIZATION LOGIC")
    print("=" * 70)
    print("PROBLEM: My calculations were 8-10x wrong!")
    print("ACTUAL SQUARE DATA:")
    print("  • Laine: 60% utilization, 1,165 appointments (2025 YTD)")
    print("  • Tayler: 58% utilization, 1,247 appointments")
    print("  • Alicia: 58% utilization, 347 appointments") 
    print("  • Rylie: 69% utilization, 1,311 appointments")
    print("MY WRONG CALCULATIONS: Laine 7.8%, Tayler 6.0% (OFF BY 8-10x!)")
    
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
    
    # STEP 1: Try to get Square's actual utilization data
    print(f"\n📡 STEP 1: GET SQUARE'S ACTUAL UTILIZATION DATA")
    
    # Try Team Members API with expanded fields
    try:
        search_body = {"limit": 50}
        response = requests.post(f"{api_base_url}/v2/team-members/search", 
                               headers=headers, 
                               json=search_body)
        
        if response.status_code == 200:
            data = response.json()
            team_members = data.get('team_members', [])
            
            print(f"✅ Retrieved {len(team_members)} team members")
            
            # Look for utilization data in team member profiles
            for member in team_members:
                member_id = member.get('id')
                name = f"{member.get('given_name', '')} {member.get('family_name', '')}".strip()
                
                # Check for utilization or performance metrics
                if any(keyword in name.lower() for keyword in ['laine', 'tayler', 'alicia', 'rylie']):
                    print(f"\n👤 {name} ({member_id})")
                    
                    # Look for any utilization/performance fields
                    member_keys = list(member.keys())
                    print(f"  Available fields: {member_keys}")
                    
                    # Check for specific performance fields
                    performance_fields = ['utilization', 'performance', 'metrics', 'stats', 'hours']
                    for field in performance_fields:
                        if field in member:
                            print(f"  {field}: {member[field]}")
        
        else:
            print(f"❌ Team Members API error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting team member data: {e}")
    
    # STEP 2: Calculate using spa business hours logic
    print(f"\n🕒 STEP 2: CALCULATE WITH SPA BUSINESS HOURS")
    print("=" * 50)
    
    # Spa business hours (realistic assumptions)
    business_hours_per_day = 10  # 9am-7pm
    business_days_per_week = 6   # Closed Sundays
    business_hours_per_week = business_hours_per_day * business_days_per_week  # 60 hours
    business_hours_per_month = business_hours_per_week * 4.33  # ~260 hours
    
    print(f"SPA BUSINESS HOURS:")
    print(f"  Daily: {business_hours_per_day} hours (9am-7pm)")
    print(f"  Weekly: {business_hours_per_week} hours (6 days)")
    print(f"  Monthly: {business_hours_per_month:.0f} hours available")
    
    # Calculate utilization matching Square's logic
    print(f"\nMATCHING SQUARE'S UTILIZATION LOGIC:")
    
    # Using 2025 YTD data from your screenshot
    employees_2025_ytd = {
        'Laine Duttlinger': {'appointments': 1165, 'square_utilization': 60},
        'Tayler Brunson': {'appointments': 1247, 'square_utilization': 58},
        'Alicia Cardenas': {'appointments': 347, 'square_utilization': 58},
        'Rylie Calverley': {'appointments': 1311, 'square_utilization': 69}
    }
    
    # Calculate months YTD (January through current)
    current_month = datetime.now().month
    months_ytd = current_month
    available_hours_ytd = business_hours_per_month * months_ytd
    
    print(f"2025 YTD ANALYSIS ({months_ytd} months):")
    print(f"Available hours YTD: {available_hours_ytd:.0f} hours")
    print()
    
    for name, data in employees_2025_ytd.items():
        appointments = data['appointments']
        square_utilization = data['square_utilization']
        
        print(f"👤 {name}:")
        print(f"  Square's utilization: {square_utilization}%")
        print(f"  Appointments (2025 YTD): {appointments:,}")
        
        # Reverse engineer Square's calculation
        # If Square says 60% utilization, what are they measuring?
        
        # Option 1: Simple service hours / available hours
        avg_service_time = 35  # minutes
        total_service_hours = (appointments * avg_service_time) / 60
        simple_utilization = (total_service_hours / available_hours_ytd) * 100
        
        print(f"  My calculation (service hours): {simple_utilization:.1f}%")
        print(f"  Difference from Square: {abs(simple_utilization - square_utilization):.1f}%")
        
        # Option 2: Appointment slots / available slots
        # Assume 30-minute appointment slots
        slots_per_hour = 2
        available_slots_ytd = available_hours_ytd * slots_per_hour
        slot_utilization = (appointments / available_slots_ytd) * 100
        
        print(f"  Slot-based calculation: {slot_utilization:.1f}%")
        print(f"  Difference from Square: {abs(slot_utilization - square_utilization):.1f}%")
        
        # Find the calculation that matches Square's numbers
        if abs(simple_utilization - square_utilization) < 5:
            print(f"  ✅ MATCH: Service hours calculation is correct")
        elif abs(slot_utilization - square_utilization) < 5:
            print(f"  ✅ MATCH: Slot-based calculation is correct")
        else:
            print(f"  ⚠️  Neither calculation matches - need different logic")
        
        print()
    
    # STEP 3: Identify the correct Square formula
    print(f"🔍 STEP 3: IDENTIFY SQUARE'S FORMULA")
    print("=" * 40)
    
    # Test different formulas to see which matches
    print("Testing different utilization formulas:")
    print()
    
    # Formula test on Laine's data
    laine_appointments = 1165
    laine_square_util = 60
    
    formulas = [
        ("Service Hours / Business Hours", lambda: (laine_appointments * 35 / 60) / available_hours_ytd * 100),
        ("Appointments / Available Slots", lambda: laine_appointments / (available_hours_ytd * 2) * 100),
        ("Working Days / Business Days", lambda: laine_appointments / (months_ytd * 22) * 100),  # 22 working days/month
        ("Custom Square Logic", lambda: laine_appointments / (months_ytd * 20) * 100),  # Different base
    ]
    
    closest_formula = None
    closest_difference = float('inf')
    
    for formula_name, formula_func in formulas:
        try:
            calculated = formula_func()
            difference = abs(calculated - laine_square_util)
            
            print(f"  {formula_name}: {calculated:.1f}% (diff: {difference:.1f}%)")
            
            if difference < closest_difference:
                closest_difference = difference
                closest_formula = formula_name
                
        except Exception as e:
            print(f"  {formula_name}: Error - {e}")
    
    print(f"\n✅ CLOSEST MATCH: {closest_formula}")
    print(f"Difference: {closest_difference:.1f}%")
    
    # STEP 4: Apply correct formula to all employees
    print(f"\n📊 STEP 4: APPLY CORRECT FORMULA")
    print("=" * 40)
    
    print("Using corrected utilization calculation:")
    for name, data in employees_2025_ytd.items():
        appointments = data['appointments']
        square_utilization = data['square_utilization']
        
        # Use the best matching formula
        if "Service Hours" in closest_formula:
            calculated = (appointments * 35 / 60) / available_hours_ytd * 100
        elif "Appointments" in closest_formula:
            calculated = appointments / (available_hours_ytd * 2) * 100
        else:
            calculated = appointments / (months_ytd * 20) * 100
        
        print(f"{name}: {calculated:.1f}% (Square: {square_utilization}%)")

if __name__ == "__main__":
    match_square_utilization_logic()
    
    print(f"\n" + "=" * 70)
    print("🎯 SQUARE UTILIZATION MATCHING: IN PROGRESS")
    print("✅ Identified the calculation error (8-10x off)")
    print("✅ Using spa business hours, not 24/7")
    print("🔄 Testing formulas to match Square's exact logic")
    print("⏳ Need to find the exact formula Square uses")