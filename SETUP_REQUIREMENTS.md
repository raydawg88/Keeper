# Keeper Setup Requirements - What Ray Needs to Provide

## 🚨 **IMMEDIATE NEEDS (Before We Start Building)**

### 1. **Square Developer Account & API Keys**
**What I need:**
- Square Application ID
- Square Application Secret 
- Square Sandbox Access Token (for testing)
- Square Sandbox Application ID

**How to get:**
1. Go to https://developer.squareup.com/
2. Create developer account (if you don't have one)
3. Create new application called "Keeper"
4. Copy Application ID and Secret from dashboard
5. Generate Sandbox Access Token

**Why I need this:**
- OAuth flow setup
- Test data pipeline with Square Sandbox
- All Square API calls during development

### 2. **Supabase Project**
**What I need:**
- Supabase Project URL
- Supabase Anon Key
- Supabase Service Role Key (secret)

**How to get:**
1. Go to https://supabase.com/
2. Create new project called "keeper-prod"
3. Wait for database to initialize
4. Go to Project Settings > API
5. Copy URL, anon key, and service_role key

**Why I need this:**
- Database setup and schema creation
- Authentication system
- Vector storage for embeddings

### 3. **OpenAI API Key**
**What I need:**
- OpenAI API Key with GPT-4/embeddings access

**How to get:**
1. Go to https://platform.openai.com/api-keys
2. Create new key called "keeper-development"  
3. Add some credits ($20-50 for development)

**Why I need this:**
- Text embeddings for similarity search
- Insight generation (backup to Claude)
- Customer context analysis

---

## 📅 **PHASE 1 NEEDS (Week 1 - Data Pipeline)**

### 4. **Anthropic API Key**
**What I need:**
- Anthropic API Key (for Claude 3 Haiku/Sonnet)

**How to get:**
1. Go to https://console.anthropic.com/
2. Create API key called "keeper-insights"
3. Add credits for development

**Why I need this:**
- Primary AI for insight generation
- Report writing with Claude Sonnet
- Task script generation

### 5. **Redis/Upstash**
**What I need:**
- Upstash Redis URL
- Upstash Redis Token

**How to get:**
1. Go to https://upstash.com/
2. Create new Redis database called "keeper-cache"
3. Copy UPSTASH_REDIS_REST_URL and token

**Why I need this:**
- Caching layer for performance
- Agent coordination via pub/sub
- Queue management for Celery

### 6. **Your Wife's Spa Data (Test Data)**
**What I need:**
- Square Dashboard access OR exported CSV files
- Customer notes spreadsheet (if exists)
- Any no-show tracking data
- Staff schedule data

**Files needed:**
- square-customers.csv
- square-transactions.csv  
- square-appointments.csv
- customer-notes.csv (optional)
- no-shows.xlsx (optional)

**Why I need this:**
- Real data for testing matching accuracy
- Validate insights make sense
- Prove $3,000+ revenue discovery

---

## 📅 **PHASE 2 NEEDS (Week 2 - Infrastructure)**

### 7. **Railway Account**
**What I need:**
- Railway project for backend deployment

**How to get:**
1. Go to https://railway.app/
2. Connect your GitHub account
3. Create new project from Keeper repo (when ready)

**Why I need this:**
- Backend API deployment
- Environment variable management
- Database connections

### 8. **Vercel Account**  
**What I need:**
- Vercel project for frontend deployment

**How to get:**
1. Go to https://vercel.com/
2. Connect GitHub account
3. Import Keeper repository (when ready)

**Why I need this:**
- Frontend deployment
- keeper.tools domain connection
- Preview deployments

---

## 📅 **PHASE 3 NEEDS (Week 3 - Production Setup)**

### 9. **Domain DNS Configuration**
**What I need from you:**
- Add DNS records for keeper.tools

**Records needed:**
- A record: `keeper.tools` → Vercel IP
- CNAME: `api.keeper.tools` → Railway domain
- CNAME: `staging-api.keeper.tools` → Railway staging

**Why I need this:**
- Production domain setup
- API subdomain configuration
- SSL certificate generation

### 10. **Email Service (Optional)**
**What I need:**
- Email service for notifications (Resend/SendGrid)

**Options:**
- Resend API key (recommended, $0/month for 3k emails)
- SendGrid API key  
- Or just use Gmail SMTP for now

**Why I need this:**
- Daily report emails
- Task notifications  
- System alerts

---

## 📅 **PHASE 4 NEEDS (Week 4 - Review Scraping)**

### 11. **Review Platform Access**
**What I need:**
- Google Business Profile URL (for review scraping)
- Yelp business URL
- Facebook business page URL (optional)

**Why I need this:**
- Review monitoring system
- Competitor mention detection
- Sentiment analysis

---

## 🔐 **Environment Variables Template**

I'll need these in a `.env` file format:

```bash
# Square API
SQUARE_APPLICATION_ID=your_app_id_here
SQUARE_APPLICATION_SECRET=your_secret_here
SQUARE_ACCESS_TOKEN=sandbox_token_here  # For testing
SQUARE_ENVIRONMENT=sandbox  # Change to production later

# Supabase
SUPABASE_URL=your_project_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# AI APIs
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Redis
UPSTASH_REDIS_REST_URL=your_redis_url
UPSTASH_REDIS_REST_TOKEN=your_redis_token

# Email (later)
RESEND_API_KEY=your_resend_key

# App Config
NEXTAUTH_SECRET=your_random_secret_here
NEXTAUTH_URL=http://localhost:3000  # Change for production
```

---

## 🎯 **What I'll Ask For When I Need It**

I'll be proactive and ask for these things specifically when I hit each development phase:

### **This Week (I'll ask for):**
- "Ray, I need your Square sandbox credentials to test OAuth"
- "Ray, set up the Supabase project so I can create the database schema"  
- "Ray, I need your wife's spa data export to test matching"

### **Next Week (I'll ask for):**
- "Ray, time to deploy - need Railway and Vercel setup"
- "Ray, let's configure the keeper.tools domain DNS"

### **Later (I'll ask for):**
- "Ray, need access to review platforms for scraping setup"
- "Ray, ready to switch from sandbox to production Square API"

---

## 🚀 **Priority Order**

**Start immediately with:**
1. Square Developer Account + Sandbox keys
2. Supabase project
3. OpenAI API key

**Everything else I'll ask for as we reach those phases!**

I'll be specific about what I need and when, so you can prepare ahead of time or get it right when I need it.

**Ready to start as soon as you get the Square + Supabase + OpenAI credentials!** 🎯