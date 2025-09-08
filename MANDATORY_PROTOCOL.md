# MANDATORY PROTOCOL - MUST FOLLOW EVERY TIME

## SECTION 1: ABSOLUTE RULES (NEVER VIOLATE)

### Rule 1: NO FAKE DATA
- NEVER use mock, sample, or generated data
- NEVER create placeholder data
- NEVER simulate API responses
- If real data unavailable: STOP and report the issue
- Violation = IMMEDIATE RESET

### Rule 2: TEST EVERYTHING
- NEVER claim success without proof
- NEVER say "Updated!" without showing test results
- NEVER move to next task without verifying current task
- Pattern: CODE → TEST → SHOW OUTPUT → WAIT FOR CONFIRMATION

### Rule 3: NO CSV WORKAROUNDS
- CSV imports are BANNED except for initial comparison
- The product MUST work through API integration only
- If API doesn't work: FIX THE API, don't use CSV
- "We'll use CSV for now" = FORBIDDEN

### Rule 4: COMPLETE DATA RETRIEVAL
- If API returns 10 results but there are 10,000: PAGINATE
- NEVER accept first page as complete dataset
- ALWAYS verify counts match expected totals
- 10 bookings when expecting 55,000 = BROKEN

### Rule 5: DON'T ASSUME ABSENCE
- 404 doesn't mean "feature doesn't exist"
- Try multiple endpoints before declaring failure
- Check documentation for correct endpoint
- Empty result doesn't mean no data exists

## SECTION 2: CHECKPOINT PROTOCOL

### After EVERY Action:

**STATE**: "CHECKPOINT REACHED: [what was just done]"  
**SHOW**: Display proof of completion  
**TEST**: Run verification test  
**REPORT**: Show test results  
**WAIT**: "Awaiting CONTINUE command to proceed"  
**STOP**: Do nothing until user says "CONTINUE"

### Example:
**CHECKPOINT REACHED**: Added Payments API integration  
**PROOF**: [show code]  
**TEST**: Retrieved 5 payments totaling $385.23  
**VERIFICATION**: Database shows 5 records  
**Awaiting CONTINUE command to proceed**

## SECTION 3: API TESTING REQUIREMENTS

### For EVERY API Endpoint:
1. Show the EXACT API call made
2. Show the FULL response (or first 100 lines)
3. Check for pagination (cursor, next_page, has_more)
4. Compare count to expected (if known)
5. Store in database
6. Verify storage with SELECT COUNT(*)

### Pagination Requirement:
```python
# WRONG:
response = api.get_bookings(limit=10)
return response  # Only 10 results

# RIGHT:
all_bookings = []
cursor = None
while True:
    response = api.get_bookings(limit=200, cursor=cursor)
    all_bookings.extend(response.bookings)
    if not response.has_more:
        break
    cursor = response.cursor
return all_bookings  # ALL results
```

## SECTION 4: PROBLEM DETECTION

### Red Flags That Require IMMEDIATE STOP:

- Found 10 records but expecting thousands
- API returns "not found" for known features  
- Success rate below 50%
- Database has different count than API
- Any mention of using CSV as solution

### When Red Flag Detected:

1. **STOP** all work
2. **Report** the exact issue
3. **Show** what was expected vs what happened
4. **Ask** for guidance
5. **Do NOT** proceed
6. **Do NOT** work around with CSV

## SECTION 5: VERIFICATION REQUIREMENTS

### Before Claiming Any Feature Works:

- ✅ Real API call made (not mocked)
- ✅ Real data returned (not generated)
- ✅ Data stored in database
- ✅ Count verified against expected
- ✅ Can retrieve data back from database
- ✅ Works with pagination if applicable
- ✅ No CSV files involved

### The Success Template:
**FEATURE**: [Name]  
**API CALL**: [Exact endpoint and parameters]  
**RESPONSE**: [Actual data received]  
**RECORDS**: [Count] retrieved, [Count] expected  
**DATABASE**: [Count] stored successfully  
**VERIFICATION**: SELECT COUNT(*) = [Count]  
**STATUS**: ✅ Working | ❌ Failed | ⚠️ Partial

## SECTION 6: FORBIDDEN PHRASES

### NEVER say these without proof:

- "Successfully updated"
- "Everything is working"
- "Mission accomplished"
- "All tests complete"
- "Fully functional"
- "Integration complete"

### NEVER suggest these:

- "We can use CSV for now"
- "Let's import from the export"
- "We'll manually map the data"
- "Create a lookup table from CSV"

## SECTION 7: MANDATORY REPORTING

### After Each Work Session, Report:

**WORK COMPLETED:**
- [Specific task with proof]

**WORK REMAINING:**
- [Specific incomplete items]

**BLOCKING ISSUES:**
- [Problems preventing progress]

**DATA ACCURACY:**
- Expected records: [X]
- Actually retrieved: [Y]
- Percentage complete: [Z%]

**NEXT STEPS:**
- [Specific next action]
- [Wait for user confirmation]

## SECTION 8: RESET CONDITIONS

### You MUST reset and start over if:

- You've added features not requested
- You've used mock data
- You've suggested CSV solutions
- You've claimed false success
- You've skipped testing
- User says "RESET"

## SECTION 9: THE GOLDEN RULE

**Real Data → Real Testing → Real Proof → Real Success**

Anything else is failure.

## ENFORCEMENT

### Before EVERY response, ask yourself:

- Am I about to use fake data? **STOP**
- Am I about to claim untested success? **STOP**
- Am I about to suggest CSV? **STOP**
- Am I about to skip pagination? **STOP**
- Am I about to assume something doesn't exist? **STOP**

If any answer is YES: **STOP** and follow this protocol instead.