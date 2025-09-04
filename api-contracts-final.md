# Keeper API Contracts

## Base URL Structure
```
Production: https://api.keeper.tools/v1
Staging: https://staging-api.keeper.tools/v1
Local: http://localhost:8000/v1
```

## Authentication
All requests require Bearer token in header:
```
Authorization: Bearer {jwt_token}
```

## Core Endpoints

### 0. Network Learning

#### GET /network/patterns
**Retrieve network patterns for enhancement**
```typescript
// Request
{
  pattern_type?: "churn_prevention" | "modifier_opportunity" | "employee_issue";
  business_category?: "spa" | "salon" | "gym";
  min_success_rate?: number;
  limit?: number;
}

// Response (200)
{
  patterns: [
    {
      id: string;
      pattern_type: string;
      business_category: string;
      success_rate: number;
      occurrence_count: number;
      action_template: string;
      confidence_score: number;
      context: object;  // Anonymized pattern details
    }
  ];
  total_patterns: number;
}
```

#### POST /network/patterns
**Store successful pattern for network learning**
```typescript
// Request
{
  account_id: string;
  insight_id: string;
  outcome: {
    success: boolean;
    revenue_impact: number;
    customer_retained?: boolean;
    response_rate?: number;
  };
}

// Response (201)
{
  pattern_id: string;
  anonymized: boolean;
  added_to_network: boolean;
  similar_patterns_found: number;
}
```

#### GET /network/patterns/search
**Search for similar patterns**
```typescript
// Request
{
  insight: {
    type: string;
    pattern: string;
    context: object;
  };
  business_category: string;
  min_similarity?: number;
}

// Response (200)
{
  similar_patterns: [
    {
      id: string;
      similarity_score: number;
      success_rate: number;
      action_template: string;
      proven_script?: string;
      network_context: string;
    }
  ];
  enhancement_available: boolean;
}
```

### 1. Square Integration

#### POST /square/connect
**Initialize Square OAuth**
```typescript
// Request
{
  code: string;  // OAuth authorization code
}

// Response (200)
{
  success: boolean;
  account: {
    id: string;
    merchant_id: string;
    business_name: string;
    locations: Location[];
  };
  import_job_id: string;  // Track import progress
}

// Error (400)
{
  error: "INVALID_CODE" | "ALREADY_CONNECTED";
  message: string;
}
```

#### POST /square/sync
**Trigger manual sync**
```typescript
// Request
{
  account_id: string;
  sync_type: "full" | "incremental";
  since?: string;  // ISO date for incremental
}

// Response (200)
{
  job_id: string;
  estimated_time: number;  // seconds
  records_to_sync: {
    customers: number;
    payments: number;
    appointments: number;
  };
}
```

#### GET /square/sync-status/{job_id}
**Check sync progress**
```typescript
// Response (200)
{
  status: "pending" | "processing" | "completed" | "failed";
  progress: number;  // 0-100
  current_step: string;
  records_processed: number;
  errors: string[];
}
```

### 2. Data Upload

#### POST /upload/customers
**Upload external customer data**
```typescript
// Request (multipart/form-data)
{
  file: File;  // CSV or XLSX
  account_id: string;
  file_type: "customer_notes" | "no_shows" | "preferences";
}

// Response (200)
{
  upload_id: string;
  row_count: number;
  columns_detected: string[];
  matching_job_id: string;
}
```

#### GET /upload/match-status/{job_id}
**Check matching progress**
```typescript
// Response (200)
{
  status: "matching" | "completed";
  total_rows: number;
  matched_rows: number;
  match_rate: number;  // 0-1
  unmatched_customers: Array<{
    row_number: number;
    customer_name: string;
    reason: string;
  }>;
}
```

### 3. Insights & Analysis

#### POST /insights/generate
**Run analysis tournament**
```typescript
// Request
{
  account_id: string;
  models?: string[];  // Optional: specific models to run
  min_confidence?: number;  // Default: 0.75
}

// Response (200)
{
  insights: Array<{
    id: string;
    type: "churn_risk" | "modifier_opportunity" | "employee_issue";
    pattern: string;
    action: string;
    dollar_impact: number;
    confidence: number;
    customer_id?: string;
    employee_id?: string;
    expires_at: string;
  }>;
  summary: {
    total_found: number;
    total_value: number;
    by_type: Record<string, number>;
  };
}
```

