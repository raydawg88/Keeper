#!/usr/bin/env python3
"""
Extract real employee data from Bashful Beauty transactions
"""

from dotenv import load_dotenv
load_dotenv()
import pandas as pd
from incremental_loader import IncrementalDataLoader

def extract_real_employees():
    """Extract real employee information"""
    print("👥 EXTRACTING REAL BASHFUL BEAUTY EMPLOYEE DATA")
    print("=" * 50)
    
    loader = IncrementalDataLoader('b491de6e-7d5b-4e0e-b1cd-625c6c4f7d81')
    customers_df, appointments_df, transactions_df, stats = loader.load_incremental_data(full_refresh=True)

    print(f"🏢 REAL EMPLOYEE DATA FROM TRANSACTIONS:")
    employee_ids = transactions_df['employee_id'].dropna().unique()
    print(f"   Total Employees Found: {len(employee_ids)}")
    
    print(f"\n👨‍💼 REAL EMPLOYEE IDs (First 10):")
    for i, emp_id in enumerate(employee_ids[:10], 1):
        # Count transactions per employee
        emp_transactions = len(transactions_df[transactions_df['employee_id'] == emp_id])
        emp_revenue = transactions_df[transactions_df['employee_id'] == emp_id]['amount_cents'].sum() / 100
        print(f"   {i}. {emp_id} ({emp_transactions} transactions, ${emp_revenue:,.2f} revenue)")

    print(f"\n💰 REAL REVENUE DATA:")
    total_revenue = transactions_df['amount_cents'].sum() / 100
    avg_transaction = transactions_df['amount_cents'].mean() / 100
    total_tips = transactions_df['tip_cents'].sum() / 100
    
    print(f"   Total Revenue: ${total_revenue:,.2f}")
    print(f"   Average Transaction: ${avg_transaction:.2f}")
    print(f"   Total Tips: ${total_tips:.2f}")
    print(f"   Tip Rate: {(total_tips/total_revenue)*100:.1f}%")

    print(f"\n📅 REAL SERVICE DATA:")
    if not appointments_df.empty:
        service_ids = appointments_df['service_variation_id'].dropna().unique()
        print(f"   Total Services: {len(service_ids)}")
        print(f"   Sample Services: {list(service_ids[:5])}")
    
    return employee_ids, total_revenue

if __name__ == "__main__":
    extract_real_employees()