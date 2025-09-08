#!/usr/bin/env python3
"""
Compare real Square export data vs database data
Verify if database data is accurate or fake
"""

import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

def analyze_real_square_data():
    """Analyze the real Square export files"""
    print("📊 ANALYZING REAL SQUARE EXPORT DATA")
    print("=" * 50)
    
    export_path = "/Users/rayhernandez/KEEPER/manual_export/"
    
    # 1. REAL CUSTOMERS
    print("👥 REAL CUSTOMERS FROM SQUARE:")
    customers_file = f"{export_path}customers2.csv"
    customers_real = pd.read_csv(customers_file)
    print(f"   Total customers: {len(customers_real)}")
    print(f"   Columns: {list(customers_real.columns)}")
    
    if 'Customer Name' in customers_real.columns:
        real_names = customers_real['Customer Name'].dropna().unique()
        print(f"   Sample real customer names:")
        for i, name in enumerate(real_names[:10], 1):
            print(f"     {i}. {name}")
    
    # 2. REAL APPOINTMENTS  
    print(f"\n📅 REAL APPOINTMENTS FROM SQUARE:")
    appointments_file = f"{export_path}appointments-20250907T0126.csv"
    appointments_real = pd.read_csv(appointments_file)
    print(f"   Total appointments: {len(appointments_real)}")
    print(f"   Columns: {list(appointments_real.columns)}")
    
    # Look for staff/employee data in appointments
    staff_columns = [col for col in appointments_real.columns if 'staff' in col.lower() or 'employee' in col.lower() or 'team' in col.lower() or 'assigned' in col.lower()]
    print(f"   Staff-related columns: {staff_columns}")
    
    if staff_columns:
        for col in staff_columns:
            unique_staff = appointments_real[col].dropna().unique()
            print(f"   Real staff from {col}: {list(unique_staff)}")
    
    # 3. REAL TRANSACTIONS
    print(f"\n💰 REAL TRANSACTIONS FROM SQUARE:")
    
    # Load both transaction files
    trans_2024 = pd.read_csv(f"{export_path}transactions-2024-01-01-2025-01-01 (1).csv")
    trans_2025 = pd.read_csv(f"{export_path}transactions-2025-01-01-2026-01-01 (1).csv")
    
    total_transactions = len(trans_2024) + len(trans_2025)
    print(f"   Total transactions: {total_transactions}")
    print(f"   2024 transactions: {len(trans_2024)}")
    print(f"   2025 transactions: {len(trans_2025)}")
    
    print(f"   Transaction columns: {list(trans_2024.columns)}")
    
    # Calculate real revenue
    if 'Net Sales' in trans_2024.columns:
        revenue_2024 = pd.to_numeric(trans_2024['Net Sales'], errors='coerce').sum()
        revenue_2025 = pd.to_numeric(trans_2025['Net Sales'], errors='coerce').sum()
        total_revenue = revenue_2024 + revenue_2025
        print(f"   Real total revenue: ${total_revenue:,.2f}")
        print(f"   2024 revenue: ${revenue_2024:,.2f}")
        print(f"   2025 revenue: ${revenue_2025:,.2f}")
    
    # 4. REAL ITEMS/SERVICES
    print(f"\n🛍️ REAL ITEMS/SERVICES FROM SQUARE:")
    items_catalog = pd.read_csv(f"{export_path}items_catalog.csv")
    print(f"   Total items in catalog: {len(items_catalog)}")
    print(f"   Columns: {list(items_catalog.columns)}")
    
    if 'Item Name' in items_catalog.columns:
        real_services = items_catalog['Item Name'].dropna().unique()
        print(f"   Real services offered:")
        for i, service in enumerate(real_services[:10], 1):
            print(f"     {i}. {service}")
    
    return {
        'customers': customers_real,
        'appointments': appointments_real,
        'transactions_2024': trans_2024,
        'transactions_2025': trans_2025,
        'items': items_catalog
    }

