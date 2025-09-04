# Keeper Testing Protocol - BMAD Implementation

## Core Testing Philosophy
Build → Measure → Analyze → Deploy (BMAD)
- Build small increments
- Measure with real data
- Analyze actual results
- Deploy only when verified

## Test Data Setup

### Use Real Spa Data
```bash
# Export from Square Dashboard
1. Login to Square Dashboard
2. Export last 12 months:
   - Customers (all fields)
   - Transactions (with modifiers)
   - Appointments (with staff)
   - Products/Services catalog
   - Staff members
3. Save as CSV files in `/test-data/`
```

### Required Test Files
```
test-data/
├── square-customers.csv      # Real customer data
├── square-transactions.csv   # Real payments
├── square-appointments.csv   # Real bookings
├── customer-notes.csv        # Your wife's notes
├── no-show-tracker.xlsx      # No-show history
└── staff-schedule.csv        # Employee schedules
```

## Phase 0: Network Learning Foundation (Days 1-2)

### Test 0.1: Network Pattern Storage
```python
def test_network_pattern_storage():
    """Verify network patterns store and retrieve correctly"""
    
    # Test pattern creation
    test_pattern = {
        'type': 'churn_prevention',
        'business_category': 'spa',
        'trigger_conditions': {'days_since_visit': 45, 'ltv': '>1000'},
        'action_template': 'Personal call with 20% discount',
        'outcome': {'success': True, 'revenue_impact': 1200}
    }
    
    # Action
    pattern_id = store_network_pattern(test_pattern)
    
    # Measure
    assert pattern_id is not None
    stored_pattern = get_network_pattern(pattern_id)
    assert stored_pattern['success_rate'] == 1.0  # First occurrence
    assert stored_pattern['occurrence_count'] == 1
    
    print("✓ Network pattern storage working")
```

### Test 0.2: Pattern Similarity Search
```python
def test_pattern_similarity():
    """Verify similar patterns are found correctly"""
    
    # Create test patterns
    patterns = [
        create_test_pattern('churn_prevention', 'spa', 0.78),
        create_test_pattern('churn_prevention', 'spa', 0.82),
        create_test_pattern('modifier_opportunity', 'spa', 0.65)
    ]
    
    # Search for similar churn prevention patterns
    query = {
        'type': 'churn_prevention',
        'business_category': 'spa'
    }
    
    # Action
    similar = search_similar_patterns(query, min_success_rate=0.70)
    
    # Measure
    assert len(similar) == 2  # Should find 2 churn patterns above 70%
    assert all(p['success_rate'] >= 0.70 for p in similar)
    
    print("✓ Pattern similarity search working")
```

### Test 0.3: Network Enhancement Integration
```python
def test_network_enhancement():
    """Verify insights get enhanced with network intelligence"""
    
    # Create base insight
    base_insight = {
        'type': 'churn_risk',
        'customer_id': 'test_customer',
        'confidence': 0.75,
        'dollar_impact': 1500
    }
    
    # Action
    enhanced_insight = apply_network_enhancement(base_insight)
    
    # Measure
    if enhanced_insight.get('network_enhanced'):
        assert enhanced_insight['confidence'] > 0.75  # Should boost confidence
        assert 'proven_approach' in enhanced_insight
        assert 'network_context' in enhanced_insight
        print("✓ Network enhancement boosted insight confidence")
    else:
        print("ℹ No network patterns found (expected for new system)")
```

## Phase 1: Data Pipeline Testing (Days 3-9)

### Test 1.1: Square OAuth Flow
```python
def test_square_oauth():
    """Verify OAuth completes successfully"""
    
    # Action
    response = initiate_square_oauth()
    
    # Measure
    assert response.status_code == 200
    assert 'access_token' in response.json()
    assert 'merchant_id' in response.json()
    
    # Verify token storage
    stored_token = get_stored_token(test_account_id)
    assert stored_token is not None
    assert decrypt(stored_token) == response.json()['access_token']
    
    # Success: OAuth token obtained and stored
```

### Test 1.2: Historical Data Import
```python
def test_historical_import():
    """Import 12 months of real data"""
    
    # Action
    start_time = time.time()
    result = import_historical_data(test_account_id, months=12)
    import_time = time.time() - start_time
    
    # Measure
    assert import_time < 600  # Under 10 minutes
    
    # Verify counts match Square
    assert result['customers_imported'] >= 200  # Your spa has ~300
    assert result['transactions_imported'] >= 2000
    assert result['appointments_imported'] >= 1500
    
    # Spot check specific customer
    sarah_chen = get_customer_by_name('Sarah Chen')
    assert sarah_chen is not None
    assert sarah_chen['lifetime_value'] > 0
    assert sarah_chen['visit_count'] > 0
```

