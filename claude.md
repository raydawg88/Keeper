# Claude.md - Keeper Development Context

## 🎯 Project Overview

**Keeper** is an AI-powered decision engine that transforms Square POS data into actionable business insights with dollar values attached. We find hidden revenue, prevent churn, and optimize operations for SMBs (specifically spas, salons, and similar service businesses).

**Domain**: keeper.tools  
**Repository**: https://github.com/raydawg88/Keeper  
**Owner**: Ray Hernandez (ray.hernandez@gmail.com)

## 📋 Core Philosophy & Rules

### **Documentation First Rule** ⚠️ CRITICAL
**ALWAYS verify current documentation before implementing ANY external service integration**
- Use WebFetch to get the latest docs from official sources
- Never assume API endpoints, parameters, or formats from memory or old examples  
- OAuth endpoints, database schemas, API versions change frequently
- Spend 5 minutes verifying docs to save hours debugging outdated implementations
- **Examples that failed us**: Square OAuth endpoint casing, parameter requirements
- **Rule**: When integrating any service (Square, Supabase, OpenAI, etc.), first fetch current docs

### **BMAD Methodology**
- **Build** small increments
- **Measure** with real data  
- **Analyze** actual results
- **Deploy** only when verified

### **Non-Negotiable Requirements**
1. **Every insight MUST have a dollar value** - No generic advice
2. **97%+ matching accuracy** - Customer identity resolution is critical
3. **75%+ confidence threshold** - No uncertain insights
4. **No obvious insights** - Banned: "rain causes cancellations", "weekends are busier"
5. **Start with wife's spa** - Real validation before scaling
6. **Network learning from day 1** - Every customer makes every other customer smarter

### **Quality Gates**
- Confidence Check: >= 75% certainty
- Actionability Check: Specific action exists
- Obviousness Check: Not in banned_insights list
- Value Check: Dollar impact calculable
- Multi-Model Validation: 2+ models agree
- Network Enhancement: Apply collective intelligence when available

## 🏗️ Technical Architecture

### **Stack**
- **Frontend**: Next.js 14, Tailwind CSS, shadcn/ui, Vercel
- **Backend**: FastAPI, Railway
- **Database**: Supabase (PostgreSQL 15) with pgvector
- **Cache**: Redis (Upstash)
- **Queue**: Celery + Redis
- **AI**: Claude 3 (Haiku/Sonnet), OpenAI (embeddings), Gemini (backup)

### **Core Tables**
```sql
accounts - Business accounts connected via Square OAuth
customers - Square customers + fuzzy matched external context
transactions - Square payments with modifiers extracted  
insights - Patterns detected by analysis tournament
tasks - Actionable insights with dollar values and scripts
network_patterns - Collective learning patterns (anonymized)
```

### **Agent System (8 Specialized Agents)**
1. **DataAgent** - Square data sync and storage
2. **MatchingAgent** - 97%+ accuracy fuzzy matching
3. **AnalysisAgent** - Pattern detection tournament
4. **EmployeeAgent** - Staff performance analysis  
5. **ReviewAgent** - Online review monitoring
6. **InsightAgent** - Convert patterns to actionable tasks
7. **NetworkLearningAgent** - Capture/apply collective intelligence
8. **ReportAgent** - McKinsey-style narrative reports

### **Key Performance Targets**
- **7x Speedup**: Parallel agent execution (70s → 10s)
- **20% Boost**: Network learning confidence improvement
- **1000+ Scale**: Architecture proven for 1000+ accounts
- **<90 seconds**: First insight after Square connection
- **$3000+**: Hidden revenue discovery in test spa

## 🔧 Development Workflow

### **Git Commit Practice** 
**CRITICAL**: Commit progress regularly due to Claude usage limits
- After each working feature/component
- After successful tests  
- Before major refactoring
- Always include descriptive commit messages with 🤖 Generated footer

