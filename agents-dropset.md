# Keeper Agent Specifications

## Agent Overview
8 specialized agents working in coordination through Redis pub/sub and Supabase logging, with network learning intelligence.

## 1. DataAgent
**Responsibility**: Square data synchronization and storage

**Functions**:
```python
class DataAgent:
    def sync_square_data(self, account_id):
        """Pull latest data from Square API"""
        - Fetch new/updated customers
        - Fetch payments since last sync
        - Fetch appointments
        - Fetch modifiers
        - Store raw in raw_square_data
        - Publish: "square_sync_complete"
    
    def backfill_historical(self, account_id, months=12):
        """Initial historical data import"""
        - Paginate through all endpoints
        - Handle rate limits
        - Store with timestamps
```

**Triggers**: 
- Hourly cron
- Manual sync request
- After OAuth connection

**Success Metrics**:
- 100% data accuracy
- <5 minute sync time
- Zero duplicate records

---

## 2. MatchingAgent
**Responsibility**: Fuzzy matching between Square and external files

**Functions**:
```python
class MatchingAgent:
    def match_customers(self, square_customers, external_file):
        """Match uploaded CSV to Square customers"""
        - Normalize names (lowercase, remove punctuation)
        - Try exact match first
        - Fuzzy match on name (threshold: 85%)
        - Validate with phone/email if available
        - Return match confidence scores
        
    def merge_context(self, customer_id, external_data):
        """Merge external context into customer record"""
        - Append to metadata field
        - Re-generate embedding
        - Flag sensitive info (health, personal)
```

**Success Metrics**:
- 97%+ match accuracy
- <60 seconds for 1000 records
- Preserve all external context

---

## 3. AnalysisAgent
**Responsibility**: Pattern detection and insight generation

**Functions**:
```python
class AnalysisAgent:
    def run_analysis_tournament(self, account_id):
        """Run multiple models, pick best insights"""
        models = {
            'rfm': self.rfm_analysis(),
            'modifiers': self.modifier_analysis(),
            'employee': self.employee_performance(),
            'churn': self.churn_prediction(),
            'patterns': self.sequence_mining()
        }
        
        # Score and rank insights
        insights = self.tournament_judge(models)
        
        # Filter by confidence
        return [i for i in insights if i.confidence >= 0.75]
    
    def modifier_analysis(self):
        """Find modifier revenue opportunities"""
        - Calculate attach rates by employee
        - Find modifier combinations
        - Detect time-based patterns
        - Return dollar opportunities
```

**Success Metrics**:
- Find 5+ insights per analysis
- 75%+ insight accuracy
- No obvious patterns

---

## 4. EmployeeAgent
**Responsibility**: Staff performance tracking

**Functions**:
```python
class EmployeeAgent:
    def analyze_employee_performance(self, employee_id):
        """Complete employee analysis"""
        metrics = {
            'revenue_per_hour': self.calculate_rph(employee_id),
            'client_retention': self.retention_rate(employee_id),
            'modifier_attach': self.modifier_success(employee_id),
            'average_ticket': self.avg_transaction(employee_id),
            'tip_percentage': self.tip_analysis(employee_id),
            'cancellation_rate': self.cancellations(employee_id)
        }
        
        # Compare to team average
        comparison = self.compare_to_team(metrics)
        
        # Generate recommendations
        return self.employee_insights(comparison)
```

**Insights Generated**:
- "Sarah generates 40% more revenue/hour"
- "Jennifer's clients never return (12% vs 78%)"
- "Maria's tips indicate service issues"

---

## 5. ReviewAgent
**Responsibility**: Monitor and analyze online reviews

**Functions**:
```python
class ReviewAgent:
    def scrape_reviews(self, account_id):
        """Daily review collection"""
        sources = {
            'google': self.scrape_google_business(),
            'yelp': self.scrape_yelp(),
            'facebook': self.scrape_facebook()
        }
        
        for review in new_reviews:
            self.analyze_sentiment(review)
            self.extract_entities(review)  # employee, service
            self.detect_issues(review)
    
    def analyze_sentiment(self, review_text):
        """Extract actionable feedback"""
        - Overall sentiment score
        - Specific complaints/praise
        - Employee mentions
        - Service quality issues
        - Competitor mentions
```

**Alerts**:
- 1-star review: Immediate task
- Employee complaint: Flag for owner
- Competitor mention: Track pattern

---

## 6. InsightAgent
**Responsibility**: Convert patterns into actionable tasks

**Functions**:
```python
class InsightAgent:
    def generate_tasks(self, insights):
        """Convert insights to specific tasks"""
        for insight in insights:
            task = {
                'title': self.create_title(insight),
                'customer_name': insight.customer.name,
                'dollar_value': insight.impact,
                'priority': self.calculate_priority(insight),
                'action_script': self.generate_script(insight),
                'expires_at': datetime.now() + timedelta(days=7)
            }
            
            # Use Claude for script generation
            task['script'] = self.ai_generate_script(task)
            
            yield task
    
    def calculate_priority(self, insight):
        """Score 1-3 based on impact and urgency"""
        score = 0
        score += insight.dollar_impact / 1000  # $1000 = 1 point
        score += insight.time_sensitivity * 2   # urgency weighted 2x
        score += insight.ease_of_execution      # easy = bonus
        
        if insight.has_human_element:  # cancer, divorce, etc
            score *= 1.5
        
        return min(1, max(3, int(score)))
```

