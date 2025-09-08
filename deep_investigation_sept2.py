#!/usr/bin/env python3
"""
DEEP INVESTIGATION OF SEPTEMBER 2 MISSING DATA
- Find missing $102 revenue
- Find missing employee appointments
- Check raw API responses without filtering
- Investigate different data sources
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def deep_investigation_sept2():
    """Deep investigation of all data sources for September 2"""
    
    print("🕵️ DEEP INVESTIGATION: SEPTEMBER 2, 2025")
    print("=" * 60)
    print("MISSING: $102.00 revenue")
    print("MISSING: 2 employees (Doan, Joley, Alexa, Audrey)")
    print("INVESTIGATING: All possible data sources")
    
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
    
    # Define September 2, 2025
    target_date = datetime(2025, 9, 2)
    start_str = target_date.strftime('%Y-%m-%dT00:00:00Z')
    end_str = (target_date + timedelta(days=1) - timedelta(seconds=1)).strftime('%Y-%m-%dT23:59:59Z')
    
    # ==============================================================
    # CHECK 1: ORDERS API FOR RETAIL/PRODUCT SALES
    # ==============================================================
    print(f"\n📦 CHECK 1: ORDERS API FOR RETAIL/PRODUCT SALES")
    print("=" * 50)
    print("Looking for product sales that might account for missing $102")
    
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
            
            print(f"✅ Orders found: {len(orders)}")
            
            orders_total = 0
            service_orders = 0
            product_orders = 0
            
            for order in orders:
                total_money = order.get('total_money', {})
                order_amount = float(total_money.get('amount', 0)) / 100
                orders_total += order_amount
                
                line_items = order.get('line_items', [])
                has_services = False
                has_products = False
                
                for item in line_items:
                    item_type = item.get('item_type', 'Unknown')
                    if 'SERVICE' in item_type.upper():
                        has_services = True
                    elif 'PRODUCT' in item_type.upper():
                        has_products = True
                
                if has_services:
                    service_orders += 1
                if has_products:
                    product_orders += 1
            
            print(f"Orders breakdown:")
            print(f"  Total orders: {len(orders)}")
            print(f"  Total order value: ${orders_total:.2f}")
            print(f"  Service orders: {service_orders}")
            print(f"  Product orders: {product_orders}")
            
            # Show sample orders
            print(f"\nSample orders:")
            for i, order in enumerate(orders[:5], 1):
                order_id = order.get('id', 'No ID')[:12]
                total_money = order.get('total_money', {})
                amount = float(total_money.get('amount', 0)) / 100
                created_at = order.get('created_at', '')[:16]
                state = order.get('state', 'Unknown')
                
                print(f"  {i}. ${amount:.2f} | {state} | {created_at} | {order_id}")
        else:
            print(f"❌ Orders API error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting orders: {e}")
    
    # ==============================================================
    # CHECK 2: RAW BOOKINGS DATA - NO FILTERS
    # ==============================================================
    print(f"\n📋 CHECK 2: RAW BOOKINGS DATA - NO FILTERS")
    print("=" * 50)
    print("Getting ALL bookings data without any filtering")
    
    # Get completely raw bookings data
    all_raw_bookings = []
    cursor = None
    
    while True:
        # Minimal filtering - just date range
        url = f"{api_base_url}/v2/bookings?limit=200&start_at_min={start_str}&start_at_max={end_str}"
        if cursor:
            url += f"&cursor={cursor}"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                bookings = data.get('bookings', [])
                all_raw_bookings.extend(bookings)
                
                cursor = data.get('cursor')
                if not cursor:
                    break
            else:
                print(f"❌ Raw bookings error: {response.status_code}")
                break
        except Exception as e:
            print(f"❌ Error: {e}")
            break
    
    print(f"✅ Raw bookings found: {len(all_raw_bookings)}")
    
    # Analyze ALL status types
    status_breakdown = {}
    employee_breakdown = {}
    
    for booking in all_raw_bookings:
        status = booking.get('status', 'Unknown')
        status_breakdown[status] = status_breakdown.get(status, 0) + 1
        
        # Check all segments for employees
        segments = booking.get('appointment_segments', [])
        for segment in segments:
            tm_id = segment.get('team_member_id')
            if tm_id:
                employee_breakdown[tm_id] = employee_breakdown.get(tm_id, 0) + 1
    
    print(f"\nBooking status breakdown:")
    for status, count in sorted(status_breakdown.items(), key=lambda x: x[1], reverse=True):
        print(f"  {status}: {count} bookings")
    
    print(f"\nEmployee breakdown (from RAW data):")
    # Load team member names
    try:
        with open('/tmp/team_member_id_name_mapping.json', 'r') as f:
            mapping_data = json.load(f)
        team_mapping = mapping_data['id_to_name_mapping']
    except:
        team_mapping = {}
    
    for tm_id, count in sorted(employee_breakdown.items(), key=lambda x: x[1], reverse=True):
        name = team_mapping.get(tm_id, {}).get('name', 'Unknown')
        print(f"  {name} ({tm_id}): {count} appointments")
    
    # ==============================================================
    # CHECK 3: EMPLOYEE ROLES AND DETAILS
    # ==============================================================
    print(f"\n👥 CHECK 3: EMPLOYEE ROLES AND DETAILS")
    print("=" * 40)
    
    missing_employee_ids = [
        "NCDoTJ_BoSEJbZOgtTGz",  # Doan
        "TM9j4yQTVWFZxBs0",      # Joley  
        "TMWlOnAsLgKl5Cc9",      # Alexa
        "TMrs5J9E6YQmlg3V"       # Audrey
    ]
    
    print("Checking details for missing employees:")
    
    # Get detailed team member info
    try:
        search_body = {"limit": 100}
        response = requests.post(f"{api_base_url}/v2/team-members/search", 
                               headers=headers, 
                               json=search_body)
        
        if response.status_code == 200:
            data = response.json()
            all_members = data.get('team_members', [])
            
            for member in all_members:
                member_id = member.get('id')
                if member_id in missing_employee_ids:
                    name = f"{member.get('given_name', '')} {member.get('family_name', '')}".strip()
                    status = member.get('status', 'Unknown')
                    is_owner = member.get('is_owner', False)
                    
                    print(f"\n  👤 {name} ({member_id})")
                    print(f"     Status: {status}")
                    print(f"     Is Owner: {is_owner}")
                    
                    # Check wage settings for role clues
                    wage_setting = member.get('wage_setting', {})
                    if wage_setting:
                        print(f"     Wage Info: {wage_setting}")
                    
                    # Check if they appear in our booking data at all
                    if member_id in employee_breakdown:
                        print(f"     ✅ HAS APPOINTMENTS: {employee_breakdown[member_id]} on Sept 2")
                    else:
                        print(f"     ❌ NO APPOINTMENTS: Not in booking data")
    
    except Exception as e:
        print(f"❌ Error getting employee details: {e}")
    
    # ==============================================================
    # CHECK 4: PAYMENT LINE ITEM DETAILS
    # ==============================================================
    print(f"\n💰 CHECK 4: PAYMENT LINE ITEM DETAILS")
    print("=" * 40)
    print("Checking for detailed payment breakdown to find missing $102")
    
    # Get payments again and look at detailed breakdown
    cursor = None
    all_payments_detailed = []
    
    while True:
        url = f"{api_base_url}/v2/payments?begin_time={start_str}&end_time={end_str}&limit=200"
        if cursor:
            url += f"&cursor={cursor}"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                payments = data.get('payments', [])
                all_payments_detailed.extend(payments)
                
                cursor = data.get('cursor')
                if not cursor:
                    break
            else:
                break
        except:
            break
    
    # Detailed payment analysis
    completed_total = 0
    tip_total = 0
    
    print(f"Detailed payment breakdown:")
    print(f"{'#':<3} {'TIME':<8} {'STATUS':<12} {'BASE':<8} {'TIP':<8} {'TOTAL':<8} {'TYPE'}")
    print("-" * 65)
    
    for i, payment in enumerate(all_payments_detailed, 1):
        status = payment.get('status', 'Unknown')
        total_amount = float(payment.get('total_money', {}).get('amount', 0)) / 100
        tip_amount = float(payment.get('tip_money', {}).get('amount', 0)) / 100
        base_amount = total_amount - tip_amount
        
        created_time = payment.get('created_at', '')
        time_display = created_time[11:16] if created_time else 'N/A'
        source_type = payment.get('source_type', 'Unknown')
        
        print(f"{i:<3} {time_display:<8} {status:<12} ${base_amount:<7.2f} ${tip_amount:<7.2f} ${total_amount:<7.2f} {source_type}")
        
        if status == 'COMPLETED':
            completed_total += total_amount
            tip_total += tip_amount
    
    print("-" * 65)
    print(f"COMPLETED payments total: ${completed_total:.2f}")
    print(f"Tips included: ${tip_total:.2f}")
    print(f"Target: $1,217.94")
    print(f"Still missing: ${1217.94 - completed_total:.2f}")
    
    # ==============================================================
    # CHECK 5: MANUAL CALENDAR COUNT
    # ==============================================================
    print(f"\n📅 CHECK 5: MANUAL CALENDAR COUNT ANALYSIS")
    print("=" * 45)
    print("Based on calendar screenshot analysis:")
    
    # From the calendar screenshot, let me try to identify what I can see
    print("Calendar columns observed:")
    print("  • Alexa (green appointments)")
    print("  • Audrey (appointments visible)")  
    print("  • Doan (appointments visible)")
    print("  • Front Desk columns")
    print("  • Joley (appointments visible)")
    print("  • Laine (appointments visible)")
    print("  • Rylie (appointments visible)")
    print("  • Sarah (appointments visible)")
    print("  • Tayler (appointments visible)")
    
    print("\nHypothesis:")
    print("  1. Some employees do front desk/admin work (no service appointments)")
    print("  2. Some appointments might be blocked time or non-service")
    print("  3. Revenue might include retail sales not tied to appointments")
    print("  4. Date/time zone issues in API calls")
    
    return {
        'raw_bookings': len(all_raw_bookings),
        'completed_revenue': completed_total if 'completed_total' in locals() else 0,
        'employee_count': len(employee_breakdown),
        'orders_total': orders_total if 'orders_total' in locals() else 0
    }

if __name__ == "__main__":
    results = deep_investigation_sept2()
    
    print(f"\n" + "=" * 60)
    print("🕵️ INVESTIGATION SUMMARY:")
    print(f"Raw bookings: {results['raw_bookings']}")
    print(f"Employees in bookings: {results['employee_count']}")
    print(f"Completed payments: ${results['completed_revenue']:.2f}")
    print(f"Orders total: ${results['orders_total']:.2f}")
    print()
    print("NEXT: Analyze findings and implement fixes")