def compare_database_vs_real():
    """Compare database data to real Square export"""
    print(f"\n" + "="*60)
    print("🔍 DATABASE vs REAL SQUARE DATA COMPARISON")
    print("="*60)
    
    # Get real data
    real_data = analyze_real_square_data()
    
    # Get database data
    from incremental_loader import IncrementalDataLoader
    loader = IncrementalDataLoader('b491de6e-7d5b-4e0e-b1cd-625c6c4f7d81')
    customers_db, appointments_db, transactions_db, stats = loader.load_incremental_data(full_refresh=True)
    
    print(f"\n📊 COMPARISON RESULTS:")
    
    # 1. CUSTOMER COUNT COMPARISON
    real_customer_count = len(real_data['customers'])
    db_customer_count = len(customers_db)
    
    print(f"\n👥 CUSTOMERS:")
    print(f"   Real Square export: {real_customer_count}")
    print(f"   Database claims: {db_customer_count}")
    print(f"   Match: {'✅ YES' if real_customer_count == db_customer_count else '❌ NO'}")
    
    # 2. APPOINTMENT COUNT COMPARISON
    real_appointment_count = len(real_data['appointments'])
    db_appointment_count = len(appointments_db)
    
    print(f"\n📅 APPOINTMENTS:")
    print(f"   Real Square export: {real_appointment_count}")
    print(f"   Database claims: {db_appointment_count}")
    print(f"   Match: {'✅ YES' if real_appointment_count == db_appointment_count else '❌ NO'}")
    
    # 3. TRANSACTION COUNT COMPARISON
    real_transaction_count = len(real_data['transactions_2024']) + len(real_data['transactions_2025'])
    db_transaction_count = len(transactions_db)
    
    print(f"\n💰 TRANSACTIONS:")
    print(f"   Real Square export: {real_transaction_count}")
    print(f"   Database claims: {db_transaction_count}")
    print(f"   Match: {'✅ YES' if real_transaction_count == db_transaction_count else '❌ NO'}")
    
    # 4. CUSTOMER NAME COMPARISON
    print(f"\n🏷️ CUSTOMER NAMES COMPARISON:")
    if 'Customer Name' in real_data['customers'].columns and not customers_db.empty:
        real_names = set(real_data['customers']['Customer Name'].dropna().str.strip().str.lower())
        db_names = set(customers_db['name'].dropna().str.strip().str.lower())
        
        matching_names = real_names.intersection(db_names)
        print(f"   Real unique names: {len(real_names)}")
        print(f"   Database unique names: {len(db_names)}")
        print(f"   Matching names: {len(matching_names)}")
        print(f"   Match percentage: {len(matching_names)/max(len(real_names), 1)*100:.1f}%")
        
        # Show some mismatches
        only_in_real = list(real_names - db_names)[:5]
        only_in_db = list(db_names - real_names)[:5]
        
        if only_in_real:
            print(f"   Names only in REAL data: {only_in_real}")
        if only_in_db:
            print(f"   Names only in DATABASE: {only_in_db}")
    
    # 5. REVENUE COMPARISON
    print(f"\n💰 REVENUE COMPARISON:")
    
    # Real revenue
    real_revenue = 0
    if 'Net Sales' in real_data['transactions_2024'].columns:
        real_revenue_2024 = pd.to_numeric(real_data['transactions_2024']['Net Sales'], errors='coerce').sum()
        real_revenue_2025 = pd.to_numeric(real_data['transactions_2025']['Net Sales'], errors='coerce').sum()
        real_revenue = real_revenue_2024 + real_revenue_2025
    
    # Database revenue
    db_revenue = 0
    if not transactions_db.empty and 'amount_cents' in transactions_db.columns:
        db_revenue = transactions_db['amount_cents'].sum() / 100
    
    print(f"   Real Square revenue: ${real_revenue:,.2f}")
    print(f"   Database revenue: ${db_revenue:,.2f}")
    print(f"   Difference: ${abs(real_revenue - db_revenue):,.2f}")
    print(f"   Match: {'✅ YES' if abs(real_revenue - db_revenue) < 100 else '❌ NO'}")
    
    # 6. EMPLOYEE DATA COMPARISON
    print(f"\n👨‍💼 EMPLOYEE DATA:")
    
    # Look for staff in real appointments
    staff_columns = [col for col in real_data['appointments'].columns if 'staff' in col.lower() or 'employee' in col.lower() or 'team' in col.lower() or 'assigned' in col.lower()]
    
    real_staff = []
    for col in staff_columns:
        staff_in_col = real_data['appointments'][col].dropna().unique()
        real_staff.extend(staff_in_col)
    
    unique_real_staff = list(set(real_staff))
    
    # Database staff (we know this is 0)
    db_staff_count = 0
    if not transactions_db.empty and 'employee_id' in transactions_db.columns:
        db_staff_count = len(transactions_db['employee_id'].dropna().unique())
    
    print(f"   Real staff in Square: {len(unique_real_staff)}")
    if unique_real_staff:
        print(f"   Real staff names: {unique_real_staff}")
    print(f"   Database staff count: {db_staff_count}")
    print(f"   Match: {'✅ YES' if len(unique_real_staff) == db_staff_count else '❌ NO'}")
    
    # FINAL VERDICT
    print(f"\n" + "="*60)
    print("🏁 FINAL VERDICT")
    print("="*60)
    
    issues = []
    
    if real_customer_count != db_customer_count:
        issues.append(f"Customer count mismatch ({real_customer_count} vs {db_customer_count})")
    
    if real_appointment_count != db_appointment_count:
        issues.append(f"Appointment count mismatch ({real_appointment_count} vs {db_appointment_count})")
    
    if real_transaction_count != db_transaction_count:
        issues.append(f"Transaction count mismatch ({real_transaction_count} vs {db_transaction_count})")
    
    if abs(real_revenue - db_revenue) > 100:
        issues.append(f"Revenue mismatch (${real_revenue:,.2f} vs ${db_revenue:,.2f})")
    
    if len(unique_real_staff) != db_staff_count:
        issues.append(f"Staff count mismatch ({len(unique_real_staff)} vs {db_staff_count})")
    
    if issues:
        print("🔴 DATABASE DATA IS NOT ACCURATE")
        print("Issues found:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nRecommendation: Use the real Square export data for analysis")
    else:
        print("🟢 DATABASE DATA MATCHES REAL SQUARE EXPORT")
        print("Database data is accurate and can be trusted for analysis")

if __name__ == "__main__":
    compare_database_vs_real()