#!/usr/bin/env python3
"""
Inspect the actual database schema to understand table structures
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def inspect_database():
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    account_id = "b491de6e-7d5b-4e0e-b1cd-625c6c4f7d81"
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    tables = ['customers', 'appointments', 'services', 'transactions', 'staff']
    
    for table_name in tables:
        print(f"\n🔍 INSPECTING {table_name.upper()} TABLE:")
        print("=" * 50)
        
        try:
            # Get first few records to see schema
            response = supabase.table(table_name).select('*').eq('account_id', account_id).limit(3).execute()
            
            if response.data:
                print(f"✅ Found {len(response.data)} records")
                print("SAMPLE RECORD:")
                first_record = response.data[0]
                for key, value in first_record.items():
                    print(f"  {key}: {value}")
                
                print("\nCOLUMN NAMES:")
                columns = list(first_record.keys())
                print(f"  {', '.join(columns)}")
            else:
                print("❌ No records found")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    inspect_database()