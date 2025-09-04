# Keeper Data Pipeline Specification

## Pipeline Overview
```
Square API → Raw Storage → Normalization → Enrichment → Analysis → Insights
                ↑                              ↑
          External Files                 Review APIs
```

## Phase 1: Square Data Ingestion

### OAuth Flow
```python
@app.post("/connect-square")
async def connect_square(code: str, account_id: str):
    # Exchange code for token
    token_response = square.oauth.obtain_token(
        code=code,
        client_id=SQUARE_CLIENT_ID,
        client_secret=SQUARE_CLIENT_SECRET
    )
    
    # Store encrypted token
    supabase.table('accounts').update({
        'square_access_token': encrypt(token_response.access_token),
        'square_refresh_token': encrypt(token_response.refresh_token),
        'square_merchant_id': token_response.merchant_id
    }).eq('id', account_id)
    
    # Trigger historical import
    celery.send_task('import_historical_data', args=[account_id])
```

### Historical Import (12 months)
```python
def import_historical_data(account_id):
    """Initial 12-month import"""
    
    endpoints = [
        ('customers', import_customers),
        ('payments', import_payments),
        ('appointments', import_appointments),
        ('catalog', import_catalog),
        ('team-members', import_team),
        ('loyalty', import_loyalty)
    ]
    
    for endpoint_name, import_func in endpoints:
        # Update progress
        redis.set(f'import_progress:{account_id}', {
            'current': endpoint_name,
            'percentage': progress
        })
        
        # Import with pagination
        import_func(account_id, months_back=12)
```

### Daily Sync (Adaptive)
```python
@celery.task
def daily_square_sync(account_id):
    """Adaptive incremental sync with intelligent rate handling"""
    
    api_manager = SquareAPIManager()
    circuit_breaker = CircuitBreaker()
    
    last_sync = get_last_sync(account_id)
    
    async def sync_with_resilience(endpoint, params, priority='normal'):
        """Resilient sync with circuit breaker"""
        return circuit_breaker.call(
            api_manager.make_request,
            endpoint=endpoint,
            params=params,
            priority=priority
        )
    
    # Prioritized sync order
    sync_tasks = [
        ('customers', sync_customers_since(last_sync), 'high'),
        ('payments', sync_payments_since(last_sync), 'high'),
        ('appointments', sync_appointments_since(last_sync), 'normal'),
        ('modifiers', extract_modifiers_from_payments(), 'low')
    ]
    
    updates = {}
    for data_type, sync_func, priority in sync_tasks:
        try:
            # Apply adaptive throttling
            throttle_delay = api_manager.adaptive_throttle(data_type)
            if throttle_delay > 0:
                await asyncio.sleep(throttle_delay)
            
            updates[data_type] = await sync_with_resilience(
                data_type, sync_func, priority
            )
            
        except CircuitOpenError:
            # Use cached data when circuit is open
            updates[data_type] = get_cached_data(account_id, data_type)
            log_degraded_mode(account_id, data_type)
    
    # Store raw with success tracking
    for data_type, records in updates.items():
        bulk_insert_raw(account_id, data_type, records)
        track_sync_success(account_id, data_type, len(records))
    
    # Trigger processing
    celery.send_task('process_raw_data', args=[account_id])
```

## Phase 2: Data Normalization

### Customer Normalization
```python
def normalize_customers(raw_customers):
    """Convert Square customer to our schema"""
    
    normalized = []
    for customer in raw_customers:
        normalized.append({
            'square_id': customer['id'],
            'name': clean_name(customer.get('given_name', '') + ' ' + 
                              customer.get('family_name', '')),
            'email': customer.get('email_address'),
            'phone': clean_phone(customer.get('phone_number')),
            'first_seen': customer['created_at'],
            'last_seen': calculate_last_visit(customer['id']),
            'metadata': {
                'birthday': customer.get('birthday'),
                'note': customer.get('note'),  # Square's note field
                'source': customer.get('creation_source')
            }
        })
    
    return normalized
```

### Modifier Extraction
```python
def extract_modifiers(payment_data):
    """Pull modifiers from line items"""
    
    modifiers = []
    for payment in payment_data:
        for line_item in payment.get('itemizations', []):
            for modifier in line_item.get('modifiers', []):
                modifiers.append({
                    'payment_id': payment['id'],
                    'customer_id': payment['customer_id'],
                    'modifier_name': modifier['name'],
                    'modifier_amount': modifier['base_price_money']['amount'],
                    'employee_id': payment['employee_id'],
                    'timestamp': payment['created_at']
                })
    
    return modifiers
```

