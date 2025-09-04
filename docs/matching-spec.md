# Keeper Identity Resolution & Matching Specification

## Core Principle
**97%+ accuracy or we're fucked.** One wrong match destroys trust. This system handles the messiest real-world data: name changes, typos, shared households, and the chaos of SMB record-keeping.

## The Identity Resolution Pipeline

### Multi-Signal Matching Algorithm
```python
class IdentityResolver:
    """
    Production-grade identity resolution that handles:
    - Name changes (marriage/divorce)
    - Typos and variations
    - Shared households
    - Employee records
    - Cross-source matching (Square + CSV + Reviews)
    """
    
    WEIGHTS = {
        'phone': 0.35,      # Most stable identifier
        'email': 0.30,      # Usually stable
        'address': 0.25,    # Household indicator
        'name': 0.10,       # Least reliable
        'behavior': 0.15    # Bonus for patterns (doesn't count against 100%)
    }
    
    THRESHOLDS = {
        'exact_match': 1.0,
        'auto_merge': 0.95,    # Automatic merge
        'manual_review': 0.85,  # Flag for review
        'no_match': 0.84        # Different people
    }
```

## Phase 1: Square Data Normalization

### Customer Identity Extraction
```python
def normalize_square_customer(raw_customer):
    """Extract and normalize Square customer data"""
    
    return {
        'id': raw_customer['id'],
        'name': normalize_name(raw_customer.get('given_name', '') + ' ' + 
                              raw_customer.get('family_name', '')),
        'phone': clean_phone(raw_customer.get('phone_number')),
        'email': normalize_email(raw_customer.get('email_address')),
        'address': normalize_address(raw_customer.get('address', {})),
        'created_at': raw_customer['created_at'],
        'last_visit': get_last_transaction_date(raw_customer['id']),
        'behavioral_signature': generate_behavioral_signature(raw_customer['id'])
    }

def clean_phone(phone):
    """Standardize phone numbers"""
    if not phone:
        return None
    
    # Remove all non-digits
    digits = re.sub(r'[^\d]', '', phone)
    
    # Handle country codes
    if len(digits) == 11 and digits[0] == '1':
        digits = digits[1:]  # Remove US country code
    
    if len(digits) == 10:
        return digits  # Standard US phone
    
    return None  # Invalid

def normalize_email(email):
    """Standardize emails"""
    if not email:
        return None
    
    email = email.lower().strip()
    
    # Handle common variations
    # sarah+spam@gmail.com -> sarah@gmail.com
    if '+' in email:
        local, domain = email.split('@')
        local = local.split('+')[0]
        email = f"{local}@{domain}"
    
    # Ignore dots in gmail
    if 'gmail.com' in email:
        local, domain = email.split('@')
        local = local.replace('.', '')
        email = f"{local}@{domain}"
    
    return email
```

## Phase 2: External File Matching

### Smart Column Detection
```python
def detect_column_mapping(columns):
    """Auto-detect what columns mean"""
    
    patterns = {
        'name': [
            r'name', r'customer', r'client', r'patient',
            r'first.*last', r'full.*name'
        ],
        'phone': [
            r'phone', r'mobile', r'cell', r'tel',
            r'contact.*number', r'ph'
        ],
        'email': [
            r'email', r'e-mail', r'mail', 
            r'contact.*email', r'email.*address'
        ],
        'address': [
            r'address', r'street', r'location',
            r'addr', r'residence'
        ],
        'notes': [
            r'note', r'comment', r'memo', r'remarks',
            r'special', r'info'
        ]
    }
    
    mapping = {}
    for col in columns:
        col_lower = col.lower().strip()
        for field, patterns_list in patterns.items():
            for pattern in patterns_list:
                if re.search(pattern, col_lower):
                    mapping[field] = col
                    break
    
    return mapping
```

