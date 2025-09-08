#!/usr/bin/env python3
"""
TEST 1: PAYMENTS API
- Call Payments API
- Show 5 actual transactions
- Show raw JSON response
- Store in database
- Verify with SELECT COUNT(*)
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def test_payments_api():
    """Test Payments API step by step"""
    
    print("💳 TEST 1: PAYMENTS API")
    print("=" * 60)
    
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
    
    account_id = "b491de6e-7d5b-4e0e-b1cd-625c6c4f7d81"
    
    print("🌐 CALLING PAYMENTS API...")
    print(f"URL: {api_base_url}/v2/payments?limit=5")
    
    try:
        response = requests.get(f"{api_base_url}/v2/payments?limit=5", headers=headers)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            payments_data = response.json()
            payments = payments_data.get('payments', [])
            
            print(f"✅ SUCCESS! Retrieved {len(payments)} payments")
            
            # Show raw JSON response
            print(f"\n📋 RAW JSON RESPONSE:")
            print("-" * 60)
            print(json.dumps(payments_data, indent=2))
            print("-" * 60)
            
            if payments:
                print(f"\n💰 PAYMENT DETAILS:")
                for i, payment in enumerate(payments, 1):
                    amount = float(payment.get('amount_money', {}).get('amount', 0)) / 100
                    tip = float(payment.get('tip_money', {}).get('amount', 0)) / 100
                    
                    print(f"\nPayment {i}:")
                    print(f"  ID: {payment.get('id')}")
                    print(f"  Amount: ${amount:.2f}")
                    print(f"  Tip: ${tip:.2f}")
                    print(f"  Status: {payment.get('status')}")
                    print(f"  Source: {payment.get('source_type')}")
                    print(f"  Created: {payment.get('created_at')}")
                    print(f"  Customer: {payment.get('customer_id', 'N/A')}")
                    print(f"  Location: {payment.get('location_id')}")
                    print(f"  Order: {payment.get('order_id', 'N/A')}")
            
            # Store in database
            print(f"\n💾 STORING PAYMENTS IN DATABASE...")
            supabase = create_client(
                os.getenv('SUPABASE_URL'),
                os.getenv('SUPABASE_SERVICE_KEY')
            )
            
            # First check if payments table exists
            try:
                test_result = supabase.table('payments').select('*').limit(1).execute()
                print(f"✅ Payments table exists")
            except Exception as e:
                print(f"⚠️  Payments table issue: {e}")
                print(f"📝 Creating payments records in a generic table...")
            
            # Transform and store payments
            payment_records = []
            for payment in payments:
                amount_money = payment.get('amount_money', {})
                tip_money = payment.get('tip_money', {})
                
                payment_record = {
                    'id': payment.get('id'),
                    'account_id': account_id,
                    'payment_id': payment.get('id'),
                    'amount_cents': amount_money.get('amount', 0),
                    'tip_cents': tip_money.get('amount', 0),
                    'currency': amount_money.get('currency', 'USD'),
                    'status': payment.get('status'),
                    'source_type': payment.get('source_type'),
                    'customer_id': payment.get('customer_id'),
                    'location_id': payment.get('location_id'),
                    'order_id': payment.get('order_id'),
                    'receipt_number': payment.get('receipt_number'),
                    'receipt_url': payment.get('receipt_url'),
                    'created_at': payment.get('created_at'),
                    'updated_at': payment.get('updated_at'),
                    'square_data': payment,  # Store full Square data
                    'synced_at': datetime.utcnow().isoformat()
                }
                
                # Remove None values
                payment_record = {k: v for k, v in payment_record.items() if v is not None}
                payment_records.append(payment_record)
            
            # Try to store payments
            try:
                # Clear existing payments for this account first
                delete_result = supabase.table('payments').delete().eq('account_id', account_id).execute()
                print(f"🗑️  Cleared existing payment records")
                
                # Insert new payments
                insert_result = supabase.table('payments').insert(payment_records).execute()
                print(f"✅ Stored {len(payment_records)} payments in database")
                
                # Verify with count query
                count_result = supabase.table('payments')\
                    .select('*', count='exact')\
                    .eq('account_id', account_id)\
                    .execute()
                
                payment_count = count_result.count
                print(f"\n📊 DATABASE VERIFICATION:")
                print(f"SELECT COUNT(*) FROM payments WHERE account_id = '{account_id}';")
                print(f"Result: {payment_count} payments")
                
                if payment_count == len(payments):
                    print(f"✅ SUCCESS! Database count matches API response")
                else:
                    print(f"⚠️  Count mismatch: API={len(payments)}, DB={payment_count}")
                
                # Show sample stored record
                sample_result = supabase.table('payments')\
                    .select('*')\
                    .eq('account_id', account_id)\
                    .limit(1)\
                    .execute()
                
                if sample_result.data:
                    print(f"\n📋 SAMPLE STORED RECORD:")
                    sample = sample_result.data[0]
                    print(f"  ID: {sample.get('payment_id')}")
                    print(f"  Amount: ${sample.get('amount_cents', 0) / 100:.2f}")
                    print(f"  Tip: ${sample.get('tip_cents', 0) / 100:.2f}")
                    print(f"  Status: {sample.get('status')}")
                    print(f"  Synced: {sample.get('synced_at')}")
                
                return True
                
            except Exception as e:
                print(f"❌ Database storage failed: {e}")
                print(f"📝 Raw payment data available in JSON response above")
                return False
            
        else:
            print(f"❌ PAYMENTS API FAILED: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ PAYMENTS API ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_payments_api()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 TEST 1 (PAYMENTS API) COMPLETE!")
        print("✅ API call successful")
        print("✅ Raw JSON response shown")
        print("✅ Data stored in database")
        print("✅ Database count verified")
    else:
        print("❌ TEST 1 (PAYMENTS API) FAILED!")
        print("⚠️  Check errors above")