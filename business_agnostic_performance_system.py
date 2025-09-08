#!/usr/bin/env python3
"""
BUSINESS-AGNOSTIC EMPLOYEE PERFORMANCE SYSTEM
- Works for ANY Square business: Spa, Restaurant, Retail, Gym, etc.
- Adapts to different compensation models and business types
- Provides actionable insights specific to each business context
"""

import os
import json
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

def create_business_agnostic_performance_system():
    """Create performance system that adapts to any Square business"""
    
    print("🏢 BUSINESS-AGNOSTIC PERFORMANCE SYSTEM")
    print("=" * 70)
    print("UNIVERSAL: Works for Spa, Restaurant, Retail, Gym, any Square business")
    print("ADAPTIVE: Detects business type and employee roles from data")
    print("ACTIONABLE: Provides specific recommendations for each context")
    
    # Load existing analysis
    try:
        with open('/tmp/adaptive_compensation_model.json', 'r') as f:
            comp_model = json.load(f)
        
        with open('/tmp/adaptive_kpis_results.json', 'r') as f:
            kpi_results = json.load(f)
    except:
        print("❌ Missing prerequisite data - run detection and KPI calculation first")
        return
    
    # STEP 1: BUSINESS TYPE ANALYSIS
    print(f"\n🎯 STEP 1: BUSINESS TYPE ANALYSIS")
    print("=" * 50)
    
    business_analysis = comp_model['business_analysis']
    business_type = business_analysis['type']
    
    # Enhanced business detection based on patterns
    business_insights = analyze_business_type(business_analysis, kpi_results)
    
    print(f"Business Type: {business_insights['type']}")
    print(f"Industry: {business_insights['industry']}")
    print(f"Service Model: {business_insights['service_model']}")
    print(f"Key Success Factors: {', '.join(business_insights['success_factors'])}")
    
    # STEP 2: EMPLOYEE ROLE CLASSIFICATION
    print(f"\n👥 STEP 2: EMPLOYEE ROLE CLASSIFICATION")
    print("=" * 50)
    
    role_classification = classify_employee_roles(comp_model, kpi_results, business_insights)
    
    print(f"{'EMPLOYEE':<20} {'ROLE':<20} {'COMPENSATION':<15} {'PERFORMANCE'}")
    print("-" * 75)
    
    for employee_id, classification in role_classification.items():
        name = classification['name'][:20]
        role = classification['role'][:20]
        comp = classification['compensation_model'][:15]
        perf = classification['performance_summary'][:20]
        print(f"{name:<20} {role:<20} {comp:<15} {perf}")
    
    # STEP 3: PERFORMANCE INSIGHTS & RECOMMENDATIONS
    print(f"\n📈 STEP 3: PERFORMANCE INSIGHTS & RECOMMENDATIONS")
    print("=" * 50)
    
    insights = generate_performance_insights(role_classification, business_insights)
    
    for category, insight_list in insights.items():
        print(f"\n{category.upper()}:")
        for insight in insight_list:
            print(f"  • {insight}")
    
    # STEP 4: BUSINESS-SPECIFIC RECOMMENDATIONS
    print(f"\n🎯 STEP 4: BUSINESS-SPECIFIC RECOMMENDATIONS")
    print("=" * 50)
    
    recommendations = generate_business_recommendations(
        business_insights, role_classification, kpi_results
    )
    
    for rec_type, rec_list in recommendations.items():
        print(f"\n{rec_type.replace('_', ' ').title()}:")
        for i, rec in enumerate(rec_list, 1):
            print(f"  {i}. {rec}")
    
    # STEP 5: SCALABILITY FRAMEWORK
    print(f"\n🚀 STEP 5: SCALABILITY FRAMEWORK")
    print("=" * 50)
    
    framework = create_scalability_framework(business_insights)
    
    print("Framework for scaling to other Square businesses:")
    for component, description in framework.items():
        print(f"  {component}: {description}")
    
    # STEP 6: SAVE COMPREHENSIVE RESULTS
    results = {
        'system_info': {
            'created_at': datetime.now().isoformat(),
            'version': '1.0',
            'business_agnostic': True
        },
        'business_analysis': business_insights,
        'employee_classification': role_classification,
        'performance_insights': insights,
        'business_recommendations': recommendations,
        'scalability_framework': framework,
        'adaptation_rules': {
            'spa_salon': 'Focus on service quality, client retention, esthetician performance',
            'restaurant': 'Focus on table turnover, tip optimization, kitchen efficiency',
            'retail': 'Focus on sales conversion, inventory turnover, customer service',
            'fitness': 'Focus on member retention, trainer utilization, class capacity',
            'professional_services': 'Focus on billable hours, client satisfaction, project delivery'
        }
    }
    
    with open('/tmp/business_agnostic_performance_system.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ BUSINESS-AGNOSTIC SYSTEM COMPLETE")
    print(f"Saved to: /tmp/business_agnostic_performance_system.json")
    
    return results

def analyze_business_type(business_analysis, kpi_results):
    """Analyze business type based on patterns"""
    avg_appointments = business_analysis['avg_appointments_per_provider']
    service_providers = business_analysis['service_providers']
    admin_staff = business_analysis['admin_staff']
    
    # Revenue per appointment analysis
    total_revenue = kpi_results['business_performance']['total_revenue']
    total_appointments = kpi_results['business_performance']['total_appointments']
    avg_ticket = total_revenue / total_appointments if total_appointments > 0 else 0
    
    # Business type detection logic
    if avg_ticket > 50 and avg_appointments > 2000:
        business_type = "HIGH_VALUE_PERSONAL_SERVICE"
        industry = "Spa/Salon/Wellness"
        service_model = "Appointment-based personal services"
        success_factors = ["Client Retention", "Service Quality", "Esthetician Performance"]
        
    elif avg_ticket < 25 and service_providers / admin_staff > 3:
        business_type = "HIGH_VOLUME_LOW_TICKET"
        industry = "Restaurant/Cafe/Food Service"
        service_model = "High-volume transactions with tips"
        success_factors = ["Table Turnover", "Tip Optimization", "Customer Satisfaction"]
        
    elif avg_ticket > 100 and service_providers < 5:
        business_type = "PROFESSIONAL_SERVICES"
        industry = "Consulting/Professional"
        service_model = "High-value consultations"
        success_factors = ["Billable Hours", "Client Satisfaction", "Expertise"]
        
    elif admin_staff > service_providers:
        business_type = "RETAIL_FOCUSED"
        industry = "Retail/Sales"
        service_model = "Product sales with service support"
        success_factors = ["Sales Conversion", "Inventory Management", "Customer Service"]
        
    else:
        business_type = "MIXED_SERVICE_MODEL"
        industry = "Multi-faceted Business"
        service_model = "Combined products and services"
        success_factors = ["Revenue Diversification", "Staff Efficiency", "Customer Retention"]
    
    return {
        'type': business_type,
        'industry': industry,
        'service_model': service_model,
        'success_factors': success_factors,
        'avg_ticket': avg_ticket,
        'business_metrics': {
            'revenue_per_appointment': avg_ticket,
            'service_to_admin_ratio': service_providers / admin_staff if admin_staff > 0 else float('inf'),
            'appointments_per_provider': avg_appointments
        }
    }

def classify_employee_roles(comp_model, kpi_results, business_insights):
    """Classify employee roles based on business context"""
    classification = {}
    
    for employee_id, kpi_data in kpi_results['employee_kpis'].items():
        name = kpi_data['name']
        compensation_model = kpi_data['compensation_model']
        kpis = kpi_data['kpis']
        
        # Role classification based on business context
        if business_insights['industry'] == "Spa/Salon/Wellness":
            if compensation_model == 'ADMINISTRATIVE':
                if 'appointments_booked' in kpis and int(kpis['appointments_booked'].split()[0]) > 50:
                    role = "Front Desk Manager"
                    performance = "High Booking Volume"
                else:
                    role = "Support Staff"
                    performance = "Administrative"
            elif compensation_model in ['COMMISSION_SERVICE', 'HOURLY_ESTHETICIAN']:
                role = "Service Provider"
                appointments = int(kpis.get('appointments_completed', '0').split()[0])
                if appointments > 100:
                    performance = "High Performer"
                elif appointments > 50:
                    performance = "Good Performer"
                else:
                    performance = "Needs Development"
            else:
                role = "Specialist"
                performance = "Variable"
                
        elif business_insights['industry'] == "Restaurant/Cafe/Food Service":
            if compensation_model == 'ADMINISTRATIVE':
                role = "Host/Manager"
                performance = "Operational Support"
            else:
                role = "Server/Bartender"
                performance = "Service Provider"
                
        elif business_insights['industry'] == "Retail/Sales":
            if compensation_model == 'ADMINISTRATIVE':
                role = "Cashier/Manager"
                performance = "Transaction Processing"
            else:
                role = "Sales Associate"
                performance = "Sales Focus"
                
        else:
            # Generic classification
            if compensation_model == 'ADMINISTRATIVE':
                role = "Administrative"
                performance = "Support Function"
            else:
                role = "Service Provider"
                performance = "Revenue Generator"
        
        classification[employee_id] = {
            'name': name,
            'role': role,
            'compensation_model': compensation_model,
            'performance_summary': performance,
            'kpis': kpis
        }
    
    return classification

def generate_performance_insights(role_classification, business_insights):
    """Generate performance insights based on business context"""
    insights = defaultdict(list)
    
    # Service provider analysis
    service_providers = [emp for emp in role_classification.values() 
                        if 'Service Provider' in emp['role'] or 'Esthetician' in emp['role']]
    
    if service_providers:
        high_performers = [emp for emp in service_providers if 'High Performer' in emp['performance_summary']]
        
        insights['top_performers'].append(f"Top service providers: {len(high_performers)} out of {len(service_providers)}")
        
        for performer in high_performers:
            appointments = performer['kpis'].get('appointments_completed', 'N/A')
            revenue = performer['kpis'].get('revenue_generated', 'N/A')
            insights['top_performers'].append(f"{performer['name']}: {appointments}, {revenue}")
    
    # Administrative efficiency
    admin_staff = [emp for emp in role_classification.values() if emp['role'] in ['Front Desk Manager', 'Support Staff', 'Administrative']]
    
    for admin in admin_staff:
        bookings = admin['kpis'].get('appointments_booked', '0 in 30 days')
        if 'bookings' not in bookings.lower() and int(bookings.split()[0]) > 100:
            insights['operational_efficiency'].append(f"{admin['name']} is booking {bookings} - excellent front desk performance")
        elif int(bookings.split()[0]) == 0:
            insights['areas_for_improvement'].append(f"{admin['name']} shows no booking activity - role clarification needed")
    
    # Business-specific insights
    if business_insights['industry'] == "Spa/Salon/Wellness":
        insights['industry_specific'].append("Focus on client retention and service quality")
        insights['industry_specific'].append("Monitor esthetician utilization rates and customer satisfaction")
        
    elif business_insights['industry'] == "Restaurant/Cafe/Food Service":
        insights['industry_specific'].append("Track table turnover and tip percentages")
        insights['industry_specific'].append("Monitor kitchen efficiency and order accuracy")
        
    return dict(insights)

def generate_business_recommendations(business_insights, role_classification, kpi_results):
    """Generate business-specific recommendations"""
    recommendations = defaultdict(list)
    
    # Performance optimization
    underperformers = [emp for emp in role_classification.values() 
                      if 'Needs Development' in emp['performance_summary']]
    
    if underperformers:
        recommendations['performance_optimization'].append(
            f"Provide additional training for {len(underperformers)} underperforming staff members"
        )
        for emp in underperformers:
            recommendations['performance_optimization'].append(
                f"Focus on {emp['name']}: specific skill development needed"
            )
    
    # Revenue optimization
    total_revenue = kpi_results['business_performance']['total_revenue']
    if total_revenue < 10000:  # Monthly revenue threshold
        recommendations['revenue_growth'].append("Revenue below optimal threshold - focus on:")
        recommendations['revenue_growth'].append("• Increase average ticket size through upselling")
        recommendations['revenue_growth'].append("• Improve appointment booking efficiency")
        recommendations['revenue_growth'].append("• Implement retention strategies for high-value clients")
    
    # Operational efficiency
    service_providers = len([emp for emp in role_classification.values() if 'Service Provider' in emp['role']])
    admin_staff = len([emp for emp in role_classification.values() if 'Administrative' in emp['role']])
    
    if admin_staff > service_providers:
        recommendations['operational_efficiency'].append("High admin-to-service ratio detected")
        recommendations['operational_efficiency'].append("Consider cross-training admin staff for service roles")
    
    # Business-specific recommendations
    if business_insights['industry'] == "Spa/Salon/Wellness":
        recommendations['industry_specific'].append("Implement client retention program")
        recommendations['industry_specific'].append("Track service quality metrics and customer feedback")
        recommendations['industry_specific'].append("Optimize esthetician schedules for maximum utilization")
        
    return dict(recommendations)

def create_scalability_framework(business_insights):
    """Create framework for scaling to other Square businesses"""
    return {
        'detection_rules': 'Analyze appointment patterns, revenue per transaction, staff roles',
        'adaptation_logic': 'Business type determines relevant KPIs and success metrics',
        'role_classification': 'Data patterns reveal compensation models, not job titles',
        'kpi_selection': 'Choose metrics relevant to specific business model and industry',
        'recommendation_engine': 'Generate actionable advice based on business context',
        'universal_applicability': 'Same system works for any Square-powered business'
    }

if __name__ == "__main__":
    system = create_business_agnostic_performance_system()
    
    print(f"\n" + "=" * 70)
    print("🎉 BUSINESS-AGNOSTIC PERFORMANCE SYSTEM: COMPLETE!")
    print("✅ Adapts to ANY Square business type")
    print("✅ Detects compensation models from data patterns")
    print("✅ Provides business-specific recommendations")
    print("✅ Scales across industries: Spa, Restaurant, Retail, Fitness, etc.")
    print("✅ Ready for Keeper's universal business intelligence engine!")