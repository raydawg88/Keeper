# Claude Development Rules for Keeper

## What Keeper Is

**Keeper: The AI Engine That Keeps Your Customers and Grows Their Value**

### What Keeper Does
Keeper is an AI-powered decision engine for ANY business using Square. We help you keep the customers you have, raise their lifetime value, and optimize your team's performance - all by showing you exactly who to focus on and what to do about it.

Every morning, you wake up to specific names, specific actions, and specific dollar amounts. Not analytics. Not reports. Actual decisions with actual outcomes.

### The Problem We Solve
Businesses are losing customers they don't even know are at risk. Employees are underperforming in ways that go unnoticed. Revenue is leaking everywhere, but nobody knows where or how to stop it.

Square shows you data. Keeper shows you decisions:
- **Customer Retention:** "Sarah Chen hasn't been in for 47 days. Call her today with this script to save $400/month"
- **Lifetime Value Growth:** "These 12 customers never buy add-ons. Here's exactly how to change that"
- **Employee Optimization:** "Jennifer's retention rate is 12% while the team averages 78%. Here's your action plan"

### How Keeper Works
1. **Connect Square** - One-click OAuth, we analyze your entire business history
2. **20+ Models Compete** - Our "model tournament" runs over 20 data science models simultaneously to find what matters most
3. **Daily Decisions** - Get 5-10 prioritized tasks each morning with names, scripts, and ROI
4. **Track Impact** - See exactly how your actions affect revenue, retention, and growth

### Built for Every Square Business
Whether you run a coffee shop, salon, restaurant, gym, retail store, or any other Square-powered business - Keeper works. We adapt our analysis to your specific business model, finding the patterns that matter for YOUR customers and YOUR team.

### Why Keeper Is Different
- **Names, Not Numbers:** We don't tell you "churn is up" - we tell you "Call Jennifer Park before she leaves"
- **Actions, Not Analytics:** Every insight comes with a specific thing to do, not just something to know
- **Team Performance:** We analyze every employee's impact on revenue, retention, and customer satisfaction
- **Network Intelligence:** Every Keeper customer makes every other customer smarter through pattern sharing

### The Core Focus
- **Keep Customers:** Know who's at risk before they leave. Get specific retention strategies that work.
- **Raise Lifetime Value:** Identify exactly which customers can spend more and how to make it happen.
- **Optimize Your Team:** See which employees drive revenue and retention, who needs coaching, and what specific changes to make.

### Business Model
- $99/month for the owner seat (full insights, reports, complete visibility)
- $49.99/month per additional seat (managers, staff - task-focused view)
- Average ROI: 3,900% (find $3,000+ monthly for $99 investment)

### The Technology
- 20+ data science models running in parallel
- 97%+ accuracy in customer matching and predictions
- Machine learning that gets smarter with every customer
- Real-time sync with Square for always-current decisions

### Current Status
- Live and generating revenue insights daily
- Proven to find $3,000+ in monthly opportunities
- Architecture ready for 10,000+ accounts
- Square App Marketplace integration underway

### The Vision
Every Square business loses money they don't know about. Customers slip away silently. Employees underperform invisibly. Opportunities pass by unnoticed.

Keeper changes that. We turn your Square data into a daily playbook for keeping customers, growing their value, and optimizing your team.

### The Bottom Line
Keeper doesn't just analyze your business. We tell you exactly how to grow it.
Customer by customer. Employee by employee. Dollar by dollar.

That's Keeper. That's keeper.tools.

---

## Core Development Philosophy

**Never do the quick thing, always think through the problem, come up with the best solution, then execute, this way we don't keep making fixes over and over again, we spend the time thinking through all the angles before we fix the problem.**

<<<<<<< Updated upstream
=======
**ALWAYS FOLLOW THE PLAN** - The planning markdown files in this repository represent weeks of careful architecture planning. NEVER deviate from the established plans. ALWAYS implement exactly what is specified in the planning documents. If you're unsure about implementation details, ask for clarification rather than improvising.

## CRITICAL RULE: REAL DATA ONLY

1. NEVER use mock/fake/simulated data
2. ALWAYS use real production data from Bashful Beauty
3. If real data breaks something, report the error
4. If real data is missing, ask for it
5. NEVER substitute fake data to make things "work"
6. Performance metrics ONLY count on real data
7. All testing must be on real customer/employee data

Mock data is ONLY allowed when explicitly requested with the phrase "use mock data for this test"

>>>>>>> Stashed changes
## Additional Rules

1. **Always hide credentials from public view** - Never commit or display sensitive information
2. **Use read-only permissions when possible** - We don't need to write anything to external services, just read data
3. **Update GitHub when finishing something** - Always commit work when a feature is complete
4. **When we mark a task as completed ALWAYS update github** - This is a strict rule, no exceptions
5. **ALWAYS read the latest official documentation** - For ANY service we use to build Keeper, ALWAYS read the latest official documentation first before making assumptions or implementing solutions. Never assume API behavior - verify with current docs.
5. **Verify connection and authentication** - Test basic connectivity before building complex features
6. **Follow existing code patterns** - Look at how the codebase already handles similar functionality
7. **Build incrementally** - Create simple working versions first, then enhance with advanced features
8. **Include proper error handling** - Account for API failures, rate limits, and edge cases
9. **Log progress for long operations** - Show users what's happening during data syncs and migrations
10. **Create reusable components** - Build utilities that can be used across the application

## Data Sync Guidelines

- Always implement rate limiting for external APIs
- Use pagination for large datasets
- Include retry logic with exponential backoff
- Validate data before inserting into database
- Track sync status and provide meaningful error messages
- Support incremental syncs to avoid reprocessing all data

## Testing Requirements

- Test with sandbox data before production
- Verify edge cases (empty responses, API errors, network failures)
- Validate data transformations
- Test rate limiting and retry mechanisms
- Ensure proper cleanup of test data

## MCP Integration Guidelines

- **Always use Supabase MCP** for database operations when available - Direct SQL execution, table management, and data queries
- **Always use Square MCP** for Square API operations when available - Customer data, payments, appointments, and analytics
- MCP tools provide better error handling and optimized performance compared to direct API calls
- Leverage MCP pagination and rate limiting features for large datasets
- Use MCP tools for complex data transformations and bulk operations

## Keeper Advanced Insight Engine

- **Reference Architecture:** The advanced insight engine is based on the proven tournament system from [DropSet](https://github.com/raydawg88/DropSet)
- **20-Round Progressive Analysis:** Foundation → Advanced AI → Intelligence Mastery → Complete Intelligence rounds
- **30+ AI Models:** Random Forest, LSTM, Transformers, Ensemble Methods, Bayesian Networks, XGBoost, and more
- **Tournament System:** Multiple models compete to find the most valuable insights, similar to DropSet's approach
- **Golden Nuggets:** Each insight must have dollar value, confidence score, implementation plan, and evidence
- **Target Performance:** Generate $3,000+ in actionable revenue opportunities with 80%+ average confidence
- **Universal Business Focus:** Adapted from gym member churn prediction to universal business optimization for all Square-powered businesses (restaurants, retail, services, salons, fitness, etc.)
- **Multi-Platform Future:** Designed to expand beyond Square to Clover, QuickBooks, and other business management platforms