# Keeper Technical Architecture

## Stack Overview

### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI**: Tailwind CSS + shadcn/ui
- **State**: Zustand + React Query
- **Charts**: Recharts
- **Deployment**: Vercel

### Backend
- **API**: FastAPI (Python 3.11+)
- **Database**: Supabase (PostgreSQL 15)
- **Cache**: Redis (Upstash)
- **Queue**: Celery + Redis
- **File Storage**: Supabase Storage
- **Deployment**: Railway

### Analytics
- **Core**: Pandas, NumPy, SciKit-Learn
- **Time Series**: Prophet
- **Fuzzy Matching**: RapidFuzz (faster than FuzzyWuzzy)
- **Vectors**: pgvector in Supabase

### AI/ML
- **RAG**: Supabase pgvector + OpenAI embeddings
- **Task Generation**: Claude 3 Haiku
- **Reports**: Claude 3.5 Sonnet
- **Context**: LangChain for prompt management

## Database Schema

```sql
-- Core Business Data
CREATE TABLE accounts (
    id UUID PRIMARY KEY,
    square_merchant_id TEXT UNIQUE,
    business_name TEXT,
    business_category TEXT, -- 'spa', 'salon', 'gym'
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE locations (
    id UUID PRIMARY KEY,
    account_id UUID REFERENCES accounts(id),
    square_location_id TEXT,
    name TEXT,
    address JSONB
);

-- Square Data (Raw)
CREATE TABLE raw_square_data (
    id UUID PRIMARY KEY,
    account_id UUID REFERENCES accounts(id),
    data_type TEXT, -- 'customer', 'payment', 'appointment', etc
    square_id TEXT,
    payload JSONB,
    ingested_at TIMESTAMP DEFAULT NOW()
);

-- Processed Data
CREATE TABLE customers (
    id UUID PRIMARY KEY,
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
    metadata JSONB, -- merged external data
    embedding VECTOR(1536) -- for RAG
);

CREATE TABLE transactions (
    id UUID PRIMARY KEY,
    account_id UUID REFERENCES accounts(id),
    customer_id UUID REFERENCES customers(id),
    square_payment_id TEXT,
    amount DECIMAL,
    modifiers JSONB,
    employee_id UUID,
    timestamp TIMESTAMP
);

-- Agent System
CREATE TABLE agent_logs (
    id UUID PRIMARY KEY,
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
CREATE TABLE insights (
    id UUID PRIMARY KEY,
    account_id UUID REFERENCES accounts(id),
    type TEXT,
    pattern JSONB,
    confidence DECIMAL,
    dollar_impact DECIMAL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    account_id UUID REFERENCES accounts(id),
    insight_id UUID REFERENCES insights(id),
    customer_id UUID,
    priority INTEGER, -- 1=urgent, 2=high, 3=normal
    title TEXT,
    description TEXT,
    action_script TEXT,
    dollar_value DECIMAL,
    status TEXT, -- 'pending', 'completed', 'expired'
    expires_at TIMESTAMP,
    network_enhanced BOOLEAN DEFAULT FALSE,
    network_confidence DECIMAL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Network Learning System
CREATE TABLE network_patterns (
    id UUID PRIMARY KEY,
    pattern_type TEXT, -- 'churn_prevention', 'modifier_opportunity', etc
    business_category TEXT, -- 'spa', 'salon', 'gym'
    pattern_embedding VECTOR(1536), -- For similarity search
    context JSONB, -- Anonymized pattern details
    action_template TEXT, -- What worked
    success_rate DECIMAL,
    occurrence_count INTEGER,
    first_discovered DATE,
    last_validated DATE,
    confidence_score DECIMAL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_pattern_embedding ON network_patterns 
    USING ivfflat (pattern_embedding vector_cosine_ops);
CREATE INDEX idx_success_rate ON network_patterns(success_rate DESC);
CREATE INDEX idx_business_category ON network_patterns(business_category);
```

## Scale Confidence: 1,000+ Accounts

