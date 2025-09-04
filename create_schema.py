#!/usr/bin/env python3
"""
Create Keeper database schema in Supabase
"""
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

def create_schema_via_sql():
    """Create schema using Supabase REST API for SQL execution"""
    
    url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    print("🏗️  Creating Keeper database schema...")
    print("-" * 50)
    
    # Schema SQL (simplified for initial setup)
    schema_sql = '''
    -- Enable required extensions
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    -- Core Business Data
    CREATE TABLE IF NOT EXISTS accounts (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        square_merchant_id TEXT UNIQUE,
        business_name TEXT,
        business_category TEXT DEFAULT 'spa',
        created_at TIMESTAMP DEFAULT NOW()
    );
    
    -- Processed Customer Data
    CREATE TABLE IF NOT EXISTS customers (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        account_id UUID REFERENCES accounts(id),
        square_id TEXT,
        name TEXT,
        email TEXT,
        phone TEXT,
        first_seen DATE,
        last_seen DATE,
        lifetime_value DECIMAL,
        visit_frequency_days INTEGER,
        risk_score DECIMAL,
        metadata JSONB,
        created_at TIMESTAMP DEFAULT NOW()
    );
    
    -- Transactions
    CREATE TABLE IF NOT EXISTS transactions (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        account_id UUID REFERENCES accounts(id),
        customer_id UUID REFERENCES customers(id),
        square_payment_id TEXT,
        amount DECIMAL,
        modifiers JSONB,
        employee_id TEXT,
        timestamp TIMESTAMP
    );
    
    -- Insights & Tasks
    CREATE TABLE IF NOT EXISTS insights (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        account_id UUID REFERENCES accounts(id),
        type TEXT,
        pattern JSONB,
        confidence DECIMAL,
        dollar_impact DECIMAL,
        created_at TIMESTAMP DEFAULT NOW()
    );
    
    CREATE TABLE IF NOT EXISTS tasks (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        account_id UUID REFERENCES accounts(id),
        insight_id UUID REFERENCES insights(id),
        customer_id UUID,
        priority INTEGER,
        title TEXT,
        description TEXT,
        action_script TEXT,
        dollar_value DECIMAL,
        status TEXT DEFAULT 'pending',
        expires_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT NOW()
    );
    
    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_customers_account_id ON customers(account_id);
    CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id);
    CREATE INDEX IF NOT EXISTS idx_tasks_account_id ON tasks(account_id);
    CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
    '''
    
    # Try using httpx to make direct SQL API call
    headers = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json'
    }
    
    # Execute SQL using Supabase SQL API
    sql_url = f"{url}/sql"
    
    try:
        with httpx.Client() as client:
            response = client.post(
                sql_url,
                headers=headers,
                json={"query": schema_sql}
            )
            
            if response.status_code == 200:
                print("✅ Database schema created successfully!")
                return True
            else:
                print(f"❌ Schema creation failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Schema creation error: {str(e)}")
        return False

def test_tables_exist():
    """Test that our tables were created properly"""
    from supabase import create_client
    
    url = os.getenv("SUPABASE_URL")  
    service_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    supabase = create_client(url, service_key)
    
    tables_to_test = ['accounts', 'customers', 'transactions', 'insights', 'tasks']
    
    print("\n🔍 Verifying table creation...")
    print("-" * 50)
    
    for table in tables_to_test:
        try:
            result = supabase.table(table).select('*').limit(1).execute()
            print(f"✅ {table} - table accessible")
        except Exception as e:
            print(f"❌ {table} - error: {str(e)}")
    
    print("-" * 50)
    print("✅ Schema verification complete!")

if __name__ == "__main__":
    if create_schema_via_sql():
        test_tables_exist()
    else:
        print("❌ Schema creation failed")