## Phase 3: External Data Enrichment

### File Upload Handler
```python
@app.post("/upload-customer-data")
async def upload_external_file(file: UploadFile, account_id: str):
    """Process uploaded CSV/Excel"""
    
    # Parse file
    if file.filename.endswith('.csv'):
        df = pd.read_csv(file.file)
    else:
        df = pd.read_excel(file.file)
    
    # Detect columns
    columns = detect_column_mapping(df.columns)
    
    # Start matching job
    job_id = celery.send_task('match_external_data', 
                              args=[account_id, df.to_json(), columns])
    
    return {'job_id': job_id, 'row_count': len(df)}
```

### Fuzzy Matching Pipeline
```python
def match_external_data(account_id, external_df, column_mapping):
    """Match external data to Square customers"""
    
    square_customers = get_square_customers(account_id)
    matches = []
    
    for _, external_row in external_df.iterrows():
        # Try exact match first
        exact = exact_match(external_row, square_customers)
        if exact:
            matches.append((external_row, exact, 1.0))
            continue
        
        # Fuzzy match
        best_match = None
        best_score = 0
        
        for square_customer in square_customers:
            score = calculate_match_score(
                external_row[column_mapping['name']],
                square_customer['name'],
                external_row.get(column_mapping.get('phone')),
                square_customer.get('phone'),
                external_row.get(column_mapping.get('email')),
                square_customer.get('email')
            )
            
            if score > best_score and score >= 0.85:
                best_match = square_customer
                best_score = score
        
        if best_match:
            matches.append((external_row, best_match, best_score))
    
    # Merge matched data
    merge_external_context(matches)
    
    return {
        'total_rows': len(external_df),
        'matched': len(matches),
        'match_rate': len(matches) / len(external_df)
    }
```

### Review Data Pipeline
```python
@celery.task(schedule=cron(hour=4, minute=0))  # Daily at 4 AM
def scrape_reviews(account_id):
    """Collect reviews from all sources"""
    
    business_info = get_business_info(account_id)
    
    reviews = []
    
    # Google Business
    if business_info.get('google_business_url'):
        reviews.extend(scrape_google_reviews(business_info['google_business_url']))
    
    # Yelp
    if business_info.get('yelp_url'):
        reviews.extend(scrape_yelp_reviews(business_info['yelp_url']))
    
    # Process each review
    for review in reviews:
        # Sentiment analysis
        sentiment = analyze_sentiment(review['text'])
        
        # Entity extraction
        entities = extract_entities(review['text'])  # employees, services
        
        # Store
        store_review(account_id, review, sentiment, entities)
        
        # Alert on urgent issues
        if review['rating'] == 1 or 'rude' in review['text'].lower():
            create_urgent_task(account_id, review)
```

## Phase 4: Context Engineering (RAG)

### Customer Embedding Pipeline
```python
def generate_customer_embedding(customer_id):
    """Create searchable context for each customer"""
    
    # Gather all context
    customer = get_customer(customer_id)
    transactions = get_transactions(customer_id)
    appointments = get_appointments(customer_id)
    external_notes = get_external_notes(customer_id)
    
    # Build context document
    context = f"""
    Customer: {customer['name']}
    Contact: {customer['email']} / {customer['phone']}
    
    Lifetime Value: ${customer['lifetime_value']}
    First Visit: {customer['first_seen']}
    Last Visit: {customer['last_seen']}
    Visit Frequency: Every {customer['avg_days_between']} days
    
    Favorite Services: {', '.join(customer['top_services'])}
    Favorite Employee: {customer['preferred_employee']}
    Average Spend: ${customer['avg_transaction']}
    
    Modifiers Purchased: {', '.join(customer['modifier_history'])}
    
    Special Notes: {external_notes}
    
    Recent Activity:
    {format_recent_activity(transactions[-5:])}
    """
    
    # Generate embedding
    embedding = openai.embeddings.create(
        input=context,
        model="text-embedding-3-small"
    )
    
    # Store
    supabase.table('customers').update({
        'embedding': embedding.data[0].embedding,
        'context_updated_at': datetime.now()
    }).eq('id', customer_id)
```

