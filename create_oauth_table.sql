CREATE TABLE IF NOT EXISTS oauth_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    state VARCHAR(64) UNIQUE NOT NULL,
    redirect_uri TEXT NOT NULL,
    business_name TEXT,
    account_id UUID REFERENCES accounts(id),
    status VARCHAR(20) DEFAULT 'pending',
    error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE
);
