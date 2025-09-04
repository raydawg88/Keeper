# Keeper Context Engineering System

## Overview
Context is everything. The difference between generic and valuable insights is context depth plus network intelligence.

## Context Layers (Enhanced with Network Learning)

### Layer 1: Square Data Context
```python
def build_square_context(customer_id):
    """Core transactional context"""
    
    customer = get_customer(customer_id)
    
    context = {
        'identity': {
            'name': customer['name'],
            'email': customer['email'],
            'phone': customer['phone'],
            'customer_since': customer['created_at']
        },
        'behavior': {
            'lifetime_value': customer['ltv'],
            'visit_frequency': customer['avg_days_between_visits'],
            'last_visit': customer['last_seen'],
            'days_since_visit': (datetime.now() - customer['last_seen']).days,
            'favorite_service': customer['top_service'],
            'favorite_employee': customer['preferred_employee'],
            'average_spend': customer['avg_transaction']
        },
        'modifiers': {
            'usually_buys': customer['common_modifiers'],
            'never_buys': customer['never_purchased_modifiers'],
            'last_purchased': customer['recent_modifiers']
        },
        'risk_indicators': {
            'is_churning': customer['days_since_visit'] > customer['avg_days_between_visits'] * 2,
            'declining_spend': customer['recent_avg_spend'] < customer['lifetime_avg_spend'] * 0.7,
            'stopped_modifiers': customer['modifier_decline']
        }
    }
    
    return context
```

### Layer 2: Network Pattern Context
```python
def build_network_context(customer_id, insight_type):
    """Collective intelligence from network patterns"""
    
    customer = get_customer(customer_id)
    business_category = get_business_category(customer['account_id'])
    
    # Create insight signature for pattern matching
    insight_signature = {
        'type': insight_type,
        'customer_segment': classify_customer_segment(customer),
        'business_context': {
            'category': business_category,
            'ltv_range': categorize_ltv(customer['ltv']),
            'frequency_pattern': categorize_frequency(customer['visit_pattern']),
            'risk_level': assess_risk_level(customer)
        }
    }
    
    # Search for similar successful patterns
    similar_patterns = search_network_patterns(
        insight_signature,
        min_success_rate=0.60,
        min_occurrences=3
    )
    
    network_context = {}
    if similar_patterns:
        best_pattern = max(similar_patterns, key=lambda x: x['success_rate'])
        
        network_context = {
            'proven_approach': best_pattern['action_template'],
            'success_rate': best_pattern['success_rate'],
            'similar_cases': best_pattern['occurrence_count'],
            'best_script': best_pattern.get('proven_script'),
            'network_confidence': best_pattern['confidence_score'],
            'context_note': f"This approach worked {best_pattern['success_rate']*100:.0f}% "
                           f"of the time across {best_pattern['occurrence_count']} similar businesses",
            'last_validated': best_pattern['last_validated'],
            'pattern_evolution': track_pattern_evolution(best_pattern['id'])
        }
    
    return network_context
```

### Layer 3: External File Context
```python
def build_external_context(customer_id):
    """Private knowledge from uploads"""
    
    external = get_external_data(customer_id)
    
    context = {
        'personal': {
            'life_events': extract_life_events(external['notes']),  # divorce, illness, job loss
            'preferences': external.get('preferences'),
            'complaints': external.get('complaints'),
            'special_needs': external.get('allergies', 'conditions')
        },
        'relationships': {
            'referred_by': external.get('referrer'),
            'refers': external.get('referred_others'),
            'comes_with': external.get('companion')  # spouse, friend
        },
        'communication': {
            'prefers_channel': external.get('contact_preference'),  # text, call, email
            'best_time': external.get('contact_time'),
            'language': external.get('language', 'English')
        }
    }
    
    return context
```

### Layer 3: Review Context
```python
def build_review_context(customer_id):
    """What they're saying publicly"""
    
    reviews = get_customer_reviews(customer_id)
    
    context = {
        'sentiment': {
            'overall': calculate_sentiment_score(reviews),
            'trending': 'improving' if recent_sentiment > old_sentiment else 'declining',
            'last_review': reviews[0] if reviews else None
        },
        'mentions': {
            'employees': extract_employee_mentions(reviews),
            'services': extract_service_mentions(reviews),
            'competitors': extract_competitor_mentions(reviews)
        },
        'issues': extract_complaints(reviews)
    }
    
    return context
```

