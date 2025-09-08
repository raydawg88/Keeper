# KEEPER LESSONS LEARNED - CRITICAL FAILURES TO NEVER REPEAT

## UTILIZATION CALCULATION DISASTERS
### ❌ WRONG: Dividing by theoretical years of time
- **Calculated**: 7.8% utilization (Laine working 3 hours/week)
- **Reality**: 60% utilization per Square's actual data
- **LESSON**: Use business hours, not 24/7/365
- **FORMULA**: (service_hours / (spa_open_hours * days_worked)) * 100

### ❌ WRONG: Not accounting for business hours
- **Assumed**: 168 hours/week available
- **Reality**: ~60 hours/week (spa hours)
- **LESSON**: Every business has operating hours
- **CHECK**: Get business hours from Locations API

### ❌ WRONG: Still can't match Square's utilization formula
- **My Best**: 29.1% (Laine) vs Square's 60%
- **Problem**: Still 2x off after corrections
- **LESSON**: Need to reverse-engineer Square's exact logic
- **TODO**: Find Square's utilization calculation method

## EMPLOYEE DATA FAILURES
### ❌ WRONG: Including all historical employees
- **Found**: 46 "employees" (everyone ever employed)
- **Reality**: 15-16 active employees
- **LESSON**: Filter by last service date < 60 days
- **NEVER**: Show fired/quit employees in current reports

### ❌ WRONG: Not combining rehire IDs
- **Problem**: Laine had 2 IDs (quit and rehired)
- **Impact**: Appointments split, undercount performance
- **LESSON**: Detect and merge duplicate employee IDs
- **CHECK**: Look for same name, different IDs

## COMPENSATION MODEL FAILURES
### ❌ WRONG: Assuming role = pay type
- **Assumed**: All estheticians on commission
- **Reality**: Tayler chose hourly, others commission
- **LESSON**: Use data patterns, not job titles
- **DETECT**: wages + appointments = service provider type

## DATA COMPLETENESS FAILURES
### ❌ WRONG: Claiming success with 19% of data
- **Retrieved**: 10,590 of 55,236 appointments
- **Claimed**: "Mission accomplished!"
- **LESSON**: Need ALL data before analysis
- **RULE**: Never analyze partial datasets

### ❌ WRONG: Not handling API pagination
- **Got**: 10 bookings (first page only)
- **Reality**: 55,236 total appointments
- **LESSON**: Always check for pagination/cursors
- **MUST**: Retrieve ALL pages, not just first

### ❌ WRONG: Still incomplete appointment data
- **Current**: 36,940 appointments (67% of expected)
- **Target**: 55,236 total appointments
- **LESSON**: May need different date ranges or search strategies
- **ISSUE**: Business may not have 55K appointments, or they're in different time periods

## API INTEGRATION FAILURES
### ❌ WRONG: Assuming 404 = doesn't exist
- **Said**: "No subscriptions found"
- **Reality**: $55/month memberships exist
- **LESSON**: Try multiple endpoints/approaches
- **CHECK**: Catalog, Invoices, recurring patterns

### ❌ WRONG: Saying "blocked by location_id"
- **Problem**: Cash Drawer needs location_id
- **Solution**: Just call Locations API first
- **LESSON**: Chain API calls to get required data
- **NEVER**: Declare blocked without trying

### ❌ WRONG: Assuming no cash drawer usage
- **Assumed**: "Spa likely doesn't use physical cash drawers (card payments only)"
- **Reality**: Business DOES use cash drawer (you confirmed this)
- **LESSON**: NEVER assume business operations without data
- **FIX**: Need to check cash payments in Payments API, not just drawer shifts

## BUSINESS LOGIC FAILURES
### ❌ WRONG: One-size-fits-all approach
- **Assumed**: All businesses work the same
- **Reality**: Spa ≠ Restaurant ≠ Retail ≠ Gym
- **LESSON**: Detect business type, adapt logic
- **BUILD**: Flexible architecture for each vertical

## CSV ANTI-PATTERN
### ❌ NEVER: Suggest CSV imports as solution
- **Wrong**: "We'll use CSV data for missing employees"
- **Right**: Find data in Square API or fix integration
- **LESSON**: CSV = manual process = not a product
- **RULE**: API-only for production features

## ASSUMPTION FAILURES
### ❌ WRONG: Making assumptions about business operations
- **Cash Drawer**: Assumed spa doesn't use cash
- **Business Hours**: Assumed 9am-7pm without checking
- **Employee Status**: Assumed API status = current status
- **LESSON**: GET DATA, don't assume
- **RULE**: If in doubt, ask or find the data

## TESTING REQUIREMENTS
### ✅ RIGHT: Test with real data
- Show actual API responses
- Verify counts match expected
- Compare to ground truth (screenshots)
- **NEVER**: Use mock data in production

## THE PATTERNS TO REMEMBER

### When Square Data Seems Wrong:
1. Check if you're using the right time period
2. Check if you're accounting for business hours
3. Check if you need to combine multiple IDs
4. Check if you're paginating properly
5. Compare to Square's own calculations

### When API "Doesn't Work":
1. Try different endpoints
2. Check for required parameters
3. Look for data in related APIs
4. Don't assume feature doesn't exist

### When Math Seems Off:
1. Get ground truth from Square reports
2. Match their calculation method
3. Account for business reality
4. Never show impossible numbers (>100% or <5% utilization)

### When Making Business Assumptions:
1. **STOP** - Don't assume
2. **ASK** - Get clarification from user
3. **DATA** - Find evidence in APIs
4. **VERIFY** - Cross-check with multiple sources

## MANDATORY CHECKS BEFORE CLAIMING SUCCESS
- [ ] Retrieved 100% of expected data
- [ ] Math matches Square's own reports
- [ ] No former employees in current analysis
- [ ] Utilization between 40-80% for active staff
- [ ] All employee IDs mapped to names
- [ ] Business hours accounted for
- [ ] No CSV workarounds used
- [ ] No assumptions about business operations
- [ ] Cash transactions verified if cash drawer exists
- [ ] All API endpoints properly explored

## IMMEDIATE ACTIONS NEEDED
1. **Fix Cash Drawer**: Look for cash payments in Payments API, not just drawer shifts
2. **Fix Utilization**: Find Square's exact calculation method
3. **Complete Data**: Get remaining appointments or verify expected total
4. **Stop Assumptions**: Ask questions instead of guessing

## BEFORE STARTING ANY NEW TASK:
**READ THIS FILE FIRST** - Don't repeat these mistakes!