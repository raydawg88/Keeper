# Claude Development Rules for Keeper

## Core Development Philosophy

**Never do the quick thing, always think through the problem, come up with the best solution, then execute, this way we don't keep making fixes over and over again, we spend the time thinking through all the angles before we fix the problem.**

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