### The Matching Engine
```python
def match_records(external_record, square_customers):
    """Core matching algorithm with name-change detection"""
    
    matches = []
    
    for square_customer in square_customers:
        # Calculate base score
        score = calculate_identity_score(external_record, square_customer)
        
        # Check for name change patterns
        if score > 0.7 and score < 0.95:
            if detect_name_change_pattern(external_record, square_customer):
                score *= 1.2  # Boost score for likely name change
        
        if score >= THRESHOLDS['manual_review']:
            matches.append({
                'square_customer': square_customer,
                'external_record': external_record,
                'score': score,
                'match_type': determine_match_type(score),
                'signals': get_matching_signals(external_record, square_customer)
            })
    
    return sorted(matches, key=lambda x: x['score'], reverse=True)

def calculate_identity_score(record_a, record_b):
    """Multi-factor identity scoring"""
    
    total_score = 0
    matched_signals = []
    
    # Phone matching (highest weight)
    if record_a.get('phone') and record_b.get('phone'):
        phone_score = phone_similarity(record_a['phone'], record_b['phone'])
        total_score += phone_score * WEIGHTS['phone']
        if phone_score > 0.9:
            matched_signals.append('phone')
    
    # Email matching
    if record_a.get('email') and record_b.get('email'):
        email_score = email_similarity(record_a['email'], record_b['email'])
        total_score += email_score * WEIGHTS['email']
        if email_score > 0.9:
            matched_signals.append('email')
    
    # Address matching
    if record_a.get('address') and record_b.get('address'):
        address_score = address_similarity(record_a['address'], record_b['address'])
        total_score += address_score * WEIGHTS['address']
        if address_score > 0.8:
            matched_signals.append('address')
    
    # Name matching (lowest weight due to changes)
    if record_a.get('name') and record_b.get('name'):
        name_score = name_similarity(record_a['name'], record_b['name'])
        total_score += name_score * WEIGHTS['name']
        if name_score > 0.8:
            matched_signals.append('name')
    
    # Behavioral bonus (doesn't count against total)
    if len(matched_signals) >= 2:
        behavior_score = check_behavioral_patterns(record_a, record_b)
        if behavior_score > 0.7:
            total_score += behavior_score * WEIGHTS['behavior']
            matched_signals.append('behavior')
    
    return min(total_score, 1.0)  # Cap at 1.0
```

## Phase 3: Name Change Detection

### Marriage/Divorce Pattern Recognition
```python
class NameChangeDetector:
    """Detect and handle name changes automatically"""
    
    def detect_name_change_pattern(self, old_record, new_record):
        """Identify likely name changes"""
        
        indicators = []
        
        # Last name changed but first name same
        old_first, old_last = split_name(old_record['name'])
        new_first, new_last = split_name(new_record['name'])
        
        if old_first == new_first and old_last != new_last:
            indicators.append('last_name_change')
        
        # Hyphenated name (marriage)
        if '-' in new_last and old_last in new_last:
            indicators.append('hyphenation')
        
        # Timeline analysis (one stopped, other started)
        if self.check_sequential_timeline(old_record, new_record):
            indicators.append('sequential_visits')
        
        # Same household members
        if self.check_household_connections(old_record, new_record):
            indicators.append('household_match')
        
        # Email prefix match (sarah.chen@ -> sarah.martinez@)
        if self.check_email_prefix_match(old_record, new_record):
            indicators.append('email_prefix')
        
        return len(indicators) >= 2
    
    def check_sequential_timeline(self, old, new):
        """Check if one record stopped when other started"""
        
        if not (old.get('last_visit') and new.get('created_at')):
            return False
        
        gap_days = (new['created_at'] - old['last_visit']).days
        
        # Stopped coming, then "new" customer appeared within 60 days
        return 0 <= gap_days <= 60
```

### Employee Name Change Handling
```python
def match_employee_records(square_employee, external_record):
    """Special handling for employee matching"""
    
    # Employees often have more stable identifiers
    employee_weights = {
        'employee_id': 0.40,   # Square employee ID
        'ssn_last4': 0.30,     # If available in external data
        'phone': 0.20,
        'address': 0.10
    }
    
    score = 0
    
    # Check employee-specific identifiers
    if external_record.get('employee_id') == square_employee.get('id'):
        score += employee_weights['employee_id']
    
    # Regular identity matching
    score += calculate_identity_score(external_record, square_employee) * 0.6
    
    return score
```

