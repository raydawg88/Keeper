#!/usr/bin/env python3
"""
Check what tables exist in the database
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_tables():
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    account_id = "b491de6e-7d5b-4e0e-b1cd-625c6c4f7d81"
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Common table names to try
    possible_tables = [
        'customers', 'appointments', 'services', 'transactions', 'staff',
        'orders', 'payments', 'bookings', 'team_members', 'catalog_items',
        'service_variations', 'locations', 'catalog_objects'
    ]
    
    existing_tables = []
    
    for table_name in possible_tables:
        try:
            response = supabase.table(table_name).select('*').eq('account_id', account_id).limit(1).execute()
            existing_tables.append(table_name)
            print(f"✅ {table_name}: {len(response.data)} records found")
        except Exception as e:
            if "Could not find the table" in str(e):
                print(f"❌ {table_name}: Table does not exist")
            else:
                print(f"⚠️  {table_name}: Error - {e}")
    
    print(f"\n📊 EXISTING TABLES: {existing_tables}")
    
    # Get detailed info for existing tables
    for table_name in existing_tables:
        print(f"\n🔍 {table_name.upper()} DETAILS:")
        try:
            response = supabase.table(table_name).select('*').eq('account_id', account_id).execute()
            print(f"  Total records: {len(response.data)}")
            if response.data:
                print(f"  Columns: {list(response.data[0].keys())}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    check_tables()