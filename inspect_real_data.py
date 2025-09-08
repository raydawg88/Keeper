#!/usr/bin/env python3
"""
Inspect the real Bashful Beauty data structure
Show actual column names and data types
"""

from dotenv import load_dotenv
load_dotenv()

from incremental_loader import IncrementalDataLoader

def inspect_real_data():
    """Inspect real data columns and structure"""
    print("🔍 INSPECTING REAL BASHFUL BEAUTY DATA STRUCTURE")
    print("=" * 60)
    
    account_id = "b491de6e-7d5b-4e0e-b1cd-625c6c4f7d81"
    loader = IncrementalDataLoader(account_id)
    
    # Load real data
    customers_df, appointments_df, transactions_df, stats = loader.load_incremental_data(full_refresh=True)
    
    print(f"✅ LOADED {len(customers_df)} customers, {len(appointments_df)} appointments, {len(transactions_df)} transactions")
    
    if not customers_df.empty:
        print(f"\n📊 REAL CUSTOMER DATA STRUCTURE:")
        print(f"   Columns ({len(customers_df.columns)}): {list(customers_df.columns)}")
        print(f"   Data Types:")
        for col in customers_df.columns:
            print(f"     {col}: {customers_df[col].dtype}")
        
        print(f"\n👤 SAMPLE REAL CUSTOMER RECORD:")
        sample = customers_df.iloc[0]
        for key, value in sample.items():
            if pd.notna(value):
                print(f"     {key}: {repr(value)}")
    
    if not appointments_df.empty:
        print(f"\n📅 REAL APPOINTMENTS DATA STRUCTURE:")
        print(f"   Columns ({len(appointments_df.columns)}): {list(appointments_df.columns)}")
        
        # Look for staff/employee related columns
        staff_cols = [col for col in appointments_df.columns if any(word in col.lower() for word in ['staff', 'employee', 'team', 'member', 'worker', 'service_provider'])]
        print(f"   Staff-related columns: {staff_cols}")
        
        print(f"\n📅 SAMPLE REAL APPOINTMENT RECORD:")
        sample = appointments_df.iloc[0]
        for key, value in sample.items():
            if pd.notna(value):
                print(f"     {key}: {repr(value)}")
    
    if not transactions_df.empty:
        print(f"\n💰 REAL TRANSACTIONS DATA STRUCTURE:")
        print(f"   Columns ({len(transactions_df.columns)}): {list(transactions_df.columns)}")
        
        print(f"\n💰 SAMPLE REAL TRANSACTION RECORD:")
        sample = transactions_df.iloc[0]
        for key, value in sample.items():
            if pd.notna(value):
                print(f"     {key}: {repr(value)}")
    
    # Find customer names in the actual data
    if not customers_df.empty:
        print(f"\n👥 FINDING REAL CUSTOMER NAMES:")
        name_columns = [col for col in customers_df.columns if 'name' in col.lower()]
        print(f"   Name-related columns: {name_columns}")
        
        # Try different name combinations
        for col in name_columns[:5]:  # Check first 5 name columns
            unique_values = customers_df[col].dropna().unique()
            print(f"   {col} sample values: {list(unique_values[:5])}")

if __name__ == "__main__":
    import pandas as pd
    inspect_real_data()