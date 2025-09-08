#!/usr/bin/env python3
"""
Load REAL Bashful Beauty data from Supabase
Show actual employee names and customer names
"""

import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from incremental_loader import IncrementalDataLoader

def load_real_bashful_data():
    """Load real data from Bashful Beauty Supabase database"""
    print("🔍 LOADING REAL BASHFUL BEAUTY DATA")
    print("=" * 50)
    
    # Use actual Bashful Beauty account ID
    account_id = "b491de6e-7d5b-4e0e-b1cd-625c6c4f7d81"
    
    # Initialize loader with real credentials
    loader = IncrementalDataLoader(account_id)
    
    print(f"🔑 Supabase URL: {os.getenv('SUPABASE_URL')}")
    print(f"🔑 API Key: {'***' + os.getenv('SUPABASE_SERVICE_KEY', '')[-4:] if os.getenv('SUPABASE_SERVICE_KEY') else 'NOT SET'}")
    
    # Load real data
    print("\n📊 Loading real customer, appointment, and transaction data...")
    customers_df, appointments_df, transactions_df, stats = loader.load_incremental_data(full_refresh=True)
    
    print(f"\n✅ REAL DATA LOADED:")
    print(f"   📈 Customers: {len(customers_df)}")
    print(f"   📅 Appointments: {len(appointments_df)}")
    print(f"   💰 Transactions: {len(transactions_df)}")
    print(f"   ⏱️  Load Time: {stats.load_time_seconds:.2f}s")
    
    if not customers_df.empty:
        print(f"\n👥 REAL CUSTOMER SAMPLE (10 recognizable names):")
        customer_names = customers_df['given_name'].fillna('') + ' ' + customers_df['family_name'].fillna('')
        customer_names = customer_names.str.strip()
        unique_names = customer_names[customer_names != ''].unique()
        
        for i, name in enumerate(unique_names[:10], 1):
            print(f"   {i}. {name}")
    
    if not appointments_df.empty:
        print(f"\n👨‍💼 REAL EMPLOYEE DATA:")
        # Check for team member info in appointments
        if 'team_member_id' in appointments_df.columns:
            team_members = appointments_df['team_member_id'].dropna().unique()
            print(f"   Team Member IDs: {list(team_members[:5])}")
        
        # Check for any staff name fields
        staff_columns = [col for col in appointments_df.columns if 'staff' in col.lower() or 'employee' in col.lower() or 'team' in col.lower()]
        print(f"   Staff-related columns: {staff_columns}")
        
        # Show appointment columns to understand data structure
        print(f"   Appointment columns: {list(appointments_df.columns)}")
        
        # Show a sample appointment
        if len(appointments_df) > 0:
            print(f"\n📅 SAMPLE APPOINTMENT:")
            sample = appointments_df.iloc[0]
            for key, value in sample.items():
                if pd.notna(value):
                    print(f"     {key}: {value}")
    
    if not transactions_df.empty and len(transactions_df) > 0:
        print(f"\n💰 REAL TRANSACTION SAMPLE:")
        sample_tx = transactions_df.iloc[0]
        for key, value in sample_tx.items():
            if pd.notna(value):
                print(f"     {key}: {value}")
    
    # Check if any data is actually loaded
    if customers_df.empty and appointments_df.empty and transactions_df.empty:
        print("\n❌ NO REAL DATA LOADED - Possible issues:")
        print("   1. API key permissions")
        print("   2. Account ID mismatch") 
        print("   3. Database connection issues")
        print("   4. Data not in expected tables")
        return None, None, None
    
    return customers_df, appointments_df, transactions_df

if __name__ == "__main__":
    customers, appointments, transactions = load_real_bashful_data()