#### GET /insights/list
**Get current insights**
```typescript
// Query params
{
  account_id: string;
  status?: "active" | "expired" | "completed";
  type?: string;
  min_value?: number;
  page?: number;
  limit?: number;
}

// Response (200)
{
  insights: Insight[];
  pagination: {
    total: number;
    page: number;
    pages: number;
  };
}
```

### 4. Tasks

#### GET /tasks/inbox
**Get task inbox (network enhanced)**
```typescript
// Query params
{
  account_id: string;
  priority?: 1 | 2 | 3;
  status?: "pending" | "completed" | "expired";
  assignee?: string;  // employee_id
  network_enhanced?: boolean;
}

// Response (200)
{
  tasks: Array<{
    id: string;
    title: string;
    customer_name: string;
    customer_id: string;
    action: string;
    script: string;
    dollar_value: number;
    priority: number;
    status: string;
    expires_at: string;
    created_at: string;
    network_enhanced: boolean;
    network_confidence?: number;
    expected_success_rate?: number;
    network_context?: string;
    priority_label?: "Network Validated" | "High Confidence" | "Standard";
  }>;
  summary: {
    urgent: number;
    pending: number;
    completed_today: number;
    expired: number;
    total_value: number;
    network_enhanced_count: number;
  };
}
```

#### PUT /tasks/{task_id}/complete
**Mark task complete (triggers network learning)**
```typescript
// Request
{
  outcome?: "success" | "failed" | "partial";
  notes?: string;
  actual_value?: number;
  revenue_impact?: number;
  customer_retained?: boolean;
  response_rate?: number;
}

// Response (200)
{
  task_id: string;
  status: "completed";
  impact_tracking_id: string;  // For ROI tracking
}
```

### 5. Employee Analytics

#### GET /employees/performance
**Get employee metrics**
```typescript
// Query params
{
  account_id: string;
  employee_id?: string;  // Specific or all
  date_from: string;
  date_to: string;
}

// Response (200)
{
  employees: Array<{
    id: string;
    name: string;
    metrics: {
      revenue_per_hour: number;
      client_retention_rate: number;
      modifier_attach_rate: number;
      average_ticket: number;
      average_tip_percent: number;
      cancellation_rate: number;
    };
    comparison: {
      vs_team_average: Record<string, number>;
      rank: number;
      percentile: number;
    };
    insights: string[];
  }>;
}
```

#### GET /employees/{id}/review
**Generate employee review**
```typescript
// Query params
{
  period: "annual" | "quarterly" | "custom";
  date_from?: string;
  date_to?: string;
}

// Response (200)
{
  employee: {
    id: string;
    name: string;
  };
  period: string;
  performance_summary: string;
  metrics: EmployeeMetrics;
  achievements: string[];
  areas_for_improvement: string[];
  customer_feedback: {
    positive: string[];
    negative: string[];
  };
  recommendation: "raise" | "maintain" | "coach" | "warning";
  suggested_action: string;
}
```

### 6. Reports

#### POST /reports/generate
**Generate report**
```typescript
// Request
{
  account_id: string;
  report_type: "daily" | "weekly" | "monthly" | "quarterly" | "annual";
  format: "json" | "pdf" | "html";
  email_to?: string[];
}

// Response (200)
{
  report_id: string;
  status: "generating";
  estimated_time: number;
  download_url?: string;  // When complete
}
```

#### GET /reports/{report_id}
**Get report content**
```typescript
// Response (200)
{
  id: string;
  type: string;
  period: {
    from: string;
    to: string;
  };
  content: {
    executive_summary: string;
    key_metrics: Record<string, any>;
    insights: Insight[];
    recommendations: string[];
    employee_rankings: EmployeeRank[];
    financial_breakdown: FinancialSummary;
  };
  generated_at: string;
  pdf_url?: string;
}
```

### 7. Customer Intelligence

#### GET /customers/{id}/profile
**Get enriched customer profile**
```typescript
// Response (200)
{
  customer: {
    id: string;
    square_id: string;
    name: string;
    email: string;
    phone: string;
  };
  metrics: {
    lifetime_value: number;
    visit_frequency_days: number;
    last_visit: string;
    days_since_visit: number;
    favorite_service: string;
    favorite_employee: string;
    average_spend: number;
    risk_score: number;
  };
  modifiers: {
    usually_purchases: string[];
    never_purchased: string[];
    potential_upsells: string[];
  };
  context: {
    external_notes: string;
    life_events: string[];
    preferences: string[];
    communication_preference: string;
  };
  predictions: {
    churn_probability: number;
    next_visit_estimate: string;
    lifetime_value_forecast: number;
  };
}
```