### Test 1.3: Daily Sync
```python
def test_daily_sync():
    """Verify incremental sync works"""
    
    # Setup: Add new transaction in Square Sandbox
    new_payment = create_test_payment_in_square()
    
    # Action
    sync_result = daily_square_sync(test_account_id)
    
    # Measure
    assert new_payment['id'] in sync_result['new_payments']
    assert sync_result['sync_time'] < 120  # Under 2 minutes
    
    # Verify no duplicates
    payment_count = count_payments(new_payment['id'])
    assert payment_count == 1
```

## Phase 2: Fuzzy Matching Testing (Days 10-16)

### Test 2.1: Customer Matching Accuracy
```python
def test_fuzzy_matching():
    """Test with real customer notes file"""
    
    # Setup
    square_customers = get_all_customers(test_account_id)
    external_file = pd.read_csv('test-data/customer-notes.csv')
    
    # Action
    matches = match_external_data(
        test_account_id,
        external_file,
        column_mapping={'name': 'Customer Name', 'notes': 'Notes'}
    )
    
    # Measure
    assert matches['match_rate'] >= 0.97  # 97%+ accuracy
    
    # Verify specific matches
    test_cases = [
        ('Sara Chen', 'Sarah Chen'),  # Spelling variation
        ('Jennifer Park', 'Jennifer Park'),  # Exact match
        ('Maria Rodriguez', 'Maria Rodriguez')  # Exact match
    ]
    
    for external_name, square_name in test_cases:
        match = find_match(external_name)
        assert match['square_name'] == square_name
        assert match['confidence'] >= 0.85
```

### Test 2.2: Context Merge
```python
def test_context_merge():
    """Verify external data merges correctly"""
    
    # Setup: Customer with note "husband has cancer"
    customer = get_customer_by_name('Lisa Thompson')
    
    # Action
    merge_external_context(customer['id'], {
        'note': 'Husband diagnosed with cancer, be gentle',
        'preferences': 'Quiet room, no small talk'
    })
    
    # Measure
    updated = get_customer(customer['id'])
    assert 'cancer' in updated['metadata']['external_notes']
    assert updated['metadata']['preferences'] == 'Quiet room, no small talk'
    
    # Verify context affects task priority
    task = generate_task_for_customer(customer['id'])
    assert task['has_human_context'] == True
    assert task['priority_boost'] == True
```

## Phase 3: Insight Generation Testing (Days 15-21)

### Test 3.1: Insight Quality
```python
def test_insight_quality():
    """Ensure insights meet quality standards"""
    
    # Action
    insights = run_analysis_tournament(test_account_id)
    
    # Measure - Quantity
    assert len(insights) >= 5  # Minimum 5 insights
    
    # Measure - Quality
    for insight in insights:
        # Has required fields
        assert insight['pattern'] is not None
        assert insight['action'] is not None
        assert insight['dollar_impact'] > 0
        assert insight['confidence'] >= 0.75
        
        # Not obvious
        assert 'rain' not in insight['pattern'].lower()
        assert 'weekend' not in insight['pattern'].lower()
        assert 'busy' not in insight['pattern'].lower()
        
        # Specific, not generic
        assert any([
            'Sarah' in insight['pattern'],
            'Jennifer' in insight['pattern'],
            '%' in insight['pattern'],
            '$' in insight['pattern']
        ])
```

### Test 3.2: Modifier Analysis
```python
def test_modifier_insights():
    """Test modifier opportunity detection"""
    
    # Action
    modifier_insights = ModifierAnalyzer().analyze(test_account_id)
    
    # Measure
    assert len(modifier_insights) > 0
    
    # Verify specific pattern (from your data)
    jennifer_insight = find_insight_about('Jennifer', modifier_insights)
    assert jennifer_insight is not None
    assert 'modifier' in jennifer_insight['pattern'].lower()
    assert jennifer_insight['dollar_impact'] >= 1000  # Significant opportunity
```

### Test 3.3: Employee Performance
```python
def test_employee_analysis():
    """Test employee performance insights"""
    
    # Action
    employee_insights = EmployeeAnalyzer().analyze(test_account_id)
    
    # Measure
    for insight in employee_insights:
        # Must compare to team average
        assert 'average' in insight['pattern'] or '%' in insight['pattern']
        
        # Must have actionable recommendation
        assert any([
            'train' in insight['action'],
            'shadow' in insight['action'],
            'review' in insight['action']
        ])
        
        # Must quantify impact
        assert insight['dollar_impact'] > 0
```

## Phase 4: Task Generation Testing (Days 22-28)

### Test 4.1: Task Specificity
```python
def test_task_generation():
    """Ensure tasks are specific and actionable"""
    
    # Setup
    churn_insight = {
        'type': 'churn_risk',
        'customer_id': 'sarah_chen_id',
        'pattern': 'Sarah Chen hasn't visited in 47 days',
        'dollar_impact': 400
    }
    
    # Action
    task = generate_task_from_insight(churn_insight)
    
    # Measure
    assert task['customer_name'] == 'Sarah Chen'
    assert task['dollar_value'] == 400
    assert len(task['action_script']) > 50  # Detailed script
    assert 'dermaplaning' in task['action_script']  # Her favorite service
    assert task['expires_at'] == datetime.now() + timedelta(days=7)
```

