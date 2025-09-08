#!/usr/bin/env python3
"""
STEP 1: Generate Square OAuth URL for Bashful Beauty
"""

import os
from dotenv import load_dotenv
from urllib.parse import urlencode
import uuid

load_dotenv()

def generate_oauth_url():
    client_id = os.getenv('SQUARE_APPLICATION_ID')
    oauth_base_url = 'https://connect.squareup.com'
    
    # Generate secure state parameter
    state = str(uuid.uuid4())
    
    # COMPREHENSIVE READ-ONLY scopes for Keeper - ALL business data viewing
    # NO WRITE permissions - Keeper only analyzes, never modifies
    scopes = [
        'CUSTOMERS_READ',
        'PAYMENTS_READ', 
        'ORDERS_READ',
        'APPOINTMENTS_READ',
        'APPOINTMENTS_ALL_READ',
        'APPOINTMENTS_BUSINESS_SETTINGS_READ',
        'ITEMS_READ',
        'INVENTORY_READ', 
        'EMPLOYEES_READ',
        'TIMECARDS_READ',
        'TIMECARDS_SETTINGS_READ',
        'MERCHANT_PROFILE_READ',
        'CASH_DRAWER_READ',
        'INVOICES_READ',
        'LOYALTY_READ',
        'SUBSCRIPTIONS_READ',
        'DISPUTES_READ',
        'GIFTCARDS_READ',
        'ONLINE_STORE_SITE_READ'
    ]
    
    # OAuth parameters
    params = {
        'client_id': client_id,
        'scope': ' '.join(scopes),
        'state': state,
        'response_type': 'code'
    }
    
    auth_url = f"{oauth_base_url}/oauth2/authorize?" + urlencode(params)
    
    print("🚀 SQUARE OAUTH URL FOR BASHFUL BEAUTY")
    print("=" * 80)
    print(auth_url)
    print("=" * 80)
    print(f"State: {state}")
    print()
    print("📝 INSTRUCTIONS:")
    print("1. Copy the URL above")
    print("2. Open in your browser")
    print("3. Log in to Bashful Beauty Square account") 
    print("4. Click 'Allow' to authorize Keeper")
    print("5. Copy the authorization code from redirect URL")
    print("6. Come back here for Step 2")
    
    return auth_url, state

if __name__ == "__main__":
    generate_oauth_url()