### Layer 4: Environmental Context
```python
def build_environmental_context(account_id):
    """Business environment factors"""
    
    context = {
        'temporal': {
            'day_of_week': datetime.now().strftime('%A'),
            'time_of_day': 'morning' if datetime.now().hour < 12 else 'afternoon',
            'season': get_current_season(),
            'holidays': get_upcoming_holidays()
        },
        'competition': {
            'new_competitors': get_new_competitors_nearby(account_id),
            'competitor_promotions': scrape_competitor_offers(account_id)
        },
        'performance': {
            'business_trend': 'growing' if revenue_trend > 0 else 'declining',
            'busy_level': calculate_capacity_usage(account_id)
        }
    }
    
    return context
```

## RAG Implementation

### Embedding Generation
```python
def generate_customer_embedding(customer_id):
    """Create searchable vector for customer"""
    
    # Gather all context layers
    square = build_square_context(customer_id)
    external = build_external_context(customer_id)
    reviews = build_review_context(customer_id)
    
    # Create narrative document
    document = f"""
    Customer Profile: {square['identity']['name']}
    
    Financial Value:
    - Lifetime value: ${square['behavior']['lifetime_value']}
    - Monthly value: ${square['behavior']['lifetime_value'] / months_active}
    - Average transaction: ${square['behavior']['average_spend']}
    
    Behavioral Pattern:
    - Visits every {square['behavior']['visit_frequency']} days
    - Last visit: {square['behavior']['last_visit']} ({square['behavior']['days_since_visit']} days ago)
    - Favorite service: {square['behavior']['favorite_service']}
    - Preferred staff: {square['behavior']['favorite_employee']}
    
    Modifier Behavior:
    - Usually adds: {', '.join(square['modifiers']['usually_buys'])}
    - Never purchases: {', '.join(square['modifiers']['never_buys'])}
    
    Personal Context:
    {external['personal']['life_events']}
    {external['personal']['special_needs']}
    
    Risk Status:
    - Churn risk: {'HIGH' if square['risk_indicators']['is_churning'] else 'LOW'}
    - Spending trend: {'DECLINING' if square['risk_indicators']['declining_spend'] else 'STABLE'}
    
    Review Sentiment:
    {reviews['sentiment']['overall']} - {reviews['sentiment']['trending']}
    Issues: {', '.join(reviews['issues'])}
    """
    
    # Generate embedding
    embedding = openai.embeddings.create(
        input=document,
        model="text-embedding-3-small"
    )
    
    # Store with metadata
    supabase.table('customer_embeddings').upsert({
        'customer_id': customer_id,
        'embedding': embedding.data[0].embedding,
        'document': document,
        'metadata': {
            'ltv': square['behavior']['lifetime_value'],
            'risk_score': calculate_risk_score(square),
            'days_since_visit': square['behavior']['days_since_visit']
        },
        'updated_at': datetime.now()
    })
```

### Context Retrieval
```python
def retrieve_context_for_task(task_type, customer_id=None, **filters):
    """Get relevant context for task generation"""
    
    if task_type == 'churn_prevention':
        # Get similar churned customers who were saved
        similar = vector_similarity_search(
            customer_id,
            filter={'saved': True, 'was_churning': True},
            limit=5
        )
        
        context = {
            'customer': get_full_context(customer_id),
            'successful_saves': similar,
            'best_approaches': extract_winning_strategies(similar)
        }
    
    elif task_type == 'employee_coaching':
        employee = filters['employee_id']
        
        context = {
            'employee_metrics': get_employee_metrics(employee),
            'top_performer_metrics': get_top_performer_metrics(),
            'specific_gaps': identify_performance_gaps(employee),
            'customer_feedback': get_employee_reviews(employee)
        }
    
    elif task_type == 'modifier_upsell':
        context = {
            'customer': get_full_context(customer_id),
            'never_tried': get_untried_modifiers(customer_id),
            'similar_customers_buy': get_peer_modifier_patterns(customer_id),
            'high_margin_options': get_best_margin_modifiers()
        }
    
    return context
```

