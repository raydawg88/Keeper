-- Add missing columns to accounts table
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS refresh_token TEXT;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS token_expires_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS square_locations JSONB;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS subscription_status TEXT DEFAULT 'trial';
