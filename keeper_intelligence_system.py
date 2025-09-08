#!/usr/bin/env python3
"""
KEEPER COMPLETE INTELLIGENCE SYSTEM
- Employee Intelligence Dashboard (5 categories)
- Customer Intelligence Dashboard (4 categories)
- Cross-Analysis Pattern Detection
- Sample analysis for one employee and one customer

This is the $99/month value - complete business intelligence
"""

import os
import json
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

def keeper_intelligence_system():
    """Build complete intelligence system for employees and customers"""
    
    print("🧠 KEEPER COMPLETE INTELLIGENCE SYSTEM")
    print("=" * 60)
    print("Building the $99/month business intelligence engine")
    print("EMPLOYEE INTELLIGENCE + CUSTOMER INTELLIGENCE + PATTERN ANALYSIS")
    
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
    
    # Analysis period - last 30 days for meaningful patterns
    end_date = datetime(2025, 9, 8)  # Today
    start_date = end_date - timedelta(days=30)
    
    start_str = start_date.strftime('%Y-%m-%dT00:00:00Z')
    end_str = end_date.strftime('%Y-%m-%dT23:59:59Z')
    
    print(f"Analysis Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} (30 days)")
    
    # ==============================================================
    # DATA COLLECTION: APPOINTMENTS, PAYMENTS, CUSTOMERS
    # ==============================================================
    print(f"\n📊 STEP 1: COLLECT ALL BUSINESS DATA")
    print("=" * 35)
    
    # Get all appointments
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
                break
        except:
            break
    
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
    
    # Get customer database
    all_customers = []
    cursor = None
    while True:
        url = f"{api_base_url}/v2/customers?limit=100"
        if cursor:
            url += f"&cursor={cursor}"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                customers = data.get('customers', [])
                all_customers.extend(customers)
                cursor = data.get('cursor')
                if not cursor:
                    break
            else:
                break
        except:
            break
    
    print(f"✅ Data collected:")
    print(f"  Appointments: {len(all_appointments)}")
    print(f"  Payments: {len(all_payments)}")  
    print(f"  Customers: {len(all_customers)}")
    
    # Get team members
    team_members = {}
    try:
        search_body = {"limit": 100}
        response = requests.post(f"{api_base_url}/v2/team-members/search", 
                               headers=headers, 
                               json=search_body)
        
        if response.status_code == 200:
            data = response.json()
            members = data.get('team_members', [])
            for member in members:
                member_id = member.get('id')
                full_name = f"{member.get('given_name', '')} {member.get('family_name', '')}".strip()
                team_members[member_id] = {
                    'name': full_name,
                    'status': member.get('status', 'Unknown'),
                    'data': member
                }
        
        print(f"  Team members: {len(team_members)}")
        
    except Exception as e:
        print(f"⚠️  Could not load team members: {e}")
    
    # ==============================================================
    # EMPLOYEE INTELLIGENCE DASHBOARD
    # ==============================================================
    print(f"\n👩‍💼 STEP 2: EMPLOYEE INTELLIGENCE DASHBOARD")
    print("=" * 45)
    
    employee_intelligence = {}
    
    # Process each team member
    estheticians = []  # Filter to only service providers
    
    for member_id, member_info in team_members.items():
        name = member_info['name']
        
        # Skip front desk and inactive employees
        if member_info['status'] != 'ACTIVE':
            continue
        if 'front desk' in name.lower() or 'ipad' in name.lower():
            continue
            
        # Check if they have appointments (service provider)
        has_appointments = False
        for apt in all_appointments:
            segments = apt.get('appointment_segments', [])
            for segment in segments:
                if segment.get('team_member_id') == member_id:
                    has_appointments = True
                    break
            if has_appointments:
                break
        
        if has_appointments:
            estheticians.append(member_id)
    
    print(f"Active estheticians found: {len(estheticians)}")
    for member_id in estheticians:
        print(f"  • {team_members[member_id]['name']}")
    
    # Analyze each esthetician
    for member_id in estheticians:
        employee_name = team_members[member_id]['name']
        
        # ==============================================================
        # 1. UTILIZATION METRICS
        # ==============================================================
        employee_appointments = []
        total_appointment_minutes = 0
        
        for apt in all_appointments:
            segments = apt.get('appointment_segments', [])
            for segment in segments:
                if segment.get('team_member_id') == member_id:
                    employee_appointments.append({
                        'appointment': apt,
                        'segment': segment,
                        'start_time': apt.get('start_at'),
                        'status': apt.get('status'),
                        'customer_id': apt.get('customer_id')
                    })
                    total_appointment_minutes += segment.get('duration_minutes', 0)
        
        total_appointment_hours = total_appointment_minutes / 60
        
        # Assume 8 hours/day, 5 days/week for 30 days = ~173 hours available
        estimated_available_hours = (30 / 7) * 5 * 8  # 30 days worth of work
        utilization = (total_appointment_hours / estimated_available_hours) * 100 if estimated_available_hours > 0 else 0
        
        # ==============================================================
        # 2. REVENUE METRICS  
        # ==============================================================
        employee_payments = []
        total_revenue = 0
        total_tips = 0
        total_base_revenue = 0
        
        # Match payments to appointments by time/customer
        for payment in all_payments:
            payment_time = payment.get('created_at')
            payment_customer = payment.get('customer_id')
            
            # Look for appointments around the same time
            if payment.get('status') == 'COMPLETED':
                payment_date = payment_time[:10] if payment_time else ''
                
                for emp_apt in employee_appointments:
                    apt_date = emp_apt['start_time'][:10] if emp_apt['start_time'] else ''
                    apt_customer = emp_apt['customer_id']
                    
                    # Match by date and customer
                    if payment_date == apt_date and payment_customer == apt_customer:
                        employee_payments.append(payment)
                        
                        amount = float(payment.get('total_money', {}).get('amount', 0)) / 100
                        tip = float(payment.get('tip_money', {}).get('amount', 0)) / 100
                        base = amount - tip
                        
                        total_revenue += amount
                        total_tips += tip
                        total_base_revenue += base
                        break
        
        revenue_per_hour = total_revenue / total_appointment_hours if total_appointment_hours > 0 else 0
        avg_ticket_size = total_revenue / len(employee_payments) if employee_payments else 0
        
        # ==============================================================
        # 3. SERVICE QUALITY INDICATORS
        # ==============================================================
        tip_percentage = (total_tips / total_base_revenue) * 100 if total_base_revenue > 0 else 0
        avg_tip_per_appointment = total_tips / len(employee_appointments) if employee_appointments else 0
        
        # ==============================================================
        # 4. RELIABILITY METRICS
        # ==============================================================
        completed_appointments = [apt for apt in employee_appointments if apt['status'] == 'COMPLETED']
        canceled_appointments = [apt for apt in employee_appointments if apt['status'] in ['CANCELED', 'CANCELLED']]
        
        completion_rate = (len(completed_appointments) / len(employee_appointments)) * 100 if employee_appointments else 0
        cancellation_rate = (len(canceled_appointments) / len(employee_appointments)) * 100 if employee_appointments else 0
        
        # ==============================================================
        # 5. CLIENT RETENTION (SIMPLIFIED)
        # ==============================================================
        unique_customers = set()
        repeat_customers = set()
        customer_visit_count = defaultdict(int)
        
        for apt in completed_appointments:
            customer_id = apt['customer_id']
            if customer_id:
                customer_visit_count[customer_id] += 1
                unique_customers.add(customer_id)
                if customer_visit_count[customer_id] > 1:
                    repeat_customers.add(customer_id)
        
        retention_rate = (len(repeat_customers) / len(unique_customers)) * 100 if unique_customers else 0
        
        # Store employee intelligence
        employee_intelligence[member_id] = {
            'name': employee_name,
            'utilization': {
                'appointment_hours': total_appointment_hours,
                'available_hours': estimated_available_hours,
                'utilization_percentage': utilization,
                'total_appointments': len(employee_appointments)
            },
            'revenue': {
                'total_revenue': total_revenue,
                'revenue_per_hour': revenue_per_hour,
                'avg_ticket_size': avg_ticket_size,
                'total_tips': total_tips,
                'base_revenue': total_base_revenue
            },
            'quality': {
                'tip_percentage': tip_percentage,
                'avg_tip_per_appointment': avg_tip_per_appointment
            },
            'reliability': {
                'completion_rate': completion_rate,
                'cancellation_rate': cancellation_rate,
                'completed_appointments': len(completed_appointments),
                'canceled_appointments': len(canceled_appointments)
            },
            'retention': {
                'unique_customers': len(unique_customers),
                'repeat_customers': len(repeat_customers),
                'retention_rate': retention_rate
            }
        }
    
    print(f"✅ Employee intelligence calculated for {len(employee_intelligence)} estheticians")
    
    # ==============================================================
    # CUSTOMER INTELLIGENCE DASHBOARD  
    # ==============================================================
    print(f"\n👤 STEP 3: CUSTOMER INTELLIGENCE DASHBOARD")
    print("=" * 40)
    
    customer_intelligence = {}
    
    # Analyze top customers (those with multiple visits)
    customer_appointments = defaultdict(list)
    customer_payments = defaultdict(list)
    
    # Group appointments by customer
    for apt in all_appointments:
        customer_id = apt.get('customer_id')
        if customer_id and apt.get('status') == 'COMPLETED':
            customer_appointments[customer_id].append(apt)
    
    # Group payments by customer
    for payment in all_payments:
        customer_id = payment.get('customer_id')
        if customer_id and payment.get('status') == 'COMPLETED':
            customer_payments[customer_id].append(payment)
    
    # Analyze top customers (3+ visits or $200+ spent)
    top_customers = []
    for customer_id in customer_appointments.keys():
        if len(customer_appointments[customer_id]) >= 3:  # 3+ visits
            top_customers.append(customer_id)
        elif customer_id in customer_payments:
            total_spent = sum(float(p.get('total_money', {}).get('amount', 0)) / 100 
                            for p in customer_payments[customer_id])
            if total_spent >= 200:  # $200+ spent
                top_customers.append(customer_id)
    
    print(f"Analyzing top {len(top_customers)} customers")
    
    # Analyze each top customer
    for customer_id in top_customers[:10]:  # Analyze top 10 customers
        # Find customer details
        customer_name = customer_id[:12] + "..."  # Default to ID
        customer_email = ""
        
        for customer in all_customers:
            if customer.get('id') == customer_id:
                given_name = customer.get('given_name', '')
                family_name = customer.get('family_name', '')
                customer_name = f"{given_name} {family_name}".strip() or customer_id[:12] + "..."
                customer_email = customer.get('email_address', '')
                break
        
        # ==============================================================
        # 1. VALUE METRICS
        # ==============================================================
        customer_apts = customer_appointments[customer_id]
        customer_pays = customer_payments.get(customer_id, [])
        
        lifetime_value = sum(float(p.get('total_money', {}).get('amount', 0)) / 100 
                            for p in customer_pays)
        
        # Calculate visit frequency
        if len(customer_apts) > 1:
            first_visit = min(apt.get('start_at', '') for apt in customer_apts)
            last_visit = max(apt.get('start_at', '') for apt in customer_apts)
            
            if first_visit and last_visit:
                try:
                    first_date = datetime.fromisoformat(first_visit.replace('Z', '+00:00'))
                    last_date = datetime.fromisoformat(last_visit.replace('Z', '+00:00'))
                    days_span = (last_date - first_date).days
                    visit_frequency = len(customer_apts) / (days_span / 30) if days_span > 0 else 0  # visits per month
                except:
                    visit_frequency = 0
            else:
                visit_frequency = 0
        else:
            visit_frequency = 0
        
        avg_spend = lifetime_value / len(customer_pays) if customer_pays else 0
        
        # ==============================================================
        # 2. BEHAVIOR PATTERNS
        # ==============================================================
        # Find favorite employee
        employee_visits = defaultdict(int)
        for apt in customer_apts:
            segments = apt.get('appointment_segments', [])
            for segment in segments:
                emp_id = segment.get('team_member_id')
                if emp_id and emp_id in team_members:
                    employee_visits[emp_id] += 1
        
        favorite_employee = ""
        if employee_visits:
            fav_emp_id = max(employee_visits.items(), key=lambda x: x[1])[0]
            favorite_employee = team_members[fav_emp_id]['name']
        
        # Calculate days since last visit
        if customer_apts:
            last_visit_str = max(apt.get('start_at', '') for apt in customer_apts)
            if last_visit_str:
                try:
                    last_visit_date = datetime.fromisoformat(last_visit_str.replace('Z', '+00:00'))
                    days_since_last = (end_date.replace(tzinfo=last_visit_date.tzinfo) - last_visit_date).days
                except:
                    days_since_last = 999
            else:
                days_since_last = 999
        else:
            days_since_last = 999
        
        # ==============================================================
        # 3. RISK INDICATORS
        # ==============================================================
        at_risk = False
        risk_factors = []
        
        if days_since_last > 60:
            at_risk = True
            risk_factors.append(f"No visit in {days_since_last} days")
        
        if visit_frequency < 0.5:  # Less than once every 2 months
            risk_factors.append("Low visit frequency")
        
        if avg_spend < 50:  # Low average spend
            risk_factors.append("Low average spend")
        
        # ==============================================================
        # 4. QUALITY INDICATORS
        # ==============================================================
        total_tips = sum(float(p.get('tip_money', {}).get('amount', 0)) / 100 
                        for p in customer_pays)
        total_base = lifetime_value - total_tips
        tip_percentage = (total_tips / total_base) * 100 if total_base > 0 else 0
        
        # Store customer intelligence
        customer_intelligence[customer_id] = {
            'name': customer_name,
            'email': customer_email,
            'value': {
                'lifetime_value': lifetime_value,
                'visit_frequency': visit_frequency,  # visits per month
                'avg_spend': avg_spend,
                'total_visits': len(customer_apts)
            },
            'behavior': {
                'favorite_employee': favorite_employee,
                'days_since_last_visit': days_since_last,
                'employee_visits': dict(employee_visits)
            },
            'risk': {
                'at_risk': at_risk,
                'risk_factors': risk_factors,
                'days_since_last': days_since_last
            },
            'quality': {
                'tip_percentage': tip_percentage,
                'avg_tip': total_tips / len(customer_pays) if customer_pays else 0
            }
        }
    
    print(f"✅ Customer intelligence calculated for {len(customer_intelligence)} customers")
    
    # ==============================================================
    # SAMPLE ANALYSIS: ONE EMPLOYEE + ONE CUSTOMER
    # ==============================================================
    print(f"\n🎯 STEP 4: SAMPLE KEEPER INTELLIGENCE REPORT")
    print("=" * 45)
    
    # Pick Laine as sample employee
    sample_employee_id = None
    for emp_id, emp_data in employee_intelligence.items():
        if 'laine' in emp_data['name'].lower():
            sample_employee_id = emp_id
            break
    
    # Pick top customer as sample
    sample_customer_id = None
    if customer_intelligence:
        # Pick customer with highest lifetime value
        sample_customer_id = max(customer_intelligence.items(), 
                               key=lambda x: x[1]['value']['lifetime_value'])[0]
    
    if sample_employee_id and sample_customer_id:
        emp_data = employee_intelligence[sample_employee_id]
        cust_data = customer_intelligence[sample_customer_id]
        
        print(f"📊 EMPLOYEE ANALYSIS: {emp_data['name']}")
        print("-" * 30)
        print(f"UTILIZATION:")
        print(f"  ✅ {emp_data['utilization']['utilization_percentage']:.1f}% utilization ({emp_data['utilization']['appointment_hours']:.1f}h booked)")
        print(f"  📅 {emp_data['utilization']['total_appointments']} appointments in 30 days")
        
        print(f"\nREVENUE PERFORMANCE:")
        print(f"  💰 ${emp_data['revenue']['total_revenue']:.0f} total revenue")
        print(f"  ⏰ ${emp_data['revenue']['revenue_per_hour']:.0f}/hour average")
        print(f"  🎫 ${emp_data['revenue']['avg_ticket_size']:.0f} average ticket")
        
        print(f"\nSERVICE QUALITY:")
        print(f"  💸 {emp_data['quality']['tip_percentage']:.1f}% average tips")
        print(f"  🏆 ${emp_data['quality']['avg_tip_per_appointment']:.2f} average tip per service")
        
        print(f"\nRELIABILITY:")
        print(f"  ✅ {emp_data['reliability']['completion_rate']:.1f}% completion rate")
        print(f"  ❌ {emp_data['reliability']['cancellation_rate']:.1f}% cancellation rate")
        
        print(f"\nCLIENT RETENTION:")
        print(f"  🔄 {emp_data['retention']['retention_rate']:.1f}% client retention")
        print(f"  👥 {emp_data['retention']['unique_customers']} unique clients")
        
        # Generate insights
        insights = []
        if emp_data['quality']['tip_percentage'] > 20:
            insights.append(f"🌟 HIGH PERFORMER: {emp_data['quality']['tip_percentage']:.1f}% tips indicates excellent service")
        if emp_data['retention']['retention_rate'] > 60:
            insights.append(f"👑 CLIENT FAVORITE: {emp_data['retention']['retention_rate']:.1f}% retention - clients love them")
        if emp_data['utilization']['utilization_percentage'] > 50:
            insights.append(f"📈 BUSY EMPLOYEE: {emp_data['utilization']['utilization_percentage']:.1f}% utilization - consider raise")
        
        print(f"\n💡 INSIGHTS:")
        for insight in insights:
            print(f"  {insight}")
        
        print(f"\n" + "=" * 45)
        print(f"👤 CUSTOMER ANALYSIS: {cust_data['name']}")
        print("-" * 30)
        print(f"VALUE METRICS:")
        print(f"  💰 ${cust_data['value']['lifetime_value']:.0f} lifetime value")
        print(f"  📅 {cust_data['value']['visit_frequency']:.1f} visits/month")
        print(f"  🎫 ${cust_data['value']['avg_spend']:.0f} average spend")
        print(f"  📊 {cust_data['value']['total_visits']} total visits")
        
        print(f"\nBEHAVIOR PATTERNS:")
        print(f"  ⭐ Favorite employee: {cust_data['behavior']['favorite_employee']}")
        print(f"  ⏰ Last visit: {cust_data['behavior']['days_since_last_visit']} days ago")
        
        print(f"\nRISK ANALYSIS:")
        print(f"  🚨 At risk: {'YES' if cust_data['risk']['at_risk'] else 'NO'}")
        if cust_data['risk']['risk_factors']:
            for factor in cust_data['risk']['risk_factors']:
                print(f"    • {factor}")
        
        print(f"\nQUALITY INDICATORS:")
        print(f"  💸 {cust_data['quality']['tip_percentage']:.1f}% tip rate")
        print(f"  💵 ${cust_data['quality']['avg_tip']:.2f} average tip")
        
        # Generate customer insights
        customer_insights = []
        if cust_data['risk']['at_risk']:
            customer_insights.append(f"🚨 AT RISK: Contact immediately - ${cust_data['value']['lifetime_value']:.0f} customer!")
        if cust_data['value']['lifetime_value'] > 500:
            customer_insights.append(f"👑 VIP CUSTOMER: ${cust_data['value']['lifetime_value']:.0f} lifetime value - priority treatment")
        if cust_data['quality']['tip_percentage'] > 25:
            customer_insights.append(f"😊 HAPPY CUSTOMER: {cust_data['quality']['tip_percentage']:.1f}% tips - excellent satisfaction")
        
        print(f"\n💡 INSIGHTS:")
        for insight in customer_insights:
            print(f"  {insight}")
    
    return {
        'employee_intelligence': employee_intelligence,
        'customer_intelligence': customer_intelligence,
        'estheticians_analyzed': len(employee_intelligence),
        'customers_analyzed': len(customer_intelligence)
    }

if __name__ == "__main__":
    result = keeper_intelligence_system()
    
    print(f"\n" + "=" * 60)
    print("🧠 KEEPER INTELLIGENCE SYSTEM COMPLETE")
    
    if result:
        print(f"✅ Employee intelligence: {result['estheticians_analyzed']} estheticians")
        print(f"✅ Customer intelligence: {result['customers_analyzed']} customers")
        print(f"\n🏆 THIS IS THE $99/MONTH VALUE:")
        print(f"  • Complete employee performance analysis")
        print(f"  • Customer risk and value assessment") 
        print(f"  • Actionable insights for business growth")
        print(f"  • Revenue optimization recommendations")
        
        print(f"\n💰 BUSINESS IMPACT:")
        print(f"  • Identify underperforming employees")
        print(f"  • Prevent customer churn")
        print(f"  • Optimize pricing and services")
        print(f"  • Improve staff utilization")
    else:
        print(f"❌ INTELLIGENCE SYSTEM BUILD FAILED")