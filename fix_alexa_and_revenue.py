#!/usr/bin/env python3
"""
FIX ALEXA APPOINTMENTS AND REVENUE GAP
- Alexa DEFINITELY has appointments but not showing in API
- Check date/timezone issues for Alexa's appointments
- Check cancellations, refunds, gift cards, failed payments
- Get COMPLETE revenue picture including all transaction states
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def fix_alexa_and_revenue():
    """Fix Alexa's missing appointments and find the revenue gap"""
    
    print("🔧 FIX ALEXA APPOINTMENTS & REVENUE GAP")
    print("=" * 50)
    print("ISSUES:")
    print("1. Alexa (Esthetician) has appointments in calendar but not in API")
    print("2. Missing $102.00 in revenue ($1,115.94 vs $1,217.94)")
    print("3. Need to check cancellations, refunds, gift cards")
    
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
    
    # Alexa's team member ID
    alexa_id = "TMWlOnAsLgKl5Cc9"
    
    # ==============================================================
    # FIX 1: FIND ALEXA'S APPOINTMENTS - TRY DIFFERENT DATE RANGES
    # ==============================================================
    print(f"\n🔍 FIX 1: FIND ALEXA'S APPOINTMENTS")
    print("=" * 40)
    print(f"Alexa ID: {alexa_id}")
    print("Testing different date/time ranges for Sept 2:")
    
    # Try different time boundaries - maybe timezone issue
    date_variants = [
        # Standard day
        (datetime(2025, 9, 2, 0, 0, 0), datetime(2025, 9, 2, 23, 59, 59), "00:00-23:59"),
        # Business day (early morning to late night)
        (datetime(2025, 9, 2, 6, 0, 0), datetime(2025, 9, 3, 2, 0, 0), "06:00-02:00"),
        # Previous day overlap
        (datetime(2025, 9, 1, 18, 0, 0), datetime(2025, 9, 2, 23, 59, 59), "Prev 18:00-23:59"),
        # Next day overlap  
        (datetime(2025, 9, 2, 0, 0, 0), datetime(2025, 9, 3, 6, 0, 0), "00:00-Next 06:00"),
        # Full 48 hours
        (datetime(2025, 9, 1, 0, 0, 0), datetime(2025, 9, 3, 23, 59, 59), "Sept 1-3 Full")
    ]
    
    alexa_appointments_found = []
    
    for start_dt, end_dt, label in date_variants:
        start_str = start_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_str = end_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        print(f"\n  📅 Testing {label}:")
        print(f"     Range: {start_str} to {end_str}")
        
        # Get appointments for this range
        cursor = None
        range_appointments = []
        
        while True:
            url = f"{api_base_url}/v2/bookings?limit=200&start_at_min={start_str}&start_at_max={end_str}"
            if cursor:
                url += f"&cursor={cursor}"
            
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    bookings = data.get('bookings', [])
                    range_appointments.extend(bookings)
                    
                    cursor = data.get('cursor')
                    if not cursor:
                        break
                else:
                    break
            except:
                break
        
        # Check for Alexa in this range
        alexa_count_in_range = 0
        for apt in range_appointments:
            segments = apt.get('appointment_segments', [])
            for segment in segments:
                if segment.get('team_member_id') == alexa_id:
                    alexa_count_in_range += 1
                    alexa_appointments_found.append({
                        'appointment': apt,
                        'date_range': label,
                        'start_time': apt.get('start_at')
                    })
        
        print(f"     Total appointments: {len(range_appointments)}")
        print(f"     Alexa appointments: {alexa_count_in_range}")
        
        if alexa_count_in_range > 0:
            print(f"     ✅ FOUND ALEXA APPOINTMENTS!")
            for alexa_apt in alexa_appointments_found[-alexa_count_in_range:]:
                start_time = alexa_apt['start_time']
                print(f"       • {start_time}")
    
    # ==============================================================
    # FIX 2: COMPREHENSIVE REVENUE ANALYSIS
    # ==============================================================
    print(f"\n💰 FIX 2: COMPREHENSIVE REVENUE ANALYSIS")
    print("=" * 45)
    print("Checking ALL transaction types for missing $102")
    
    # Get payments with ALL statuses
    target_date = datetime(2025, 9, 2)
    start_str = target_date.strftime('%Y-%m-%dT00:00:00Z')
    end_str = (target_date + timedelta(days=1) - timedelta(seconds=1)).strftime('%Y-%m-%dT23:59:59Z')
    
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
    
    # Comprehensive payment analysis
    payment_states = {}
    total_by_state = {}
    
    for payment in all_payments:
        status = payment.get('status', 'Unknown')
        amount = float(payment.get('total_money', {}).get('amount', 0)) / 100
        
        payment_states[status] = payment_states.get(status, 0) + 1
        total_by_state[status] = total_by_state.get(status, 0) + amount
    
    print(f"\nPayment status breakdown:")
    for status, count in sorted(payment_states.items()):
        total = total_by_state[status]
        print(f"  {status}: {count} payments = ${total:.2f}")
    
    # Calculate different revenue scenarios
    print(f"\nRevenue scenarios:")
    completed_only = total_by_state.get('COMPLETED', 0)
    all_non_failed = sum(total for status, total in total_by_state.items() if status not in ['FAILED', 'CANCELED'])
    everything = sum(total_by_state.values())
    
    print(f"  COMPLETED only: ${completed_only:.2f}")
    print(f"  All non-FAILED/CANCELED: ${all_non_failed:.2f}")
    print(f"  Everything: ${everything:.2f}")
    print(f"  Target: $1,217.94")
    
    # Check what gets us closest
    scenarios = [
        ("COMPLETED only", completed_only),
        ("All non-FAILED/CANCELED", all_non_failed),
        ("Everything", everything)
    ]
    
    closest_scenario = min(scenarios, key=lambda x: abs(x[1] - 1217.94))
    print(f"\nClosest to target: {closest_scenario[0]} = ${closest_scenario[1]:.2f}")
    print(f"Difference: ${abs(closest_scenario[1] - 1217.94):.2f}")
    
    # ==============================================================
    # FIX 3: CHECK ORDERS FOR COMPLETED VS DRAFT
    # ==============================================================
    print(f"\n📦 FIX 3: ORDERS ANALYSIS - COMPLETED VS DRAFT")
    print("=" * 45)
    
    try:
        search_body = {
            "location_ids": ["F3XKQZW5S5M0V"],
            "query": {
                "filter": {
                    "date_time_filter": {
                        "created_at": {
                            "start_at": start_str,
                            "end_at": end_str
                        }
                    }
                }
            },
            "limit": 200
        }
        
        response = requests.post(f"{api_base_url}/v2/orders/search", 
                               headers=headers, 
                               json=search_body)
        
        if response.status_code == 200:
            data = response.json()
            orders = data.get('orders', [])
            
            orders_by_state = {}
            total_by_order_state = {}
            
            for order in orders:
                state = order.get('state', 'Unknown')
                total_money = order.get('total_money', {})
                amount = float(total_money.get('amount', 0)) / 100
                
                orders_by_state[state] = orders_by_state.get(state, 0) + 1
                total_by_order_state[state] = total_by_order_state.get(state, 0) + amount
            
            print(f"Orders by state:")
            for state, count in sorted(orders_by_state.items()):
                total = total_by_order_state[state]
                print(f"  {state}: {count} orders = ${total:.2f}")
            
            # Check if COMPLETED orders match our target
            completed_orders_total = total_by_order_state.get('COMPLETED', 0)
            print(f"\nCOMPLETED orders total: ${completed_orders_total:.2f}")
            if abs(completed_orders_total - 1217.94) < 0.01:
                print("✅ COMPLETED orders match target exactly!")
            
    except Exception as e:
        print(f"❌ Orders analysis error: {e}")
    
    # ==============================================================
    # SUMMARY AND FIXES
    # ==============================================================
    print(f"\n📋 SUMMARY OF FIXES NEEDED")
    print("=" * 35)
    
    if alexa_appointments_found:
        print(f"✅ ALEXA APPOINTMENTS: Found {len(alexa_appointments_found)} appointments")
        print("   - Likely date/timezone issue in initial query")
        print("   - Need to use correct date range for future queries")
    else:
        print(f"❌ ALEXA APPOINTMENTS: Still not found")
        print("   - May need different API endpoint or parameters")
    
    print(f"\nRevenue Analysis:")
    if closest_scenario[0] == "COMPLETED only" and abs(closest_scenario[1] - 1217.94) < 5:
        print(f"✅ REVENUE: Close to target with COMPLETED payments")
    else:
        print(f"❌ REVENUE: Still missing ${abs(closest_scenario[1] - 1217.94):.2f}")
        print("   - Check for gift cards, refunds, or other transaction types")
    
    print(f"\nEmployee Status:")
    print(f"✅ Joley & Audrey: Front desk (no appointments expected)")  
    print(f"✅ Doan: Owner (occasional appointments only)")
    print(f"{'✅' if alexa_appointments_found else '❌'} Alexa: Esthetician (should have appointments)")
    
    return len(alexa_appointments_found), closest_scenario[1]

if __name__ == "__main__":
    alexa_count, best_revenue = fix_alexa_and_revenue()
    
    print(f"\n" + "=" * 50)
    print("🔧 FIX RESULTS:")
    print(f"Alexa appointments found: {alexa_count}")
    print(f"Best revenue match: ${best_revenue:.2f}")
    print(f"Revenue gap: ${abs(best_revenue - 1217.94):.2f}")
    
    if alexa_count > 0 and abs(best_revenue - 1217.94) < 5:
        print("🏆 FIXES SUCCESSFUL - READY FOR PHASE 2!")
    else:
        print("⚠️  STILL NEED MORE INVESTIGATION")