#!/usr/bin/env python3
"""
SAMPLE KEEPER INTELLIGENCE REPORT
Generate detailed sample analysis for one employee (Laine) with real data
Show the $99/month value proposition
"""

import os
import json
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

def sample_keeper_intelligence():
    """Generate sample Keeper intelligence report for Laine"""
    
    print("🎯 KEEPER SAMPLE INTELLIGENCE REPORT")
    print("=" * 60)
    print("Demonstrating the $99/month business intelligence value")
    print("EMPLOYEE: Laine Duttlinger (Sample Analysis)")
    
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
    
    # Laine's ID and analysis period (last 30 days)
    laine_id = "TMZx2T5T5arYJTm7"
    end_date = datetime(2025, 9, 8)
    start_date = end_date - timedelta(days=30)
    
    start_str = start_date.strftime('%Y-%m-%dT00:00:00Z')
    end_str = end_date.strftime('%Y-%m-%dT23:59:59Z')
    
    print(f"Analysis Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # ==============================================================
    # GET LAINE'S APPOINTMENTS
    # ==============================================================
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
                
                for apt in bookings:
                    segments = apt.get('appointment_segments', [])
                    for segment in segments:
                        if segment.get('team_member_id') == laine_id:
                            laine_appointments.append({
                                'appointment_id': apt.get('id'),
                                'customer_id': apt.get('customer_id'),
                                'start_at': apt.get('start_at'),
                                'status': apt.get('status'),
                                'segment': segment
                            })
                
                cursor = data.get('cursor')
                if not cursor:
                    break
            else:
                break
        except:
            break
    
    # ==============================================================
    # GET PAYMENTS FOR LAINE'S APPOINTMENTS
    # ==============================================================
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
    
    # ==============================================================
    # MATCH PAYMENTS TO LAINE'S APPOINTMENTS
    # ==============================================================
    laine_payments = []
    
    # Create customer sets for Laine's appointments
    laine_customers = set()
    appointment_dates = set()
    
    for apt in laine_appointments:
        if apt['customer_id']:
            laine_customers.add(apt['customer_id'])
        if apt['start_at']:
            appointment_dates.add(apt['start_at'][:10])  # Date only
    
    # Find payments from Laine's customers on appointment dates
    for payment in all_payments:
        if payment.get('status') == 'COMPLETED':
            payment_customer = payment.get('customer_id')
            payment_date = payment.get('created_at', '')[:10]
            
            # If payment is from Laine's customer on appointment date
            if payment_customer in laine_customers and payment_date in appointment_dates:
                laine_payments.append(payment)
    
    print(f"✅ Data collected:")
    print(f"  Laine's appointments: {len(laine_appointments)}")
    print(f"  Matching payments: {len(laine_payments)}")
    print(f"  Unique customers: {len(laine_customers)}")
    
    # ==============================================================
    # CALCULATE EMPLOYEE INTELLIGENCE METRICS
    # ==============================================================
    print(f"\n📊 LAINE DUTTLINGER - EMPLOYEE INTELLIGENCE")
    print("=" * 50)
    
    # 1. UTILIZATION METRICS
    total_appointment_minutes = sum(apt['segment'].get('duration_minutes', 0) for apt in laine_appointments)
    total_appointment_hours = total_appointment_minutes / 60
    
    # Estimate available hours (assume 8 hours/day, 5 days/week)
    working_days = (end_date - start_date).days * (5/7)  # Weekdays only
    estimated_available_hours = working_days * 8
    utilization = (total_appointment_hours / estimated_available_hours) * 100 if estimated_available_hours > 0 else 0
    
    print(f"1️⃣  UTILIZATION ANALYSIS:")
    print(f"   📅 {len(laine_appointments)} appointments in 30 days")
    print(f"   ⏰ {total_appointment_hours:.1f} hours booked")
    print(f"   📊 {utilization:.1f}% utilization")
    
    if utilization > 60:
        print(f"   ✅ HIGH UTILIZATION - Busy employee, consider raise")
    elif utilization > 40:
        print(f"   🟡 MODERATE UTILIZATION - Room for growth")
    else:
        print(f"   🔴 LOW UTILIZATION - Needs improvement")
    
    # 2. REVENUE METRICS
    total_revenue = sum(float(p.get('total_money', {}).get('amount', 0)) / 100 for p in laine_payments)
    total_tips = sum(float(p.get('tip_money', {}).get('amount', 0)) / 100 for p in laine_payments)
    total_base_revenue = total_revenue - total_tips
    
    revenue_per_hour = total_revenue / total_appointment_hours if total_appointment_hours > 0 else 0
    avg_ticket_size = total_revenue / len(laine_payments) if laine_payments else 0
    
    print(f"\n2️⃣  REVENUE PERFORMANCE:")
    print(f"   💰 ${total_revenue:.0f} total revenue (30 days)")
    print(f"   ⏰ ${revenue_per_hour:.0f}/hour productivity")
    print(f"   🎫 ${avg_ticket_size:.0f} average ticket size")
    print(f"   📈 ${total_revenue * 12:.0f} annual revenue projection")
    
    # 3. SERVICE QUALITY INDICATORS  
    tip_percentage = (total_tips / total_base_revenue) * 100 if total_base_revenue > 0 else 0
    avg_tip_per_appointment = total_tips / len(laine_appointments) if laine_appointments else 0
    
    print(f"\n3️⃣  SERVICE QUALITY:")
    print(f"   💸 {tip_percentage:.1f}% tip rate")
    print(f"   🏆 ${avg_tip_per_appointment:.2f} average tip per service")
    print(f"   💵 ${total_tips:.0f} total tips earned")
    
    if tip_percentage > 20:
        print(f"   ✅ EXCELLENT SERVICE - Clients love Laine!")
    elif tip_percentage > 15:
        print(f"   🟡 GOOD SERVICE - Above average tips")
    else:
        print(f"   🔴 SERVICE ISSUE - Low tip rate")
    
    # 4. RELIABILITY METRICS
    completed_appointments = [apt for apt in laine_appointments if apt['status'] == 'COMPLETED']
    canceled_appointments = [apt for apt in laine_appointments if apt['status'] in ['CANCELED', 'CANCELLED']]
    
    completion_rate = (len(completed_appointments) / len(laine_appointments)) * 100 if laine_appointments else 0
    cancellation_rate = (len(canceled_appointments) / len(laine_appointments)) * 100 if laine_appointments else 0
    
    print(f"\n4️⃣  RELIABILITY:")
    print(f"   ✅ {completion_rate:.1f}% completion rate")
    print(f"   ❌ {cancellation_rate:.1f}% cancellation rate")
    print(f"   📊 {len(completed_appointments)} completed, {len(canceled_appointments)} canceled")
    
    if completion_rate > 90:
        print(f"   ✅ HIGHLY RELIABLE - Excellent attendance")
    elif completion_rate > 80:
        print(f"   🟡 RELIABLE - Good attendance")
    else:
        print(f"   🔴 RELIABILITY ISSUE - High cancellation rate")
    
    # 5. CLIENT RETENTION
    customer_visit_count = defaultdict(int)
    repeat_customers = set()
    
    for apt in completed_appointments:
        customer_id = apt['customer_id']
        if customer_id:
            customer_visit_count[customer_id] += 1
            if customer_visit_count[customer_id] > 1:
                repeat_customers.add(customer_id)
    
    unique_customers = len(customer_visit_count)
    retention_rate = (len(repeat_customers) / unique_customers) * 100 if unique_customers > 0 else 0
    
    print(f"\n5️⃣  CLIENT RETENTION:")
    print(f"   👥 {unique_customers} unique customers")
    print(f"   🔄 {len(repeat_customers)} repeat customers")
    print(f"   📈 {retention_rate:.1f}% retention rate")
    
    if retention_rate > 70:
        print(f"   ✅ EXCELLENT RETENTION - Clients love coming back!")
    elif retention_rate > 50:
        print(f"   🟡 GOOD RETENTION - Above average loyalty")
    else:
        print(f"   🔴 RETENTION ISSUE - Clients not returning")
    
    # ==============================================================
    # KEEPER INSIGHTS GENERATION
    # ==============================================================
    print(f"\n💡 KEEPER AI INSIGHTS:")
    print("=" * 25)
    
    insights = []
    actions = []
    
    # Utilization insights
    if utilization > 60:
        insights.append(f"🌟 Laine is a HIGH PERFORMER with {utilization:.1f}% utilization")
        actions.append(f"💰 RECOMMEND RAISE: Laine is maximizing her time")
    elif utilization < 40:
        insights.append(f"⚠️  Laine has LOW utilization at {utilization:.1f}%")
        actions.append(f"📈 INCREASE BOOKINGS: Marketing focus or schedule optimization")
    
    # Tip insights
    if tip_percentage > 20:
        insights.append(f"👑 Clients LOVE Laine - {tip_percentage:.1f}% tips vs ~15% average")
        actions.append(f"🏆 PROMOTE AS PREMIUM PROVIDER: Charge higher rates")
    
    # Revenue insights  
    if revenue_per_hour > 80:
        insights.append(f"💎 Laine generates ${revenue_per_hour:.0f}/hour - high productivity")
    elif revenue_per_hour < 50:
        insights.append(f"💸 Laine generates only ${revenue_per_hour:.0f}/hour - below target")
        actions.append(f"💰 UPSELLING TRAINING: Increase average ticket size")
    
    # Retention insights
    if retention_rate > 70:
        insights.append(f"🎯 EXCELLENT client retention at {retention_rate:.1f}%")
        actions.append(f"📚 USE AS TRAINING EXAMPLE: Study what Laine does right")
    
    # Print insights
    for insight in insights:
        print(f"   {insight}")
    
    print(f"\n🎯 RECOMMENDED ACTIONS:")
    for action in actions:
        print(f"   {action}")
    
    # ==============================================================
    # BUSINESS IMPACT CALCULATION
    # ==============================================================
    print(f"\n💰 BUSINESS IMPACT ANALYSIS:")
    print("=" * 30)
    
    # Calculate potential improvements
    if utilization < 60:
        potential_hours = (60 - utilization) / 100 * estimated_available_hours
        potential_revenue = potential_hours * revenue_per_hour
        print(f"📈 GROWTH OPPORTUNITY:")
        print(f"   Increase utilization to 60% = +{potential_hours:.1f} hours/month")
        print(f"   Potential revenue gain: +${potential_revenue:.0f}/month")
    
    # Annual projections
    annual_revenue = total_revenue * 12
    annual_tips = total_tips * 12
    
    print(f"\n📊 ANNUAL PROJECTIONS:")
    print(f"   💰 ${annual_revenue:.0f} revenue per year")
    print(f"   💸 ${annual_tips:.0f} tips per year")
    print(f"   👥 {unique_customers * 12} customers per year")
    
    # ROI on Keeper
    keeper_monthly_cost = 99
    keeper_annual_cost = keeper_monthly_cost * 12
    
    if len(insights) >= 2:  # If we found multiple actionable insights
        print(f"\n🏆 KEEPER ROI ANALYSIS:")
        print(f"   📱 Keeper cost: ${keeper_monthly_cost}/month (${keeper_annual_cost}/year)")
        print(f"   💡 Insights generated: {len(insights)} actionable items")
        print(f"   🎯 Actions recommended: {len(actions)} improvement opportunities")
        
        if utilization < 60:
            roi_percentage = (potential_revenue * 12 / keeper_annual_cost) * 100
            print(f"   📈 Potential ROI: {roi_percentage:.0f}% (${potential_revenue * 12:.0f}/${keeper_annual_cost})")
    
    return {
        'employee_name': 'Laine Duttlinger',
        'utilization': utilization,
        'revenue_per_hour': revenue_per_hour,
        'tip_percentage': tip_percentage,
        'retention_rate': retention_rate,
        'insights_generated': len(insights),
        'actions_recommended': len(actions),
        'total_revenue': total_revenue
    }

if __name__ == "__main__":
    result = sample_keeper_intelligence()
    
    print(f"\n" + "=" * 60)
    print("🎯 KEEPER INTELLIGENCE SAMPLE COMPLETE")
    
    if result:
        print(f"✅ Analysis complete for {result['employee_name']}")
        print(f"📊 Key metrics calculated:")
        print(f"   • {result['utilization']:.1f}% utilization")
        print(f"   • ${result['revenue_per_hour']:.0f}/hour productivity")
        print(f"   • {result['tip_percentage']:.1f}% tip rate")
        print(f"   • {result['retention_rate']:.1f}% retention")
        print(f"   • {result['insights_generated']} insights generated")
        print(f"   • {result['actions_recommended']} actions recommended")
        
        print(f"\n💎 THIS IS THE $99/MONTH VALUE:")
        print(f"   🧠 Complete employee intelligence analysis")
        print(f"   🎯 Actionable insights for business growth") 
        print(f"   💰 Revenue optimization opportunities")
        print(f"   📈 Performance improvement recommendations")
        
        print(f"\n🚀 NEXT: Scale to all employees and add customer intelligence")
    else:
        print(f"❌ SAMPLE ANALYSIS FAILED")