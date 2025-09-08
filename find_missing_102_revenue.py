#!/usr/bin/env python3
"""
FIND MISSING $102 REVENUE - LASER FOCUS
- Current: $1,115.94 (COMPLETED payments)
- Target: $1,217.94 (Square's actual)
- Missing: $102.00 exactly
- Check tips, cash, gift cards, service fees, manual adjustments
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def find_missing_102_revenue():
    """Laser focus on finding the exact $102 revenue gap"""
    
    print("💰 FIND MISSING $102 REVENUE")
    print("=" * 40)
    print("SOLVED: Employees (correct), Appointments (correct)")
    print("ONLY ISSUE: Revenue gap")
    print("Current: $1,115.94")
    print("Target: $1,217.94") 
    print("Missing: $102.00")
    
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
    
    # Define September 2, 2025
    target_date = datetime(2025, 9, 2)
    start_str = target_date.strftime('%Y-%m-%dT00:00:00Z')
    end_str = (target_date + timedelta(days=1) - timedelta(seconds=1)).strftime('%Y-%m-%dT23:59:59Z')
    
    # ==============================================================
    # DETAILED PAYMENT BREAKDOWN - BASE vs TIPS
    # ==============================================================
    print(f"\n🔍 DETAILED PAYMENT BREAKDOWN")
    print("=" * 35)
    
    # Get all payments
    all_payments = []
    cursor = None
    
    while True:
        url = f"{api_base_url}/v2/payments?begin_time={start_str}&end_time={end_str}&limit=200"
        if cursor:
            url += f"&cursor={cursor}"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                payments = data.get('payments', [])
                all_payments.extend(payments)
                
                cursor = data.get('cursor')
                if not cursor:
                    break
            else:
                break
        except:
            break
    
    # Detailed breakdown
    completed_base_total = 0
    completed_tip_total = 0
    all_base_total = 0
    all_tip_total = 0
    cash_total = 0
    card_total = 0
    
    print(f"PAYMENT ANALYSIS:")
    print(f"{'#':<3} {'TIME':<8} {'STATUS':<10} {'TYPE':<4} {'BASE':<8} {'TIP':<8} {'TOTAL':<8}")
    print("-" * 60)
    
    for i, payment in enumerate(all_payments, 1):
        status = payment.get('status', 'Unknown')
        source_type = payment.get('source_type', 'Unknown')
        
        total_amount = float(payment.get('total_money', {}).get('amount', 0)) / 100
        tip_amount = float(payment.get('tip_money', {}).get('amount', 0)) / 100
        base_amount = total_amount - tip_amount
        
        created_time = payment.get('created_at', '')
        time_display = created_time[11:16] if created_time else 'N/A'
        
        print(f"{i:<3} {time_display:<8} {status:<10} {source_type:<4} ${base_amount:<7.2f} ${tip_amount:<7.2f} ${total_amount:<7.2f}")
        
        # Track totals
        all_base_total += base_amount
        all_tip_total += tip_amount
        
        if status == 'COMPLETED':
            completed_base_total += base_amount
            completed_tip_total += tip_amount
            
            if source_type == 'CASH':
                cash_total += total_amount
            elif source_type == 'CARD':
                card_total += total_amount
    
    print("-" * 60)
    print(f"COMPLETED PAYMENTS BREAKDOWN:")
    print(f"  Base amounts: ${completed_base_total:.2f}")
    print(f"  Tips: ${completed_tip_total:.2f}")
    print(f"  Total: ${completed_base_total + completed_tip_total:.2f}")
    print(f"  Cash: ${cash_total:.2f}")
    print(f"  Card: ${card_total:.2f}")
    
    print(f"\nALL PAYMENTS (including FAILED):")
    print(f"  Base amounts: ${all_base_total:.2f}")
    print(f"  Tips: ${all_tip_total:.2f}")
    print(f"  Total: ${all_base_total + all_tip_total:.2f}")
    
    print(f"\nTARGET ANALYSIS:")
    print(f"  Square target: $1,217.94")
    print(f"  COMPLETED total: ${completed_base_total + completed_tip_total:.2f}")
    print(f"  Gap: ${1217.94 - (completed_base_total + completed_tip_total):.2f}")
    
    # ==============================================================
    # CHECK FOR OTHER REVENUE SOURCES
    # ==============================================================
    print(f"\n🔍 OTHER REVENUE SOURCES")
    print("=" * 30)
    
    # Check gift card activity
    print(f"1. GIFT CARD ACTIVITY:")
    try:
        # Gift cards might be in different API
        gift_url = f"{api_base_url}/v2/gift-cards"
        # This might not work without specific gift card endpoints
        print("   Gift card API check needed...")
    except:
        print("   Gift card data not accessible")
    
    # Check refunds
    print(f"\n2. REFUNDS:")
    try:
        refunds_url = f"{api_base_url}/v2/refunds?begin_time={start_str}&end_time={end_str}"
        response = requests.get(refunds_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            refunds = data.get('refunds', [])
            refund_total = sum(float(r.get('amount_money', {}).get('amount', 0)) / 100 for r in refunds)
            print(f"   Refunds: {len(refunds)} totaling ${refund_total:.2f}")
        else:
            print(f"   Refunds API: {response.status_code}")
    except:
        print("   Refunds check failed")
    
    # Check orders for product sales
    print(f"\n3. PRODUCT/SERVICE BREAKDOWN:")
    try:
        search_body = {
            "location_ids": ["F3XKQZW5S5M0V"],
            "query": {
                "filter": {
                    "date_time_filter": {
                        "created_at": {
                            "start_at": start_str,
                            "end_at": end_str
                        }
                    },
                    "state_filter": {
                        "states": ["COMPLETED"]
                    }
                }
            },
            "limit": 200
        }
        
        response = requests.post(f"{api_base_url}/v2/orders/search", 
                               headers=headers, 
                               json=search_body)
        
        if response.status_code == 200:
            data = response.json()
            orders = data.get('orders', [])
            
            service_total = 0
            product_total = 0
            tax_total = 0
            discount_total = 0
            
            for order in orders:
                # Analyze line items
                line_items = order.get('line_items', [])
                for item in line_items:
                    base_price_money = item.get('base_price_money', {})
                    base_price = float(base_price_money.get('amount', 0)) / 100
                    quantity = int(item.get('quantity', 1))
                    item_total = base_price * quantity
                    
                    # Try to determine if service or product
                    item_name = item.get('name', 'Unknown')
                    if any(word in item_name.lower() for word in ['service', 'treatment', 'facial', 'massage']):
                        service_total += item_total
                    else:
                        product_total += item_total
                
                # Check taxes
                taxes = order.get('taxes', [])
                for tax in taxes:
                    tax_amount = float(tax.get('applied_money', {}).get('amount', 0)) / 100
                    tax_total += tax_amount
                
                # Check discounts
                discounts = order.get('discounts', [])
                for discount in discounts:
                    discount_amount = float(discount.get('applied_money', {}).get('amount', 0)) / 100
                    discount_total += discount_amount
            
            orders_total = sum(float(o.get('total_money', {}).get('amount', 0)) / 100 for o in orders)
            
            print(f"   COMPLETED orders: {len(orders)} = ${orders_total:.2f}")
            print(f"   Services: ${service_total:.2f}")
            print(f"   Products: ${product_total:.2f}")
            print(f"   Taxes: ${tax_total:.2f}")
            print(f"   Discounts: -${discount_total:.2f}")
            
            if abs(orders_total - 1217.94) < 0.01:
                print(f"   🎯 ORDERS MATCH TARGET EXACTLY!")
            
    except Exception as e:
        print(f"   Orders breakdown error: {e}")
    
    # ==============================================================
    # FINAL REVENUE RECONCILIATION
    # ==============================================================
    print(f"\n🎯 FINAL REVENUE RECONCILIATION")
    print("=" * 40)
    
    print(f"Square's Target: $1,217.94")
    print(f"COMPLETED Payments: ${completed_base_total + completed_tip_total:.2f}")
    print(f"COMPLETED Orders: ${orders_total if 'orders_total' in locals() else 'Unknown':.2f}")
    
    # Test different combinations
    scenarios = [
        ("COMPLETED Payments", completed_base_total + completed_tip_total),
        ("COMPLETED Orders", orders_total if 'orders_total' in locals() else 0),
        ("Base + Tips", completed_base_total + completed_tip_total),
        ("Cash + Card", cash_total + card_total)
    ]
    
    print(f"\nSCENARIO TESTING:")
    for scenario_name, amount in scenarios:
        gap = abs(amount - 1217.94)
        if gap < 0.01:
            print(f"  ✅ {scenario_name}: ${amount:.2f} - PERFECT MATCH!")
        else:
            print(f"  • {scenario_name}: ${amount:.2f} (gap: ${gap:.2f})")
    
    # Find the closest match
    closest = min(scenarios, key=lambda x: abs(x[1] - 1217.94))
    print(f"\nCLOSEST MATCH: {closest[0]} = ${closest[1]:.2f}")
    print(f"Gap: ${abs(closest[1] - 1217.94):.2f}")
    
    if abs(closest[1] - 1217.94) < 0.01:
        print(f"\n🏆 REVENUE RECONCILED!")
        print(f"Use {closest[0]} for accurate revenue calculation")
    else:
        print(f"\n⚠️  Still missing ${abs(closest[1] - 1217.94):.2f}")
        print("May need to check additional Square APIs")
    
    return closest[1], abs(closest[1] - 1217.94)

if __name__ == "__main__":
    best_revenue, gap = find_missing_102_revenue()
    
    print(f"\n" + "=" * 40)
    print("💰 REVENUE INVESTIGATION COMPLETE")
    print(f"Best match: ${best_revenue:.2f}")
    print(f"Remaining gap: ${gap:.2f}")
    
    if gap < 0.01:
        print("🏆 REVENUE RECONCILED - READY FOR PHASE 2!")
    else:
        print("⚠️  Minor gap remains - may be acceptable for production")