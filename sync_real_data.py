#!/usr/bin/env python3
"""
STEP 4: Sync ALL real Bashful Beauty data to database
Remove artificial limits and store actual Square data
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

class RealDataSync:
    def __init__(self):
        # Load the access token we just got
        with open('/tmp/bashful_beauty_token.json', 'r') as f:
            token_data = json.load(f)
        
        self.access_token = token_data['access_token']
        self.account_id = "b491de6e-7d5b-4e0e-b1cd-625c6c4f7d81"  # Bashful Beauty account ID
        
        # Initialize Square API
        self.api_base_url = 'https://connect.squareup.com'
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Square-Version': '2025-08-20',
            'Content-Type': 'application/json'
        }
        
        # Initialize Supabase
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_SERVICE_KEY')
        )
        
        print(f"🔄 REAL DATA SYNC INITIALIZED")
        print(f"   Account: {self.account_id}")
        print(f"   Token: {self.access_token[:20]}...")
        
    def get_all_customers(self):
        """Get ALL customers from Square API (no limits)"""
        print(f"\n👥 SYNCING ALL CUSTOMERS...")
        
        all_customers = []
        cursor = None
        page = 0
        
        while True:
            page += 1
            
            # Build URL with cursor if available
            url = f"{self.api_base_url}/v2/customers?limit=100"
            if cursor:
                url += f"&cursor={cursor}"
            
            print(f"   📄 Page {page}: Requesting 100 customers...")
            
            try:
                response = requests.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    customers = data.get('customers', [])
                    cursor = data.get('cursor')
                    
                    all_customers.extend(customers)
                    print(f"   ✅ Got {len(customers)} customers (total: {len(all_customers)})")
                    
                    # If no more pages, break
                    if not cursor:
                        break
                        
                elif response.status_code == 429:
                    print(f"   ⏸️  Rate limited, waiting 60 seconds...")
                    import time
                    time.sleep(60)
                    continue
                    
                else:
                    print(f"   ❌ API Error: {response.status_code}")
                    print(f"   Response: {response.text}")
                    break
                    
            except Exception as e:
                print(f"   ❌ Request Error: {e}")
                break
        
        print(f"✅ CUSTOMER SYNC COMPLETE: {len(all_customers)} total customers")
        return all_customers
    
    def sync_customers_to_database(self, customers):
        """Sync customers to Supabase database"""
        print(f"\n💾 SYNCING {len(customers)} CUSTOMERS TO DATABASE...")
        
        # Clear existing fake data first
        print(f"   🗑️  Clearing existing fake customer data...")
        try:
            delete_result = self.supabase.table('customers').delete().eq('account_id', self.account_id).execute()
            print(f"   ✅ Cleared existing data")
        except Exception as e:
            print(f"   ⚠️  Clear failed: {e}")
        
        # Insert real customers in batches
        batch_size = 50
        inserted = 0
        
        for i in range(0, len(customers), batch_size):
            batch = customers[i:i + batch_size]
            
            # Transform Square customers to our schema
            customer_records = []
            for customer in batch:
                customer_record = {
                    'id': customer.get('id'),
                    'account_id': self.account_id,
                    'given_name': customer.get('given_name'),
                    'family_name': customer.get('family_name'),
                    'nickname': customer.get('nickname'),
                    'company_name': customer.get('company_name'),
                    'email_address': customer.get('email_address'),
                    'phone_number': customer.get('phone_number'),
                    'birthday': customer.get('birthday'),
                    'note': customer.get('note'),
                    'reference_id': customer.get('reference_id'),
                    'creation_source': customer.get('creation_source'),
                    'version': customer.get('version', 0),
                    'created_at': customer.get('created_at'),
                    'updated_at': customer.get('updated_at'),
                    'synced_at': datetime.utcnow().isoformat()
                }
                customer_records.append(customer_record)
            
            try:
                insert_result = self.supabase.table('customers').insert(customer_records).execute()
                inserted += len(customer_records)
                print(f"   ✅ Batch {i//batch_size + 1}: Inserted {len(customer_records)} customers (total: {inserted})")
                
            except Exception as e:
                print(f"   ❌ Batch {i//batch_size + 1} failed: {e}")
        
        print(f"✅ DATABASE SYNC COMPLETE: {inserted} customers inserted")
        return inserted
    
    def verify_database_sync(self):
        """Verify the database now has real data"""
        print(f"\n🔍 VERIFYING DATABASE SYNC...")
        
        try:
            # Count total customers
            count_result = self.supabase.table('customers')\
                .select('*', count='exact')\
                .eq('account_id', self.account_id)\
                .execute()
            
            total_count = count_result.count
            print(f"   📊 Database now has {total_count} customers")
            
            # Get sample customers
            sample_result = self.supabase.table('customers')\
                .select('*')\
                .eq('account_id', self.account_id)\
                .limit(5)\
                .execute()
            
            if sample_result.data:
                print(f"   📋 Sample customers in database:")
                for i, customer in enumerate(sample_result.data, 1):
                    name = f"{customer.get('given_name', '')} {customer.get('family_name', '')}".strip()
                    print(f"      {i}. {name}")
                    print(f"         ID: {customer.get('id')}")
                    print(f"         Email: {customer.get('email_address', 'No email')}")
            
            return total_count
            
        except Exception as e:
            print(f"   ❌ Verification failed: {e}")
            return 0

def main():
    print("🚀 STEP 4: SYNC ALL REAL BASHFUL BEAUTY DATA")
    print("🎯 Goal: Replace fake 1,000 records with ALL real Square data")
    print("=" * 80)
    
    sync = RealDataSync()
    
    # Step 1: Get all customers from Square
    customers = sync.get_all_customers()
    
    if not customers:
        print("❌ No customers retrieved from Square API")
        return
    
    # Step 2: Sync to database
    inserted = sync.sync_customers_to_database(customers)
    
    if inserted == 0:
        print("❌ No customers synced to database")
        return
    
    # Step 3: Verify sync
    db_count = sync.verify_database_sync()
    
    if db_count > 0:
        print(f"\n🎉 SUCCESS! REAL DATA SYNC COMPLETE!")
        print(f"✅ Square API: {len(customers)} customers retrieved")
        print(f"✅ Database: {db_count} customers stored")
        print(f"✅ Fake data: REPLACED with real data")
        print(f"🚀 Database now has REAL Bashful Beauty customers!")
    else:
        print(f"\n❌ SYNC VERIFICATION FAILED")

if __name__ == "__main__":
    main()