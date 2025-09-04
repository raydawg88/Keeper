# Keeper Project Structure

## 📂 Directory Organization

```
/keeper
├── .env                    # Environment variables (gitignored)
├── .env.example           # Environment template
├── keeper-env/           # Python virtual environment
│
├── /src                   # Main source code
│   ├── /app              # Next.js frontend
│   ├── /api              # FastAPI backend
│   │   └── /routes       # API endpoint routes
│   ├── /agents           # 8 specialized agents
│   ├── /lib              # Shared utilities
│   │   ├── /db           # Database operations
│   │   │   ├── square_data_sync.py    # Square API sync
│   │   │   └── customer_matching.py   # 97%+ accuracy matching
│   │   ├── square_oauth.py            # OAuth integration
│   │   ├── quick_health_check.py      # Environment validation
│   │   └── update_session_state.py    # Development tracking
│   └── /components       # React components
│
├── /supabase            # Database management
│   ├── /migrations      # Database schema changes
│   │   ├── *.sql       # All schema update files
│   └── /functions       # Edge functions
│
├── /docs               # All planning documents
│   ├── claude.md                      # Complete context
│   ├── DEVELOPMENT_STATE.md           # Current progress
│   ├── architecture-dropset.md       # Technical architecture
│   ├── agents-dropset.md             # 8 agent specifications
│   ├── api-contracts-final.md        # API endpoints
│   ├── data-pipeline-final.md        # Data sync specs
│   ├── matching-spec.md              # Customer matching
│   ├── insight-engine-dropset.md     # AI analysis
│   ├── network-learning-system.md    # Collective intelligence
│   ├── scale-architecture-final.md   # 1000+ account scaling
│   ├── square-api-resilience.md      # Rate limiting strategy
│   ├── testing-protocol-final.md     # Testing approach
│   └── user-stories-dropset.md       # What we're building
│
├── /test               # Test files and validation
│   ├── test_complete_setup.py        # Full integration test
│   ├── test_square_connection.py     # Square API test
│   ├── test_supabase_connection.py   # Database test
│   ├── test_oauth_*.py              # OAuth flow tests
│   └── create_test_account.py       # Test account creation
│
└── /test-data          # Real spa data for validation
```

## 🎯 Key Files by Function

### **Data Operations**
- `src/lib/db/square_data_sync.py` - Pulls customers/transactions from Square
- `src/lib/db/customer_matching.py` - 97%+ accuracy fuzzy matching
- `supabase/migrations/*.sql` - Database schema evolution

### **Authentication & Integration**
- `src/lib/square_oauth.py` - Business account connection
- Test Account: `27d755f9-87fd-40e8-a541-3a0478816395`

### **Development Workflow**
- `docs/claude.md` - Complete session context
- `docs/DEVELOPMENT_STATE.md` - Real-time progress tracking
- `src/lib/update_session_state.py` - Automated progress updates

### **Testing & Validation**
- `test/test_complete_setup.py` - Verify all integrations
- `src/lib/quick_health_check.py` - Fast environment validation

## 📋 Development Rules

1. **New Files Location**:
   - Agents: `src/agents/`
   - API endpoints: `src/api/routes/`
   - React components: `src/components/`
   - Database operations: `src/lib/db/`

2. **Always Maintain**:
   - Update `docs/DEVELOPMENT_STATE.md` after major progress
   - Test integrations with `test/test_complete_setup.py`
   - Commit frequently with descriptive messages

3. **Documentation First**:
   - Fetch latest docs before implementing external services
   - Update `docs/claude.md` with new API information
   - Keep session continuity information current

## 🚀 Current Status

**✅ Completed**:
- Square OAuth integration and test account creation
- Data sync pipeline (customers/transactions)
- Customer matching engine with embeddings
- Organized project structure

**🔄 Next**:
- Insight generation with dollar values
- Task management system
- Agent coordination system
- Frontend dashboard (Next.js)

---

**Ready to build the definitive SMB decision intelligence platform!** 🎯