## Phase 4: Household Clustering

### Address-Based Grouping
```python
class HouseholdAnalyzer:
    """Group and analyze household patterns"""
    
    def create_household_clusters(self, customers):
        """Group customers by household"""
        
        households = defaultdict(list)
        
        for customer in customers:
            if customer.get('address'):
                # Create household key
                household_key = self.get_household_key(customer['address'])
                households[household_key].append(customer)
        
        # Analyze multi-person households
        insights = []
        for address, members in households.items():
            if len(members) > 1:
                insight = self.analyze_household(members)
                if insight:
                    insights.append(insight)
        
        return insights
    
    def analyze_household(self, members):
        """Generate insights for household"""
        
        total_value = sum(m.get('lifetime_value', 0) for m in members)
        active_members = [m for m in members if m.get('days_since_visit', 999) < 60]
        
        if len(active_members) < len(members):
            # Some household members stopped coming
            return {
                'type': 'household_churn_risk',
                'priority': 'high',
                'message': f"Household at {members[0]['address']} has "
                          f"{len(members) - len(active_members)} inactive members",
                'value_at_risk': total_value * 0.6,
                'action': 'Offer family package discount to reactivate'
            }
        
        return None
```

## Phase 5: Cross-Source Matching

### Review Platform Identity Resolution
```python
def match_review_to_customer(review, customers):
    """Match review authors to customer database"""
    
    # Reviews often have limited info
    review_name = review.get('author_name', '')
    review_date = review.get('date')
    
    candidates = []
    
    for customer in customers:
        score = 0
        
        # Name similarity (fuzzy due to platform variations)
        if review_name:
            name_score = fuzzy_name_match(review_name, customer['name'])
            score += name_score * 0.4
        
        # Timeline matching (reviewed after visit)
        if review_date and customer.get('last_visit'):
            days_diff = (review_date - customer['last_visit']).days
            if 0 <= days_diff <= 14:  # Review within 2 weeks
                score += 0.4
        
        # Service mentioned matching
        if check_service_match(review.get('text'), customer.get('services')):
            score += 0.2
        
        if score > 0.6:
            candidates.append((customer, score))
    
    return sorted(candidates, key=lambda x: x[1], reverse=True)
```

## Testing Strategy

### Real Data Validation
```python
def test_with_spa_data(spa_square_data, spa_csv_data):
    """Test matching accuracy with real spa data"""
    
    results = {
        'total_records': len(spa_csv_data),
        'exact_matches': 0,
        'fuzzy_matches': 0,
        'manual_review': 0,
        'no_matches': 0,
        'false_positives': 0,
        'false_negatives': 0
    }
    
    # Run matching
    for csv_record in spa_csv_data:
        matches = match_records(csv_record, spa_square_data)
        
        if matches:
            best_match = matches[0]
            if best_match['score'] >= THRESHOLDS['exact_match']:
                results['exact_matches'] += 1
            elif best_match['score'] >= THRESHOLDS['auto_merge']:
                results['fuzzy_matches'] += 1
            elif best_match['score'] >= THRESHOLDS['manual_review']:
                results['manual_review'] += 1
        else:
            results['no_matches'] += 1
    
    # Calculate accuracy
    accuracy = (results['exact_matches'] + results['fuzzy_matches']) / results['total_records']
    
    print(f"Matching Accuracy: {accuracy:.2%}")
    print(f"Require Manual Review: {results['manual_review']}")
    
    # Must achieve 97%+ accuracy
    assert accuracy >= 0.97, f"Accuracy {accuracy:.2%} below 97% threshold"
    
    return results
```