### Test 4.2: Task Priority
```python
def test_task_prioritization():
    """Verify tasks are correctly prioritized"""
    
    # Action
    tasks = generate_all_tasks(test_account_id)
    urgent_tasks = [t for t in tasks if t['priority'] == 1]
    
    # Measure
    # Urgent tasks should have high dollar value or time sensitivity
    for task in urgent_tasks:
        assert task['dollar_value'] >= 300 or 'today' in task['action']
    
    # Human context should boost priority
    lisa_task = find_task_for('Lisa Thompson', tasks)
    assert lisa_task['priority'] == 1  # Boosted due to cancer note
```

## Phase 5: Integration Testing (Week 4)

### Test 5.1: End-to-End Flow
```python
def test_complete_flow():
    """Test entire pipeline with real data"""
    
    # 1. Import data
    import_result = import_historical_data(test_account_id)
    assert import_result['success'] == True
    
    # 2. Upload external file
    upload_result = upload_customer_notes('test-data/customer-notes.csv')
    assert upload_result['match_rate'] >= 0.97
    
    # 3. Run analysis
    insights = run_analysis_tournament(test_account_id)
    assert len(insights) >= 5
    
    # 4. Generate tasks
    tasks = generate_tasks_from_insights(insights)
    assert len(tasks) >= 5
    
    # 5. Create report
    report = generate_daily_report(test_account_id)
    assert 'Sarah Chen' in report  # Specific customer mentioned
    assert '$' in report  # Dollar values included
```

### Test 5.2: Performance Testing
```python
def test_system_performance():
    """Ensure system meets performance targets"""
    
    metrics = {
        'oauth_complete': measure_time(complete_oauth_flow),
        'import_12_months': measure_time(import_historical_data),
        'daily_sync': measure_time(daily_square_sync),
        'fuzzy_match_1000': measure_time(match_1000_customers),
        'generate_insights': measure_time(run_analysis_tournament),
        'generate_report': measure_time(generate_weekly_report)
    }
    
    # Performance requirements
    assert metrics['oauth_complete'] < 30  # seconds
    assert metrics['import_12_months'] < 600  # 10 minutes
    assert metrics['daily_sync'] < 120  # 2 minutes
    assert metrics['fuzzy_match_1000'] < 60  # 1 minute
    assert metrics['generate_insights'] < 30  # seconds
    assert metrics['generate_report'] < 10  # seconds
```

## Success Criteria

### Week 1: Data Pipeline ✓
- [ ] Square OAuth working
- [ ] 12 months data imported
- [ ] Daily sync operational
- [ ] No duplicate records
- [ ] 100% data accuracy

### Week 2: Intelligence Layer ✓
- [ ] 97%+ fuzzy matching
- [ ] 5+ insights generated
- [ ] No obvious insights
- [ ] All insights have dollar values
- [ ] 75%+ confidence on all insights

### Week 3: Task System ✓
- [ ] Tasks use real names
- [ ] Tasks have specific scripts
- [ ] Tasks expire after 7 days
- [ ] Priority reflects value + urgency
- [ ] Human context affects priority

### Week 4: Production Ready ✓
- [ ] All tests passing
- [ ] Performance targets met
- [ ] Your wife's spa connected
- [ ] 3 documented wins
- [ ] Ready for first paying customer

## Test Execution Schedule

### Daily Testing Routine
```bash
# Morning (9 AM)
npm run test:square-sync
npm run test:new-insights

# Afternoon (2 PM)
npm run test:task-generation
npm run test:report-generation

# Evening (6 PM)
npm run test:full-suite
npm run test:performance
```

### Continuous Monitoring
```python
# Monitor production metrics
PRODUCTION_MONITORS = {
    'sync_success_rate': lambda: rate > 0.999,
    'insight_accuracy': lambda: accuracy > 0.75,
    'task_completion_rate': lambda: rate > 0.30,
    'customer_satisfaction': lambda: nps > 50
}
```

## Rollback Criteria

If any of these occur, rollback immediately:
1. Data accuracy drops below 95%
2. False insights exceed 25%
3. Sync failures exceed 1%
4. Page load exceeds 3 seconds
5. Customer complains about incorrect data

## Testing Notes

### Real Data Advantages
- Actual patterns emerge
- Edge cases discovered
- True value demonstrated
- Wife becomes first testimonial

### Privacy Considerations
- Keep production data secure
- Don't commit real names to git
- Use data only for testing
- Delete test data after launch

### Success Metrics
- Find $3,000+ in opportunities
- Identify 10+ at-risk customers
- Discover 5+ employee improvements
- Generate 20+ actionable tasks
- All with your spa's real data