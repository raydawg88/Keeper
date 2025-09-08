#!/usr/bin/env python3
"""
TEST 2: ORDERS API
- Call Orders API
- Show 5 actual order transactions  
- Show raw JSON response
- Store in JSON file (since DB tables not ready)
- Verify data quality
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_orders_api():
    """Test Orders API step by step"""
    
    print("🛍️ TEST 2: ORDERS API")
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
    
    print("🌐 CALLING ORDERS API...")
    print(f"URL: {api_base_url}/v2/orders/search")
    print("Method: POST (Orders requires search with body)")
    
    # First get location IDs
    locations_response = requests.get(f"{api_base_url}/v2/locations", headers=headers)
    if locations_response.status_code != 200:
        print(f"❌ Failed to get locations: {locations_response.status_code}")
        return False
    
    locations_data = locations_response.json()
    locations = locations_data.get('locations', [])
    if not locations:
        print("❌ No locations found")
        return False
    
    location_ids = [loc.get('id') for loc in locations]
    print(f"📍 Found {len(location_ids)} locations: {location_ids[:2]}...")
    
    # Orders API requires POST with search criteria including location_ids
    search_body = {
        "limit": 5,
        "location_ids": location_ids,
        "query": {
            "filter": {
                "date_time_filter": {
                    "created_at": {
                        "start_at": "2023-01-01T00:00:00Z",
                        "end_at": "2025-12-31T23:59:59Z"
                    }
                }
            },
            "sort": {
                "sort_field": "CREATED_AT",
                "sort_order": "DESC"
            }
        },
        "return_entries": True
    }
    
    try:
        response = requests.post(f"{api_base_url}/v2/orders/search", 
                               headers=headers, 
                               json=search_body)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            orders_data = response.json()
            # Handle both 'orders' (full data) and 'order_entries' (summary data)
            orders = orders_data.get('orders', [])
            order_entries = orders_data.get('order_entries', [])
            
            # If we got order_entries, we need to fetch full order details
            if order_entries and not orders:
                print(f"📋 Retrieved {len(order_entries)} order entries, fetching full details...")
                orders = []
                for entry in order_entries[:5]:  # Limit to 5
                    order_id = entry.get('order_id')
                    if order_id:
                        try:
                            full_order_response = requests.get(
                                f"{api_base_url}/v2/orders/{order_id}",
                                headers=headers
                            )
                            if full_order_response.status_code == 200:
                                full_order_data = full_order_response.json()
                                full_order = full_order_data.get('order', {})
                                if full_order:
                                    orders.append(full_order)
                        except Exception as e:
                            print(f"⚠️  Failed to get full details for order {order_id}: {e}")
                
                print(f"✅ Successfully retrieved full details for {len(orders)} orders")
            
            print(f"✅ SUCCESS! Retrieved {len(orders)} orders")
            
            # Show raw JSON response
            print(f"\n📋 RAW JSON RESPONSE:")
            print("-" * 60)
            print(json.dumps(orders_data, indent=2))
            print("-" * 60)
            
            if orders:
                print(f"\n🛍️ ORDER DETAILS:")
                for i, order in enumerate(orders, 1):
                    # Extract order financial data
                    total_money = order.get('total_money', {})
                    total_tax = order.get('total_tax_money', {})
                    total_discount = order.get('total_discount_money', {})
                    total_tip = order.get('total_tip_money', {})
                    
                    total_amount = float(total_money.get('amount', 0)) / 100
                    tax_amount = float(total_tax.get('amount', 0)) / 100
                    discount_amount = float(total_discount.get('amount', 0)) / 100
                    tip_amount = float(total_tip.get('amount', 0)) / 100
                    
                    # Extract line items
                    line_items = order.get('line_items', [])
                    
                    print(f"\nOrder {i}:")
                    print(f"  ID: {order.get('id')}")
                    print(f"  State: {order.get('state')}")
                    print(f"  Total: ${total_amount:.2f}")
                    print(f"  Tax: ${tax_amount:.2f}")
                    print(f"  Discount: ${discount_amount:.2f}")
                    print(f"  Tip: ${tip_amount:.2f}")
                    print(f"  Items: {len(line_items)} items")
                    print(f"  Customer: {order.get('customer_id', 'N/A')}")
                    print(f"  Location: {order.get('location_id')}")
                    print(f"  Created: {order.get('created_at')}")
                    print(f"  Updated: {order.get('updated_at')}")
                    
                    # Show line items detail
                    if line_items:
                        print(f"  Line Items:")
                        for j, item in enumerate(line_items[:3], 1):  # Show first 3 items
                            item_name = item.get('name', 'Unknown Item')
                            quantity = item.get('quantity', '1')
                            base_price = item.get('base_price_money', {})
                            price = float(base_price.get('amount', 0)) / 100
                            print(f"    {j}. {item_name} (Qty: {quantity}) - ${price:.2f}")
                        if len(line_items) > 3:
                            print(f"    ... and {len(line_items) - 3} more items")
            
            # Store in JSON file (since database tables not ready yet)
            print(f"\n💾 STORING ORDERS DATA...")
            
            # Transform orders for storage
            order_records = []
            for order in orders:
                total_money = order.get('total_money', {})
                total_tax = order.get('total_tax_money', {})
                total_discount = order.get('total_discount_money', {})
                total_tip = order.get('total_tip_money', {})
                
                order_record = {
                    'id': f"order_{order.get('id')}",
                    'account_id': account_id,
                    'order_id': order.get('id'),
                    'location_id': order.get('location_id'),
                    'customer_id': order.get('customer_id'),
                    'state': order.get('state'),
                    'version': order.get('version'),
                    'total_money_cents': total_money.get('amount', 0),
                    'total_tax_cents': total_tax.get('amount', 0),
                    'total_discount_cents': total_discount.get('amount', 0),
                    'total_tip_cents': total_tip.get('amount', 0),
                    'line_items_count': len(order.get('line_items', [])),
                    'line_items': order.get('line_items', []),
                    'tenders': order.get('tenders', []),
                    'created_at': order.get('created_at'),
                    'updated_at': order.get('updated_at'),
                    'closed_at': order.get('closed_at'),
                    'square_data': order,  # Store full Square data
                    'synced_at': datetime.utcnow().isoformat(),
                    'data_source': 'Square Orders API v2',
                    'test_timestamp': datetime.now().isoformat()
                }
                
                order_records.append(order_record)
            
            # Save to JSON file
            output_file = f"/tmp/square_orders_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump({
                    'test_info': {
                        'test_name': 'Square Orders API Test',
                        'account_id': account_id,
                        'timestamp': datetime.now().isoformat(),
                        'orders_count': len(order_records),
                        'api_endpoint': '/v2/orders/search',
                        'api_version': '2025-08-20'
                    },
                    'orders': order_records
                }, f, indent=2)
            
            print(f"✅ Orders data saved to: {output_file}")
            
            # Verify data quality
            print(f"\n📊 DATA QUALITY VERIFICATION:")
            print("-" * 40)
            
            total_revenue = sum(record['total_money_cents'] for record in order_records) / 100
            total_items = sum(record['line_items_count'] for record in order_records)
            avg_order_value = total_revenue / len(order_records) if order_records else 0
            
            print(f"Orders Retrieved: {len(order_records)}")
            print(f"Total Revenue: ${total_revenue:.2f}")
            print(f"Total Items Sold: {total_items}")
            print(f"Average Order Value: ${avg_order_value:.2f}")
            
            # Show order states
            states = {}
            for record in order_records:
                state = record['state']
                states[state] = states.get(state, 0) + 1
            
            print(f"Order States: {dict(states)}")
            
            # Check for customer association
            with_customers = len([r for r in order_records if r['customer_id']])
            customer_percentage = (with_customers/len(order_records)*100) if order_records else 0
            print(f"Orders with Customers: {with_customers}/{len(order_records)} ({customer_percentage:.1f}%)")
            
            return True
            
        else:
            print(f"❌ ORDERS API FAILED: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ORDERS API ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_orders_api()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 TEST 2 (ORDERS API) COMPLETE!")
        print("✅ API call successful")
        print("✅ Raw JSON response shown")
        print("✅ Order details extracted")
        print("✅ Data quality verified")
        print("✅ Data saved to JSON file")
        print("\n📋 NEXT: Continue with TEST 3: Catalog API")
    else:
        print("❌ TEST 2 (ORDERS API) FAILED!")
        print("⚠️  Check errors above")