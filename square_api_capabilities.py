#!/usr/bin/env python3
"""
COMPLETE SQUARE API CAPABILITIES ANALYSIS
What data we CAN get vs what we ARE getting
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def analyze_square_api_capabilities():
    """Analyze what Square API can provide vs what we're currently getting"""
    
    print("🔍 COMPLETE SQUARE API CAPABILITIES ANALYSIS")
    print("=" * 80)
    
    # Load our access token
    try:
        with open('/tmp/bashful_beauty_token.json', 'r') as f:
            token_data = json.load(f)
        access_token = token_data['access_token']
    except:
        print("❌ No access token found")
        return
    
    api_base_url = 'https://connect.squareup.com'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Square-Version': '2025-08-20',
        'Content-Type': 'application/json'
    }
    
    # Define ALL Square API endpoints and what data they provide
    square_api_endpoints = {
        # MERCHANT & BUSINESS INFO
        "merchants": {
            "endpoint": "/v2/merchants",
            "description": "Business information, settings, capabilities",
            "keeper_value": "Business context for insights",
            "data_includes": [
                "business_name", "merchant_id", "country", "language_code",
                "currency", "business_type", "owner_email", "created_at"
            ]
        },
        
        "locations": {
            "endpoint": "/v2/locations", 
            "description": "Physical locations, addresses, business hours",
            "keeper_value": "Location-based performance analysis",
            "data_includes": [
                "location_id", "name", "address", "timezone", "business_hours",
                "phone_number", "website_url", "capabilities", "status"
            ]
        },
        
        # CUSTOMER DATA
        "customers": {
            "endpoint": "/v2/customers",
            "description": "Complete customer profiles and preferences",
            "keeper_value": "Customer segmentation and churn prediction",
            "data_includes": [
                "customer_id", "given_name", "family_name", "email_address",
                "phone_number", "address", "birthday", "note", "preferences",
                "creation_source", "version", "created_at", "updated_at"
            ]
        },
        
        "customer_groups": {
            "endpoint": "/v2/customers/groups",
            "description": "Customer segmentation groups",
            "keeper_value": "Pre-built customer segments",
            "data_includes": [
                "group_id", "name", "query", "created_at", "updated_at"
            ]
        },
        
        "customer_segments": {
            "endpoint": "/v2/customers/segments",
            "description": "Dynamic customer segments based on behavior",
            "keeper_value": "Automatic customer categorization",
            "data_includes": [
                "segment_id", "name", "created_at", "updated_at"
            ]
        },
        
        # PAYMENT & TRANSACTION DATA
        "payments": {
            "endpoint": "/v2/payments",
            "description": "All payment transactions with full details",
            "keeper_value": "Revenue analysis, payment patterns, fraud detection",
            "data_includes": [
                "payment_id", "created_at", "updated_at", "amount_money", "status",
                "source_type", "customer_id", "order_id", "location_id",
                "receipt_number", "receipt_url", "risk_evaluation", "processing_fee",
                "card_details", "cash_details", "bank_account_details", "external_details"
            ]
        },
        
        "refunds": {
            "endpoint": "/v2/refunds",
            "description": "Refund transactions and reasons",
            "keeper_value": "Customer satisfaction analysis, refund patterns",
            "data_includes": [
                "refund_id", "payment_id", "order_id", "amount_money", "reason",
                "status", "created_at", "updated_at", "location_id"
            ]
        },
        
        # ORDER & SALES DATA
        "orders": {
            "endpoint": "/v2/orders/search",
            "description": "Complete order details, items, modifiers",
            "keeper_value": "Product performance, upselling opportunities",
            "data_includes": [
                "order_id", "location_id", "customer_id", "state", "version",
                "created_at", "updated_at", "closed_at", "total_money",
                "total_tax_money", "total_discount_money", "total_tip_money",
                "line_items", "discounts", "taxes", "service_charges", "fulfillments"
            ]
        },
        
        # INVENTORY & CATALOG
        "catalog": {
            "endpoint": "/v2/catalog/list",
            "description": "Products, services, variations, categories",
            "keeper_value": "Service performance analysis, pricing optimization", 
            "data_includes": [
                "object_id", "type", "updated_at", "version", "is_deleted",
                "catalog_v1_ids", "present_at_all_locations", "present_at_location_ids",
                "item_data", "category_data", "variation_data", "tax_data",
                "discount_data", "modifier_list_data", "modifier_data", "pricing_rule_data"
            ]
        },
        
        "inventory": {
            "endpoint": "/v2/inventory/counts",
            "description": "Inventory levels and adjustments",
            "keeper_value": "Stock-based service availability",
            "data_includes": [
                "catalog_object_id", "location_id", "quantity", "calculated_at"
            ]
        },
        
        # EMPLOYEE & TEAM DATA
        "team_members": {
            "endpoint": "/v2/team-members",
            "description": "Employee information and roles",
            "keeper_value": "Staff performance analysis, scheduling insights",
            "data_includes": [
                "team_member_id", "reference_id", "is_owner", "status",
                "given_name", "family_name", "email_address", "phone_number",
                "created_at", "updated_at", "assigned_locations"
            ]
        },
        
        "labor": {
            "endpoint": "/v2/labor/workweeks",
            "description": "Work schedules and time tracking",
            "keeper_value": "Staff efficiency, labor cost analysis",
            "data_includes": [
                "workweek_id", "team_member_ids", "start_date", "end_date",
                "wages", "tips", "overtime"
            ]
        },
        
        "wage_settings": {
            "endpoint": "/v2/labor/team-member-wages",
            "description": "Employee wage and compensation data",
            "keeper_value": "Labor cost per service/customer",
            "data_includes": [
                "team_member_id", "hourly_rate", "annual_salary", "job_assignments"
            ]
        },
        
        # APPOINTMENT & BOOKING DATA
        "bookings": {
            "endpoint": "/v2/bookings",
            "description": "Appointment bookings and scheduling",
            "keeper_value": "Appointment efficiency, no-show patterns",
            "data_includes": [
                "booking_id", "created_at", "updated_at", "booking_status",
                "location_id", "start_at", "customer_id", "customer_note",
                "seller_note", "appointment_segments", "transition_time_minutes",
                "all_day", "location_type", "creator_details"
            ]
        },
        
        "booking_custom_attributes": {
            "endpoint": "/v2/bookings/custom-attributes",
            "description": "Custom booking data and preferences",
            "keeper_value": "Service customization patterns",
            "data_includes": [
                "booking_id", "key", "value", "version", "visibility",
                "definition", "created_at", "updated_at"
            ]
        },
        
        # LOYALTY & MARKETING
        "loyalty_programs": {
            "endpoint": "/v2/loyalty/programs",
            "description": "Loyalty program configuration",
            "keeper_value": "Customer retention program effectiveness",
            "data_includes": [
                "program_id", "status", "reward_tiers", "expiration_policy",
                "terminology", "location_ids", "created_at", "updated_at"
            ]
        },
        
        "loyalty_accounts": {
            "endpoint": "/v2/loyalty/accounts",
            "description": "Individual customer loyalty data",
            "keeper_value": "Customer engagement and reward patterns",
            "data_includes": [
                "account_id", "program_id", "balance", "lifetime_balance",
                "customer_id", "enrolled_at", "created_at", "updated_at"
            ]
        },
        
        "gift_cards": {
            "endpoint": "/v2/gift-cards",
            "description": "Gift card sales and redemptions",
            "keeper_value": "Customer acquisition and retention via gifts",
            "data_includes": [
                "gift_card_id", "type", "state", "balance_money", "gan_source",
                "created_at", "customer_ids"
            ]
        },
        
        # SUBSCRIPTIONS & RECURRING
        "subscriptions": {
            "endpoint": "/v2/subscriptions",
            "description": "Recurring payment subscriptions",
            "keeper_value": "Recurring revenue analysis, churn prediction",
            "data_includes": [
                "subscription_id", "location_id", "plan_id", "customer_id",
                "start_date", "status", "price_override_money", "version",
                "created_at", "card_id", "timezone", "source", "actions"
            ]
        },
        
        # DISPUTES & CHARGEBACKS
        "disputes": {
            "endpoint": "/v2/disputes",
            "description": "Payment disputes and chargebacks",
            "keeper_value": "Customer satisfaction issues, fraud patterns",
            "data_includes": [
                "dispute_id", "amount_money", "reason", "state", "due_at",
                "disputed_payment", "evidence_ids", "card_brand", "created_at"
            ]
        },
        
        # WEBHOOKS & EVENTS
        "webhook_subscriptions": {
            "endpoint": "/v2/webhooks/subscriptions",
            "description": "Real-time event notifications",
            "keeper_value": "Live data updates for real-time insights",
            "data_includes": [
                "subscription_id", "name", "enabled", "event_types",
                "notification_url", "api_version", "signature_key", "created_at"
            ]
        },
        
        # CASH DRAWERS & TERMINALS
        "cash_drawers": {
            "endpoint": "/v2/cash-drawers/shifts",
            "description": "Cash drawer activity and shifts",
            "keeper_value": "Daily operations analysis, cash handling",
            "data_includes": [
                "shift_id", "location_id", "team_member_ids", "opened_at",
                "ended_at", "opening_cash_money", "cash_payment_money",
                "cash_refunds_money", "expected_cash_money", "closed_cash_money"
            ]
        },
        
        "terminal_checkout": {
            "endpoint": "/v2/terminal/checkouts",
            "description": "Terminal transaction data",
            "keeper_value": "In-person vs online transaction analysis",
            "data_includes": [
                "checkout_id", "amount_money", "reference_id", "device_options",
                "status", "payment_ids", "created_at", "updated_at"
            ]
        },
        
        # INVOICES & BILLING
        "invoices": {
            "endpoint": "/v2/invoices",
            "description": "Invoice generation and payments",
            "keeper_value": "B2B customer analysis, payment timing",
            "data_includes": [
                "invoice_id", "version", "location_id", "order_id", "primary_recipient",
                "payment_requests", "delivery_method", "invoice_number",
                "title", "description", "scheduled_at", "accepted_payment_methods",
                "custom_fields", "created_at", "updated_at", "status"
            ]
        },
        
        # SITES & ONLINE PRESENCE
        "sites": {
            "endpoint": "/v2/sites",
            "description": "Online Square sites and stores",
            "keeper_value": "Online vs offline customer behavior",
            "data_includes": [
                "site_id", "site_title", "domain", "is_published", "created_at", "updated_at"
            ]
        },
        
        # SNIPPETS & CUSTOM CODE
        "snippets": {
            "endpoint": "/v2/snippets",
            "description": "Custom tracking code and analytics",
            "keeper_value": "Enhanced tracking and attribution",
            "data_includes": [
                "snippet_id", "site_id", "content", "created_at", "updated_at"
            ]
        }
    }
    
    # What we're currently getting
    current_endpoints = [
        "merchants",
        "locations", 
        "customers",
        "bookings",
        # Not currently getting: payments, orders, team_members, catalog, etc.
    ]
    
    print(f"📊 COMPLETE SQUARE API CAPABILITIES")
    print(f"Total Available Endpoints: {len(square_api_endpoints)}")
    print(f"Currently Using: {len(current_endpoints)} endpoints")
    print(f"Missing Opportunities: {len(square_api_endpoints) - len(current_endpoints)} endpoints")
    
    print(f"\n✅ ENDPOINTS WE'RE CURRENTLY USING:")
    print("-" * 60)
    for endpoint in current_endpoints:
        if endpoint in square_api_endpoints:
            info = square_api_endpoints[endpoint]
            print(f"🟢 {endpoint.upper()}: {info['description']}")
            print(f"   Value: {info['keeper_value']}")
            print(f"   Data: {', '.join(info['data_includes'][:5])}...")
            print()
    
    print(f"\n🚨 HIGH-VALUE ENDPOINTS WE'RE MISSING:")
    print("-" * 60)
    
    high_value_missing = [
        "payments", "orders", "team_members", "catalog", "loyalty_accounts",
        "subscriptions", "refunds", "customer_segments"
    ]
    
    for endpoint in high_value_missing:
        if endpoint in square_api_endpoints:
            info = square_api_endpoints[endpoint]
            print(f"🔴 {endpoint.upper()}: {info['description']}")
            print(f"   Keeper Value: {info['keeper_value']}")
            print(f"   Missing Data: {', '.join(info['data_includes'][:5])}...")
            print()
    
    print(f"\n💡 SPECIALIZED ENDPOINTS FOR ADVANCED INSIGHTS:")
    print("-" * 60)
    
    specialized = [
        "disputes", "labor", "cash_drawers", "loyalty_programs",
        "gift_cards", "invoices", "webhook_subscriptions"
    ]
    
    for endpoint in specialized:
        if endpoint in square_api_endpoints:
            info = square_api_endpoints[endpoint]
            print(f"⭐ {endpoint.upper()}: {info['description']}")
            print(f"   Advanced Value: {info['keeper_value']}")
            print()
    
    # Test access to key missing endpoints
    print(f"\n🧪 TESTING ACCESS TO KEY MISSING ENDPOINTS:")
    print("-" * 60)
    
    test_endpoints = [
        ("/v2/payments?limit=1", "Payments"),
        ("/v2/orders/search", "Orders"), 
        ("/v2/team-members?limit=1", "Team Members"),
        ("/v2/catalog/list?types=ITEM&limit=1", "Catalog"),
        ("/v2/loyalty/programs", "Loyalty Programs")
    ]
    
    for endpoint_url, name in test_endpoints:
        try:
            if name == "Orders":
                # Orders requires POST
                response = requests.post(f"{api_base_url}{endpoint_url}", 
                                       headers=headers, 
                                       json={"limit": 1})
            else:
                response = requests.get(f"{api_base_url}{endpoint_url}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                record_count = len(data.get(list(data.keys())[0], [])) if data else 0
                print(f"✅ {name}: Available ({record_count} records found)")
            elif response.status_code == 403:
                print(f"🔒 {name}: Requires additional permissions")
            elif response.status_code == 404:
                print(f"⚠️  {name}: Endpoint not found")
            else:
                print(f"❌ {name}: Error {response.status_code}")
                
        except Exception as e:
            print(f"❌ {name}: Connection error")
    
    # RECOMMENDATIONS
    print(f"\n🎯 RECOMMENDATIONS FOR KEEPER:")
    print("-" * 60)
    
    recommendations = [
        {
            "priority": "🔥 CRITICAL",
            "endpoints": ["payments", "orders"],
            "reason": "Revenue analysis, transaction patterns, product performance"
        },
        {
            "priority": "⚡ HIGH",
            "endpoints": ["team_members", "catalog"],
            "reason": "Staff performance analysis, service optimization"
        },
        {
            "priority": "💎 VALUABLE", 
            "endpoints": ["loyalty_accounts", "customer_segments"],
            "reason": "Advanced customer segmentation and retention"
        },
        {
            "priority": "🚀 ADVANCED",
            "endpoints": ["subscriptions", "refunds", "disputes"],
            "reason": "Churn prediction, satisfaction analysis, fraud detection"
        }
    ]
    
    for rec in recommendations:
        print(f"{rec['priority']}: {', '.join([e.upper() for e in rec['endpoints']])}")
        print(f"   Why: {rec['reason']}")
        print()
    
    print(f"📋 SUMMARY:")
    print(f"   Currently using: {len(current_endpoints)}/{len(square_api_endpoints)} endpoints ({len(current_endpoints)/len(square_api_endpoints)*100:.1f}%)")
    print(f"   Data richness: BASIC (missing payments, orders, staff)")
    print(f"   Insight potential: 25% of maximum possible")
    print(f"   Recommendation: Add payments + orders APIs immediately")

if __name__ == "__main__":
    analyze_square_api_capabilities()