#### POST /customers/search
**Search customers with context**
```typescript
// Request
{
  query: string;
  account_id: string;
  filters?: {
    at_risk?: boolean;
    high_value?: boolean;
    new?: boolean;
    min_ltv?: number;
  };
}

// Response (200)
{
  results: Array<{
    customer: Customer;
    relevance_score: number;
    matched_on: string[];
  }>;
}
```

### 8. Reviews

#### POST /reviews/analyze
**Analyze review sentiment**
```typescript
// Request
{
  review_text: string;
  source: "google" | "yelp" | "facebook" | "square";
  rating?: number;
}

// Response (200)
{
  sentiment: {
    overall: "positive" | "negative" | "neutral";
    score: number;  // -1 to 1
  };
  entities: {
    employees_mentioned: string[];
    services_mentioned: string[];
    competitors_mentioned: string[];
  };
  issues_detected: string[];
  suggested_response?: string;
  urgency: "immediate" | "high" | "normal" | "low";
}
```

### 9. Settings

#### GET /settings/business
**Get business settings**
```typescript
// Response (200)
{
  business: {
    name: string;
    type: string;
    locations: Location[];
  };
  integrations: {
    square: {
      connected: boolean;
      last_sync: string;
    };
    google_business: {
      url?: string;
    };
    yelp: {
      url?: string;
    };
  };
  preferences: {
    task_expiry_days: number;
    min_confidence: number;
    email_time: string;
  };
}
```

#### PUT /settings/preferences
**Update preferences**
```typescript
// Request
{
  task_expiry_days?: number;
  min_confidence?: number;
  email_time?: string;
  notification_channels?: string[];
}

// Response (200)
{
  updated: boolean;
  preferences: Preferences;
}
```

## WebSocket Events

### Connection
```javascript
const ws = new WebSocket('wss://api.dropset.io/v1/ws');
ws.send(JSON.stringify({
  type: 'auth',
  token: jwt_token
}));
```

### Event Types
```typescript
// Sync progress
{
  type: "sync_progress";
  data: {
    job_id: string;
    progress: number;
    current: string;
  };
}

// New insight
{
  type: "insight_found";
  data: {
    insight: Insight;
    account_id: string;
  };
}

// Task expired
{
  type: "task_expired";
  data: {
    task_id: string;
    customer_name: string;
    value_lost: number;
  };
}

// Urgent alert
{
  type: "urgent_alert";
  data: {
    message: string;
    action_required: string;
    link: string;
  };
}
```

## Error Handling

### Standard Error Response
```typescript
{
  error: {
    code: string;
    message: string;
    details?: any;
    request_id: string;
  };
}
```

### Error Codes
```
AUTH_001: Invalid token
AUTH_002: Token expired
AUTH_003: Insufficient permissions

SQUARE_001: Square API error
SQUARE_002: Rate limit exceeded
SQUARE_003: Invalid merchant

DATA_001: Invalid file format
DATA_002: Matching failed
DATA_003: Duplicate data

INSIGHT_001: Insufficient data
INSIGHT_002: Analysis failed
INSIGHT_003: No insights found

SYSTEM_001: Internal server error
SYSTEM_002: Database error
SYSTEM_003: Service unavailable
```

## Rate Limits

```
Standard tier:
- 100 requests/minute
- 1000 requests/hour
- 10000 requests/day

Bulk operations:
- Data upload: 10/hour
- Report generation: 20/day
- Full sync: 4/day
```

## Pagination

All list endpoints support pagination:
```
?page=1&limit=20&sort=created_at&order=desc
```

## Versioning

API version in URL: `/v1/`
Breaking changes will increment version.
Deprecation notice: 6 months.

## Testing

### Sandbox Environment
```
Base URL: https://sandbox-api.dropset.io/v1
Square: Use Square Sandbox
Data: Anonymized test data
```

### Test Account
```
Email: test@keeper.tools
Password: TestKeeper2024!
Account ID: test-account-123
```