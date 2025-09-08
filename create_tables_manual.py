#!/usr/bin/env python3
"""
MANUAL DATABASE TABLE CREATION
Creates payments, orders, team_members, and catalog_items tables
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def create_database_tables():
    """Create all required tables manually"""
    
    print("🔧 MANUAL DATABASE TABLE CREATION")
    print("=" * 60)
    
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_KEY')
    )
    
    # CREATE PAYMENTS TABLE
    try:
        # First check if table exists
        result = supabase.table('payments').select('*').limit(1).execute()
        print("✅ PAYMENTS table already exists")
    except Exception:
        print("🔧 Creating PAYMENTS table...")
        # Table doesn't exist, let's create it by inserting a test record
        # then deleting it to establish the schema
        
        test_payment = {
            'id': 'test-payment-id',
            'account_id': 'test-account',
            'payment_id': 'test-payment',
            'amount_cents': 1000,
            'tip_cents': 200,
            'currency': 'USD',
            'status': 'COMPLETED',
            'source_type': 'CARD',
            'created_at': '2023-01-01T00:00:00Z',
            'square_data': {}
        }
        
        try:
            supabase.table('payments').insert(test_payment).execute()
            supabase.table('payments').delete().eq('id', 'test-payment-id').execute()
            print("✅ PAYMENTS table created successfully")
        except Exception as e:
            print(f"❌ Failed to create PAYMENTS table: {e}")
    
    # CREATE ORDERS TABLE
    try:
        result = supabase.table('orders').select('*').limit(1).execute()
        print("✅ ORDERS table already exists")
    except Exception:
        print("🔧 Creating ORDERS table...")
        
        test_order = {
            'id': 'test-order-id',
            'account_id': 'test-account',
            'order_id': 'test-order',
            'state': 'COMPLETED',
            'total_money_cents': 1500,
            'created_at': '2023-01-01T00:00:00Z',
            'square_data': {}
        }
        
        try:
            supabase.table('orders').insert(test_order).execute()
            supabase.table('orders').delete().eq('id', 'test-order-id').execute()
            print("✅ ORDERS table created successfully")
        except Exception as e:
            print(f"❌ Failed to create ORDERS table: {e}")
    
    # CREATE TEAM_MEMBERS TABLE
    try:
        result = supabase.table('team_members').select('*').limit(1).execute()
        print("✅ TEAM_MEMBERS table already exists")
    except Exception:
        print("🔧 Creating TEAM_MEMBERS table...")
        
        test_member = {
            'id': 'test-member-id',
            'account_id': 'test-account',
            'team_member_id': 'test-member',
            'status': 'ACTIVE',
            'given_name': 'Test',
            'family_name': 'Member',
            'created_at': '2023-01-01T00:00:00Z',
            'square_data': {}
        }
        
        try:
            supabase.table('team_members').insert(test_member).execute()
            supabase.table('team_members').delete().eq('id', 'test-member-id').execute()
            print("✅ TEAM_MEMBERS table created successfully")
        except Exception as e:
            print(f"❌ Failed to create TEAM_MEMBERS table: {e}")
    
    # CREATE CATALOG_ITEMS TABLE
    try:
        result = supabase.table('catalog_items').select('*').limit(1).execute()
        print("✅ CATALOG_ITEMS table already exists")
    except Exception:
        print("🔧 Creating CATALOG_ITEMS table...")
        
        test_item = {
            'id': 'test-item-id',
            'account_id': 'test-account',
            'catalog_object_id': 'test-item',
            'object_type': 'ITEM',
            'item_name': 'Test Item',
            'created_at': '2023-01-01T00:00:00Z',
            'square_data': {}
        }
        
        try:
            supabase.table('catalog_items').insert(test_item).execute()
            supabase.table('catalog_items').delete().eq('id', 'test-item-id').execute()
            print("✅ CATALOG_ITEMS table created successfully")
        except Exception as e:
            print(f"❌ Failed to create CATALOG_ITEMS table: {e}")
    
    # VERIFY ALL TABLES EXIST
    print(f"\n📊 VERIFYING ALL TABLES EXIST:")
    print("-" * 40)
    
    tables = ['payments', 'orders', 'team_members', 'catalog_items']
    existing_tables = []
    
    for table in tables:
        try:
            result = supabase.table(table).select('*').limit(1).execute()
            print(f"✅ {table}: EXISTS")
            existing_tables.append(table)
        except Exception as e:
            print(f"❌ {table}: MISSING - {e}")
    
    print(f"\n🎉 DATABASE SETUP COMPLETE!")
    print(f"Created/verified {len(existing_tables)}/{len(tables)} tables")
    
    return len(existing_tables) == len(tables)

if __name__ == "__main__":
    success = create_database_tables()
    if success:
        print("✅ Ready to continue with API tests!")
    else:
        print("❌ Some tables failed to create")