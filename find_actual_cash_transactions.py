#!/usr/bin/env python3
"""
FIND ACTUAL CASH TRANSACTIONS
- Stop assuming - look for real cash payments
- Check Payments API for payment_source_type = "CASH"
- Show actual cash transaction data
- Fix my wrong assumption about no cash usage
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def find_actual_cash_transactions():
    """Find actual cash transactions in Payments API"""
    
    print("💵 FIND ACTUAL CASH TRANSACTIONS")
    print("=" * 50)
    print("FIXING MY WRONG ASSUMPTION:")
    print("❌ I said: 'Spa likely doesn't use cash drawers'")
    print("✅ You said: 'We DO use a cash drawer'")
    print("🔍 SOLUTION: Look for cash payments in Payments API")
    
    # Load comprehensive access token
    try:
        with open('/tmp/comprehensive_square_token.json', 'r') as f:
            token_data = json.load(f)
        access_token = token_data['access_token']
    except:
        print("❌ No comprehensive token found")
        return

    # Set up API call
    api_base_url = 'https://connect.squareup.com'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Square-Version': '2025-08-20',
        'Content-Type': 'application/json'
    }
    
    # Search for cash payments in different time periods
    time_periods = [
        ("Last 30 days", 30),
        ("Last 90 days", 90),
        ("Last 180 days", 180)
    ]
    
    total_cash_found = 0
    all_cash_payments = []
    
    for period_name, days_back in time_periods:
        print(f"\n📅 SEARCHING {period_name.upper()}")
        print("-" * 40)
        
        # Date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        start_str = start_date.strftime('%Y-%m-%dT00:00:00Z')
        end_str = end_date.strftime('%Y-%m-%dT23:59:59Z')
        
        # Get payments for this period
        cash_payments = []
        cursor = None
        
        while True:
            url = f"{api_base_url}/v2/payments?begin_time={start_str}&end_time={end_str}&limit=200"
            if cursor:
                url += f"&cursor={cursor}"
            
            try:
                response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    print(f"❌ API Error: {response.status_code}")
                    break
                
                data = response.json()
                payments = data.get('payments', [])
                cursor = data.get('cursor')
                
                # Filter for cash payments
                for payment in payments:
                    # Check for cash payment sources
                    source_type = payment.get('source_type', '')
                    card_details = payment.get('card_details', {})
                    
                    # Look for cash indicators
                    is_cash = False
                    if source_type == 'CASH':
                        is_cash = True
                    elif 'cash' in str(payment).lower():
                        is_cash = True
                    elif card_details.get('entry_method') == 'MANUALLY_ENTERED' and not card_details.get('card'):
                        # Might be cash entered manually
                        is_cash = True
                    
                    if is_cash:
                        cash_payments.append(payment)
                
                if not cursor:
                    break
                    
            except Exception as e:
                print(f"❌ Error searching payments: {e}")
                break
        
        # Report results for this period
        if cash_payments:
            period_total = sum(float(p.get('total_money', {}).get('amount', 0)) / 100 for p in cash_payments)
            total_cash_found += period_total
            all_cash_payments.extend(cash_payments)
            
            print(f"✅ Found {len(cash_payments)} cash payments")
            print(f"💰 Total cash: ${period_total:,.2f}")
            
            # Show sample cash payments
            print(f"\nSample cash payments:")
            for i, payment in enumerate(cash_payments[:5], 1):
                payment_id = payment.get('id', 'N/A')[:12]
                amount = float(payment.get('total_money', {}).get('amount', 0)) / 100
                created_at = payment.get('created_at', '')
                date_str = datetime.fromisoformat(created_at.replace('Z', '+00:00')).strftime('%Y-%m-%d') if created_at else 'N/A'
                source_type = payment.get('source_type', 'Unknown')
                
                print(f"  {i}. ${amount:.2f} on {date_str} ({source_type}) [{payment_id}]")
        else:
            print(f"⚠️  No cash payments found in {period_name.lower()}")
            
            # Show sample payment methods to understand what we're seeing
            print(f"\nSample payment methods found:")
            try:
                # Get a few payments to see their structure
                url = f"{api_base_url}/v2/payments?begin_time={start_str}&end_time={end_str}&limit=10"
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    payments = data.get('payments', [])
                    
                    payment_methods = {}
                    for payment in payments[:10]:
                        source_type = payment.get('source_type', 'Unknown')
                        payment_methods[source_type] = payment_methods.get(source_type, 0) + 1
                    
                    for method, count in payment_methods.items():
                        print(f"    {method}: {count} payments")
                        
            except:
                pass
    
    # Final summary
    print(f"\n" + "=" * 50)
    if total_cash_found > 0:
        print(f"✅ CASH TRANSACTIONS FOUND!")
        print(f"Total cash payments: {len(all_cash_payments)}")
        print(f"Total cash amount: ${total_cash_found:,.2f}")
        print(f"✅ CONFIRMED: Business DOES use cash payments")
        
        # Save cash transaction data
        with open('/tmp/cash_transactions_found.json', 'w') as f:
            json.dump({
                'total_cash_payments': len(all_cash_payments),
                'total_cash_amount': total_cash_found,
                'search_periods': [p[0] for p in time_periods],
                'cash_payments': all_cash_payments[:50]  # Save first 50 for analysis
            }, f, indent=2)
        
        print(f"✅ Cash data saved: /tmp/cash_transactions_found.json")
        
    else:
        print(f"⚠️  NO CASH PAYMENTS FOUND")
        print(f"This could mean:")
        print(f"  • Cash payments use different source_type")
        print(f"  • Cash payments recorded differently")
        print(f"  • Need to search different time periods")
        print(f"  • Cash drawer shifts don't sync with payments")
        
        print(f"\n🔍 NEED TO INVESTIGATE:")
        print(f"  • Check Orders API for cash orders")
        print(f"  • Look at different payment source types")
        print(f"  • Check if cash recorded as manual payments")
    
    return len(all_cash_payments), total_cash_found

if __name__ == "__main__":
    cash_count, cash_total = find_actual_cash_transactions()
    
    print(f"\n📝 LESSON LEARNED:")
    print(f"NEVER assume business operations without checking the data!")
    print(f"Always verify assumptions with actual API data.")
    
    # Update lessons learned
    if cash_count == 0:
        print(f"\n⚠️  Still investigating cash transactions")
        print(f"Need to check Orders API or other endpoints")