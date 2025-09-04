-- Square Data Models for Keeper Business Intelligence
-- Designed based on actual Square API exploration results
-- These tables store synced Square data for analysis

-- =============================================
-- CORE BUSINESS ENTITIES
-- =============================================

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
  capabilities TEXT[], -- Array of capabilities like 'CREDIT_CARD_PROCESSING'
  status TEXT NOT NULL,
  location_type TEXT, -- 'PHYSICAL', 'MOBILE', etc.
  business_name TEXT,
  mcc TEXT, -- Merchant Category Code
  business_hours JSONB, -- Store business hours as JSON
  created_at TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  synced_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- CUSTOMER DATA (Core for Keeper Intelligence)
-- =============================================

-- Store Square customers with enhanced fields for fuzzy matching
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
  customer_embedding VECTOR(3072), -- OpenAI embedding for fuzzy matching
  customer_profile JSONB, -- Computed customer profile/segments
  lifetime_value DECIMAL(10,2),
  visit_frequency TEXT, -- 'daily', 'weekly', 'monthly', 'occasional'
  churn_risk_score DECIMAL(3,2), -- 0.00 to 1.00
  last_visit_date TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  synced_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Indexes for fuzzy matching and analysis
  CONSTRAINT unique_customer_per_account UNIQUE(account_id, id)
);

-- Create vector similarity index for customer matching
CREATE INDEX IF NOT EXISTS idx_square_customers_embedding 
ON square_customers USING ivfflat (customer_embedding vector_cosine_ops);

-- Create indexes for customer analysis
CREATE INDEX IF NOT EXISTS idx_square_customers_account_email 
ON square_customers(account_id, email_address);

CREATE INDEX IF NOT EXISTS idx_square_customers_phone 
ON square_customers(account_id, phone_number);

CREATE INDEX IF NOT EXISTS idx_square_customers_name 
ON square_customers(account_id, given_name, family_name);

-- =============================================
-- TRANSACTION DATA (Revenue Intelligence)
-- =============================================