---

## 7. NetworkLearningAgent
**Responsibility**: Capture successful patterns and apply network intelligence

**Functions**:
```python
class NetworkLearningAgent:
    def capture_successful_pattern(self, account_id, insight, outcome):
        """When an action succeeds, learn from it"""
        
        # Anonymize but preserve the pattern
        pattern = {
            'type': insight['type'],
            'business_category': self.get_business_category(account_id),
            'trigger_conditions': self.extract_conditions(insight),
            'action_taken': insight['action'],
            'outcome_metrics': {
                'success': outcome['success'],
                'revenue_impact': outcome['revenue_impact'],
                'customer_retained': outcome.get('retained', False)
            }
        }
        
        # Generate embedding for similarity matching
        embedding = self.create_pattern_embedding(pattern)
        
        # Store in network knowledge base
        existing = self.find_similar_pattern(embedding)
        if existing and existing['similarity'] > 0.95:
            self.update_pattern_success(existing['id'], outcome)
        else:
            self.create_network_pattern(pattern, embedding)
    
    def apply_network_knowledge(self, account_id, new_insight):
        """Enhance insights with network intelligence"""
        
        similar_patterns = self.search_patterns(
            new_insight,
            business_type=self.get_business_category(account_id),
            min_success_rate=0.60,
            min_occurrences=3
        )
        
        if similar_patterns:
            best_pattern = max(similar_patterns, key=lambda x: x['success_rate'])
            
            # Enhance the insight
            new_insight['network_enhanced'] = True
            new_insight['confidence'] *= (1 + best_pattern['success_rate'] * 0.3)
            new_insight['proven_approach'] = best_pattern['action_template']
            new_insight['expected_success_rate'] = best_pattern['success_rate']
            new_insight['network_context'] = (
                f"This approach worked {best_pattern['success_rate']*100:.0f}% "
                f"of the time across {best_pattern['occurrence_count']} similar cases"
            )
        
        return new_insight
```

**Success Metrics**:
- Pattern discovery rate: 10+ new patterns/week
- Cross-application rate: 60%+ patterns used by multiple accounts
- Success rate improvement: 20%+ boost from network enhancement
- Pattern accuracy: 85%+ validation rate

**Triggers**:
- After successful task completion (capture pattern)
- During insight generation (apply intelligence)
- Weekly pattern validation runs

---

## 8. ReportAgent
**Responsibility**: Generate narrative reports

**Functions**:
```python
class ReportAgent:
    def generate_daily_report(self, account_id):
        """Create daily summary"""
        - New insights found
        - Tasks completed impact
        - Key metrics changes
        
    def generate_weekly_report(self, account_id):
        """McKinsey-style analysis"""
        context = self.gather_week_context()
        prompt = self.build_report_prompt(context)
        report = claude.generate(prompt, model='sonnet')
        return self.format_as_pdf(report)
    
    def annual_employee_review(self, employee_id):
        """Complete performance review"""
        - 12 months of metrics
        - Comparison to team
        - Growth trajectory
        - Specific wins/losses
        - Recommended actions
```

---

## Agent Coordination

### Communication Protocol
```python
# Agent publishes when starting work
redis.publish('agent_channel', {
    'agent': self.name,
    'status': 'analyzing',
    'entity': entity_id,
    'timestamp': now()
})

# Network learning notifications
redis.publish('network_channel', {
    'agent': 'NetworkLearningAgent',
    'action': 'pattern_applied',
    'insight_id': insight_id,
    'confidence_boost': 0.23
})

# Parallel execution coordination
async def coordinate_parallel_agents(account_id):
    """Run compatible agents in parallel"""
    tasks = [
        matching_agent.process(account_id),
        review_agent.scrape(account_id),
        employee_agent.analyze(account_id),
        network_agent.update_patterns(account_id)
    ]
    
    results = await asyncio.gather(*tasks)
    return merge_results(results)

# Lock only for conflicting operations
if redis.get(f'lock:{entity_id}'):
    await_completion()
else:
    redis.set(f'lock:{entity_id}', self.name, ex=300)
```

### Daily Workflow (Parallel Execution)
```
3:00 AM: DataAgent syncs Square (triggers parallel pipeline)
3:30 AM: Parallel execution begins:
  ├── MatchingAgent processes new data
  ├── ReviewAgent scrapes reviews  
  ├── NetworkLearningAgent updates patterns
  └── EmployeeAgent analyzes staff
4:00 AM: AnalysisAgent runs tournament (enhanced with network intelligence)
4:15 AM: InsightAgent generates tasks (network-enhanced)
4:30 AM: ReportAgent creates daily summary
5:00 AM: Email notifications sent
```

### Parallel Processing Benefits
- **Before**: 70 seconds sequential execution
- **After**: 10 seconds parallel execution  
- **Improvement**: 7x speedup via asyncio.gather()

### Network Learning Workflow
```python
# When task completes successfully
async def on_task_completion(task_id, outcome):
    task = get_task(task_id)
    insight = get_insight(task.insight_id)
    
    # Capture the successful pattern
    network_agent = NetworkLearningAgent()
    await network_agent.capture_successful_pattern(
        task.account_id, insight, outcome
    )
    
    # Notify other agents of new learning
    redis.publish('network_channel', {
        'action': 'pattern_learned',
        'pattern_type': insight['type'],
        'success_rate': outcome['success_rate']
    })
```