### Proven Capacity
```yaml
Database (Supabase PostgreSQL):
  Rows: 10+ billion capacity
  At 1,000 accounts: 300,000 rows (trivial)
  Storage: 50GB total (10% of base tier)
  Vectors: pgvector handles millions efficiently
  
API (FastAPI + Railway):
  Single server: 1,000 requests/second
  Concurrent connections: 10,000 with async
  Horizontal scaling: Add workers at $20/month each
  
Queue (Celery + Redis):
  Current: 10,000 requests/second capacity
  At 1,000 accounts: 41 syncs/hour (nothing)
  Cost scaling: Linear with usage
```

## Agent Communication

### Real-time Coordination (Redis Pub/Sub)
```python
# Publishing
redis.publish('agent_channel', {
    'agent': 'DataAgent',
    'action': 'analyzing_customer',
    'customer_id': 'abc123',
    'timestamp': datetime.now()
})

# Network learning coordination
redis.publish('network_channel', {
    'agent': 'NetworkLearningAgent',
    'action': 'pattern_discovered',
    'pattern_type': 'churn_prevention',
    'success_rate': 0.78
})

# Subscribing
for message in redis.listen('agent_channel'):
    if message['customer_id'] in my_queue:
        skip_customer(message['customer_id'])
```

### Permanent Audit (Supabase)
```python
supabase.table('agent_logs').insert({
    'agent_name': 'InsightAgent',
    'action_type': 'pattern_detected',
    'entity_type': 'customer',
    'entity_id': customer_id,
    'decision': {
        'pattern': 'modifier_decline',
        'confidence': 0.89,
        'impact': -3200
    }
})
```

## RAG Implementation

### Document Embedding Pipeline
```python
def embed_customer_context(customer_data, external_notes):
    # Combine all context
    context = f"""
    Customer: {customer_data['name']}
    Lifetime Value: ${customer_data['ltv']}
    Visit Pattern: Every {customer_data['frequency']} days
    Last Visit: {customer_data['last_seen']}
    Preferences: {customer_data['services']}
    Notes: {external_notes}
    """
    
    # Generate embedding
    embedding = openai.Embedding.create(
        input=context,
        model="text-embedding-3-small"
    )
    
    # Store in pgvector
    supabase.table('customers').update({
        'embedding': embedding
    }).eq('id', customer_data['id'])
```

### Context Retrieval
```python
def get_customer_context(customer_name):
    # Vector similarity search
    results = supabase.rpc('match_customers', {
        'query_embedding': embed(customer_name),
        'match_threshold': 0.8,
        'match_count': 5
    })
    
    return results
```

## Quality Gates

Every insight must pass:
1. **Confidence Check**: >= 75% confidence
2. **Actionability Check**: Specific action exists
3. **Obviousness Check**: Not in banned_insights list
4. **Value Check**: Dollar impact calculable
5. **Multi-Model Validation**: 2+ models agree
6. **Network Enhancement**: Apply network intelligence when patterns exist

## Network Learning Integration

### Pattern Storage
```python
# When insight succeeds
def capture_successful_pattern(insight, outcome):
    pattern = {
        'type': insight['type'],
        'business_category': get_business_category(insight['account_id']),
        'trigger_conditions': extract_conditions(insight),
        'action_template': insight['action'],
        'success_rate': outcome['success_rate'],
        'revenue_impact': outcome['revenue_impact']
    }
    
    # Generate embedding for similarity matching
    embedding = openai.embeddings.create(
        input=serialize_pattern(pattern),
        model="text-embedding-3-small"
    ).data[0].embedding
    
    # Store anonymized pattern
    store_network_pattern(pattern, embedding)
```

### Pattern Application
```python
# Enhance insights with network intelligence
def enhance_with_network(insight):
    similar_patterns = search_similar_patterns(
        insight,
        min_success_rate=0.60,
        min_occurrences=3
    )
    
    if similar_patterns:
        best = max(similar_patterns, key=lambda x: x['success_rate'])
        insight['network_enhanced'] = True
        insight['confidence'] *= (1 + best['success_rate'] * 0.3)
        insight['proven_approach'] = best['action_template']
        insight['network_context'] = f"Works {best['success_rate']*100:.0f}% of the time"
    
    return insight
```

## Error Handling

- All Square API calls wrapped in retry logic
- Failed tasks logged to dead letter queue
- Agent failures trigger alerts
- Data inconsistencies flagged for review