-- Store Square payments (transactions)
CREATE TABLE IF NOT EXISTS square_payments (
  id TEXT PRIMARY KEY,
  account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
  location_id TEXT REFERENCES square_locations(id),
  order_id TEXT, -- Reference to square_orders
  customer_id TEXT REFERENCES square_customers(id),
  
  -- Payment details
  amount_money DECIMAL(10,2) NOT NULL,
  currency TEXT NOT NULL,
  status TEXT NOT NULL,
  source_type TEXT, -- 'CARD', 'CASH', etc.
  receipt_number TEXT,
  receipt_url TEXT,
  
  -- Timing
  created_at TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ,
  processed_at TIMESTAMPTZ,
  
  -- Payment method details (stored as JSONB for flexibility)
  payment_source JSONB,
  
  -- Risk and processing
  risk_evaluation JSONB,
  processing_fee DECIMAL(8,2),
  
  -- Keeper-specific analytics
  time_of_day INTEGER, -- Hour (0-23) for pattern analysis
  day_of_week INTEGER, -- 0=Sunday, 6=Saturday
  is_weekend BOOLEAN,
  season TEXT, -- 'spring', 'summer', 'fall', 'winter'
  
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
  state TEXT NOT NULL, -- 'DRAFT', 'OPEN', 'COMPLETED', 'CANCELED'
  version BIGINT,
  
  -- Money fields
  total_money DECIMAL(10,2),
  total_tax_money DECIMAL(10,2),
  total_discount_money DECIMAL(10,2),
  total_tip_money DECIMAL(10,2),
  total_service_charge_money DECIMAL(10,2),
  
  -- Order items and modifiers (stored as JSONB for analysis)
  line_items JSONB, -- Full line items with quantities, modifiers, etc.
  fulfillments JSONB, -- Delivery/pickup info
  
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

-- =============================================
-- CATALOG DATA (Service/Product Intelligence)
-- =============================================

-- Store Square catalog items (services, products)
CREATE TABLE IF NOT EXISTS square_catalog_items (
  id TEXT PRIMARY KEY,
  account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
  type TEXT NOT NULL, -- 'ITEM', 'ITEM_VARIATION', 'CATEGORY', etc.
  version BIGINT,
  
  -- Item details
  name TEXT NOT NULL,
  description TEXT,
  category_id TEXT,
  
  -- Variations and pricing
  variations JSONB, -- Item variations with pricing
  modifier_list_info JSONB, -- Available modifiers
  
  -- Keeper analytics
  popularity_score DECIMAL(5,2), -- Based on order frequency
  avg_revenue_per_sale DECIMAL(8,2),
  seasonality JSONB, -- Sales patterns by season/time
  profit_margin DECIMAL(5,2),
  
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ,
  synced_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_catalog_item_per_account UNIQUE(account_id, id)
);

-- =============================================
-- EMPLOYEE DATA (Staff Performance Intelligence)
-- =============================================

-- Store Square team members (employees)
CREATE TABLE IF NOT EXISTS square_team_members (
  id TEXT PRIMARY KEY,
  account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
  
  -- Employee details
  given_name TEXT,
  family_name TEXT,
  email_address TEXT,
  phone_number TEXT,
  status TEXT, -- 'ACTIVE', 'INACTIVE'
  
  -- Work details
  assigned_locations TEXT[], -- Array of location IDs
  wage_settings JSONB, -- Wage and compensation info
  
  -- Keeper analytics
  performance_score DECIMAL(3,2), -- 0.00 to 1.00
  avg_sales_per_hour DECIMAL(8,2),
  customer_satisfaction_score DECIMAL(3,2),
  upsell_rate DECIMAL(3,2), -- Percentage of transactions with modifiers
  
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ,
  synced_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_team_member_per_account UNIQUE(account_id, id)
);

-- =============================================
-- APPOINTMENT DATA (Spa/Salon Intelligence)
-- =============================================

-- Store Square appointments (crucial for spa/salon businesses)
CREATE TABLE IF NOT EXISTS square_appointments (
  id TEXT PRIMARY KEY,
  account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
  location_id TEXT REFERENCES square_locations(id),
  customer_id TEXT REFERENCES square_customers(id),
  team_member_id TEXT REFERENCES square_team_members(id),
  
  -- Appointment details
  service_duration INTEGER, -- Minutes
  status TEXT, -- 'PENDING', 'ACCEPTED', 'CANCELLED', 'COMPLETED'
  start_at TIMESTAMPTZ NOT NULL,
  
  -- Service details
  services JSONB, -- Services booked
  total_price DECIMAL(8,2),
  
  -- Keeper analytics for spa optimization
  lead_time_days INTEGER, -- Days between booking and appointment
  is_no_show BOOLEAN DEFAULT FALSE,
  is_repeat_customer BOOLEAN,
  booking_channel TEXT, -- 'online', 'phone', 'walk-in'
  
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ,
  synced_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_appointment_per_account UNIQUE(account_id, id)
);

-- =============================================
-- DATA SYNC TRACKING
-- =============================================

-- Track sync operations for each account
CREATE TABLE IF NOT EXISTS square_sync_status (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
  entity_type TEXT NOT NULL, -- 'customers', 'payments', 'orders', etc.
  last_sync_at TIMESTAMPTZ,
  last_cursor TEXT, -- For pagination
  sync_status TEXT DEFAULT 'pending', -- 'pending', 'running', 'completed', 'error'
  error_message TEXT,
  records_synced INTEGER DEFAULT 0,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT unique_sync_per_account_entity UNIQUE(account_id, entity_type)
);

-- =============================================
-- INDEXES FOR PERFORMANCE
-- =============================================

-- Payment analysis indexes
CREATE INDEX IF NOT EXISTS idx_square_payments_account_date 
ON square_payments(account_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_square_payments_customer_date 
ON square_payments(customer_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_square_payments_location_date 
ON square_payments(location_id, created_at DESC);

-- Order analysis indexes  
CREATE INDEX IF NOT EXISTS idx_square_orders_account_date 
ON square_orders(account_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_square_orders_customer 
ON square_orders(customer_id, created_at DESC);

-- Appointment analysis indexes
CREATE INDEX IF NOT EXISTS idx_square_appointments_account_date 
ON square_appointments(account_id, start_at DESC);

CREATE INDEX IF NOT EXISTS idx_square_appointments_customer 
ON square_appointments(customer_id, start_at DESC);

CREATE INDEX IF NOT EXISTS idx_square_appointments_team_member 
ON square_appointments(team_member_id, start_at DESC);

-- Sync status indexes
CREATE INDEX IF NOT EXISTS idx_square_sync_status_account 
ON square_sync_status(account_id, entity_type);

-- =============================================
-- COMMENTS AND NOTES
-- =============================================

COMMENT ON TABLE square_merchants IS 'Core business information from Square';
COMMENT ON TABLE square_locations IS 'Physical/digital business locations';
COMMENT ON TABLE square_customers IS 'Customer data with Keeper intelligence fields';
COMMENT ON TABLE square_payments IS 'Transaction data with time-based analytics';
COMMENT ON TABLE square_orders IS 'Detailed order breakdowns with modifier analysis';
COMMENT ON TABLE square_catalog_items IS 'Products/services with performance metrics';
COMMENT ON TABLE square_team_members IS 'Employee data with performance tracking';
COMMENT ON TABLE square_appointments IS 'Appointment data for spa/salon optimization';
COMMENT ON TABLE square_sync_status IS 'Tracks data synchronization operations';

COMMENT ON COLUMN square_customers.customer_embedding IS 'OpenAI embedding for 97%+ fuzzy matching';
COMMENT ON COLUMN square_customers.churn_risk_score IS 'AI-computed churn probability (0.0-1.0)';
COMMENT ON COLUMN square_payments.time_of_day IS 'Hour of transaction for pattern analysis';
COMMENT ON COLUMN square_orders.modifier_count IS 'Count of modifiers for upselling analysis';