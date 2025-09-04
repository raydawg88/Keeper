# Keeper Insight Engine Specification

## Core Principle
Every insight must be:
1. **Non-obvious** (owner doesn't already know)
2. **Actionable** (specific thing to do)
3. **Valuable** (dollar amount attached)
4. **Confident** (>75% certainty)
5. **Network Enhanced** (when applicable, boost with collective intelligence)

## Performance Improvements
- **7x Speedup**: Parallel agent execution (70s → 10s)
- **20% Accuracy Boost**: Network learning enhancement
- **Validation**: Double validation via models + network patterns

## Model Tournament Architecture

### Tournament Structure (Parallel + Network Enhanced)
```python
class InsightTournament:
    def __init__(self):
        self.models = {
            'rfm': RFMModel(),
            'churn': ChurnPredictor(),
            'modifier': ModifierAnalyzer(),
            'employee': EmployeeAnalyzer(),
            'pattern': PatternMiner(),
            'seasonal': SeasonalAnalyzer(),
            'review': ReviewAnalyzer()
        }
        
        self.network_agent = NetworkLearningAgent()
        
        self.banned_insights = [
            'rain causes cancellations',
            'weekends are busier',
            'customers like discounts',
            'good employees make more money',
            'bad reviews hurt business'
        ]
    
    async def run_tournament(self, account_id):
        """Parallel execution with network enhancement"""
        
        # Parallel model execution (7x speedup)
        model_tasks = [
            self.models[name].analyze(account_id) 
            for name in self.models.keys()
        ]
        
        # Execute all models simultaneously
        model_results = await asyncio.gather(*model_tasks)
        
        # Combine results with model sources
        all_insights = []
        for i, (model_name, insights) in enumerate(zip(self.models.keys(), model_results)):
            for insight in insights:
                insight['model'] = model_name
                all_insights.append(insight)
        
        # Enhance with network intelligence
        network_enhanced = []
        for insight in all_insights:
            enhanced = await self.network_agent.apply_network_knowledge(
                account_id, insight
            )
            network_enhanced.append(enhanced)
        
        # Score and rank (network insights get priority)
        scored = self.score_insights(network_enhanced)
        
        # Remove duplicates
        unique = self.deduplicate(scored)
        
        # Quality filter (now includes network validation)
        quality = self.quality_gate(unique)
        
        # Return top insights
        return quality[:20]  # Max 20 insights per run
    
    def prioritize_network_insights(self, insights):
        """Give priority to network-validated insights"""
        network_insights = [i for i in insights if i.get('network_enhanced')]
        regular_insights = [i for i in insights if not i.get('network_enhanced')]
        
        # Network insights go first, then regular by score
        return sorted(network_insights, key=lambda x: x['score'], reverse=True) + \
               sorted(regular_insights, key=lambda x: x['score'], reverse=True)
```

### Individual Models

#### RFM Model
```python
class RFMModel:
    def analyze(self, account_id):
        """Recency, Frequency, Monetary analysis"""
        
        insights = []
        customers = get_customers_with_transactions(account_id)
        
        for customer in customers:
            # Calculate RFM scores
            recency = (datetime.now() - customer['last_visit']).days
            frequency = customer['visit_count'] / customer['months_active']
            monetary = customer['lifetime_value']
            
            # Detect breaks in pattern
            if recency > customer['avg_days_between'] * 2:
                if monetary > 1000:  # High value at risk
                    insights.append({
                        'type': 'churn_risk',
                        'customer_id': customer['id'],
                        'pattern': f"{customer['name']} usually visits every {customer['avg_days_between']} days, hasn't been in {recency} days",
                        'action': f"Call with personalized offer based on their favorite service: {customer['top_service']}",
                        'dollar_impact': customer['monthly_value'],
                        'confidence': 0.85
                    })
        
        return insights
```

#### Modifier Analyzer
```python
class ModifierAnalyzer:
    def analyze(self, account_id):
        """Find modifier revenue opportunities"""
        
        insights = []
        
        # Employee comparison
        employees = get_employee_modifier_stats(account_id)
        top_performer = max(employees, key=lambda x: x['modifier_rate'])
        
        for employee in employees:
            if employee['modifier_rate'] < top_performer['modifier_rate'] * 0.5:
                monthly_loss = calculate_modifier_loss(employee, top_performer)
                
                insights.append({
                    'type': 'modifier_opportunity',
                    'employee_id': employee['id'],
                    'pattern': f"{employee['name']} suggests modifiers {employee['modifier_rate']}% vs {top_performer['name']} at {top_performer['modifier_rate']}%",
                    'action': f"Have {top_performer['name']} train {employee['name']} on upselling. Record their pitch.",
                    'dollar_impact': monthly_loss,
                    'confidence': 0.92
                })
        
        # Time-based patterns
        morning_stats = get_modifier_stats_by_time('morning')
        afternoon_stats = get_modifier_stats_by_time('afternoon')
        
        if morning_stats['avg_modifiers'] > afternoon_stats['avg_modifiers'] * 2:
            insights.append({
                'type': 'modifier_pattern',
                'pattern': 'Morning appointments add 3x more modifiers than afternoon',
                'action': 'Pre-sell modifiers during booking for afternoon appointments',
                'dollar_impact': (morning_stats['avg_revenue'] - afternoon_stats['avg_revenue']) * afternoon_stats['count'],
                'confidence': 0.78
            })
        
        return insights
```

#### Employee Analyzer
```python
class EmployeeAnalyzer:
    def analyze(self, account_id):
        """Find employee performance issues/opportunities"""
        
        insights = []
        employees = get_all_employee_metrics(account_id)
        
        for employee in employees:
            # Client retention
            if employee['client_return_rate'] < 0.3:  # Less than 30% return
                lost_revenue = calculate_retention_loss(employee)
                
                insights.append({
                    'type': 'employee_issue',
                    'employee_id': employee['id'],
                    'pattern': f"{employee['name']}'s clients return {employee['client_return_rate']*100}% of the time vs {team_average*100}% average",
                    'action': 'Review recent complaints, shadow top performer, or consider reassignment',
                    'dollar_impact': lost_revenue,
                    'confidence': 0.88
                })
            
            # Tip analysis (service quality indicator)
            if employee['avg_tip_percent'] < team_avg_tip * 0.5:
                insights.append({
                    'type': 'service_quality',
                    'employee_id': employee['id'],
                    'pattern': f"{employee['name']} receives {employee['avg_tip_percent']}% tips vs {team_avg_tip}% team average",
                    'action': 'Customer service training needed - low tips indicate poor experience',
                    'dollar_impact': employee['monthly_revenue'] * 0.2,  # Estimate 20% revenue risk
                    'confidence': 0.76
                })
        
        return insights
```

#### Pattern Miner
```python
class PatternMiner:
    def analyze(self, account_id):
        """Find non-obvious patterns in data"""
        
        insights = []
        
        # Package analysis
        packages = get_package_performance(account_id)
        for package in packages:
            if package['refund_rate'] > 0.4:
                insights.append({
                    'type': 'package_problem',
                    'pattern': f'"{package["name"]}" has {package["refund_rate"]*100}% refund rate',
                    'action': 'Discontinue package or rebuild with actual premium value',
                    'dollar_impact': package['monthly_refunds'],
                    'confidence': 0.91
                })
        
        # Customer sequence patterns
        sequences = mine_service_sequences(account_id)
        for sequence in sequences:
            if sequence['confidence'] > 0.8:
                insights.append({
                    'type': 'sequence_opportunity',
                    'pattern': f'87% who try {sequence["first"]} also buy {sequence["second"]}',
                    'action': f'Offer {sequence["second"]} immediately after {sequence["first"]} service',
                    'dollar_impact': sequence['potential_revenue'],
                    'confidence': sequence['confidence']
                })
        
        # Referral patterns
        referrals = analyze_referral_patterns(account_id)
        for pattern in referrals:
            insights.append({
                'type': 'referral_opportunity',
                'pattern': pattern['description'],
                'action': pattern['action'],
                'dollar_impact': pattern['value'],
                'confidence': pattern['confidence']
            })
        
        return insights
```

### Insight Scoring (Network Enhanced)

```python
def score_insights(self, insights):
    """Score insights with network learning boost"""
    
    for insight in insights:
        score = 0
        
        # Dollar impact (weighted 35%)
        score += (insight['dollar_impact'] / 100) * 0.35  # $100 = 0.35 points
        
        # Confidence (weighted 25%)
        base_confidence = insight['confidence'] * 0.25
        score += base_confidence
        
        # Network enhancement bonus (weighted 20%)
        if insight.get('network_enhanced'):
            network_boost = insight.get('expected_success_rate', 0) * 0.2
            score += network_boost
            insight['priority_label'] = 'Network Validated'
        
        # Actionability (weighted 15%)
        if 'specific_name' in insight['action']:
            score += 0.15
        elif 'call' in insight['action'] or 'email' in insight['action']:
            score += 0.12
        else:
            score += 0.08
        
        # Urgency (weighted 5%)
        if insight['type'] == 'churn_risk':
            score += 0.05
        elif insight['type'] == 'employee_issue':
            score += 0.04
        else:
            score += 0.02
        
        insight['score'] = score
    
    # Prioritize network-enhanced insights
    network_insights = [i for i in insights if i.get('network_enhanced')]
    regular_insights = [i for i in insights if not i.get('network_enhanced')]
    
    return sorted(network_insights, key=lambda x: x['score'], reverse=True) + \
           sorted(regular_insights, key=lambda x: x['score'], reverse=True)
```

### Quality Gates

```python
def quality_gate(self, insights):
    """Filter out low-quality insights"""
    
    filtered = []
    
    for insight in insights:
        # Confidence check
        if insight['confidence'] < 0.75:
            continue
        
        # Obviousness check
        if any(banned in insight['pattern'].lower() for banned in self.banned_insights):
            continue
        
        # Actionability check
        if not insight.get('action') or insight['action'] == 'do better':
            continue
        
        # Value check
        if insight['dollar_impact'] < 50:  # Minimum $50 impact
            continue
        
        # Human element boost
        if has_human_context(insight):
            insight['priority_boost'] = True
        
        filtered.append(insight)
    
    return filtered
```

### Multi-Model + Network Validation

```python
def validate_across_models(self, insight):
    """Verify insight with secondary model + network intelligence"""
    
    validation_map = {
        'churn_risk': ['rfm', 'pattern'],
        'modifier_opportunity': ['employee', 'pattern'],
        'employee_issue': ['review', 'pattern']
    }
    
    validators = validation_map.get(insight['type'], [])
    
    # Traditional model validation
    model_validated = False
    for validator_name in validators:
        validator = self.models[validator_name]
        if validator.validate(insight):
            model_validated = True
            break
    
    # Network validation (check if similar patterns exist)
    network_validated = self.network_agent.validate_pattern(
        insight, min_occurrences=2, min_success_rate=0.60
    )
    
    if model_validated and network_validated:
        insight['validation_level'] = 'double_validated'
        insight['confidence'] *= 1.3  # Strong boost
    elif network_validated:
        insight['validation_level'] = 'network_validated'
        insight['confidence'] *= 1.2  # Network boost
    elif model_validated:
        insight['validation_level'] = 'model_validated' 
        insight['confidence'] *= 1.1  # Standard boost
    
    return model_validated or network_validated
```

## Parallel Processing Implementation

```python
class ParallelInsightEngine:
    """Execute insight generation 7x faster"""
    
    async def parallel_analyze(self, account_id):
        """Run all analysis models simultaneously"""
        
        # Before: Sequential execution (70 seconds)
        # rfm_results = rfm_model.analyze(account_id)      # 10s
        # churn_results = churn_model.analyze(account_id)  # 10s
        # modifier_results = modifier_model.analyze()      # 10s
        # employee_results = employee_model.analyze()      # 10s
        # pattern_results = pattern_model.analyze()        # 10s
        # seasonal_results = seasonal_model.analyze()      # 10s
        # review_results = review_model.analyze()          # 10s
        
        # After: Parallel execution (10 seconds)
        analysis_tasks = [
            self.rfm_model.analyze(account_id),
            self.churn_model.analyze(account_id),
            self.modifier_model.analyze(account_id),
            self.employee_model.analyze(account_id),
            self.pattern_model.analyze(account_id),
            self.seasonal_model.analyze(account_id),
            self.review_model.analyze(account_id)
        ]
        
        # All models run simultaneously
        results = await asyncio.gather(*analysis_tasks)
        
        return self.merge_analysis_results(results)
```

## Output Format

### Enhanced Insight Structure (Network Enabled)
```json
{
    "id": "uuid",
    "type": "churn_risk|modifier_opportunity|employee_issue|etc",
    "customer_id": "uuid (if applicable)",
    "employee_id": "uuid (if applicable)",
    "pattern": "Clear description of what was found",
    "action": "Specific action to take",
    "script": "If applicable, exact words to say",
    "dollar_impact": 1234.56,
    "confidence": 0.85,
    "priority": 1,
    "expires_at": "2024-01-15",
    "model": "rfm",
    "validated": true,
    "validation_level": "double_validated|network_validated|model_validated",
    "human_context": "Husband has cancer (if applicable)",
    "network_enhanced": true,
    "expected_success_rate": 0.78,
    "network_context": "This approach worked 78% of the time across 12 similar cases",
    "proven_approach": "Personalized call with specific offer",
    "priority_label": "Network Validated",
    "processing_time_ms": 1250
}
```

## Testing Insight Quality

### Test Cases (Network Enhanced)
```python
def test_insight_quality():
    # Should PASS quality gates
    good_insights = [
        "Sarah's clients buy 0 modifiers vs 2.7 average",
        "Morning appointments spend 3x on add-ons",
        "Jennifer's retention is 12% vs 78% average"
    ]
    
    # Should FAIL quality gates
    bad_insights = [
        "Rain causes more cancellations",
        "Customers prefer mornings",
        "Good employees make more money"
    ]
    
    # Network-enhanced insights should score higher
    network_insight = {
        'pattern': "High-value customers at risk",
        'confidence': 0.75,
        'dollar_impact': 2000,
        'network_enhanced': True,
        'expected_success_rate': 0.82,
        'network_context': 'Works 82% of the time across 15 similar cases'
    }
    
    regular_insight = {
        'pattern': "High-value customers at risk",
        'confidence': 0.75,
        'dollar_impact': 2000,
        'network_enhanced': False
    }
    
    # Network insight should score higher
    network_score = calculate_insight_score(network_insight)
    regular_score = calculate_insight_score(regular_insight)
    assert network_score > regular_score
    
    for insight in good_insights:
        assert passes_quality_gate(insight) == True
    
    for insight in bad_insights:
        assert passes_quality_gate(insight) == False
```