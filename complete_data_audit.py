#!/usr/bin/env python3
"""
COMPLETE BASHFUL BEAUTY DATA AUDIT
Analyze EVERY piece of available data to build confidence
Show exactly what we have vs what's missing
"""

from dotenv import load_dotenv
load_dotenv()
import pandas as pd
import json
from datetime import datetime
from supabase import create_client
import os

def complete_data_audit():
    """Comprehensive audit of ALL available Bashful Beauty data"""
    print("🔍 COMPLETE BASHFUL BEAUTY DATA AUDIT")
    print("=" * 60)
    print("📊 Analyzing EVERY table and data point available")
    
    # Initialize Supabase client directly
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_KEY')
    )
    
    account_id = "b491de6e-7d5b-4e0e-b1cd-625c6c4f7d81"
    
    # 1. DISCOVER ALL AVAILABLE TABLES
    print(f"\n1️⃣ DISCOVERING ALL AVAILABLE TABLES...")
    
    tables_to_check = [
        'customers', 'appointments', 'transactions', 
        'team_members', 'employees', 'staff',
        'services', 'locations', 'bookings',
        'payments', 'orders', 'items'
    ]
    
    available_tables = {}
    
    for table in tables_to_check:
        try:
            response = supabase.table(table).select('*').eq('account_id', account_id).limit(1).execute()
            if response.data:
                available_tables[table] = len(response.data)
                print(f"   ✅ {table}: Data available")
            else:
                available_tables[table] = 0
                print(f"   ⚠️  {table}: Empty")
        except Exception as e:
            print(f"   ❌ {table}: Not accessible ({str(e)[:50]}...)")
    
    # 2. COMPLETE DATA INVENTORY
    print(f"\n2️⃣ COMPLETE DATA INVENTORY...")
    
    total_data = {}
    
    for table, has_data in available_tables.items():
        if has_data:
            try:
                # Get full table data
                response = supabase.table(table).select('*').eq('account_id', account_id).execute()
                df = pd.DataFrame(response.data)
                
                total_data[table] = {
                    'count': len(df),
                    'columns': list(df.columns),
                    'data': df
                }
                
                print(f"   📊 {table.upper()}: {len(df)} records, {len(df.columns)} columns")
                
                # Show column details
                for col in df.columns:
                    non_null = df[col].notna().sum()
                    unique_vals = df[col].nunique() if not df.empty else 0
                    print(f"     - {col}: {non_null}/{len(df)} filled, {unique_vals} unique")
                
            except Exception as e:
                print(f"   ❌ Error loading {table}: {e}")
    
    # 3. EMPLOYEE DATA DEEP DIVE
    print(f"\n3️⃣ EMPLOYEE DATA DEEP DIVE...")
    
    employee_sources = []
    
    # Check if team_members table exists
    try:
        team_response = supabase.table('team_members').select('*').execute()
        if team_response.data:
            employee_sources.append(('team_members', len(team_response.data)))
            print(f"   ✅ team_members table: {len(team_response.data)} records")
            
            # Show sample team member
            if team_response.data:
                sample = team_response.data[0]
                print(f"   Sample team member: {sample}")
        else:
            print(f"   ⚠️  team_members table: Empty")
    except:
        print(f"   ❌ team_members table: Not accessible")
    
    # Check Square booking data for team members
    if 'appointments' in total_data:
        appointments_df = total_data['appointments']['data']
        
        # Check for team member data in square booking IDs
        booking_ids = appointments_df['square_booking_id'].dropna().unique()
        print(f"   📅 Square booking IDs: {len(booking_ids)} unique")
        
        # Try to get team member data from Square API via bookings
        print(f"   🔍 Need to query Square API for team member assignments")
    
    # 4. REVENUE AND BUSINESS METRICS
    print(f"\n4️⃣ BUSINESS INTELLIGENCE METRICS...")
    
    business_metrics = {}
    
    if 'customers' in total_data:
        customers_df = total_data['customers']['data']
        
        # Customer metrics
        total_customers = len(customers_df)
        customers_with_email = customers_df['email'].notna().sum()
        customers_with_phone = customers_df['phone'].notna().sum()
        customers_with_ltv = customers_df['lifetime_value'].notna().sum()
        
        business_metrics['customers'] = {
            'total': total_customers,
            'with_email': customers_with_email,
            'with_phone': customers_with_phone,
            'with_ltv': customers_with_ltv
        }
        
        print(f"   👥 CUSTOMERS: {total_customers} total")
        print(f"     - With email: {customers_with_email} ({customers_with_email/total_customers*100:.1f}%)")
        print(f"     - With phone: {customers_with_phone} ({customers_with_phone/total_customers*100:.1f}%)")
        print(f"     - With LTV: {customers_with_ltv} ({customers_with_ltv/total_customers*100:.1f}%)")
        
        # LTV analysis
        if customers_with_ltv > 0:
            ltv_values = pd.to_numeric(customers_df['lifetime_value'], errors='coerce').dropna()
            avg_ltv = ltv_values.mean()
            total_ltv = ltv_values.sum()
            print(f"     - Average LTV: ${avg_ltv:.2f}")
            print(f"     - Total LTV: ${total_ltv:,.2f}")
    
    if 'transactions' in total_data:
        transactions_df = total_data['transactions']['data']
        
        # Transaction metrics
        total_transactions = len(transactions_df)
        total_revenue = transactions_df['amount_cents'].sum() / 100 if 'amount_cents' in transactions_df.columns else 0
        total_tips = transactions_df['tip_cents'].sum() / 100 if 'tip_cents' in transactions_df.columns else 0
        
        business_metrics['transactions'] = {
            'total': total_transactions,
            'revenue': total_revenue,
            'tips': total_tips
        }
        
        print(f"   💰 TRANSACTIONS: {total_transactions} total")
        print(f"     - Total Revenue: ${total_revenue:,.2f}")
        print(f"     - Total Tips: ${total_tips:,.2f}")
        print(f"     - Tip Rate: {(total_tips/total_revenue*100) if total_revenue > 0 else 0:.1f}%")
        print(f"     - Average Transaction: ${total_revenue/total_transactions if total_transactions > 0 else 0:.2f}")
    
    if 'appointments' in total_data:
        appointments_df = total_data['appointments']['data']
        
        # Appointment metrics
        total_appointments = len(appointments_df)
        status_counts = appointments_df['status'].value_counts()
        service_counts = appointments_df['service_variation_id'].nunique()
        
        business_metrics['appointments'] = {
            'total': total_appointments,
            'by_status': status_counts.to_dict(),
            'unique_services': service_counts
        }
        
        print(f"   📅 APPOINTMENTS: {total_appointments} total")
        print(f"     - Unique Services: {service_counts}")
        for status, count in status_counts.items():
            print(f"     - {status}: {count} ({count/total_appointments*100:.1f}%)")
    
    # 5. DATA QUALITY ASSESSMENT
    print(f"\n5️⃣ DATA QUALITY ASSESSMENT...")
    
    quality_score = 0
    max_score = 0
    issues = []
    
    # Check customer data quality
    if 'customers' in total_data:
        max_score += 30
        customers_df = total_data['customers']['data']
        
        # Name completeness
        names_complete = customers_df['name'].notna().sum() / len(customers_df)
        quality_score += names_complete * 10
        
        # Contact info completeness
        contact_complete = (customers_df['email'].notna() | customers_df['phone'].notna()).sum() / len(customers_df)
        quality_score += contact_complete * 10
        
        # LTV data completeness
        ltv_complete = customers_df['lifetime_value'].notna().sum() / len(customers_df)
        quality_score += ltv_complete * 10
        
        if names_complete < 0.9:
            issues.append(f"Customer names: {names_complete:.1%} complete")
        if contact_complete < 0.8:
            issues.append(f"Customer contact info: {contact_complete:.1%} complete")
        if ltv_complete < 0.5:
            issues.append(f"Customer LTV data: {ltv_complete:.1%} complete")
    
    # Check transaction data quality
    if 'transactions' in total_data:
        max_score += 20
        transactions_df = total_data['transactions']['data']
        
        # Amount data completeness
        amounts_complete = transactions_df['amount_cents'].notna().sum() / len(transactions_df)
        quality_score += amounts_complete * 10
        
        # Employee data completeness
        employee_complete = transactions_df['employee_id'].notna().sum() / len(transactions_df)
        quality_score += employee_complete * 10
        
        if amounts_complete < 0.95:
            issues.append(f"Transaction amounts: {amounts_complete:.1%} complete")
        if employee_complete < 0.1:
            issues.append(f"Employee data in transactions: {employee_complete:.1%} complete")
    
    final_quality_score = (quality_score / max_score * 100) if max_score > 0 else 0
    
    print(f"   📊 OVERALL DATA QUALITY: {final_quality_score:.1f}%")
    if issues:
        print(f"   ⚠️  ISSUES FOUND:")
        for issue in issues:
            print(f"     - {issue}")
    else:
        print(f"   ✅ No major data quality issues detected")
    
    # 6. ANALYSIS READINESS
    print(f"\n6️⃣ ANALYSIS READINESS ASSESSMENT...")
    
    can_analyze = {
        'customer_segmentation': 'customers' in total_data and len(total_data['customers']['data']) > 100,
        'revenue_analysis': 'transactions' in total_data and total_data['transactions']['data']['amount_cents'].notna().sum() > 0,
        'churn_prediction': 'customers' in total_data and 'appointments' in total_data,
        'employee_performance': False  # No employee data available
    }
    
    print(f"   🎯 ANALYSIS CAPABILITIES:")
    for analysis_type, can_do in can_analyze.items():
        status = "✅ READY" if can_do else "❌ NOT READY"
        print(f"     - {analysis_type}: {status}")
    
    # 7. IMMEDIATE ACTIONABLE INSIGHTS
    print(f"\n7️⃣ IMMEDIATE ACTIONABLE INSIGHTS...")
    
    if 'customers' in total_data and 'transactions' in total_data:
        customers_df = total_data['customers']['data']
        transactions_df = total_data['transactions']['data']
        
        # High-value customers at risk
        if customers_df['lifetime_value'].notna().sum() > 0:
            ltv_numeric = pd.to_numeric(customers_df['lifetime_value'], errors='coerce')
            high_ltv = customers_df[ltv_numeric > ltv_numeric.quantile(0.8)]['name'].dropna()
            print(f"   💰 HIGH-VALUE CUSTOMERS: {len(high_ltv)} identified")
            for i, name in enumerate(high_ltv.head(5), 1):
                print(f"     {i}. {name}")
        
        # Revenue trends
        if 'square_created_at' in transactions_df.columns:
            recent_transactions = transactions_df[
                pd.to_datetime(transactions_df['square_created_at'], errors='coerce') 
                > datetime.now() - pd.Timedelta(days=30)
            ]
            recent_revenue = recent_transactions['amount_cents'].sum() / 100
            print(f"   📈 RECENT PERFORMANCE (30 days): ${recent_revenue:,.2f}")
    
    # FINAL SUMMARY
    print(f"\n" + "="*60)
    print(f"📋 COMPLETE DATA AUDIT SUMMARY")
    print(f"="*60)
    print(f"✅ Tables Available: {len([t for t in available_tables.values() if t > 0])}")
    print(f"📊 Total Records: {sum(total_data[t]['count'] for t in total_data)}")
    print(f"🎯 Data Quality: {final_quality_score:.1f}%")
    print(f"⚡ Analysis Ready: {sum(can_analyze.values())}/{len(can_analyze)} capabilities")
    
    if final_quality_score >= 70:
        print(f"🟢 CONFIDENCE LEVEL: HIGH - Ready for comprehensive analysis")
    elif final_quality_score >= 50:
        print(f"🟡 CONFIDENCE LEVEL: MEDIUM - Can run analysis with limitations")
    else:
        print(f"🔴 CONFIDENCE LEVEL: LOW - Significant data gaps exist")
    
    return total_data, business_metrics, final_quality_score

if __name__ == "__main__":
    complete_data_audit()