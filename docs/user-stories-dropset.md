# Keeper User Stories

## Epic 1: Owner Onboarding
**As a spa owner, I want to connect my Square account and see immediate value**

### Story 1.1: Square Connection
```
GIVEN I'm a new user
WHEN I click "Connect Square Account"
THEN I'm redirected to Square OAuth
AND I can approve permissions
AND I return to see data importing
```

**Acceptance Criteria**:
- OAuth completes in <30 seconds
- Progress bar shows data types importing
- First insight appears within 90 seconds

### Story 1.2: First Value Moment
```
GIVEN my Square data is imported
WHEN the analysis completes
THEN I see a specific customer at risk
AND I see their exact dollar value
AND I see their name and history
```

**Test Case**:
- Import includes customer "Sarah Chen"
- Sarah hasn't visited in 47 days
- System shows: "Sarah Chen ($400/mo) at risk"

### Story 1.3: External Data Upload
```
GIVEN I have a customer notes spreadsheet
WHEN I upload the CSV file
THEN I see match percentage
AND matched customers get enriched context
AND new insights appear from merged data
```

**Success Metrics**:
- 97%+ customers matched
- New insight within 60 seconds
- Context visible in customer profiles

---

## Epic 2: Daily Operations
**As a spa owner, I want actionable tasks every morning**

### Story 2.1: Task Inbox
```
GIVEN it's 7 AM
WHEN I open Keeper
THEN I see urgent tasks first
AND each task has a dollar value
AND each task has specific actions
```

**Task Example**:
```
Title: Save Sarah Chen - $400/month at risk
Action: Call today with this script
Script: "Hi Sarah, we've missed you! Your favorite dermaplaning service has a new upgrade..."
Value: $400/month retained
Expires: 7 days
```

### Story 2.2: Task Completion
```
GIVEN I have a task to call Sarah
WHEN I complete the call
THEN I mark task complete
AND the system tracks success
AND impact shows in tomorrow's report
```

---

## Epic 3: Employee Intelligence
**As a spa owner, I want to know which employees make me money**

### Story 3.1: Performance Comparison
```
GIVEN I have multiple employees
WHEN I view employee dashboard
THEN I see revenue per hour for each
AND I see retention rates
AND I see modifier attachment rates
```

**Display Format**:
```
Jennifer: $47/hour, 12% retention, 0.3 modifiers/service
Sarah: $89/hour, 78% retention, 2.7 modifiers/service
Team Avg: $62/hour, 54% retention, 1.4 modifiers/service
```

### Story 3.2: Annual Review
```
GIVEN it's time for annual reviews
WHEN I generate employee report
THEN I get complete 12-month analysis
AND specific examples of wins/losses
AND recommended raise/coaching/termination
```

---

## Epic 4: Financial Intelligence
**As a spa owner, I want to see where money is hiding**

### Story 4.1: Modifier Opportunities
```
GIVEN customers buy services
WHEN I view modifier analysis
THEN I see untapped add-on revenue
AND which employees need training
AND specific upsell scripts
```

**Insight Example**:
"Morning appointments add 3x more modifiers. Schedule high-value clients in AM. Impact: +$1,800/month"

### Story 4.2: Churn Prevention
```
GIVEN customers have patterns
WHEN someone breaks their pattern
THEN I get an urgent task
AND personalized win-back offer
AND their lifetime value highlighted
```

---

## Epic 5: Competitive Intelligence
**As a spa owner, I want to know about competition**

### Story 5.1: Review Monitoring
```
GIVEN customers leave reviews
WHEN a review mentions competitors
THEN I get an alert
AND sentiment analysis
AND suggested response
```

### Story 5.2: Lost Customer Patterns
```
GIVEN customers stop coming
WHEN multiple mention same competitor
THEN I see the pattern
AND what they're offering
AND how to counter
```

---

## Epic 6: Reporting
**As a spa owner, I want professional reports**

### Story 6.1: Weekly Strategic Report
```
GIVEN a week of operations
WHEN Monday morning arrives
THEN I get McKinsey-quality analysis
AND specific wins/losses
AND next week's focus areas
```

### Story 6.2: Monthly Comparison
```
GIVEN a month completes
WHEN I view monthly report
THEN I see week-over-week trends
AND employee rankings
AND revenue breakdown by category
```

---

## Testing Checklist

### Data Accuracy Tests
- [ ] Square sync matches 100%
- [ ] Fuzzy matching >97% accurate
- [ ] Dollar calculations correct
- [ ] No duplicate records

### Insight Quality Tests
- [ ] No obvious insights (rain = cancellations)
- [ ] All insights have dollar values
- [ ] Confidence scores >75%
- [ ] Actions are specific and doable

### User Experience Tests
- [ ] First insight in <90 seconds
- [ ] Page loads <2 seconds
- [ ] Mobile responsive
- [ ] PDF reports generate correctly

### Business Value Tests
- [ ] Find $3,000+ in opportunities
- [ ] Identify 5+ at-risk customers
- [ ] Show 3+ employee improvements
- [ ] Generate 10+ actionable tasks