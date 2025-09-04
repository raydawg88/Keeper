# Keeper Square API Resilience Strategy

## Core Principle
Square doesn't publish rate limits intentionally - they want adaptive systems. Build for resilience, not specific numbers.

## Rate Limit Handling

### Adaptive Rate Management
```python
class SquareAPIManager:
    """Intelligent rate limit handling without fixed limits"""
    
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
    
    def get_recent_request_rate(self, endpoint):
        """Calculate requests per second for last minute"""
        now = time.time()
        recent = [t for t in self.request_timing[endpoint] if now - t < 60]
        return len(recent) / 60 if recent else 0
    
    def adaptive_throttle(self, endpoint):
        """Preemptively slow down if detecting issues"""
        
        success_ratio = (
            self.success_rate[endpoint]['success'] / 
            self.success_rate[endpoint]['total']
            if self.success_rate[endpoint]['total'] > 0 else 1
        )
        
        if success_ratio < 0.95:  # More than 5% failures
            # Slow down
            return 0.5 + (1 - success_ratio) * 2  # Dynamic delay
        
        return 0  # No delay needed
```

### Intelligent Retry Strategy
```python
class RetryQueue:
    """Priority-based retry queue for failed requests"""
    
    def __init__(self):
        self.high_priority = asyncio.Queue()
        self.normal_priority = asyncio.Queue()
        self.low_priority = asyncio.Queue()
        
    async def add_retry(self, request, priority='normal'):
        """Queue failed request for retry"""
        
        request['retry_count'] = request.get('retry_count', 0) + 1
        request['next_retry'] = time.time() + (2 ** request['retry_count'])
        
        if request['retry_count'] > 5:
            # Max retries exceeded
            await self.handle_permanent_failure(request)
            return
        
        # Add to appropriate queue
        queue_map = {
            'high': self.high_priority,
            'normal': self.normal_priority, 
            'low': self.low_priority
        }
        
        await queue_map[priority].put(request)
    
    async def process_retries(self):
        """Background worker for retries"""
        
        while True:
            # Process high priority first
            for queue in [self.high_priority, self.normal_priority, self.low_priority]:
                if not queue.empty():
                    request = await queue.get()
                    
                    if time.time() >= request['next_retry']:
                        await self.retry_request(request)
                    else:
                        # Not ready, put back
                        await queue.put(request)
            
            await asyncio.sleep(1)
```

## Request Prioritization

### Priority Levels
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

## Square Partnership Path

### Scaling Strategy
```markdown
## Phase 1: Standard API (Now)
- Use public API with smart rate handling
- Monitor actual limits through 429 responses
- Build reputation as quality app

## Phase 2: Square App Marketplace (Month 3)
- Apply with 3 customer success stories
- Get featured in spa/salon category
- Gain Square's attention as valuable partner

## Phase 3: Partner Discussion (Month 6)
- Request increased rate limits
- Negotiate based on value to Square merchants
- Potential revenue share for premium access

## Phase 4: Premier Partner (Year 2)
- Custom rate limits
- Direct Square support
- Co-marketing opportunities
- Beta access to new APIs
```

### Contact Template for Square
```markdown
Subject: Keeper - Increasing Square Merchant Revenue by 23%

Hi Square Partnerships Team,

Keeper is helping [X] Square merchants increase revenue by an average of 23% 
through AI-driven insights from their Square data.

Current metrics:
- Average merchant revenue increase: $3,200/month
- Merchant retention: 94%
- 5-star rating in App Marketplace

We're experiencing rate limits that slow our growth. Our merchants need:
- Real-time sync for urgent insights
- Historical analysis requiring bulk data
- Multi-location support

Can we discuss premium API access or partner tier?

Best,
[Your name]
```

## Multi-POS Preparation

