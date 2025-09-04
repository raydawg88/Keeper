# Keeper - Square Data Decision Engine

## Overview
Keeper transforms Square POS data into actionable business decisions with dollar values attached. We find hidden revenue, prevent churn, and optimize operations for SMBs.

## Core Philosophy
- **BMAD**: Build small, Measure everything, Analyze results, Deploy incrementally
- **Money First**: Every insight must have a dollar value
- **Accuracy Over Volume**: Better to show 3 correct insights than 10 guesses
- **Human Context**: Combine Square data with owner knowledge for non-obvious patterns

## Quick Start
1. Clone repository
2. Set up Square Sandbox credentials
3. Configure Supabase project
4. Deploy base infrastructure
5. Follow TESTING_PROTOCOL.md for BMAD cycles

## File Structure
```
dropset/
├── agents/           # Individual agent modules
├── api/             # FastAPI backend
├── components/      # React components
├── lib/            # Shared utilities
├── pipelines/      # Data processing
├── tests/          # Test suites
└── docs/           # These specification files
```

## Development Order
1. Week 1: Data Pipeline (Square OAuth, sync, storage)
2. Week 2: Analysis Engine (RFM, modifiers, patterns)
3. Week 3: Agent System (7 specialized agents)
4. Week 4: Interface (dashboards, reports, tasks)

## Success Criteria
- Finds $3,000+ in hidden revenue for test spa
- 97%+ accuracy on customer matching
- 75%+ confidence on all insights
- Zero obvious/generic insights

## Contact
Ray Hernandez - ray.hernandez@gmail.com
Repository: github.com/raydawg88/Keeper