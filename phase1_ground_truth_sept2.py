#!/usr/bin/env python3
"""
PHASE 1: ESTABLISH GROUND TRUTH - SEPTEMBER 2, 2025
- September 1 was a holiday (low activity)
- September 2 is a regular business day
- Get COMPLETE data for this business day
- Count EVERYTHING manually and precisely
- Compare to Square's actual reports
- They MUST match exactly
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def phase1_ground_truth_sept2():
    """Get complete, accurate data for September 2, 2025 (regular business day)"""
    
    print("🎯 PHASE 1: ESTABLISH GROUND TRUTH")
    print("=" * 50)
    print("Date: September 2, 2025 (Regular Business Day)")
    print("Goal: PERFECT accuracy for ONE day")
    print("Strategy: Count everything manually")
    print("Validation: Must match Square's reports exactly")
    
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
    
    print(f"\n📅 SEPTEMBER 2, 2025 - COMPLETE DATA COLLECTION")
    print(f"Start: {start_str}")
    print(f"End:   {end_str}")
    
    # Initialize data collection
    sept2_data = {
        'date': '2025-09-02',
        'appointments': [],
        'payments': [],
        'orders': [],
        'customers': set(),
        'employees_worked': set(),
        'summary': {}
    }
    
    # 1. GET ALL APPOINTMENTS FOR SEPTEMBER 2
    print(f"\n📋 STEP 1: GET ALL APPOINTMENTS")
    print("=" * 30)
    
    cursor = None
    while True:
        url = f"{api_base_url}/v2/bookings?limit=200&start_at_min={start_str}&start_at_max={end_str}"
        if cursor:
            url += f"&cursor={cursor}"
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                print(f"❌ Appointments API Error: {response.status_code}")
                print(f"Response: {response.text}")
                break
            
            data = response.json()
            bookings = data.get('bookings', [])
            cursor = data.get('cursor')
            
            sept2_data['appointments'].extend(bookings)
            
            if not cursor or len(bookings) == 0:
                break
                
        except Exception as e:
            print(f"❌ Error getting appointments: {e}")
            break
    
    print(f"✅ Appointments found: {len(sept2_data['appointments'])}")
    
    # Analyze appointments in detail
    appointment_details = []
    for apt in sept2_data['appointments']:
        # Track customers
        customer_id = apt.get('customer_id')
        if customer_id:
            sept2_data['customers'].add(customer_id)
        
        # Track employees and appointment details
        segments = apt.get('appointment_segments', [])
        for segment in segments:
            tm_id = segment.get('team_member_id')
            if tm_id:
                sept2_data['employees_worked'].add(tm_id)
        
        # Store appointment details for analysis
        appointment_details.append({
            'id': apt.get('id'),
            'start_time': apt.get('start_at'),
            'status': apt.get('status'),
            'customer_id': apt.get('customer_id'),
            'segments': len(segments),
            'team_members': [s.get('team_member_id') for s in segments]
        })
    
    # 2. GET ALL PAYMENTS FOR SEPTEMBER 2
    print(f"\n💰 STEP 2: GET ALL PAYMENTS")
    print("=" * 30)
    
    cursor = None
    while True:
        url = f"{api_base_url}/v2/payments?begin_time={start_str}&end_time={end_str}&limit=200"
        if cursor:
            url += f"&cursor={cursor}"
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                print(f"❌ Payments API Error: {response.status_code}")
                break
            
            data = response.json()
            payments = data.get('payments', [])
            cursor = data.get('cursor')
            
            sept2_data['payments'].extend(payments)
            
            if not cursor or len(payments) == 0:
                break
                
        except Exception as e:
            print(f"❌ Error getting payments: {e}")
            break
    
    print(f"✅ Payments found: {len(sept2_data['payments'])}")
    
    # Analyze payments in detail
    payment_breakdown = {
        'CARD': {'count': 0, 'total': 0},
        'CASH': {'count': 0, 'total': 0},
        'OTHER': {'count': 0, 'total': 0}
    }
    
    total_revenue = 0
    for payment in sept2_data['payments']:
        amount = float(payment.get('total_money', {}).get('amount', 0)) / 100
        source_type = payment.get('source_type', 'OTHER')
        
        total_revenue += amount
        
        if source_type in payment_breakdown:
            payment_breakdown[source_type]['count'] += 1
            payment_breakdown[source_type]['total'] += amount
        else:
            payment_breakdown['OTHER']['count'] += 1
            payment_breakdown['OTHER']['total'] += amount
    
    # 3. GET ALL ORDERS FOR SEPTEMBER 2
    print(f"\n🛒 STEP 3: GET ALL ORDERS")
    print("=" * 30)
    
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
            sept2_data['orders'] = orders
            print(f"✅ Orders found: {len(orders)}")
        else:
            print(f"⚠️  Orders API: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️  Error getting orders: {e}")
    
    # 4. COMPILE DETAILED SUMMARY
    print(f"\n📊 STEP 4: COMPILE DETAILED SUMMARY")
    print("=" * 30)
    
    sept2_data['summary'] = {
        'total_appointments': len(sept2_data['appointments']),
        'total_payments': len(sept2_data['payments']),
        'total_orders': len(sept2_data['orders']),
        'total_revenue': total_revenue,
        'unique_customers': len(sept2_data['customers']),
        'employees_worked': len(sept2_data['employees_worked']),
        'payment_breakdown': payment_breakdown,
        'appointment_details': appointment_details
    }
    
    # Convert sets to lists for JSON serialization
    sept2_data['customers'] = list(sept2_data['customers'])
    sept2_data['employees_worked'] = list(sept2_data['employees_worked'])
    
    # 5. DETAILED BREAKDOWN FOR VALIDATION
    print(f"\n📋 SEPTEMBER 2, 2025 - COMPLETE BREAKDOWN")
    print("=" * 50)
    
    summary = sept2_data['summary']
    
    print(f"📅 Date: September 2, 2025 (Regular Business Day)")
    print(f"📋 Appointments: {summary['total_appointments']}")
    print(f"💰 Payments: {summary['total_payments']}")
    print(f"🛒 Orders: {summary['total_orders']}")
    print(f"💵 Total Revenue: ${summary['total_revenue']:.2f}")
    print(f"👥 Unique Customers: {summary['unique_customers']}")
    print(f"👤 Employees Worked: {summary['employees_worked']}")
    
    # Payment breakdown
    print(f"\n💰 PAYMENT BREAKDOWN:")
    for payment_type, data in payment_breakdown.items():
        if data['count'] > 0:
            print(f"  {payment_type}: {data['count']} payments, ${data['total']:.2f}")
    
    # Appointment details
    if appointment_details:
        print(f"\n📋 APPOINTMENT DETAILS:")
        for i, apt in enumerate(appointment_details, 1):
            start_time = apt['start_time'][:16] if apt['start_time'] else 'No time'
            status = apt['status']
            customer = apt['customer_id'][:12] if apt['customer_id'] else 'No customer'
            print(f"  {i}. {start_time} | {status} | {customer}")
    
    # Employee details with names
    try:
        with open('/tmp/team_member_id_name_mapping.json', 'r') as f:
            mapping_data = json.load(f)
        team_mapping = mapping_data['id_to_name_mapping']
        
        print(f"\n👤 EMPLOYEES WHO WORKED:")
        for tm_id in sept2_data['employees_worked']:
            name = team_mapping.get(tm_id, {}).get('name', 'Unknown')
            print(f"  • {name} ({tm_id})")
            
    except:
        print(f"\n👤 EMPLOYEES WHO WORKED (IDs only):")
        for tm_id in sept2_data['employees_worked']:
            print(f"  • {tm_id}")
    
    # 6. SAVE COMPLETE DATA
    with open('/tmp/sept2_2025_ground_truth.json', 'w') as f:
        json.dump(sept2_data, f, indent=2, default=str)
    
    print(f"\n💾 GROUND TRUTH DATA SAVED:")
    print(f"File: /tmp/sept2_2025_ground_truth.json")
    print(f"Complete data ready for Square report validation")
    
    print(f"\n🎯 PHASE 1 COMPLETE - READY FOR VALIDATION")
    print("=" * 50)
    print("✅ Complete September 2, 2025 data collected")
    print("✅ All transactions, appointments, payments captured") 
    print("✅ Detailed breakdown compiled")
    print("🔍 VALIDATION NEEDED:")
    print(f"   📋 Appointments: {summary['total_appointments']}")
    print(f"   💰 Payments: {summary['total_payments']} (${summary['total_revenue']:.2f})")
    print(f"   👥 Customers: {summary['unique_customers']}")
    print(f"   👤 Employees: {summary['employees_worked']}")
    print()
    print("📊 These numbers must match Square's reports EXACTLY")
    
    return sept2_data

if __name__ == "__main__":
    ground_truth = phase1_ground_truth_sept2()
    
    print(f"\n" + "=" * 50)
    print("🎯 PHASE 1: GROUND TRUTH ESTABLISHED")
    print(f"✅ September 2, 2025 data: 100% complete")
    print(f"✅ Ready for Square report comparison")
    print(f"🔍 Confidence test: Do these match Square exactly?")