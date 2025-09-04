# Square OAuth Setup Instructions

## 🎯 What We Just Built

Complete Square OAuth integration that allows businesses to connect their Square accounts to Keeper for data analysis.

## 📋 Required Setup Steps

### 1. Create OAuth Sessions Table
Run this SQL in your Supabase dashboard:

```sql
CREATE TABLE IF NOT EXISTS oauth_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    state VARCHAR(64) UNIQUE NOT NULL,
    redirect_uri TEXT NOT NULL,
    business_name TEXT,
    account_id UUID REFERENCES accounts(id),
    status VARCHAR(20) DEFAULT 'pending',
    error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE
);
```

### 2. Add Square Client Secret
Add this to your `.env` file (you'll get this from Square Developer Dashboard):
```
SQUARE_CLIENT_SECRET=your_client_secret_here
```

## 🔧 Testing the OAuth Flow

### Step 1: Generate OAuth URL
```bash
source keeper-env/bin/activate
python test_oauth_flow.py
```

This generates a secure OAuth URL that businesses can use to authorize Keeper.

### Step 2: Test Authorization (Manual)
1. Copy the generated OAuth URL
2. Open it in a browser  
3. Authorize the Keeper application
4. Copy the `code` and `state` from the callback URL

### Step 3: Handle Callback
```bash
python test_oauth_callback.py <code> <state>
```

This exchanges the authorization code for an access token and creates the business account.

## 📊 What Happens During OAuth

1. **URL Generation**: Creates secure authorization URL with state parameter
2. **User Authorization**: Business owner approves Keeper access to Square data
3. **Callback Handling**: Exchange authorization code for access token
4. **Account Creation**: Store encrypted tokens and business info in database
5. **Location Discovery**: Fetch all business locations for data sync

## 🔐 Security Features

- **State Parameter**: Prevents CSRF attacks
- **Session Tracking**: 10-minute expiration on OAuth sessions
- **Token Storage**: Access tokens stored securely (encrypt in production)
- **Merchant Validation**: Verify merchant info before account creation

## 🚀 Production Readiness Checklist

- [ ] Add token encryption for production database
- [ ] Set up production Square application 
- [ ] Configure real callback URLs (keeper.tools domain)
- [ ] Add webhook handling for token refresh
- [ ] Implement automatic token refresh before expiration

## 🎪 Integration Points

Once OAuth is complete:
- `square_oauth.py` - Core OAuth functionality
- `accounts` table - Business account storage
- `oauth_sessions` table - Security session tracking
- Ready for data sync pipeline development

## 💡 Next Development Steps

1. **Data Sync Pipeline** - Pull customers and transactions
2. **Customer Matching** - 97%+ accuracy fuzzy matching
3. **Insight Generation** - Find $3000+ revenue opportunities

---

**Ready to connect Ray's wife's spa as the first test business!** 🎯