### Context Retrieval for Tasks
```python
def get_context_for_task(customer_id, task_type):
    """Retrieve relevant context for task generation"""
    
    # Get base context
    customer = get_customer_with_embedding(customer_id)
    
    # Add task-specific context
    if task_type == 'churn_prevention':
        context = get_churn_context(customer)
    elif task_type == 'upsell':
        context = get_upsell_context(customer)
    elif task_type == 'reactivation':
        context = get_reactivation_context(customer)
    
    return context
```

## Data Quality Checks

### Validation Rules
```python
VALIDATION_RULES = {
    'customer_name': lambda x: len(x) > 1 and len(x) < 100,
    'email': lambda x: '@' in x if x else True,
    'phone': lambda x: len(clean_phone(x)) >= 10 if x else True,
    'amount': lambda x: x > 0 and x < 10000,
    'date': lambda x: x < datetime.now() and x > datetime(2015, 1, 1)
}

def validate_data(record, record_type):
    """Validate data quality"""
    errors = []
    
    for field, rule in VALIDATION_RULES.items():
        if field in record:
            if not rule(record[field]):
                errors.append(f"Invalid {field}: {record[field]}")
    
    return errors
```

### Duplicate Detection
```python
def detect_duplicates(new_records, existing_records):
    """Prevent duplicate data"""
    
    duplicates = []
    
    for new_record in new_records:
        # Check by unique ID
        if new_record['id'] in existing_records:
            duplicates.append(new_record['id'])
            continue
        
        # Check by composite key (customer + timestamp)
        composite_key = f"{new_record['customer_id']}_{new_record['timestamp']}"
        if composite_key in existing_composite_keys:
            duplicates.append(new_record['id'])
    
    return duplicates
```

## Performance Optimization

### Batch Processing
```python
def batch_process_records(records, batch_size=100):
    """Process records in batches for efficiency"""
    
    batches = [records[i:i+batch_size] for i in range(0, len(records), batch_size)]
    
    for batch in batches:
        # Bulk insert
        supabase.table('raw_square_data').insert(batch).execute()
        
        # Update progress
        progress = (batches.index(batch) + 1) / len(batches) * 100
        redis.set(f'processing_progress', progress)
```

### Caching Strategy
```python
CACHE_TTL = {
    'customer_profile': 3600,      # 1 hour
    'employee_metrics': 7200,      # 2 hours
    'business_summary': 86400,     # 24 hours
    'historical_data': 604800      # 7 days
}

def get_cached_or_compute(key, compute_func, ttl):
    """Check cache before computing"""
    
    # Check cache
    cached = redis.get(key)
    if cached:
        return json.loads(cached)
    
    # Compute
    result = compute_func()
    
    # Cache result
    redis.set(key, json.dumps(result), ex=ttl)
    
    return result
```

## Adaptive Square API Management

### Intelligent Rate Limiting
```python
class SquareAPIManager:
    """Adaptive rate limit handling without fixed limits"""
    
    def __init__(self):
        self.request_timing = defaultdict(list)
        self.backoff_state = defaultdict(int)
        self.success_rate = defaultdict(lambda: {'success': 0, 'total': 0})
        
    async def make_request(self, endpoint, params, priority='normal'):
        """Smart request with adaptive timing"""
        
        # Check if we're in backoff
        if self.backoff_state[endpoint] > 0:
            wait_time = 2 ** self.backoff_state[endpoint]
            await asyncio.sleep(wait_time + random.uniform(0, 1))  # Jitter
        
        try:
            response = await self.square_client.request(endpoint, params)
            
            # Track success
            self.success_rate[endpoint]['success'] += 1
            self.success_rate[endpoint]['total'] += 1
            
            # Reduce backoff on success
            if self.backoff_state[endpoint] > 0:
                self.backoff_state[endpoint] -= 1
            
            # Track timing for adaptive throttling
            self.request_timing[endpoint].append(time.time())
            
            return response
            
        except RateLimitError as e:
            # Increment backoff
            self.backoff_state[endpoint] = min(self.backoff_state[endpoint] + 1, 6)  # Max 64 seconds
            
            # Store request for retry
            await self.queue_for_retry(endpoint, params, priority)
            
            # Log for analysis
            self.log_rate_limit(endpoint, self.get_recent_request_rate(endpoint))
            
            # If high priority, retry sooner
            if priority == 'high':
                await asyncio.sleep(2 ** (self.backoff_state[endpoint] - 1))
                return await self.make_request(endpoint, params, priority)
            
            raise
    
    def adaptive_throttle(self, endpoint):
        """Preemptively slow down if detecting issues"""
        
        success_ratio = (
            self.success_rate[endpoint]['success'] / 
            self.success_rate[endpoint]['total']
            if self.success_rate[endpoint]['total'] > 0 else 1
        )
        
        if success_ratio < 0.95:  # More than 5% failures
            return 0.5 + (1 - success_ratio) * 2  # Dynamic delay
        
        return 0  # No delay needed
```