**Commit Template**:
```
Brief description of what was built/fixed

Details of changes:
- Specific feature implemented
- Tests that pass
- Integration points added

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### **Development Phases**
1. **Week 1**: Data Pipeline (Square OAuth, sync, storage)
2. **Week 2**: Analysis Engine (RFM, modifiers, patterns) 
3. **Week 3**: Agent System (8 specialized agents)
4. **Week 4**: Interface (dashboards, reports, tasks)

### **Current Environment Status**
- ✅ Square API: Connected (sandbox credentials)
- ✅ Supabase: Database schema created, tables accessible
- ✅ AI APIs: OpenAI, Anthropic, Gemini configured
- ✅ Development environment: Python virtual env with all dependencies

## 📊 User Stories & Acceptance Criteria

### **Epic 1: Owner Onboarding**
- Square OAuth in <30 seconds
- First insight in <90 seconds
- External file upload with 97%+ matching

### **Epic 2: Daily Operations** 
- Morning task inbox with dollar values
- Specific action scripts for each task
- Success tracking and ROI measurement

### **Epic 3: Employee Intelligence**
- Performance comparison dashboard
- Revenue/hour, retention rates, modifier attachment
- Annual review generation with recommendations

### **Epic 4: Financial Intelligence**
- Modifier opportunity detection  
- Churn prevention with personalized offers
- Hidden revenue discovery ($3000+ target)

### **Epic 5: Competitive Intelligence**
- Review monitoring with competitor mentions
- Lost customer pattern analysis
- Response templates for negative reviews

### **Epic 6: Reporting**
- Weekly McKinsey-style strategic reports
- Monthly comparison with trends
- PDF generation for professional presentation

## 🔒 Security & Privacy

### **Data Protection**
- All Square API credentials encrypted
- Customer PII never logged or exposed
- Network learning patterns fully anonymized
- Environment variables protected in .gitignore

### **Network Learning Anonymization**
- Remove all customer names, emails, phone numbers
- Replace with generic markers [high_value_customer]
- Hash any remaining identifiers
- Store only pattern abstractions, never raw data

## 🧪 Testing Protocol

### **BMAD Testing Approach**
- Use real spa data from Ray's wife's business
- 97%+ matching accuracy validation
- $3000+ revenue discovery requirement
- No obvious insights allowed in output

### **Test Data Requirements**
```
test-data/
├── square-customers.csv
├── square-transactions.csv  
├── square-appointments.csv
├── customer-notes.csv
└── staff-schedule.csv
```

### **Success Criteria**
- Find $3,000+ hidden revenue in test spa
- 97%+ customer matching accuracy
- 75%+ confidence on all insights  
- Zero obvious/generic insights
- <90 seconds to first insight

## 🚀 Network Learning System

### **Core Principle**
"Every customer makes every other customer smarter" - patterns discovered at one spa benefit all spas.

### **Pattern Types**
- **Churn Prevention**: Break in visit patterns, personalized win-back
- **Modifier Opportunities**: Employee coaching, time-based upselling
- **Review Response**: Template responses for different scenarios
- **Employee Issues**: Performance problems, coaching recommendations

### **Network Effect Timeline**
- Month 1-3: 100 patterns from 10 customers
- Month 4-6: 1,000+ patterns, cross-category insights
- Month 7-12: 10,000+ patterns, new customers get instant intelligence
- Year 2+: Competitive moat established

## 📈 Scale Architecture

### **Proven Capacity**
- **Database**: Supabase handles 10+ billion rows easily
- **At 1,000 accounts**: 300,000 rows (trivial), 50GB storage (10% of tier)
- **API Processing**: FastAPI handles 1,000 req/sec, horizontal scaling ready
- **Queue System**: Redis 10,000 req/sec, Celery infinitely scalable

### **Cost Scaling**
- 100 accounts: $75/month (0.75% of revenue)
- 1,000 accounts: $1,200/month (1.2% of revenue)  
- 10,000 accounts: $10,700/month (1.07% of revenue)

## 🔄 Square API Resilience

### **Adaptive Rate Limiting**
- No fixed rate limits assumed
- Learn from 429 responses dynamically
- Exponential backoff with jitter
- Circuit breaker pattern for outages
- Request prioritization (critical/high/normal/low)

### **Graceful Degradation**
- Use cached data when Square is down
- Notify users of reduced functionality
- Queue requests for retry when service resumes

## 🎯 Current Development Status

### **✅ Completed**
- Project setup and environment configuration
- Square API integration and testing
- Supabase database schema creation
- All AI API keys configured and validated
- Comprehensive documentation and architecture
- Git repository with regular commit workflow established

### **🔄 Next Steps (In Priority Order)**
1. **Square OAuth Flow** - Real business connection
2. **Data Sync Pipeline** - Customer/transaction import
3. **Fuzzy Matching Engine** - 97%+ accuracy customer resolution
4. **Insight Tournament** - Multi-model pattern detection
5. **Task Generation** - Actionable insights with scripts
6. **Agent Coordination** - Parallel processing system
7. **Network Learning** - Pattern capture and application
8. **Frontend Dashboard** - Next.js interface

### **🎪 Ready to Build**
All foundations are in place. The next Claude session can immediately continue from the Square OAuth integration development.

## 📚 Current API Documentation Status (Updated 2025-09-03)

### **Square API (v2025-08-20)**
- ⚠️ **Breaking Change**: Customer `cards` field retired - use `ListCards` endpoint  
- **Rate Limits**: ~10 QPS with exponential backoff for 429 errors
- **Current Integration**: Test account connected with token `EAAAly9q...`
- **Account**: 27d755f9-87fd-40e8-a541-3a0478816395 (Default Test Account)

### **Supabase (2024-2025)**
- **Performance**: RLS policies require proper indexing for large datasets
- **Real-time**: Channel-based subscriptions for live updates
- **Current Schema**: All OAuth columns added, accounts table ready

### **OpenAI API (2024-2025)**
- **Latest Embeddings**: text-embedding-3-large (3,072 dimensions) for 97%+ matching
- **Cost Optimization**: Batch API offers 50% discount for bulk processing
- **GPT Models**: GPT-4.1 series for superior code generation

### **FastAPI (2024-2025)**
- **Async Patterns**: Never block event loop in async routes
- **Real-time**: Native WebSocket support for dashboard updates
- **Background Tasks**: Built-in for lightweight operations

## 🚨 Important Notes for Future Claude Sessions

### **Context Restoration**
This project has extensive documentation:
- Complete technical specifications in 16 .md files
- All environment variables configured in .env (not committed)
- Database schema updated with OAuth columns
- Square test account successfully connected

### **Development Continuity**
- Use BMAD methodology - build small, test with real data
- Commit frequently due to usage limit constraints  
- Focus on finding actual $3000+ revenue opportunities
- **Always fetch latest documentation** before implementing integrations

### **Key Passwords/Credentials Location**
- All credentials stored in .env file (gitignored)
- Supabase project: keeper-prod  
- Square app: "Keeper" (sandbox environment)
- Test Account ID: 27d755f9-87fd-40e8-a541-3a0478816395
- Domain: keeper.tools (recently purchased)

---

**Remember**: This isn't just another SaaS - we're building the definitive SMB decision intelligence platform. Every feature must deliver measurable business value with dollar amounts attached. The wife's spa is our proof of concept for transforming how small businesses make decisions. 🎯