-- Square Data Models for Keeper (Simplified version)
-- Basic tables without vector extension dependencies

-- Store Square merchants (businesses)
CREATE TABLE IF NOT EXISTS square_merchants (
  id TEXT PRIMARY KEY,
  account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
  business_name TEXT NOT NULL,
  country TEXT NOT NULL,
  language_code TEXT NOT NULL,
  currency TEXT NOT NULL,
  status TEXT NOT NULL,
  main_location_id TEXT,
  owner_email TEXT,
  created_at TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  synced_at TIMESTAMPTZ DEFAULT NOW()
);

-- Store Square locations (physical/digital business locations)
CREATE TABLE IF NOT EXISTS square_locations (
  id TEXT PRIMARY KEY,
  merchant_id TEXT REFERENCES square_merchants(id) ON DELETE CASCADE,
  account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  address_line_1 TEXT,
  address_line_2 TEXT,
  locality TEXT,
  administrative_district_level_1 TEXT,
  postal_code TEXT,
  country TEXT,
  timezone TEXT,
  capabilities TEXT[],
  status TEXT NOT NULL,
  location_type TEXT,
  business_name TEXT,
  mcc TEXT,
  business_hours JSONB,
  created_at TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  synced_at TIMESTAMPTZ DEFAULT NOW()
);

-- Store Square customers (basic version without vector embedding)
CREATE TABLE IF NOT EXISTS square_customers (
  id TEXT PRIMARY KEY,
  account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
  location_id TEXT REFERENCES square_locations(id),
  given_name TEXT,
  family_name TEXT,
  nickname TEXT,
  company_name TEXT,
  email_address TEXT,
  phone_number TEXT,
  birthday TEXT,
  note TEXT,
  reference_id TEXT,
  creation_source TEXT,
  email_unsubscribed BOOLEAN DEFAULT FALSE,
  version BIGINT,
  
  -- Address fields
  address_line_1 TEXT,
  address_line_2 TEXT,
  locality TEXT,
  administrative_district_level_1 TEXT,
  postal_code TEXT,
  country TEXT,
  
  -- Keeper-specific fields for intelligence
  customer_profile JSONB,
  lifetime_value DECIMAL(10,2),
  visit_frequency TEXT,
  churn_risk_score DECIMAL(3,2),
  last_visit_date TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  synced_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_customer_per_account UNIQUE(account_id, id)
);

-- Store Square payments (transactions)
CREATE TABLE IF NOT EXISTS square_payments (
  id TEXT PRIMARY KEY,
  account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
  location_id TEXT REFERENCES square_locations(id),
  order_id TEXT,
  customer_id TEXT REFERENCES square_customers(id),
  
  -- Payment details
  amount_money DECIMAL(10,2) NOT NULL,
  currency TEXT NOT NULL,
  status TEXT NOT NULL,
  source_type TEXT,
  receipt_number TEXT,
  receipt_url TEXT,
  
  -- Timing
  created_at TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ,
  processed_at TIMESTAMPTZ,
  
  -- Payment method details
  payment_source JSONB,
  risk_evaluation JSONB,
  processing_fee DECIMAL(8,2),
  
  -- Keeper analytics
  time_of_day INTEGER,
  day_of_week INTEGER,
  is_weekend BOOLEAN,
  season TEXT,
  
  synced_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_payment_per_account UNIQUE(account_id, id)
);

-- Store Square orders (detailed transaction breakdowns)
CREATE TABLE IF NOT EXISTS square_orders (
  id TEXT PRIMARY KEY,
  account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
  location_id TEXT REFERENCES square_locations(id),
  customer_id TEXT REFERENCES square_customers(id),
  
  -- Order details
  state TEXT NOT NULL,
  version BIGINT,
  
  -- Money fields
  total_money DECIMAL(10,2),
  total_tax_money DECIMAL(10,2),
  total_discount_money DECIMAL(10,2),
  total_tip_money DECIMAL(10,2),
  total_service_charge_money DECIMAL(10,2),
  
  -- Order items and modifiers
  line_items JSONB,
  fulfillments JSONB,
  
  -- Keeper analytics
  item_count INTEGER,
  modifier_count INTEGER,
  total_modifiers_value DECIMAL(8,2),
  avg_item_price DECIMAL(8,2),
  
  created_at TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ,
  closed_at TIMESTAMPTZ,
  synced_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_order_per_account UNIQUE(account_id, id)
);

-- Store Square sync status
CREATE TABLE IF NOT EXISTS square_sync_status (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
  entity_type TEXT NOT NULL,
  last_sync_at TIMESTAMPTZ,
  last_cursor TEXT,
  sync_status TEXT DEFAULT 'pending',
  error_message TEXT,
  records_synced INTEGER DEFAULT 0,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_sync_per_account_entity UNIQUE(account_id, entity_type)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_square_payments_account_date 
ON square_payments(account_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_square_customers_account_email 
ON square_customers(account_id, email_address);

CREATE INDEX IF NOT EXISTS idx_square_customers_phone 
ON square_customers(account_id, phone_number);

CREATE INDEX IF NOT EXISTS idx_square_sync_status_account 
ON square_sync_status(account_id, entity_type);