### Request Prioritization
```python
REQUEST_PRIORITIES = {
    'critical': {
        'examples': ['payment_verification', 'auth_refresh'],
        'retry_immediately': True,
        'max_retries': 10
    },
    'high': {
        'examples': ['new_customer_sync', 'today_transactions'],
        'retry_delay': '2^n seconds',
        'max_retries': 5
    },
    'normal': {
        'examples': ['daily_sync', 'catalog_update'],
        'retry_delay': '2^n minutes', 
        'max_retries': 3
    },
    'low': {
        'examples': ['historical_backfill', 'report_generation'],
        'retry_delay': 'next_scheduled_run',
        'max_retries': 1
    }
}
```

## Error Handling

### Circuit Breaker Pattern
```python
class CircuitBreaker:
    """Prevent cascading failures"""
    
    def __init__(self):
        self.failure_count = defaultdict(int)
        self.last_failure = defaultdict(float)
        self.state = defaultdict(lambda: 'closed')  # closed, open, half_open
        
    def call(self, func, *args, **kwargs):
        endpoint = kwargs.get('endpoint', 'unknown')
        
        if self.state[endpoint] == 'open':
            # Check if we should try again
            if time.time() - self.last_failure[endpoint] > 60:
                self.state[endpoint] = 'half_open'
            else:
                raise CircuitOpenError("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            
            # Success - reset if needed
            if self.state[endpoint] == 'half_open':
                self.state[endpoint] = 'closed'
                self.failure_count[endpoint] = 0
            
            return result
            
        except Exception as e:
            self.failure_count[endpoint] += 1
            self.last_failure[endpoint] = time.time()
            
            if self.failure_count[endpoint] >= 5:
                self.state[endpoint] = 'open'
                self.alert_ops_team(endpoint)
            
            raise
```

### Data Recovery
```python
def recover_failed_sync(account_id, failure_point):
    """Resume from where sync failed"""
    
    # Get last successful checkpoint
    checkpoint = get_last_checkpoint(account_id)
    
    # Resume from checkpoint
    if checkpoint:
        resume_from = checkpoint['timestamp']
        resume_type = checkpoint['data_type']
        
        # Continue sync
        if resume_type == 'customers':
            sync_customers_since(resume_from)
        elif resume_type == 'payments':
            sync_payments_since(resume_from)
        # etc...
```

## Monitoring

### Health Checks
```python
@app.get("/health/data-pipeline")
async def pipeline_health():
    """Monitor pipeline status"""
    
    checks = {
        'square_api': check_square_connection(),
        'database': check_database_connection(),
        'redis': check_redis_connection(),
        'last_sync': get_last_sync_time(),
        'error_rate': calculate_error_rate(),
        'queue_depth': get_queue_depth()
    }
    
    status = 'healthy' if all(checks.values()) else 'unhealthy'
    
    return {
        'status': status,
        'checks': checks,
        'timestamp': datetime.now()
    }
```

## Performance Targets

- Historical import: <10 minutes for 12 months
- Daily sync: <2 minutes (with adaptive rate limiting)
- Fuzzy matching: <60 seconds for 1000 records
- Embedding generation: <100ms per customer
- Review scraping: <5 minutes for all sources
- Batch processing: 1000 records/minute
- API response time: <500ms p95
- Queue processing: <10 second lag
- Rate limit recovery: <30 seconds automatic
- Circuit breaker reset: <60 seconds

## Square API Health Monitoring

```python
@app.route('/api/square-health')
def square_health_status():
    """Real-time Square API health monitoring"""
    
    return {
        'overall_health': calculate_health_score(),
        'endpoints': {
            'customers': {
                'success_rate': '98.5%',
                'avg_response_time': '235ms',
                'rate_limit_hits': 3,
                'last_success': '2 minutes ago'
            },
            'payments': {
                'success_rate': '99.2%',
                'avg_response_time': '189ms',
                'rate_limit_hits': 0,
                'last_success': '30 seconds ago'
            }
        },
        'current_backoff': get_backoff_states(),
        'queued_retries': count_retry_queue(),
        'circuit_states': get_circuit_states(),
        'recommendations': generate_recommendations()
    }
```