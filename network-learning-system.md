# Keeper Network Learning System

## Overview
Every customer makes every other customer smarter. Patterns discovered at one spa benefit all spas. This is our competitive moat.

## Core Principle
**Learn Once, Apply Everywhere**: When Customer 1 discovers a winning pattern, Customer 100 gets that insight on day one.

## Architecture

### Network Patterns Table
```sql
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
```

## Implementation

### Pattern Capture Agent
```python
class NetworkLearningAgent:
    """Captures and applies collective intelligence"""
    
    def capture_successful_pattern(self, account_id, insight, outcome):
        """When an action succeeds, learn from it"""
        
        # Anonymize but preserve the pattern
        pattern = {
            'type': insight['type'],
            'trigger_conditions': self.extract_conditions(insight),
            'action_taken': insight['action'],
            'script_used': insight.get('script'),
            'outcome_metrics': {
                'success': outcome['success'],
                'revenue_impact': outcome['revenue_impact'],
                'customer_retained': outcome.get('retained', False),
                'response_rate': outcome.get('response_rate')
            }
        }
        
        # Generate embedding for similarity matching
        pattern_text = f"""
        Pattern: {pattern['type']}
        Conditions: {pattern['trigger_conditions']}
        Action: {pattern['action_taken']}
        Result: {pattern['outcome_metrics']}
        """
        
        embedding = openai.embeddings.create(
            input=pattern_text,
            model="text-embedding-3-small"
        ).data[0].embedding
        
        # Store in network knowledge base
        existing = self.find_similar_pattern(embedding)
        
        if existing and existing['similarity'] > 0.95:
            # Update existing pattern
            self.update_pattern_success(existing['id'], outcome)
        else:
            # Create new pattern
            self.create_network_pattern(pattern, embedding)
    
    def apply_network_knowledge(self, account_id, new_insight):
        """Enhance insights with network intelligence"""
        
        # Search for similar successful patterns
        similar_patterns = self.search_patterns(
            new_insight,
            business_type=self.get_business_type(account_id),
            min_success_rate=0.60,
            min_occurrences=3
        )
        
        if similar_patterns:
            best_pattern = max(similar_patterns, key=lambda x: x['success_rate'])
            
            # Enhance the insight
            new_insight['network_enhanced'] = True
            new_insight['confidence'] *= (1 + best_pattern['success_rate'] * 0.3)
            new_insight['suggested_approach'] = best_pattern['action_template']
            new_insight['expected_success_rate'] = best_pattern['success_rate']
            new_insight['proven_script'] = best_pattern.get('best_script')
            
            # Add network context
            new_insight['network_context'] = (
                f"This approach worked {best_pattern['success_rate']*100:.0f}% "
                f"of the time across {best_pattern['occurrence_count']} similar cases"
            )
        
        return new_insight
```

### Pattern Types & Examples

#### 1. Churn Prevention Patterns
```python
CHURN_PATTERNS = {
    'break_in_pattern': {
        'trigger': 'customer.days_since_visit > customer.avg_frequency * 2',
        'success_approach': 'personalized_reminder_with_discount',
        'best_script': "Hi {name}, we noticed you haven't been in for your {favorite_service}. "
                      "Here's 20% off your next visit - we'd love to see you again!",
        'success_rate': 0.67,
        'learned_from': 47  # number of businesses
    },
    
    'high_value_at_risk': {
        'trigger': 'customer.ltv > 1000 AND customer.frequency_declining',
        'success_approach': 'owner_personal_call',
        'best_script': "Hi {name}, this is {owner_name}. I wanted to personally check in...",
        'success_rate': 0.78,
        'learned_from': 23
    }
}
```

#### 2. Modifier Opportunities
```python
MODIFIER_PATTERNS = {
    'morning_modifier_boost': {
        'discovery': 'Morning appointments have 3x modifier attach rate',
        'action': 'Pre-sell modifiers during booking for PM appointments',
        'implementation': 'Add modifier suggestions to booking confirmation',
        'revenue_impact': '+$1,800/month average',
        'adoption_rate': 0.84
    },
    
    'employee_coaching_needed': {
        'trigger': 'employee.modifier_rate < team_average * 0.5',
        'solution': 'Pair with top performer for 3 shifts',
        'outcome': '2.3x improvement in 30 days',
        'success_rate': 0.72
    }
}
```

#### 3. Review Response Patterns
```python
REVIEW_PATTERNS = {
    'negative_review_recovery': {
        'trigger': 'review.rating <= 2',
        'successful_response_template': 
            "Thank you for your feedback. I'm {owner_name}, the owner, and "
            "I'd like to personally address your concerns. Could we speak directly? "
            "Please email me at {email} or call {phone}.",
        'follow_up_action': 'Offer complimentary service after resolution',
        'recovery_rate': 0.61,
        'rating_improvement': '+2.3 stars average'
    }
}
```

