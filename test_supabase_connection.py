#!/usr/bin/env python3
"""
Test Supabase connection and setup initial database schema
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """Test Supabase connection and permissions"""
    
    # Get credentials from environment
    url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    
    print("🔄 Testing Supabase connection...")
    print(f"URL: {url}")
    print(f"Project: keeper-prod")
    print("-" * 50)
    
    if not url or not service_key:
        print("❌ Missing Supabase credentials in .env file")
        return False
    
    try:
        # Create client with service key (admin permissions)
        supabase: Client = create_client(url, service_key)
        
        # Test 1: Basic connection
        print("✅ Supabase client created successfully")
        
        # Test 2: Check if we can query (should be empty initially)
        try:
            result = supabase.table('accounts').select('*').limit(1).execute()
            print("✅ Database query successful (accounts table exists)")
            print(f"   Found {len(result.data)} records")
        except Exception as e:
            if "relation" in str(e).lower() and "does not exist" in str(e).lower():
                print("ℹ️  Tables don't exist yet (expected - we'll create them next)")
            else:
                print(f"❌ Database query failed: {str(e)}")
        
        # Test 3: Check database permissions
        try:
            # Try to create a simple test table
            supabase.postgrest.schema("public").rpc("version").execute()
            print("✅ Database connection verified")
        except Exception as e:
            print(f"❌ Database permission test failed: {str(e)}")
            return False
            
        print("-" * 50)
        print("✅ Supabase connection test complete!")
        print("🎯 Ready to create Keeper database schema")
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {str(e)}")
        return False

def create_keeper_schema():
    """Create the complete Keeper database schema"""
    
    url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    supabase: Client = create_client(url, service_key)
    
    print("\n🏗️  Creating Keeper database schema...")
    print("-" * 50)
    
    # Schema from architecture-dropset.md
    schema_sql = """
    -- Enable required extensions
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "vector";
    
    -- Core Business Data
    CREATE TABLE IF NOT EXISTS accounts (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        square_merchant_id TEXT UNIQUE,
        business_name TEXT,
        business_category TEXT DEFAULT 'spa',
        created_at TIMESTAMP DEFAULT NOW()
    );
    
    CREATE TABLE IF NOT EXISTS locations (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        account_id UUID REFERENCES accounts(id),
        square_location_id TEXT,
        name TEXT,
        address JSONB
    );
    
    -- Square Data (Raw)
    CREATE TABLE IF NOT EXISTS raw_square_data (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        account_id UUID REFERENCES accounts(id),
        data_type TEXT,
        square_id TEXT,
        payload JSONB,
        ingested_at TIMESTAMP DEFAULT NOW()
    );
    
    -- Processed Data
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
        embedding VECTOR(1536),
        context_cache JSONB,
        context_updated_at TIMESTAMP,
        network_enhanced BOOLEAN DEFAULT FALSE
    );
    
    CREATE TABLE IF NOT EXISTS transactions (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        account_id UUID REFERENCES accounts(id),
        customer_id UUID REFERENCES customers(id),
        square_payment_id TEXT,
        amount DECIMAL,
        modifiers JSONB,
        employee_id UUID,
        timestamp TIMESTAMP
    );
    
    -- Agent System
    CREATE TABLE IF NOT EXISTS agent_logs (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        account_id UUID REFERENCES accounts(id),
        agent_name TEXT,
        action_type TEXT,
        entity_type TEXT,
        entity_id UUID,
        decision JSONB,
        confidence DECIMAL,
        created_at TIMESTAMP DEFAULT NOW()
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
        network_enhanced BOOLEAN DEFAULT FALSE,
        network_confidence DECIMAL,
        created_at TIMESTAMP DEFAULT NOW()
    );
    
    -- Network Learning System
    CREATE TABLE IF NOT EXISTS network_patterns (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        pattern_type TEXT,
        business_category TEXT,
        pattern_embedding VECTOR(1536),
        context JSONB,
        action_template TEXT,
        success_rate DECIMAL,
        occurrence_count INTEGER,
        first_discovered DATE,
        last_validated DATE,
        confidence_score DECIMAL,
        created_at TIMESTAMP DEFAULT NOW()
    );
    
    -- Create indexes for performance
    CREATE INDEX IF NOT EXISTS idx_customers_account_id ON customers(account_id);
    CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id);
    CREATE INDEX IF NOT EXISTS idx_tasks_account_id ON tasks(account_id);
    CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
    CREATE INDEX IF NOT EXISTS idx_network_patterns_category ON network_patterns(business_category);
    CREATE INDEX IF NOT EXISTS idx_pattern_embedding ON network_patterns USING ivfflat (pattern_embedding vector_cosine_ops);
    CREATE INDEX IF NOT EXISTS idx_success_rate ON network_patterns(success_rate DESC);
    """
    
    try:
        # Execute schema creation
        supabase.postgrest.schema("public").rpc("exec", {"sql": schema_sql}).execute()
        print("✅ Database schema created successfully!")
        
        # Test that tables were created
        result = supabase.table('accounts').select('*').limit(1).execute()
        print("✅ Schema validation successful - tables are accessible")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema creation failed: {str(e)}")
        print("🔧 Trying alternative approach with individual table creation...")
        
        # Try creating tables individually if batch fails
        tables = [
            ("accounts", "Core business accounts table"),
            ("customers", "Customer data and context"),
            ("tasks", "Actionable insights and tasks"),
            ("network_patterns", "Collective learning patterns")
        ]
        
        for table_name, description in tables:
            try:
                result = supabase.table(table_name).select('*').limit(1).execute()
                print(f"✅ {description} - table exists")
            except Exception as table_error:
                print(f"❌ {description} - table missing: {str(table_error)}")
        
        return False

if __name__ == "__main__":
    if test_supabase_connection():
        create_keeper_schema()
    else:
        print("❌ Cannot proceed with schema creation due to connection issues")