### Edge Case Testing
```python
test_cases = [
    {
        'name': 'Marriage name change',
        'square': {'name': 'Sarah Chen', 'phone': '555-1234', 'email': 'sarah@gmail.com'},
        'csv': {'name': 'Sarah Martinez', 'phone': '555-1234', 'email': 'sarah@gmail.com'},
        'expected_score': 0.95
    },
    {
        'name': 'Hyphenated name',
        'square': {'name': 'Jennifer Park', 'phone': '555-5678'},
        'csv': {'name': 'Jennifer Park-Kim', 'phone': '555-5678'},
        'expected_score': 0.93
    },
    {
        'name': 'Same household different person',
        'square': {'name': 'John Smith', 'address': '123 Main St'},
        'csv': {'name': 'Jane Smith', 'address': '123 Main St'},
        'expected_score': 0.45  # Should NOT match
    },
    {
        'name': 'Typo in name',
        'square': {'name': 'Catherine Johnson', 'phone': '555-9999'},
        'csv': {'name': 'Katherine Johnson', 'phone': '555-9999'},
        'expected_score': 0.92
    },
    {
        'name': 'Nickname variation',
        'square': {'name': 'Robert Williams', 'email': 'bob@email.com'},
        'csv': {'name': 'Bob Williams', 'email': 'bob@email.com'},
        'expected_score': 0.94
    }
]
```

## Performance Requirements

```yaml
Accuracy Targets:
  Overall: 97%+
  Phone matching: 99%+
  Email matching: 98%+
  Address matching: 95%+
  Name matching: 85%+ (due to variations)
  
Performance Targets:
  Single record match: <50ms
  1000 record batch: <60 seconds
  Full customer base (10,000): <10 minutes
  Daily incremental: <2 minutes
  
Memory Usage:
  Max RAM: 2GB for 100,000 records
  Caching: Redis for computed scores
  
Error Handling:
  Retry failed matches: 3 attempts
  Log all <95% confidence matches
  Alert on accuracy drop below 97%
```

## Integration Points

### With Square Sync Agent
```python
@celery.task
def post_square_sync_matching(account_id):
    """Run after daily Square sync"""
    
    # Get new Square records
    new_customers = get_new_square_customers(account_id)
    
    # Match against existing database
    for customer in new_customers:
        existing_matches = find_existing_matches(customer)
        
        if existing_matches:
            handle_potential_duplicate(customer, existing_matches)
        else:
            create_new_customer_record(customer)
```

### With Task Generation
```python
def generate_matching_tasks(account_id):
    """Create tasks for manual review"""
    
    pending_matches = get_pending_manual_matches(account_id)
    
    tasks = []
    for match in pending_matches:
        task = {
            'type': 'review_duplicate',
            'priority': 'low' if match['score'] < 0.90 else 'medium',
            'title': f'Review Possible Duplicate: {match["name"]}',
            'details': format_match_comparison(match),
            'actions': ['merge', 'keep_separate', 'investigate']
        }
        tasks.append(task)
    
    return tasks
```

## Monitoring & Alerts

```python
@monitoring.track
def matching_health_check():
    """Monitor matching system health"""
    
    metrics = {
        'daily_accuracy': calculate_daily_accuracy(),
        'pending_reviews': count_pending_reviews(),
        'false_positive_rate': calculate_false_positive_rate(),
        'avg_match_time': get_average_match_time(),
        'name_change_detections': count_name_changes_found()
    }
    
    # Alert if accuracy drops
    if metrics['daily_accuracy'] < 0.97:
        alert_team(f"Matching accuracy dropped to {metrics['daily_accuracy']:.2%}")
    
    return metrics
```

## The Bottom Line

This matching system is the foundation of trust in Keeper. Every insight, every task, every report depends on correctly identifying who is who. Get this wrong and nothing else matters.

**Key innovations:**
- Multi-signal scoring that survives name changes
- Household clustering for family insights  
- Behavioral pattern matching as backup
- Automatic name-change detection
- Cross-source identity resolution

**Remember:** We're not just matching names - we're tracking identities through all the chaos of real life.