## Network Intelligence Dashboard

### Metrics to Track
```python
class NetworkMetrics:
    def calculate_network_value(self):
        """Quantify value of collective learning"""
        
        metrics = {
            'patterns_discovered': count_unique_patterns(),
            'total_success_applications': count_successful_uses(),
            'revenue_generated_network': sum_network_assisted_revenue(),
            'average_confidence_boost': avg_confidence_increase(),
            'time_to_insight': avg_days_to_pattern_discovery(),
            'cross_pollination_rate': patterns_used_across_categories()
        }
        
        return metrics
    
    def identify_emerging_patterns(self):
        """Find new patterns forming across network"""
        
        # Look for similar insights appearing in multiple accounts
        emerging = []
        
        recent_insights = get_recent_insights(days=7)
        clusters = cluster_insights(recent_insights)
        
        for cluster in clusters:
            if cluster['size'] >= 3 and cluster['similarity'] > 0.85:
                emerging.append({
                    'pattern': cluster['common_pattern'],
                    'accounts_observing': cluster['size'],
                    'confidence': cluster['avg_confidence'],
                    'potential_value': cluster['total_impact']
                })
        
        return emerging
```

## Privacy & Anonymization

### Data Anonymization Rules
```python
def anonymize_pattern(pattern, account_id):
    """Remove all identifying information"""
    
    # Never store
    FORBIDDEN_FIELDS = [
        'customer_name',
        'customer_email', 
        'customer_phone',
        'business_name',
        'employee_names',
        'specific_addresses'
    ]
    
    # Replace with generic markers
    anonymized = deepcopy(pattern)
    
    # Replace names with roles
    anonymized = re.sub(r'Sarah Chen', '[high_value_customer]', anonymized)
    anonymized = re.sub(r'Jennifer', '[employee_1]', anonymized)
    
    # Replace specific amounts with ranges
    if pattern['dollar_value'] < 100:
        anonymized['value_range'] = 'low'
    elif pattern['dollar_value'] < 500:
        anonymized['value_range'] = 'medium'
    else:
        anonymized['value_range'] = 'high'
    
    # Hash any remaining identifiers
    for field in FORBIDDEN_FIELDS:
        if field in anonymized:
            del anonymized[field]
    
    return anonymized
```

## Network Effects Timeline

### Month 1-3: Foundation
- 10 customers = 100 patterns discovered
- Basic churn and modifier patterns established
- Initial success scripts validated

### Month 4-6: Acceleration  
- 50 customers = 1,000+ patterns
- Cross-category insights emerging (spa patterns work for salons)
- Confidence scores stabilizing at 80%+

### Month 7-12: Compounding Value
- 200 customers = 10,000+ patterns
- New customers get instant intelligence
- 90% of insights network-enhanced
- Average time-to-value: 24 hours vs 30 days

### Year 2+: Moat Established
- Patterns predict issues before they happen
- Network suggests proactive moves
- Competitors can't match accumulated intelligence
- Each new customer makes system 0.5% smarter

## Integration Points

### With Insight Engine
```python
# In insight-engine-dropset.md
class InsightTournament:
    def run_tournament(self, account_id):
        insights = self.generate_base_insights(account_id)
        
        # Enhance with network intelligence
        network_agent = NetworkLearningAgent()
        for insight in insights:
            insight = network_agent.apply_network_knowledge(
                account_id, 
                insight
            )
        
        return insights
```

### With Task Generation
```python
# In task generation
def generate_task_from_insight(insight):
    task = create_base_task(insight)
    
    if insight.get('network_enhanced'):
        task['confidence_label'] = 'Network Validated'
        task['success_probability'] = insight['expected_success_rate']
        
        if insight.get('proven_script'):
            task['script'] = insight['proven_script']
            task['script_note'] = f"This script works {insight['expected_success_rate']*100:.0f}% of the time"
    
    return task
```

## Success Metrics

### Network Health KPIs
- Pattern Discovery Rate: 10+ new patterns/week
- Cross-Application Rate: 60%+ patterns used by multiple accounts  
- Success Rate Improvement: 20%+ boost from network enhancement
- Time to First Insight: <24 hours for new customers
- Pattern Accuracy: 85%+ validation rate

### ROI Metrics
- Revenue per pattern: $500+ average
- Customer retention from network insights: 15% improvement
- New customer value acceleration: 3x faster to full value
- Competitive advantage: 6-month head start on any competitor

## The Network Advantage

**Without Network Learning**: Each business discovers patterns slowly through trial and error.

**With Network Learning**: Day 1 customers get insights that took months to discover.

This isn't just about sharing data - it's about compound learning where every success makes every future decision better. The network effect becomes Keeper's unfair advantage.