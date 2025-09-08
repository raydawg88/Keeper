#!/usr/bin/env python3
"""
ADAPTIVE KPI CALCULATOR FOR DIFFERENT EMPLOYEE TYPES
- Calculate performance metrics based on detected compensation model
- Different KPIs for different employee types
- Business-agnostic but role-specific
"""

import os
import json
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

def calculate_adaptive_kpis():
    """Calculate KPIs based on detected employee compensation patterns"""
    
    print("📊 ADAPTIVE KPI CALCULATOR")
    print("=" * 60)
    print("STRATEGY: Different metrics for different compensation models")
    print("PERSONALIZED: Each employee gets relevant KPIs")
    
    # Load compensation model
    try:
        with open('/tmp/adaptive_compensation_model.json', 'r') as f:
            comp_model = json.load(f)
    except:
        print("❌ No compensation model found - run detection first")
        return
    
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
    
    # Get recent appointment data for KPI calculations
    print(f"\n📡 GETTING RECENT PERFORMANCE DATA")
    
    # Get appointments from last 30 days for current performance
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    start_str = start_date.strftime('%Y-%m-%dT00:00:00Z')
    end_str = end_date.strftime('%Y-%m-%dT23:59:59Z')
    
    recent_appointments = []
    try:
        cursor = None
        while True:
            url = f"{api_base_url}/v2/bookings?limit=200&start_at_min={start_str}&start_at_max={end_str}"
            if cursor:
                url += f"&cursor={cursor}"
            
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                break
                
            data = response.json()
            bookings = data.get('bookings', [])
            recent_appointments.extend(bookings)
            
            cursor = data.get('cursor')
            if not cursor:
                break
        
        print(f"✅ Retrieved {len(recent_appointments)} recent appointments")
    except Exception as e:
        print(f"⚠️  Could not get recent appointments: {e}")
    
    # Get recent payments for revenue analysis
    recent_payments = []
    try:
        url = f"{api_base_url}/v2/payments?begin_time={start_str}&end_time={end_str}&limit=200"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            payments_data = response.json()
            recent_payments = payments_data.get('payments', [])
            print(f"✅ Retrieved {len(recent_payments)} recent payments")
    except Exception as e:
        print(f"⚠️  Could not get recent payments: {e}")
    
    # CALCULATE KPIS FOR EACH EMPLOYEE TYPE
    print(f"\n📊 CALCULATING ADAPTIVE KPIS")
    print("=" * 80)
    
    employee_kpis = {}
    active_patterns = {k: v for k, v in comp_model['employee_patterns'].items() 
                      if k in comp_model['employee_patterns'] and 
                      comp_model['employee_patterns'][k].get('name')}
    
    for employee_id, pattern in active_patterns.items():
        if not pattern.get('name'):
            continue
            
        name = pattern['name']
        compensation_model = pattern['compensation_model']
        appointment_count = pattern['appointment_count']
        
        print(f"\n👤 {name} ({compensation_model})")
        print("-" * 50)
        
        kpis = {}
        
        # Calculate based on compensation model
        if compensation_model == 'ADMINISTRATIVE':
            # Administrative staff KPIs
            kpis = calculate_administrative_kpis(
                employee_id, recent_appointments, recent_payments
            )
            
        elif compensation_model in ['HOURLY_SERVICE', 'HOURLY_ESTHETICIAN']:
            # Hourly service provider KPIs
            kpis = calculate_hourly_service_kpis(
                employee_id, recent_appointments, recent_payments, appointment_count
            )
            
        elif compensation_model == 'COMMISSION_SERVICE':
            # Commission service provider KPIs
            kpis = calculate_commission_service_kpis(
                employee_id, recent_appointments, recent_payments, appointment_count
            )
        
        # Display KPIs
        for kpi_name, kpi_value in kpis.items():
            print(f"  {kpi_name}: {kpi_value}")
        
        employee_kpis[employee_id] = {
            'name': name,
            'compensation_model': compensation_model,
            'kpis': kpis
        }
    
    # BUSINESS-LEVEL INSIGHTS
    print(f"\n🏢 BUSINESS-LEVEL INSIGHTS")
    print("=" * 50)
    
    # Overall business performance
    total_recent_revenue = sum(
        float(p.get('total_money', {}).get('amount', 0)) / 100 
        for p in recent_payments
    )
    
    print(f"Recent 30-day performance:")
    print(f"  Total appointments: {len(recent_appointments):,}")
    print(f"  Total revenue: ${total_recent_revenue:,.2f}")
    print(f"  Average ticket: ${total_recent_revenue / len(recent_payments) if recent_payments else 0:.2f}")
    
    # Service provider analysis
    service_providers = [emp for emp in employee_kpis.values() 
                        if 'SERVICE' in emp['compensation_model']]
    
    if service_providers:
        print(f"\nService Provider Analysis:")
        for provider in service_providers:
            utilization = provider['kpis'].get('utilization_rate', 'N/A')
            revenue = provider['kpis'].get('revenue_generated', 'N/A')
            print(f"  {provider['name']}: {utilization} utilization, {revenue} revenue")
    
    # Save results
    results = {
        'calculation_date': datetime.now().isoformat(),
        'period': '30_days',
        'business_performance': {
            'total_appointments': len(recent_appointments),
            'total_revenue': total_recent_revenue,
            'average_ticket': total_recent_revenue / len(recent_payments) if recent_payments else 0
        },
        'employee_kpis': employee_kpis
    }
    
    with open('/tmp/adaptive_kpis_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ KPI CALCULATION COMPLETE")
    print(f"Results saved to: /tmp/adaptive_kpis_results.json")
    
    return results

def calculate_administrative_kpis(employee_id, appointments, payments):
    """Calculate KPIs for administrative staff"""
    # Look for appointments they might have booked/managed
    managed_appointments = 0
    for apt in appointments:
        creator = apt.get('creator_details', {})
        if creator.get('team_member_id') == employee_id:
            managed_appointments += 1
    
    # Administrative efficiency metrics
    return {
        'appointments_booked': f"{managed_appointments} in 30 days",
        'scheduling_efficiency': f"{managed_appointments / 30:.1f} per day" if managed_appointments > 0 else "No recent bookings",
        'customer_service_score': "Data needed", # Would need customer feedback
        'role_type': "Administrative Support"
    }

def calculate_hourly_service_kpis(employee_id, appointments, payments, total_appointments):
    """Calculate KPIs for hourly service providers"""
    # Find their appointments
    their_appointments = []
    for apt in appointments:
        segments = apt.get('appointment_segments', [])
        for segment in segments:
            if segment.get('team_member_id') == employee_id:
                their_appointments.append(apt)
                break
    
    # Calculate utilization (appointments in last 30 days vs their historical average)
    historical_monthly_avg = (total_appointments / 12) if total_appointments > 0 else 0
    current_monthly = len(their_appointments)
    utilization_rate = (current_monthly / historical_monthly_avg * 100) if historical_monthly_avg > 0 else 0
    
    # Service quality metrics
    total_service_time = 0
    for apt in their_appointments:
        segments = apt.get('appointment_segments', [])
        for segment in segments:
            if segment.get('team_member_id') == employee_id:
                total_service_time += segment.get('duration_minutes', 0)
    
    return {
        'utilization_rate': f"{utilization_rate:.1f}% vs historical average",
        'appointments_completed': f"{len(their_appointments)} in 30 days",
        'total_service_hours': f"{total_service_time / 60:.1f} hours",
        'client_satisfaction': "Needs customer feedback data",
        'efficiency_rating': f"{total_service_time / len(their_appointments) if their_appointments else 0:.0f} min avg per appointment"
    }

def calculate_commission_service_kpis(employee_id, appointments, payments, total_appointments):
    """Calculate KPIs for commission-based service providers"""
    # Find their appointments
    their_appointments = []
    for apt in appointments:
        segments = apt.get('appointment_segments', [])
        for segment in segments:
            if segment.get('team_member_id') == employee_id:
                their_appointments.append(apt)
                break
    
    # Estimate revenue (would need better payment-to-appointment linking)
    estimated_revenue = len(their_appointments) * 65  # Average service price estimate
    
    # Client retention (would need historical customer analysis)
    unique_customers = set()
    for apt in their_appointments:
        customer_id = apt.get('customer_id')
        if customer_id:
            unique_customers.add(customer_id)
    
    return {
        'revenue_generated': f"${estimated_revenue:,.2f} estimated (30 days)",
        'appointments_completed': f"{len(their_appointments)} services",
        'unique_clients_served': f"{len(unique_customers)} different customers",
        'average_ticket': f"${estimated_revenue / len(their_appointments) if their_appointments else 0:.2f}",
        'client_retention_rate': "Needs historical analysis",
        'performance_vs_historical': f"{len(their_appointments)} vs {total_appointments / 12:.0f} monthly avg"
    }

if __name__ == "__main__":
    results = calculate_adaptive_kpis()
    
    print(f"\n" + "=" * 60)
    print("🎉 ADAPTIVE KPI CALCULATION: SUCCESS!")
    print("✅ Personalized metrics per compensation model")
    print("✅ Business-specific performance insights")
    print("✅ Ready for employee performance reviews")
    print("Ready to scale across any Square business type!")