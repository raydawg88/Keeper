-- DATABASE TABLES FOR SQUARE API DATA
-- Creates proper schema for payments, orders, team_members, and catalog_items

-- PAYMENTS TABLE
-- Stores transaction data from Square Payments API
CREATE TABLE IF NOT EXISTS payments (
    id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    payment_id TEXT UNIQUE NOT NULL,
    amount_cents INTEGER,
    tip_cents INTEGER DEFAULT 0,
    currency TEXT DEFAULT 'USD',
    status TEXT,
    source_type TEXT,
    customer_id TEXT,
    location_id TEXT,
    order_id TEXT,
    receipt_number TEXT,
    receipt_url TEXT,
    processing_fee_cents INTEGER,
    card_brand TEXT,
    card_last_4 TEXT,
    card_entry_method TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    square_data JSONB, -- Store complete Square response
    synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_payments_account FOREIGN KEY (account_id) REFERENCES accounts(id)
);

-- ORDERS TABLE  
-- Stores order data from Square Orders API
CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    order_id TEXT UNIQUE NOT NULL,
    location_id TEXT,
    customer_id TEXT,
    state TEXT,
    version INTEGER,
    total_money_cents INTEGER,
    total_tax_cents INTEGER,
    total_discount_cents INTEGER,
    total_tip_cents INTEGER,
    service_charge_cents INTEGER,
    net_amount_cents INTEGER,
    refunded_money_cents INTEGER,
    line_items JSONB, -- Array of line items
    discounts JSONB, -- Array of discounts
    taxes JSONB, -- Array of taxes
    service_charges JSONB, -- Array of service charges
    fulfillments JSONB, -- Array of fulfillments
    tenders JSONB, -- Payment methods used
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    closed_at TIMESTAMP WITH TIME ZONE,
    square_data JSONB, -- Store complete Square response
    synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_orders_account FOREIGN KEY (account_id) REFERENCES accounts(id)
);

-- TEAM_MEMBERS TABLE
-- Stores employee data from Square Team Members API  
CREATE TABLE IF NOT EXISTS team_members (
    id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    team_member_id TEXT UNIQUE NOT NULL,
    reference_id TEXT,
    is_owner BOOLEAN DEFAULT FALSE,
    status TEXT,
    given_name TEXT,
    family_name TEXT,
    email_address TEXT,
    phone_number TEXT,
    assigned_locations JSONB, -- Array of location IDs
    wage_settings JSONB, -- Hourly rate, salary, job assignments
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    square_data JSONB, -- Store complete Square response
    synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_team_members_account FOREIGN KEY (account_id) REFERENCES accounts(id)
);

-- CATALOG_ITEMS TABLE
-- Stores products/services from Square Catalog API
CREATE TABLE IF NOT EXISTS catalog_items (
    id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    catalog_object_id TEXT UNIQUE NOT NULL,
    object_type TEXT,
    version INTEGER,
    is_deleted BOOLEAN DEFAULT FALSE,
    present_at_all_locations BOOLEAN DEFAULT TRUE,
    present_at_location_ids JSONB, -- Array of location IDs
    item_name TEXT,
    item_description TEXT,
    category_id TEXT,
    variations JSONB, -- Price variations, modifiers
    modifier_list_ids JSONB, -- Associated modifier lists
    tax_ids JSONB, -- Associated taxes
    image_id TEXT,
    available_online BOOLEAN DEFAULT FALSE,
    available_for_pickup BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    square_data JSONB, -- Store complete Square response
    synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_catalog_items_account FOREIGN KEY (account_id) REFERENCES accounts(id)
);

-- INDEXES FOR PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_payments_account_id ON payments(account_id);
CREATE INDEX IF NOT EXISTS idx_payments_customer_id ON payments(customer_id);
CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at);
CREATE INDEX IF NOT EXISTS idx_payments_amount ON payments(amount_cents);

CREATE INDEX IF NOT EXISTS idx_orders_account_id ON orders(account_id);  
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_orders_total ON orders(total_money_cents);

CREATE INDEX IF NOT EXISTS idx_team_members_account_id ON team_members(account_id);
CREATE INDEX IF NOT EXISTS idx_team_members_status ON team_members(status);
CREATE INDEX IF NOT EXISTS idx_team_members_name ON team_members(given_name, family_name);

CREATE INDEX IF NOT EXISTS idx_catalog_items_account_id ON catalog_items(account_id);
CREATE INDEX IF NOT EXISTS idx_catalog_items_type ON catalog_items(object_type);
CREATE INDEX IF NOT EXISTS idx_catalog_items_deleted ON catalog_items(is_deleted);

-- COMMENTS FOR DOCUMENTATION
COMMENT ON TABLE payments IS 'Square Payments API data - transaction records with card details';
COMMENT ON TABLE orders IS 'Square Orders API data - complete order details with line items';  
COMMENT ON TABLE team_members IS 'Square Team Members API data - employee information and wages';
COMMENT ON TABLE catalog_items IS 'Square Catalog API data - products/services with pricing';

COMMENT ON COLUMN payments.square_data IS 'Complete Square API response for reference';
COMMENT ON COLUMN orders.square_data IS 'Complete Square API response for reference';
COMMENT ON COLUMN team_members.square_data IS 'Complete Square API response for reference';
COMMENT ON COLUMN catalog_items.square_data IS 'Complete Square API response for reference';