### Future Integration Architecture
```python
class POSAbstractionLayer:
    """Prepare for multi-POS support from day 1"""
    
    def __init__(self):
        self.providers = {
            'square': SquareProvider(),
            # Future providers
            'clover': None,  # CloverProvider()
            'toast': None,   # ToastProvider()
            'shopify': None, # ShopifyProvider()
        }
    
    async def sync_data(self, account_id):
        """Provider-agnostic sync"""
        
        provider_type = self.get_provider_type(account_id)
        provider = self.providers[provider_type]
        
        if not provider:
            raise NotImplementedError(f"{provider_type} coming soon")
        
        # Common interface regardless of provider
        return await provider.sync_all(account_id)
```

### Standard Data Model
```python
# Always normalize to this regardless of source
UNIVERSAL_SCHEMA = {
    'customer': {
        'id': 'string',
        'name': 'string',
        'email': 'string', 
        'phone': 'string',
        'first_visit': 'datetime',
        'last_visit': 'datetime',
        'lifetime_value': 'decimal',
        'metadata': 'jsonb'
    },
    'transaction': {
        'id': 'string',
        'customer_id': 'string',
        'amount': 'decimal',
        'items': 'array',
        'modifiers': 'array',
        'employee_id': 'string',
        'timestamp': 'datetime'
    }
}
```

## Failure Recovery

### Graceful Degradation
```python
class DegradationStrategy:
    """Keep working even when Square is down"""
    
    def handle_square_outage(self, account_id):
        """What to do when Square is unavailable"""
        
        # Use cached data
        last_sync = self.get_last_successful_sync(account_id)
        
        if (datetime.now() - last_sync).days <= 1:
            # Recent data available
            self.notify_user(
                "Using data from {last_sync}. "
                "New transactions will sync when Square is available."
            )
            return self.use_cached_data(account_id)
            
        elif (datetime.now() - last_sync).days <= 7:
            # Older but usable
            self.notify_user(
                "Square is temporarily unavailable. "
                "Showing insights from last week."
            )
            return self.use_cached_data(account_id, reduced_confidence=True)
            
        else:
            # Too old to be useful
            self.show_limited_features(account_id)
            return {
                'status': 'degraded',
                'available_features': [
                    'historical_reports',
                    'employee_reviews',
                    'task_management'
                ]
            }
```

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

## Monitoring & Alerting

### Square Health Dashboard
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
        'recommendations': generate_recommendations()
    }
```

### Alert Triggers
```python
ALERT_CONDITIONS = {
    'rate_limit_spike': {
        'condition': 'rate_limit_hits > 10 in 5 minutes',
        'action': 'Slow down sync frequency',
        'notification': 'slack'
    },
    'api_degradation': {
        'condition': 'success_rate < 90%',
        'action': 'Switch to cached mode',
        'notification': 'pagerduty'
    },
    'complete_outage': {
        'condition': 'all_endpoints_failing',
        'action': 'Enable read-only mode',
        'notification': 'all_channels'
    }
}
```

## Cost Optimization

### Intelligent Caching
```python
CACHE_STRATEGY = {
    'customers': {
        'ttl': 3600,  # 1 hour
        'refresh_if_stale': True
    },
    'products': {
        'ttl': 86400,  # 24 hours
        'refresh_if_stale': False
    },
    'transactions': {
        'ttl': 300,  # 5 minutes for today
        'ttl_historical': 604800  # 7 days for old data
    }
}

def should_fetch_from_api(data_type, last_fetch):
    """Determine if we need fresh data"""
    
    if urgent_request:
        return True
    
    ttl = CACHE_STRATEGY[data_type]['ttl']
    if time.time() - last_fetch > ttl:
        return True
    
    return False
```

## The Bottom Line

**We don't need published rate limits - we need resilient architecture.**

Key strategies:
1. **Adaptive throttling** based on actual responses
2. **Smart retries** with exponential backoff and jitter
3. **Request prioritization** for critical operations
4. **Graceful degradation** when Square is down
5. **Provider abstraction** for future POS systems

This approach means:
- We never lose data (queued retries)
- We never break the user experience (cached fallbacks)
- We automatically adapt to Square's actual limits
- We're ready to add Clover/Toast/Shopify when needed

**Remember**: Square wants successful apps in their ecosystem. Build something valuable, handle their API respectfully, and rate limits become a partnership discussion, not a technical limitation.