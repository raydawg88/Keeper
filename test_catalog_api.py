#!/usr/bin/env python3
"""
TEST 3: CATALOG API
- Call Catalog API to get products/services
- Show actual service offerings
- Show raw JSON response  
- Store in JSON file
- Verify service categories and pricing
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_catalog_api():
    """Test Catalog API step by step"""
    
    print("📋 TEST 3: CATALOG API")
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
    
    print("🌐 CALLING CATALOG API...")
    print(f"URL: {api_base_url}/v2/catalog/list")
    print("Getting items, categories, and variations...")
    
    try:
        # Get catalog items (products/services)
        response = requests.get(f"{api_base_url}/v2/catalog/list?types=ITEM,CATEGORY,ITEM_VARIATION", 
                               headers=headers)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            catalog_data = response.json()
            catalog_objects = catalog_data.get('objects', [])
            
            print(f"✅ SUCCESS! Retrieved {len(catalog_objects)} catalog objects")
            
            # Show raw JSON response (truncated for readability)
            print(f"\n📋 RAW JSON RESPONSE (first 2 objects):")
            print("-" * 60)
            limited_data = {
                'objects': catalog_objects[:2] if catalog_objects else [],
                'total_objects': len(catalog_objects)
            }
            print(json.dumps(limited_data, indent=2))
            print("-" * 60)
            
            # Categorize objects
            items = [obj for obj in catalog_objects if obj.get('type') == 'ITEM']
            categories = [obj for obj in catalog_objects if obj.get('type') == 'CATEGORY']
            variations = [obj for obj in catalog_objects if obj.get('type') == 'ITEM_VARIATION']
            
            print(f"\n📊 CATALOG BREAKDOWN:")
            print(f"Items (Services/Products): {len(items)}")
            print(f"Categories: {len(categories)}")
            print(f"Variations (Pricing): {len(variations)}")
            
            if categories:
                print(f"\n🏷️ SERVICE CATEGORIES:")
                for i, category in enumerate(categories[:10], 1):
                    cat_data = category.get('category_data', {})
                    print(f"  {i}. {cat_data.get('name', 'Unknown Category')}")
                    if i >= 10 and len(categories) > 10:
                        print(f"  ... and {len(categories) - 10} more categories")
                        break
            
            if items:
                print(f"\n💅 SERVICES/PRODUCTS:")
                for i, item in enumerate(items[:10], 1):
                    item_data = item.get('item_data', {})
                    name = item_data.get('name', 'Unknown Item')
                    description = item_data.get('description', '')
                    
                    # Get pricing from variations
                    variation_ids = item_data.get('variations', [])
                    prices = []
                    for var_id in variation_ids[:3]:  # Show first 3 variations
                        variation = next((v for v in variations if v.get('id') == var_id.get('id')), None)
                        if variation:
                            var_data = variation.get('item_variation_data', {})
                            price_money = var_data.get('price_money', {})
                            if price_money.get('amount'):
                                price = float(price_money.get('amount', 0)) / 100
                                prices.append(f"${price:.2f}")
                    
                    print(f"  {i}. {name}")
                    if description:
                        print(f"     Description: {description[:100]}{'...' if len(description) > 100 else ''}")
                    if prices:
                        print(f"     Pricing: {', '.join(prices)}")
                    print()
                    
                    if i >= 10 and len(items) > 10:
                        print(f"  ... and {len(items) - 10} more services/products")
                        break
            
            # Store catalog data
            print(f"💾 STORING CATALOG DATA...")
            
            # Transform catalog for storage
            catalog_records = []
            for obj in catalog_objects:
                obj_type = obj.get('type')
                
                if obj_type == 'ITEM':
                    item_data = obj.get('item_data', {})
                    
                    catalog_record = {
                        'id': f"catalog_{obj.get('id')}",
                        'account_id': account_id,
                        'catalog_object_id': obj.get('id'),
                        'object_type': obj_type,
                        'version': obj.get('version'),
                        'is_deleted': obj.get('is_deleted', False),
                        'present_at_all_locations': obj.get('present_at_all_locations', True),
                        'item_name': item_data.get('name'),
                        'item_description': item_data.get('description'),
                        'category_id': item_data.get('category_id'),
                        'variations': item_data.get('variations', []),
                        'modifier_list_ids': item_data.get('modifier_list_ids', []),
                        'available_online': item_data.get('available_online', False),
                        'available_for_pickup': item_data.get('available_for_pickup', True),
                        'created_at': obj.get('created_at'),
                        'updated_at': obj.get('updated_at'),
                        'square_data': obj,  # Store full Square data
                        'synced_at': datetime.now().isoformat(),
                        'data_source': 'Square Catalog API v2',
                        'test_timestamp': datetime.now().isoformat()
                    }
                    
                    catalog_records.append(catalog_record)
                
                elif obj_type == 'CATEGORY':
                    category_data = obj.get('category_data', {})
                    
                    catalog_record = {
                        'id': f"category_{obj.get('id')}",
                        'account_id': account_id,
                        'catalog_object_id': obj.get('id'),
                        'object_type': obj_type,
                        'version': obj.get('version'),
                        'is_deleted': obj.get('is_deleted', False),
                        'category_name': category_data.get('name'),
                        'created_at': obj.get('created_at'),
                        'updated_at': obj.get('updated_at'),
                        'square_data': obj,
                        'synced_at': datetime.now().isoformat(),
                        'data_source': 'Square Catalog API v2',
                        'test_timestamp': datetime.now().isoformat()
                    }
                    
                    catalog_records.append(catalog_record)
            
            # Save to JSON file
            output_file = f"/tmp/square_catalog_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump({
                    'test_info': {
                        'test_name': 'Square Catalog API Test',
                        'account_id': account_id,
                        'timestamp': datetime.now().isoformat(),
                        'total_objects': len(catalog_objects),
                        'items_count': len(items),
                        'categories_count': len(categories),
                        'variations_count': len(variations),
                        'api_endpoint': '/v2/catalog/list',
                        'api_version': '2025-08-20'
                    },
                    'catalog_items': [r for r in catalog_records if r['object_type'] == 'ITEM'],
                    'categories': [r for r in catalog_records if r['object_type'] == 'CATEGORY'],
                    'all_objects': catalog_objects  # Raw Square data
                }, f, indent=2)
            
            print(f"✅ Catalog data saved to: {output_file}")
            
            # Data quality verification
            print(f"\n📊 DATA QUALITY VERIFICATION:")
            print("-" * 40)
            
            item_records = [r for r in catalog_records if r['object_type'] == 'ITEM']
            category_records = [r for r in catalog_records if r['object_type'] == 'CATEGORY']
            
            print(f"Total Catalog Objects: {len(catalog_objects)}")
            print(f"Services/Products: {len(item_records)}")
            print(f"Categories: {len(category_records)}")
            print(f"Price Variations: {len(variations)}")
            
            # Check for descriptions
            with_descriptions = len([r for r in item_records if r['item_description']])
            print(f"Items with Descriptions: {with_descriptions}/{len(item_records)} ({with_descriptions/len(item_records)*100:.1f}%)" if item_records else "Items with Descriptions: 0/0 (0.0%)")
            
            # Check online availability
            online_available = len([r for r in item_records if r['available_online']])
            print(f"Available Online: {online_available}/{len(item_records)}" if item_records else "Available Online: 0/0")
            
            # Show service types from names
            service_keywords = ['brazilian', 'underarm', 'bikini', 'membership', 'waxing', 'facial']
            service_types = {}
            for record in item_records:
                name = record.get('item_name', '').lower()
                for keyword in service_keywords:
                    if keyword in name:
                        service_types[keyword] = service_types.get(keyword, 0) + 1
            
            if service_types:
                print(f"Service Types Found: {dict(service_types)}")
            
            return True
            
        else:
            print(f"❌ CATALOG API FAILED: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ CATALOG API ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_catalog_api()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 TEST 3 (CATALOG API) COMPLETE!")
        print("✅ API call successful")
        print("✅ Raw JSON response shown")
        print("✅ Services and categories extracted")
        print("✅ Pricing variations identified")
        print("✅ Data quality verified")
        print("✅ Data saved to JSON file")
        print("\n📋 NEXT: Continue with TEST 4: Team Members API")
    else:
        print("❌ TEST 3 (CATALOG API) FAILED!")
        print("⚠️  Check errors above")