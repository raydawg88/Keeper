#!/usr/bin/env python3
"""
Inspect the transaction and appointment data to understand customer linking
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from collections import Counter

# Load environment variables
load_dotenv()

def inspect_transaction_links():
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    account_id = "b491de6e-7d5b-4e0e-b1cd-625c6c4f7d81"
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    print("🔍 ANALYZING DATA RELATIONSHIPS...")
    
    # Get sample data
    customers = supabase.table('customers').select('*').eq('account_id', account_id).limit(10).execute()
    appointments = supabase.table('appointments').select('*').eq('account_id', account_id).limit(10).execute()
    transactions = supabase.table('transactions').select('*').eq('account_id', account_id).limit(10).execute()
    
    print("\n📊 CUSTOMERS SAMPLE:")
    for customer in customers.data[:3]:
        print(f"  ID: {customer.get('id')}")
        print(f"  Square ID: {customer.get('square_id')}")
        print(f"  Name: {customer.get('name')}")
        print("  ---")
    
    print("\n📅 APPOINTMENTS SAMPLE:")
    for appointment in appointments.data[:3]:
        print(f"  ID: {appointment.get('id')}")
        print(f"  Customer ID: {appointment.get('customer_id')}")
        print(f"  Start: {appointment.get('start_at')}")
        print(f"  Status: {appointment.get('status')}")
        print("  ---")
    
    print("\n💰 TRANSACTIONS SAMPLE:")
    for transaction in transactions.data[:3]:
        print(f"  ID: {transaction.get('id')}")
        print(f"  Customer ID: {transaction.get('customer_id')}")
        print(f"  Amount: ${transaction.get('amount_cents', 0) / 100:.2f}")
        print(f"  Status: {transaction.get('status')}")
        print("  ---")
    
    # Check for customer_id links
    transaction_customer_ids = [t.get('customer_id') for t in transactions.data if t.get('customer_id')]
    appointment_customer_ids = [a.get('customer_id') for a in appointments.data if a.get('customer_id')]
    
    print(f"\n🔗 LINKING ANALYSIS:")
    print(f"Transactions with customer_id: {len(transaction_customer_ids)}/{len(transactions.data)}")
    print(f"Appointments with customer_id: {len(appointment_customer_ids)}/{len(appointments.data)}")
    
    # Check if appointment customer_ids match any customer square_ids
    customer_square_ids = set(c.get('square_id') for c in customers.data if c.get('square_id'))
    appointment_matches = set(appointment_customer_ids) & customer_square_ids
    transaction_matches = set(transaction_customer_ids) & customer_square_ids
    
    print(f"Appointment customer_id matches with customer square_id: {len(appointment_matches)}")
    print(f"Transaction customer_id matches with customer square_id: {len(transaction_matches)}")
    
    # Sample the matching data
    if appointment_customer_ids:
        print(f"\nSample appointment customer_ids: {appointment_customer_ids[:5]}")
    if transaction_customer_ids:
        print(f"Sample transaction customer_ids: {transaction_customer_ids[:5]}")
    print(f"Sample customer square_ids: {list(customer_square_ids)[:5]}")

if __name__ == "__main__":
    inspect_transaction_links()