## Prompt Engineering

### Task Generation Prompts
```python
TASK_PROMPT_TEMPLATE = """
You are a business advisor for a {business_type}. Generate a specific, actionable task based on this context:

Customer: {customer_name}
Lifetime Value: ${ltv}
Risk: {risk_level}
Pattern: {pattern_description}

{additional_context}

Generate a task with:
1. Specific action (call, email, text)
2. Exact script or message
3. Best timing
4. Expected outcome

The script should be:
- Personal (use their history)
- Natural (not salesy)
- Specific (mention exact services/products)
- Valuable (clear benefit to customer)

Format:
Action: [CALL/EMAIL/TEXT]
When: [SPECIFIC TIME]
Script: [EXACT WORDS]
Expected Result: [CUSTOMER ACTION]
Value: $[AMOUNT]
"""

def generate_task_with_context(insight, context):
    """Create task using full context"""
    
    prompt = TASK_PROMPT_TEMPLATE.format(
        business_type=context['business']['type'],
        customer_name=context['customer']['name'],
        ltv=context['customer']['ltv'],
        risk_level='HIGH' if context['customer']['is_churning'] else 'NORMAL',
        pattern_description=insight['pattern'],
        additional_context=format_relevant_context(context)
    )
    
    response = claude.generate(
        prompt=prompt,
        model='claude-3-haiku',
        temperature=0.3  # Lower temperature for consistency
    )
    
    return parse_task_response(response)
```

### Report Generation Prompts
```python
WEEKLY_REPORT_TEMPLATE = """
You are a McKinsey consultant analyzing a {business_type}'s weekly performance.

This Week's Data:
- Revenue: ${revenue} ({revenue_change}% vs last week)
- Customers Served: {customer_count}
- New Customers: {new_customers}
- Lost Customers: {churned_customers}
- Task Completion: {tasks_completed}/{tasks_created}

Key Insights Found:
{insights}

Employee Performance:
{employee_metrics}

Write an executive summary that:
1. Starts with the most important finding
2. Explains what's driving changes
3. Identifies hidden opportunities
4. Recommends 3 specific actions for next week
5. Quantifies the impact of recommendations

Use clear, confident language. No hedging. Be specific with names and numbers.
"""
```

## Context Freshness

### Update Triggers
```python
CONTEXT_UPDATE_TRIGGERS = {
    'transaction': update_transaction_context,
    'appointment': update_appointment_context,
    'review': update_review_context,
    'external_upload': regenerate_full_context,
    'day_boundary': update_temporal_context
}

@celery.task
def maintain_context_freshness(account_id):
    """Keep context current"""
    
    stale_customers = supabase.table('customer_embeddings')\
        .select('customer_id')\
        .lt('updated_at', datetime.now() - timedelta(days=7))\
        .execute()
    
    for customer in stale_customers.data:
        generate_customer_embedding(customer['customer_id'])
```

## Testing Context Quality

```python
def test_context_completeness():
    """Ensure context captures all important data"""
    
    test_customer = create_test_customer()
    context = build_full_context(test_customer['id'])
    
    # Should include all layers
    assert 'identity' in context
    assert 'behavior' in context
    assert 'personal' in context
    assert 'risk_indicators' in context
    
    # Should have specific fields
    assert context['behavior']['lifetime_value'] > 0
    assert context['behavior']['visit_frequency'] > 0
    
    # Should handle missing data gracefully
    assert context.get('personal', {}).get('life_events') is not None

def test_prompt_generation():
    """Ensure prompts use context effectively"""
    
    context = build_test_context()
    prompt = generate_task_prompt(context)
    
    # Should include specific details
    assert context['customer']['name'] in prompt
    assert str(context['customer']['ltv']) in prompt
    assert context['customer']['favorite_service'] in prompt
    
    # Should not include generic language
    assert 'valued customer' not in prompt
    assert 'great offer' not in prompt
```