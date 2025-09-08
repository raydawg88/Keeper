#!/usr/bin/env python3
"""
INVESTIGATE SERVICE CATALOG MAPPING ISSUE
- Why are services showing as "Regular" instead of actual names?
- Are we getting the right service variations?
- What are the expected durations for spa services?
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def investigate_service_catalog():
    """Deep dive into service catalog to understand mapping issues"""
    
    print("🔍 INVESTIGATE SERVICE CATALOG MAPPING")
    print("=" * 50)
    
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
    
    # ==============================================================
    # GET FULL CATALOG WITH ALL TYPES
    # ==============================================================
    print(f"\n📋 STEP 1: GET FULL CATALOG")
    print("=" * 30)
    
    try:
        # Get all catalog objects
        catalog_url = f"{api_base_url}/v2/catalog/list"
        response = requests.get(catalog_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            objects = data.get('objects', [])
            
            print(f"✅ Found {len(objects)} catalog objects")
            
            # Analyze by type
            types_count = {}
            for obj in objects:
                obj_type = obj.get('type', 'Unknown')
                types_count[obj_type] = types_count.get(obj_type, 0) + 1
            
            print(f"\nCatalog object types:")
            for obj_type, count in sorted(types_count.items()):
                print(f"  {obj_type}: {count} objects")
            
        else:
            print(f"❌ Catalog API error: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # ==============================================================
    # EXAMINE SERVICE ITEMS IN DETAIL
    # ==============================================================
    print(f"\n🛍️  STEP 2: EXAMINE SERVICE ITEMS")
    print("=" * 35)
    
    service_items = []
    service_variations = {}
    
    for obj in objects:
        if obj.get('type') == 'ITEM':
            item_id = obj.get('id')
            item_data = obj.get('item_data', {})
            name = item_data.get('name', 'No Name')
            description = item_data.get('description', '')
            
            service_items.append({
                'id': item_id,
                'name': name,
                'description': description,
                'data': item_data
            })
            
            # Get variations
            variations = item_data.get('variations', [])
            for variation in variations:
                variation_id = variation.get('id')
                variation_data = variation.get('item_variation_data', {})
                variation_name = variation_data.get('name', name)
                
                service_variations[variation_id] = {
                    'name': variation_name,
                    'parent_name': name,
                    'parent_id': item_id,
                    'data': variation_data
                }
    
    print(f"Found {len(service_items)} service items")
    print(f"Found {len(service_variations)} service variations")
    
    # Show sample services
    print(f"\nSample service items:")
    for i, item in enumerate(service_items[:10], 1):
        print(f"  {i}. '{item['name']}' ({item['id']})")
        if item['description']:
            print(f"     Description: {item['description'][:50]}...")
    
    print(f"\nSample service variations:")
    for i, (var_id, var_data) in enumerate(list(service_variations.items())[:10], 1):
        print(f"  {i}. '{var_data['name']}' - Parent: '{var_data['parent_name']}' ({var_id})")
    
    # ==============================================================  
    # CHECK SPECIFIC APPOINTMENT SERVICE IDs
    # ==============================================================
    print(f"\n🎯 STEP 3: CHECK APPOINTMENT SERVICE IDs")
    print("=" * 40)
    
    # Get a few appointments to see what service IDs they use
    laine_id = "TMZx2T5T5arYJTm7"
    target_date = datetime(2025, 9, 2)
    start_str = target_date.strftime('%Y-%m-%dT00:00:00Z')
    end_str = (target_date + timedelta(days=1) - timedelta(seconds=1)).strftime('%Y-%m-%dT23:59:59Z')
    
    try:
        url = f"{api_base_url}/v2/bookings?limit=10&start_at_min={start_str}&start_at_max={end_str}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            bookings = data.get('bookings', [])
            
            print(f"Checking service IDs in actual appointments:")
            
            service_ids_used = set()
            for apt in bookings:
                segments = apt.get('appointment_segments', [])
                for segment in segments:
                    if segment.get('team_member_id') == laine_id:
                        service_var_id = segment.get('service_variation_id', '')
                        service_ids_used.add(service_var_id)
                        
                        duration = segment.get('duration_minutes', 0)
                        start_time = apt.get('start_at', '')
                        
                        print(f"\n  Appointment at {start_time[11:16]}:")
                        print(f"    Service Variation ID: {service_var_id}")
                        print(f"    Duration: {duration} minutes")
                        
                        if service_var_id in service_variations:
                            var_info = service_variations[service_var_id]
                            print(f"    ✅ MAPPED: '{var_info['name']}' (Parent: '{var_info['parent_name']}')")
                            
                            # Check if variation has duration info
                            var_data = var_info['data']
                            if 'service_duration' in var_data:
                                print(f"    Expected Duration: {var_data['service_duration']} (from catalog)")
                        else:
                            print(f"    ❌ NOT FOUND in catalog")
            
            print(f"\nUnique service variation IDs used: {len(service_ids_used)}")
            for service_id in service_ids_used:
                if service_id in service_variations:
                    var_info = service_variations[service_id] 
                    print(f"  ✅ {service_id}: '{var_info['name']}'")
                else:
                    print(f"  ❌ {service_id}: NOT FOUND")
                    
        else:
            print(f"❌ Bookings API error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking appointments: {e}")
    
    # ==============================================================
    # LOOK FOR TYPICAL SPA SERVICES 
    # ==============================================================
    print(f"\n💆 STEP 4: LOOK FOR TYPICAL SPA SERVICES")
    print("=" * 40)
    
    spa_keywords = ['wax', 'facial', 'brazilian', 'massage', 'eyebrow', 'lash', 'treatment']
    
    print(f"Searching for typical spa services:")
    matching_services = []
    
    for var_id, var_info in service_variations.items():
        name_lower = var_info['name'].lower()
        parent_lower = var_info['parent_name'].lower()
        
        for keyword in spa_keywords:
            if keyword in name_lower or keyword in parent_lower:
                matching_services.append({
                    'keyword': keyword,
                    'variation_id': var_id,
                    'name': var_info['name'],
                    'parent_name': var_info['parent_name']
                })
                break
    
    print(f"\nFound {len(matching_services)} spa-related services:")
    for service in matching_services[:15]:  # Show first 15
        print(f"  • {service['name']} (Parent: {service['parent_name']}) - {service['keyword']}")
    
    if len(matching_services) > 15:
        print(f"  ... and {len(matching_services) - 15} more")
    
    return {
        'total_catalog_objects': len(objects),
        'service_items': len(service_items),
        'service_variations': len(service_variations),
        'spa_services_found': len(matching_services),
        'service_ids_in_appointments': len(service_ids_used) if 'service_ids_used' in locals() else 0
    }

if __name__ == "__main__":
    result = investigate_service_catalog()
    
    print(f"\n" + "=" * 50)
    print("🔍 SERVICE CATALOG INVESTIGATION COMPLETE")
    
    if result:
        print(f"Total catalog objects: {result['total_catalog_objects']}")
        print(f"Service items: {result['service_items']}")
        print(f"Service variations: {result['service_variations']}")
        print(f"Spa services found: {result['spa_services_found']}")
        print(f"Service IDs in appointments: {result['service_ids_in_appointments']}")
        
        print(f"\n🎯 CONCLUSION: Service catalog exists, need to debug why 'Regular' appears")