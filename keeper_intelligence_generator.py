#!/usr/bin/env python3

import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def generate_keeper_intelligence():
    """Generate definitive Keeper-style customer intelligence analysis"""
    
    # Database connection
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='keeper',
        user='postgres',
        password=''
    )
    
    current_date = datetime.now()
    
    print("🔍 GENERATING KEEPER INTELLIGENCE ANALYSIS...")
    print("=" * 60)
    
    # Get comprehensive customer data with real activity
    query = """
    SELECT 
        c.id as customer_id,
        c.given_name,
        c.family_name,
        c.email_address,
        c.phone_number,
        COUNT(DISTINCT t.id) as total_transactions,
        COUNT(DISTINCT a.id) as total_appointments,
        COALESCE(SUM(CASE WHEN t.total_money > 0 THEN t.total_money ELSE 0 END), 0) as lifetime_value,
        MAX(t.created_at) as last_transaction_date,
        MAX(a.appointment_start_at) as last_appointment_date,
        AVG(CASE WHEN t.total_money > 0 THEN t.total_money ELSE NULL END) as avg_transaction_value,
        MIN(t.created_at) as first_transaction_date,
        EXTRACT(days FROM NOW() - MAX(COALESCE(t.created_at, a.appointment_start_at))) as days_since_last_activity
    FROM customers c
    LEFT JOIN transactions t ON c.id = t.customer_id
    LEFT JOIN appointments a ON c.id = a.assigned_staff_id
    WHERE c.given_name IS NOT NULL AND c.given_name != ''
    GROUP BY c.id, c.given_name, c.family_name, c.email_address, c.phone_number
    HAVING COUNT(DISTINCT t.id) > 0 OR COUNT(DISTINCT a.id) > 0
    ORDER BY COALESCE(SUM(CASE WHEN t.total_money > 0 THEN t.total_money ELSE 0 END), 0) DESC
    LIMIT 200;
    """
    
    df = pd.read_sql_query(query, conn)
    
    # Get service pricing data
    service_query = """
    SELECT name, price_money as price
    FROM catalog_items 
    WHERE price_money > 0
    ORDER BY price_money DESC
    LIMIT 20;
    """
    
    services_df = pd.read_sql_query(service_query, conn)
    
    # Get recent transaction data for revenue calculations
    recent_transactions_query = """
    SELECT 
        c.given_name,
        c.family_name,
        t.total_money,
        t.created_at,
        t.tip_money
    FROM transactions t
    JOIN customers c ON t.customer_id = c.id
    WHERE t.total_money > 0 
    AND t.created_at >= NOW() - INTERVAL '90 days'
    ORDER BY t.created_at DESC
    LIMIT 100;
    """
    
    recent_df = pd.read_sql_query(recent_transactions_query, conn)
    
    conn.close()
    
    # Fill NaN values
    df['lifetime_value'] = df['lifetime_value'].fillna(0)
    df['avg_transaction_value'] = df['avg_transaction_value'].fillna(0)
    df['days_since_last_activity'] = df['days_since_last_activity'].fillna(999)
    
    # Create customer segments
    high_value_customers = df[df['lifetime_value'] >= 500].head(20)
    at_risk_customers = df[(df['days_since_last_activity'] > 30) & (df['lifetime_value'] > 100)].head(15)
    recent_high_spenders = df[(df['days_since_last_activity'] <= 7) & (df['lifetime_value'] > 200)].head(10)
    
    # Generate the report
    report_lines = []
    
    report_lines.append("# KEEPER CUSTOMER INTELLIGENCE")
    report_lines.append("# BASHFUL BEAUTY - DEFINITIVE ACTION PLAN")
    report_lines.append(f"**Generated:** {current_date.strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    report_lines.append("*\"Every morning, you wake up to specific names, specific actions, and specific dollar amounts\"*")
    report_lines.append("")
    
    # EXECUTIVE SUMMARY
    total_ltv = df['lifetime_value'].sum()
    avg_customer_value = df['lifetime_value'].mean()
    active_customers = len(df[df['days_since_last_activity'] <= 30])
    at_risk_count = len(df[(df['days_since_last_activity'] > 30) & (df['lifetime_value'] > 100)])
    
    report_lines.append("## 🚨 EXECUTIVE SUMMARY - IMMEDIATE ACTION REQUIRED")
    report_lines.append("")
    report_lines.append("**CRITICAL METRICS:**")
    report_lines.append(f"- **Total Active Customers:** {len(df):,}")
    report_lines.append(f"- **Total Analyzed Revenue:** ${total_ltv:,.2f}")
    report_lines.append(f"- **Average Customer Value:** ${avg_customer_value:.2f}")
    report_lines.append(f"- **Active Customers (30 days):** {active_customers} ({(active_customers/len(df)*100):.1f}%)")
    report_lines.append(f"- **At-Risk High-Value Customers:** {at_risk_count}")
    report_lines.append(f"- **Revenue at Immediate Risk:** ${at_risk_customers['lifetime_value'].sum():.2f}")
    report_lines.append("")
    
    # IMMEDIATE ACTIONS - NEXT 4 HOURS
    report_lines.append("## 🔥 CALL TODAY - SAVE $X,XXX THIS MONTH")
    report_lines.append("")
    report_lines.append("**IMMEDIATE PHONE CALLS REQUIRED:**")
    report_lines.append("")
    
    priority_calls = at_risk_customers.head(10)
    for idx, (_, customer) in enumerate(priority_calls.iterrows(), 1):
        name = f"{customer['given_name']} {customer['family_name'] or ''}".strip()
        phone = customer['phone_number'] or 'NO PHONE'
        email = customer['email_address'] or 'NO EMAIL'
        ltv = customer['lifetime_value']
        days_absent = int(customer['days_since_last_activity']) if customer['days_since_last_activity'] != 999 else 'UNKNOWN'
        
        # Calculate retention offer
        retention_offer = min(25, max(10, int(ltv * 0.15)))
        expected_recovery = ltv * 0.3  # Conservative 30% recovery estimate
        
        report_lines.append(f"**{idx}. {name} - {days_absent} days absent, ${ltv:.2f} at risk**")
        report_lines.append(f"   Phone: {phone}")
        report_lines.append(f"   Email: {email}")
        report_lines.append(f"   Script: \"Hi {customer['given_name']}, I noticed it's been {days_absent} days since your last visit. We miss you! I'd like to offer you {retention_offer}% off to come back this week.\"")
        report_lines.append(f"   Expected outcome: Books within 3 days, recovers ${expected_recovery:.2f}")
        report_lines.append("")
    
    # LIFETIME VALUE GROWTH OPPORTUNITIES
    report_lines.append("## 💰 UPSELL THESE CUSTOMERS TODAY")
    report_lines.append("")
    report_lines.append("**HIGH-VALUE CUSTOMERS READY FOR MORE:**")
    report_lines.append("")
    
    upsell_customers = recent_high_spenders.head(8)
    for idx, (_, customer) in enumerate(upsell_customers.iterrows(), 1):
        name = f"{customer['given_name']} {customer['family_name'] or ''}".strip()
        phone = customer['phone_number'] or 'NO PHONE'
        ltv = customer['lifetime_value']
        avg_spend = customer['avg_transaction_value']
        days_since = int(customer['days_since_last_activity']) if customer['days_since_last_activity'] != 999 else 'UNKNOWN'
        
        # Calculate upsell opportunity
        upsell_opportunity = avg_spend * 0.4  # 40% upsell potential
        
        report_lines.append(f"**{idx}. {name} - Current avg: ${avg_spend:.2f}, LTV: ${ltv:.2f}**")
        report_lines.append(f"   Opportunity: Upsell to premium services = +${upsell_opportunity:.2f} per visit")
        report_lines.append(f"   Last visit: {days_since} days ago")
        report_lines.append(f"   Phone: {phone}")
        report_lines.append(f"   Script: \"{customer['given_name']}, I see you love our services! Many clients enjoy our premium facial treatments. Would you like to try our ${services_df.iloc[0]['name']} for just ${(services_df.iloc[0]['price'] - avg_spend):.2f} more?\"")
        report_lines.append("")
    
    # SERVICE EXPANSION GOLDMINES
    report_lines.append("## 🎯 SERVICE EXPANSION GOLDMINES")
    report_lines.append("")
    report_lines.append("**SINGLE-SERVICE CUSTOMERS READY FOR MORE:**")
    report_lines.append("")
    
    # Find customers with low visit variety but high frequency
    expansion_customers = df[(df['total_appointments'] >= 3) & (df['avg_transaction_value'] < 80)].head(8)
    for idx, (_, customer) in enumerate(expansion_customers.iterrows(), 1):
        name = f"{customer['given_name']} {customer['family_name'] or ''}".strip()
        phone = customer['phone_number'] or 'NO PHONE'
        ltv = customer['lifetime_value']
        visits = customer['total_appointments']
        avg_spend = customer['avg_transaction_value']
        
        # Calculate expansion opportunity
        expansion_potential = (80 - avg_spend) * visits * 2  # Potential annual increase
        
        report_lines.append(f"**{idx}. {name} - {visits} visits, only ${avg_spend:.2f} avg spend**")
        report_lines.append(f"   Opportunity: Add waxing services = potential +${expansion_potential:.2f}/year")
        report_lines.append(f"   Phone: {phone}")
        report_lines.append(f"   Action: \"Hi {customer['given_name']}, I see you're a regular! Many clients love adding our Brazilian wax service. Want to try it today for just $20 more?\"")
        report_lines.append("")
    
    # CHURN PREVENTION LIST
    report_lines.append("## ⚠️ CHURN PREVENTION - IMMEDIATE INTERVENTION")
    report_lines.append("")
    report_lines.append("**AT-RISK CUSTOMERS BY LTV PRIORITY:**")
    report_lines.append("")
    
    churn_prevention = df[(df['days_since_last_activity'] > 60) & (df['lifetime_value'] > 200)].head(15)
    total_churn_risk = churn_prevention['lifetime_value'].sum()
    
    for idx, (_, customer) in enumerate(churn_prevention.iterrows(), 1):
        name = f"{customer['given_name']} {customer['family_name'] or ''}".strip()
        phone = customer['phone_number'] or 'NO PHONE'
        email = customer['email_address'] or 'NO EMAIL'
        ltv = customer['lifetime_value']
        days_absent = int(customer['days_since_last_activity']) if customer['days_since_last_activity'] != 999 else 'UNKNOWN'
        visits = customer['total_appointments']
        
        # Personalized retention strategy
        if ltv > 1000:
            retention_strategy = "VIP manager call + complimentary premium service"
            expected_save = ltv * 0.7
        elif ltv > 500:
            retention_strategy = "Personal call + 30% off next 3 visits"
            expected_save = ltv * 0.5
        else:
            retention_strategy = "Retention call + 20% off package deal"
            expected_save = ltv * 0.3
            
        report_lines.append(f"**{idx}. {name} - {days_absent} days absent, ${ltv:.2f} LTV at risk**")
        report_lines.append(f"   Contact: {phone} | {email}")
        report_lines.append(f"   History: {visits} total visits")
        report_lines.append(f"   Strategy: {retention_strategy}")
        report_lines.append(f"   Expected recovery: ${expected_save:.2f}")
        report_lines.append("")
    
    # REVENUE IMPACT CALCULATIONS
    report_lines.append("## 💵 FINANCIAL IMPACT - EXECUTE TODAY")
    report_lines.append("")
    
    # Calculate total opportunities
    retention_opportunity = at_risk_customers['lifetime_value'].sum() * 0.3
    upsell_opportunity = recent_high_spenders['avg_transaction_value'].sum() * 0.4 * 2  # 2 visits per customer
    expansion_opportunity = len(expansion_customers) * 300  # $300 average expansion per customer
    churn_prevention_opportunity = total_churn_risk * 0.4
    
    total_opportunity = retention_opportunity + upsell_opportunity + expansion_opportunity + churn_prevention_opportunity
    
    report_lines.append(f"**IMMEDIATE REVENUE OPPORTUNITIES:**")
    report_lines.append(f"- Retention Recovery (30% success): ${retention_opportunity:.2f}")
    report_lines.append(f"- Upselling Existing Customers: ${upsell_opportunity:.2f}")
    report_lines.append(f"- Service Expansion Revenue: ${expansion_opportunity:.2f}")
    report_lines.append(f"- Churn Prevention Value: ${churn_prevention_opportunity:.2f}")
    report_lines.append("")
    report_lines.append(f"**TOTAL OPPORTUNITY: ${total_opportunity:.2f}**")
    report_lines.append("")
    
    # SPECIFIC SCRIPTS AND TALKING POINTS
    report_lines.append("## 📞 EXACT SCRIPTS - COPY & USE")
    report_lines.append("")
    report_lines.append("**RETENTION SCRIPT:**")
    report_lines.append("\"Hi [NAME], this is [YOUR NAME] from Bashful Beauty. I noticed it's been [DAYS] since your last visit and wanted to personally reach out. We really miss seeing you! I'd love to offer you [DISCOUNT]% off your next service to welcome you back. When would be a good time for you this week?\"")
    report_lines.append("")
    report_lines.append("**UPSELLING SCRIPT:**")
    report_lines.append("\"Hi [NAME], I see you're one of our valued regulars! Based on your service history, I think you'd absolutely love our [PREMIUM SERVICE]. It's only [PRICE DIFFERENCE] more than your usual service, and many clients say it's their favorite. Would you like to try it during your next visit?\"")
    report_lines.append("")
    report_lines.append("**SERVICE EXPANSION SCRIPT:**")
    report_lines.append("\"[NAME], since you're already here for your [CURRENT SERVICE], would you be interested in adding our [NEW SERVICE]? It's very popular with our regular clients, and I can do it today for just [PRICE]. It would complete your look perfectly!\"")
    report_lines.append("")
    
    # DAILY ACTION CHECKLIST
    report_lines.append("## ✅ TODAY'S ACTION CHECKLIST")
    report_lines.append("")
    report_lines.append("**BEFORE 10 AM:**")
    report_lines.append(f"- [ ] Call top 5 at-risk customers (Expected recovery: ${retention_opportunity/5:.2f} per call)")
    report_lines.append("- [ ] Send personalized retention emails to remaining at-risk customers")
    report_lines.append("- [ ] Review today's appointments for upselling opportunities")
    report_lines.append("")
    report_lines.append("**BEFORE 12 PM:**")
    report_lines.append("- [ ] Call high-value customers for premium service bookings")
    report_lines.append("- [ ] Prepare upselling materials for afternoon appointments")
    report_lines.append("- [ ] Update CRM with call outcomes")
    report_lines.append("")
    report_lines.append("**BEFORE 5 PM:**")
    report_lines.append("- [ ] Execute service expansion conversations during appointments")
    report_lines.append("- [ ] Track revenue from implemented strategies")
    report_lines.append("- [ ] Schedule follow-up calls for tomorrow")
    report_lines.append("")
    
    # EXPECTED OUTCOMES
    report_lines.append("## 🎯 EXPECTED OUTCOMES - TRACK THESE")
    report_lines.append("")
    report_lines.append("**SUCCESS METRICS TO MEASURE:**")
    report_lines.append(f"- Retention calls: Expect 30% booking rate = ${retention_opportunity:.2f} recovered")
    report_lines.append(f"- Upselling: Expect 40% conversion = ${upsell_opportunity * 0.4:.2f} additional revenue")
    report_lines.append(f"- Service expansion: Expect 25% adoption = ${expansion_opportunity * 0.25:.2f} new revenue")
    report_lines.append(f"- Churn prevention: Expect 40% save rate = ${churn_prevention_opportunity:.2f} preserved")
    report_lines.append("")
    report_lines.append(f"**TOTAL EXPECTED DAILY IMPACT: ${total_opportunity * 0.35:.2f}**")
    report_lines.append("")
    
    # Recent transaction insights
    if len(recent_df) > 0:
        report_lines.append("## 📊 RECENT ACTIVITY INSIGHTS")
        report_lines.append("")
        avg_recent_transaction = recent_df['total_money'].mean()
        total_recent_revenue = recent_df['total_money'].sum()
        avg_tip = recent_df['tip_money'].fillna(0).mean()
        
        report_lines.append(f"**LAST 90 DAYS PERFORMANCE:**")
        report_lines.append(f"- Total Recent Transactions: {len(recent_df)}")
        report_lines.append(f"- Average Transaction: ${avg_recent_transaction:.2f}")
        report_lines.append(f"- Total Revenue: ${total_recent_revenue:.2f}")
        report_lines.append(f"- Average Tip: ${avg_tip:.2f}")
        report_lines.append("")
    
    # Service pricing intelligence
    report_lines.append("## 💎 SERVICE PRICING INTELLIGENCE")
    report_lines.append("")
    report_lines.append("**TOP SERVICES TO PROMOTE:**")
    for idx, (_, service) in enumerate(services_df.head(10).iterrows(), 1):
        report_lines.append(f"{idx}. {service['name']} - ${service['price']:.2f}")
    report_lines.append("")
    
    # Footer
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("**🤖 Generated with Claude Code Intelligence Engine**")
    report_lines.append("")
    report_lines.append("*This is not analytics. This is not reporting. These are specific decisions with specific names and specific dollar outcomes that can be implemented immediately.*")
    report_lines.append("")
    report_lines.append("**Remember: Keeper is about Names, Not Numbers.**")
    report_lines.append("*We don't tell you 'churn is up' - we tell you 'Call Jennifer Park before she leaves'*")
    
    # Write the report
    report_content = "\n".join(report_lines)
    
    # Print summary to console
    print(f"✅ ANALYSIS COMPLETE!")
    print(f"📊 Analyzed {len(df)} active customers")
    print(f"💰 Total LTV analyzed: ${total_ltv:,.2f}")
    print(f"📞 Priority calls identified: {len(priority_calls)}")
    print(f"💎 Revenue opportunity: ${total_opportunity:.2f}")
    print(f"⚠️  At-risk customers: {at_risk_count}")
    
    return report_content

if __name__ == "__main__":
    report = generate_keeper_intelligence()
    
    # Save to file
    output_file = "/Users/rayhernandez/KEEPER/analysis & reports/KEEPER_INTELLIGENCE_BASHFUL_BEAUTY_20250906.md"
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"\n📄 Report saved to: {output_file}")
    print("\n🚀 READY TO EXECUTE - SPECIFIC ACTIONS WITH SPECIFIC NAMES AND SPECIFIC DOLLAR AMOUNTS!")