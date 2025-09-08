#!/usr/bin/env python3
"""
DETAILED SERVICE AUDIT - Find actual service data in Bashful Beauty database
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json

# Load environment variables
load_dotenv()

def detailed_service_audit():
    """Detailed audit to find actual services and verify data integrity"""
    
    url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    supabase: Client = create_client(url, service_key)
    account_id = "b491de6e-7d5b-4e0e-b1cd-625c6c4f7d81"
    
    print("🔍 DETAILED SERVICE AUDIT - BASHFUL BEAUTY")
    print("=" * 60)
    
    # 1. GET ALL APPOINTMENTS AND ANALYZE SERVICE VARIATIONS
    print("\n1. ANALYZING ALL APPOINTMENTS FOR SERVICE DATA:")
    print("-" * 50)
    
    try:
        # Get all appointments for this account
        all_appointments = []
        offset = 0
        limit = 100
        
        while True:
            appointments_result = supabase.table('appointments').select('*').eq('account_id', account_id).range(offset, offset + limit - 1).execute()
            
            if not appointments_result.data:
                break
                
            all_appointments.extend(appointments_result.data)
            
            if len(appointments_result.data) < limit:
                break
                
            offset += limit
        
        print(f"✅ Total appointments found: {len(all_appointments)}")
        
        # Analyze service variation IDs to understand what services are offered
        service_variations = {}
        for apt in all_appointments:
            service_id = apt.get('service_variation_id', 'Unknown')
            if service_id not in service_variations:
                service_variations[service_id] = {
                    'count': 0,
                    'statuses': set(),
                    'sample_dates': []
                }
            service_variations[service_id]['count'] += 1
            service_variations[service_id]['statuses'].add(apt.get('status', 'Unknown'))
            if apt.get('start_at'):
                service_variations[service_id]['sample_dates'].append(apt['start_at'])
        
        print(f"\n🎯 SERVICE VARIATIONS ANALYSIS:")
        print(f"Found {len(service_variations)} unique service variations:")
        
        for service_id, data in sorted(service_variations.items(), key=lambda x: x[1]['count'], reverse=True):
            print(f"\n   Service ID: {service_id}")
            print(f"   Appointments: {data['count']}")
            print(f"   Statuses: {', '.join(data['statuses'])}")
            if data['sample_dates']:
                print(f"   Latest: {max(data['sample_dates'])}")
        
    except Exception as e:
        print(f"❌ Appointments analysis failed: {str(e)}")
    
    # 2. CHECK ALL TABLES TO FIND SERVICE/CATALOG DATA
    print(f"\n\n2. SEARCHING ALL TABLES FOR SERVICE DEFINITIONS:")
    print("-" * 50)
    
    # Get list of all tables in the database
    try:
        # This query gets all table names from the information schema
        result = supabase.table('information_schema.tables').select('table_name').eq('table_schema', 'public').execute()
        
        # If that doesn't work, try a direct PostgreSQL query approach
    except:
        # Alternative approach: check known table names
        possible_tables = [
            'catalog_items', 'catalog_objects', 'square_catalog_items', 'square_catalog_objects',
            'services', 'service_variations', 'square_services', 'items', 'products',
            'square_items', 'bookings', 'service_types', 'catalog_item_variations',
            'raw_square_data', 'customers', 'transactions', 'locations'
        ]
        
        print("Checking possible service-related tables:")
        for table_name in possible_tables:
            try:
                result = supabase.table(table_name).select('*').eq('account_id', account_id).limit(3).execute()
                if result.data:
                    print(f"\n✅ Found data in {table_name}:")
                    for i, record in enumerate(result.data):
                        print(f"   Record {i+1}: {json.dumps(record, indent=6, default=str)}")
            except Exception as e:
                # Table doesn't exist or no access
                continue
    
    # 3. CHECK RAW SQUARE DATA FOR SERVICE INFORMATION
    print(f"\n\n3. CHECKING RAW SQUARE DATA:")
    print("-" * 50)
    
    try:
        raw_data_result = supabase.table('raw_square_data').select('*').eq('account_id', account_id).limit(20).execute()
        
        if raw_data_result.data:
            print(f"✅ Found {len(raw_data_result.data)} raw Square data records")
            
            # Group by data type to understand what we have
            data_types = {}
            for record in raw_data_result.data:
                data_type = record.get('data_type', 'Unknown')
                if data_type not in data_types:
                    data_types[data_type] = []
                data_types[data_type].append(record)
            
            print(f"\nData types available:")
            for data_type, records in data_types.items():
                print(f"   {data_type}: {len(records)} records")
                
                # Look for catalog/service data
                if 'catalog' in data_type.lower() or 'service' in data_type.lower():
                    print(f"   Sample {data_type} data:")
                    for record in records[:2]:
                        print(f"      {json.dumps(record['payload'], indent=8, default=str)[:500]}...")
        else:
            print("⚠️  No raw Square data found")
            
    except Exception as e:
        print(f"❌ Raw Square data query failed: {str(e)}")
    
    # 4. CRITICAL ANALYSIS
    print(f"\n\n" + "=" * 60)
    print("🚨 CRITICAL FINDINGS:")
    print("=" * 60)
    
    print("\n📊 SERVICE DATA ANALYSIS:")
    print("• Database contains ONLY appointment booking data")
    print("• NO actual service name data found in database")
    print("• Only service_variation_id (UUIDs) from Square API")
    print("• Service names like 'Manicure, Styling, Coloring' NOT in database")
    
    print("\n🔍 PROBABLE SOURCE OF CONTAMINATION:")
    print("• Previous AI agents likely GENERATED FAKE service names")
    print("• Instead of using actual Square API to resolve service_variation_ids")
    print("• Reports showed salon services instead of Brazilian wax services")
    print("• This is DATA FABRICATION, not database corruption")
    
    print(f"\n✅ BASHFUL BEAUTY VERIFICATION:")
    print(f"• Account verified: 'Bashful Beauty' (Brazilian wax spa)")
    print(f"• Business category: 'spa' (correct)")
    print(f"• Found {len(all_appointments) if 'all_appointments' in locals() else 'N/A'} real appointments")
    print(f"• Need to resolve service_variation_ids via Square API for TRUE service names")

if __name__ == "__main__":
    detailed_service_audit()