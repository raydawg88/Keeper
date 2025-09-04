-- Enable pgvector extension first
CREATE EXTENSION IF NOT EXISTS vector;

-- Then add embedding columns for customer matching
ALTER TABLE customers ADD COLUMN IF NOT EXISTS embedding VECTOR(3072);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS embedding_text TEXT;
