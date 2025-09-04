#!/usr/bin/env python3
"""
Simple Keeper database setup using Supabase client
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def setup_initial_schema():
    """Set up basic schema to test Supabase integration"""
    
    url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    print("🏗️  Setting up Keeper database...")
    print(f"Project: keeper-prod")
    print("-" * 50)
    
    supabase = create_client(url, service_key)
    
    # Test 1: Create a simple accounts table to verify permissions
    try:
        # Try to insert a test record (this will create table via RLS if configured)
        result = supabase.table('accounts').insert({
            'business_name': 'Test Business',
            'business_category': 'spa'
        }).execute()
        
        print("✅ Accounts table: Created and accessible")
        
        # Clean up test record
        supabase.table('accounts').delete().eq('business_name', 'Test Business').execute()
        
    except Exception as e:
        error_msg = str(e).lower()
        if 'does not exist' in error_msg:
            print("ℹ️  Tables need to be created via Supabase dashboard SQL editor")
            print("   Go to: https://supabase.com/dashboard/project/jlawmbqoykwgrjutrfsp/sql")
            return False
        else:
            print(f"❌ Database error: {str(e)}")
            return False
    
    print("-" * 50)
    print("✅ Basic database access confirmed!")
    return True

def show_sql_for_manual_setup():
    """Show the SQL that needs to be run manually in Supabase dashboard"""
    
    print("\n📋 SQL to run in Supabase dashboard:")
    print("=" * 60)
    print("Go to: https://supabase.com/dashboard/project/jlawmbqoykwgrjutrfsp/sql")
    print("Copy and paste this SQL:")
    print()
    
    sql = '''-- Keeper Database Schema
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Core Business Data
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    square_merchant_id TEXT UNIQUE,
    business_name TEXT,
    business_category TEXT DEFAULT 'spa',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Customer Data
CREATE TABLE customers (
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
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID REFERENCES accounts(id),
    customer_id UUID REFERENCES customers(id),
    square_payment_id TEXT,
    amount DECIMAL,
    modifiers JSONB,
    employee_id TEXT,
    timestamp TIMESTAMP
);

-- Insights
CREATE TABLE insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID REFERENCES accounts(id),
    type TEXT,
    pattern JSONB,
    confidence DECIMAL,
    dollar_impact DECIMAL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tasks  
CREATE TABLE tasks (
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

-- Indexes for performance
CREATE INDEX idx_customers_account_id ON customers(account_id);
CREATE INDEX idx_transactions_account_id ON transactions(account_id);
CREATE INDEX idx_tasks_account_id ON tasks(account_id);
CREATE INDEX idx_tasks_status ON tasks(status);'''
    
    print(sql)
    print()
    print("=" * 60)
    print("After running this SQL, come back and we'll continue!")

if __name__ == "__main__":
    if not setup_initial_schema():
        show_sql_for_manual_setup()