#!/usr/bin/env python3
"""
TEST ALL NEW SQUARE API ENDPOINTS WITH COMPREHENSIVE READ-ONLY ACCESS
Exchange token and test every API endpoint with actual results
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def exchange_code_and_test_all_apis():
    """Exchange code for comprehensive token and test every API"""
    
    print("🔄 EXCHANGING CODE FOR COMPREHENSIVE ACCESS TOKEN")
    print("=" * 80)
    
    # Exchange authorization code
    client_id = os.getenv('SQUARE_APPLICATION_ID')
    client_secret = os.getenv('SQUARE_CLIENT_SECRET')
    api_base_url = 'https://connect.squareup.com'
    
    authorization_code = "sq0cgp-DOb97GuwG_PBwYxT6A6Fuw"
    state = "2b61a20b-fe9c-457e-a8d9-25037283a65a"
    
    print(f"🔑 Exchanging code: {authorization_code}")
    print(f"🔒 State: {state}")
    
    # Token exchange
    token_url = f"{api_base_url}/oauth2/token"
    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': authorization_code,
        'grant_type': 'authorization_code'
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Square-Version': '2025-08-20'
    }
    
    try:
        response = requests.post(token_url, json=token_data, headers=headers)
        
        if response.status_code == 200:
            token_result = response.json()
            access_token = token_result.get('access_token')
            expires_at = token_result.get('expires_at', 'Never')
            
            print(f"✅ TOKEN EXCHANGE SUCCESS!")
            print(f"🔑 Access Token: {access_token[:30]}...")
            print(f"⏰ Expires: {expires_at}")
            
            # Save comprehensive token
            with open('/tmp/comprehensive_square_token.json', 'w') as f:
                json.dump(token_result, f, indent=2)
            
            print(f"💾 Comprehensive token saved")
            
        else:
            print(f"❌ Token exchange failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Token exchange error: {e}")
        return None
    
    # Set up headers for API calls
    api_headers = {
        'Authorization': f'Bearer {access_token}',
        'Square-Version': '2025-08-20',
        'Content-Type': 'application/json'
    }
    
    print(f"\n🧪 TESTING ALL NEW API ENDPOINTS")
    print("=" * 80)
    
    test_results = {}
    
    # 1. TEST PAYMENTS API
    print(f"\n💳 1. TESTING PAYMENTS API")
    print("-" * 50)
    try:
        payments_response = requests.get(f"{api_base_url}/v2/payments?limit=5", headers=api_headers)
        
        if payments_response.status_code == 200:
            payments_data = payments_response.json()
            payments = payments_data.get('payments', [])
            
            print(f"✅ PAYMENTS API SUCCESS!")
            print(f"📊 Found {len(payments)} payments")
            
            if payments:
                total_amount = 0
                total_tips = 0
                
                print(f"\n📋 PAYMENT DETAILS:")
                for i, payment in enumerate(payments, 1):
                    amount = float(payment.get('amount_money', {}).get('amount', 0)) / 100
                    tip = float(payment.get('tip_money', {}).get('amount', 0)) / 100
                    total_amount += amount
                    total_tips += tip
                    
                    print(f"   Payment {i}:")
                    print(f"   - ID: {payment.get('id')}")
                    print(f"   - Amount: ${amount:.2f}")
                    print(f"   - Tip: ${tip:.2f}")
                    print(f"   - Status: {payment.get('status')}")
                    print(f"   - Source: {payment.get('source_type')}")
                    print(f"   - Created: {payment.get('created_at')}")
                    print(f"   - Customer: {payment.get('customer_id', 'N/A')}")
                
                print(f"\n💰 PAYMENT TOTALS:")
                print(f"   Total Revenue: ${total_amount:.2f}")
                print(f"   Total Tips: ${total_tips:.2f}")
                print(f"   Tip Rate: {(total_tips/total_amount*100) if total_amount > 0 else 0:.1f}%")
                
                test_results['payments'] = {
                    'success': True,
                    'count': len(payments),
                    'total_amount': total_amount,
                    'total_tips': total_tips
                }
            else:
                print(f"   📝 No payments in response")
                test_results['payments'] = {'success': True, 'count': 0}
                
        else:
            print(f"❌ PAYMENTS API FAILED: {payments_response.status_code}")
            print(f"Error: {payments_response.text}")
            test_results['payments'] = {'success': False, 'error': payments_response.status_code}
            
    except Exception as e:
        print(f"❌ PAYMENTS API ERROR: {e}")
        test_results['payments'] = {'success': False, 'error': str(e)}
    
    # 2. TEST ORDERS API
    print(f"\n🛒 2. TESTING ORDERS API")
    print("-" * 50)
    try:
        # Orders API requires POST with search criteria
        orders_body = {
            "limit": 5,
            "location_ids": ["F3XKQZW5S5M0V"]  # Use the location ID we know
        }
        orders_response = requests.post(f"{api_base_url}/v2/orders/search", 
                                      headers=api_headers, 
                                      json=orders_body)
        
        if orders_response.status_code == 200:
            orders_data = orders_response.json()
            orders = orders_data.get('orders', [])
            
            print(f"✅ ORDERS API SUCCESS!")
            print(f"📊 Found {len(orders)} orders")
            
            if orders:
                print(f"\n📋 ORDER DETAILS:")
                for i, order in enumerate(orders, 1):
                    total_money = float(order.get('total_money', {}).get('amount', 0)) / 100
                    line_items = order.get('line_items', [])
                    
                    print(f"   Order {i}:")
                    print(f"   - ID: {order.get('id')}")
                    print(f"   - Total: ${total_money:.2f}")
                    print(f"   - Status: {order.get('state')}")
                    print(f"   - Items: {len(line_items)}")
                    print(f"   - Customer: {order.get('customer_id', 'N/A')}")
                    print(f"   - Created: {order.get('created_at')}")
                    
                    # Show line items
                    for j, item in enumerate(line_items[:2], 1):  # Show first 2 items
                        item_name = item.get('name', 'Unknown Item')
                        item_price = float(item.get('total_money', {}).get('amount', 0)) / 100
                        print(f"     Item {j}: {item_name} (${item_price:.2f})")
                
                test_results['orders'] = {'success': True, 'count': len(orders)}
            else:
                print(f"   📝 No orders in response")
                test_results['orders'] = {'success': True, 'count': 0}
                
        else:
            print(f"❌ ORDERS API FAILED: {orders_response.status_code}")
            print(f"Error: {orders_response.text}")
            test_results['orders'] = {'success': False, 'error': orders_response.status_code}
            
    except Exception as e:
        print(f"❌ ORDERS API ERROR: {e}")
        test_results['orders'] = {'success': False, 'error': str(e)}
    
    # 3. TEST TEAM MEMBERS API
    print(f"\n👨‍💼 3. TESTING TEAM MEMBERS API")
    print("-" * 50)
    try:
        team_response = requests.get(f"{api_base_url}/v2/team-members", headers=api_headers)
        
        if team_response.status_code == 200:
            team_data = team_response.json()
            team_members = team_data.get('team_members', [])
            
            print(f"✅ TEAM MEMBERS API SUCCESS!")
            print(f"📊 Found {len(team_members)} team members")
            
            if team_members:
                print(f"\n📋 TEAM MEMBER DETAILS:")
                for i, member in enumerate(team_members, 1):
                    name = f"{member.get('given_name', '')} {member.get('family_name', '')}".strip()
                    print(f"   Member {i}:")
                    print(f"   - ID: {member.get('id')}")
                    print(f"   - Name: {name}")
                    print(f"   - Email: {member.get('email_address', 'N/A')}")
                    print(f"   - Phone: {member.get('phone_number', 'N/A')}")
                    print(f"   - Status: {member.get('status')}")
                    print(f"   - Is Owner: {member.get('is_owner', False)}")
                    print(f"   - Created: {member.get('created_at')}")
                
                test_results['team_members'] = {'success': True, 'count': len(team_members)}
            else:
                print(f"   📝 No team members in response")
                test_results['team_members'] = {'success': True, 'count': 0}
                
        else:
            print(f"❌ TEAM MEMBERS API FAILED: {team_response.status_code}")
            print(f"Error: {team_response.text}")
            test_results['team_members'] = {'success': False, 'error': team_response.status_code}
            
    except Exception as e:
        print(f"❌ TEAM MEMBERS API ERROR: {e}")
        test_results['team_members'] = {'success': False, 'error': str(e)}
    
    # 4. TEST CATALOG API
    print(f"\n📦 4. TESTING CATALOG API")
    print("-" * 50)
    try:
        catalog_response = requests.get(f"{api_base_url}/v2/catalog/list?types=ITEM&limit=10", headers=api_headers)
        
        if catalog_response.status_code == 200:
            catalog_data = catalog_response.json()
            catalog_items = catalog_data.get('objects', [])
            
            print(f"✅ CATALOG API SUCCESS!")
            print(f"📊 Found {len(catalog_items)} catalog items")
            
            if catalog_items:
                print(f"\n📋 CATALOG ITEM DETAILS:")
                for i, item in enumerate(catalog_items[:5], 1):  # Show first 5
                    item_data = item.get('item_data', {})
                    name = item_data.get('name', 'Unknown Item')
                    variations = item_data.get('variations', [])
                    
                    print(f"   Item {i}:")
                    print(f"   - ID: {item.get('id')}")
                    print(f"   - Name: {name}")
                    print(f"   - Type: {item.get('type')}")
                    print(f"   - Updated: {item.get('updated_at')}")
                    print(f"   - Variations: {len(variations)}")
                    
                    # Show first variation with pricing
                    if variations:
                        var = variations[0]
                        var_data = var.get('item_variation_data', {})
                        price_money = var_data.get('price_money', {})
                        if price_money:
                            price = float(price_money.get('amount', 0)) / 100
                            print(f"     Price: ${price:.2f}")
                
                test_results['catalog'] = {'success': True, 'count': len(catalog_items)}
            else:
                print(f"   📝 No catalog items in response")
                test_results['catalog'] = {'success': True, 'count': 0}
                
        else:
            print(f"❌ CATALOG API FAILED: {catalog_response.status_code}")
            print(f"Error: {catalog_response.text}")
            test_results['catalog'] = {'success': False, 'error': catalog_response.status_code}
            
    except Exception as e:
        print(f"❌ CATALOG API ERROR: {e}")
        test_results['catalog'] = {'success': False, 'error': str(e)}
    
    # 5. TEST LOYALTY API
    print(f"\n🎁 5. TESTING LOYALTY API")
    print("-" * 50)
    try:
        loyalty_response = requests.get(f"{api_base_url}/v2/loyalty/programs", headers=api_headers)
        
        if loyalty_response.status_code == 200:
            loyalty_data = loyalty_response.json()
            programs = loyalty_data.get('programs', [])
            
            print(f"✅ LOYALTY API SUCCESS!")
            print(f"📊 Found {len(programs)} loyalty programs")
            
            if programs:
                print(f"\n📋 LOYALTY PROGRAM DETAILS:")
                for i, program in enumerate(programs, 1):
                    print(f"   Program {i}:")
                    print(f"   - ID: {program.get('id')}")
                    print(f"   - Status: {program.get('status')}")
                    print(f"   - Created: {program.get('created_at')}")
                    
                    reward_tiers = program.get('reward_tiers', [])
                    print(f"   - Reward Tiers: {len(reward_tiers)}")
                
                test_results['loyalty'] = {'success': True, 'count': len(programs)}
            else:
                print(f"   📝 No loyalty programs found")
                test_results['loyalty'] = {'success': True, 'count': 0}
                
        else:
            print(f"❌ LOYALTY API FAILED: {loyalty_response.status_code}")
            print(f"Error: {loyalty_response.text}")
            test_results['loyalty'] = {'success': False, 'error': loyalty_response.status_code}
            
    except Exception as e:
        print(f"❌ LOYALTY API ERROR: {e}")
        test_results['loyalty'] = {'success': False, 'error': str(e)}
    
    # 6. TEST TIMECARDS API
    print(f"\n⏰ 6. TESTING TIMECARDS API")
    print("-" * 50)
    try:
        # Get recent timecards
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        timecards_response = requests.get(
            f"{api_base_url}/v2/labor/time-cards?begin_time={start_date}&end_time={end_date}&limit=5", 
            headers=api_headers
        )
        
        if timecards_response.status_code == 200:
            timecards_data = timecards_response.json()
            timecards = timecards_data.get('timecards', [])
            
            print(f"✅ TIMECARDS API SUCCESS!")
            print(f"📊 Found {len(timecards)} timecards (last 30 days)")
            
            if timecards:
                print(f"\n📋 TIMECARD DETAILS:")
                for i, timecard in enumerate(timecards, 1):
                    print(f"   Timecard {i}:")
                    print(f"   - ID: {timecard.get('id')}")
                    print(f"   - Employee: {timecard.get('employee_id')}")
                    print(f"   - Start: {timecard.get('start_at')}")
                    print(f"   - End: {timecard.get('end_at')}")
                    print(f"   - State: {timecard.get('state')}")
                
                test_results['timecards'] = {'success': True, 'count': len(timecards)}
            else:
                print(f"   📝 No timecards found (may not be used)")
                test_results['timecards'] = {'success': True, 'count': 0}
                
        else:
            print(f"❌ TIMECARDS API FAILED: {timecards_response.status_code}")
            print(f"Error: {timecards_response.text}")
            test_results['timecards'] = {'success': False, 'error': timecards_response.status_code}
            
    except Exception as e:
        print(f"❌ TIMECARDS API ERROR: {e}")
        test_results['timecards'] = {'success': False, 'error': str(e)}
    
    # FINAL RESULTS SUMMARY
    print(f"\n" + "=" * 80)
    print(f"📊 COMPREHENSIVE API TEST RESULTS")
    print("=" * 80)
    
    successful_apis = 0
    total_apis = len(test_results)
    
    for api_name, result in test_results.items():
        if result.get('success'):
            status = "✅ WORKING"
            if 'count' in result:
                status += f" ({result['count']} records)"
            successful_apis += 1
        else:
            status = f"❌ FAILED ({result.get('error', 'Unknown error')})"
        
        print(f"{api_name.upper()}: {status}")
    
    print(f"\n📈 SUCCESS RATE: {successful_apis}/{total_apis} APIs working ({successful_apis/total_apis*100:.1f}%)")
    
    if successful_apis > 3:  # If most APIs work
        print(f"🎉 COMPREHENSIVE SQUARE API ACCESS IS WORKING!")
        print(f"✅ Read-only permissions successfully granted")
        print(f"✅ Multiple data sources now available")
        print(f"🚀 Ready for advanced business intelligence")
    else:
        print(f"⚠️  Some APIs need additional permissions or configuration")
    
    return access_token, test_results

if __name__ == "__main__":
    exchange_code_and_test_all_apis()