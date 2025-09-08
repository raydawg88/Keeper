#!/usr/bin/env python3
"""
DURATION MISMATCH ANALYSIS
Compare appointment scheduled durations vs catalog expected durations
This could explain the utilization gap between our 47.3% and Square's 60%
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def analyze_duration_mismatch():
    """Compare scheduled vs expected durations to find utilization gap"""
    
    print("⏰ DURATION MISMATCH ANALYSIS")
    print("=" * 50)
    print("Hypothesis: Square uses EXPECTED durations, we use SCHEDULED durations")
    print("This could explain 47.3% (our calc) vs 60% (Square) utilization gap")
    
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
    
    # Load service catalog
    service_catalog = {}
    try:
        catalog_url = f"{api_base_url}/v2/catalog/list?types=ITEM"
        response = requests.get(catalog_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            objects = data.get('objects', [])
            
            for obj in objects:
                if obj.get('type') == 'ITEM':
                    item_data = obj.get('item_data', {})
                    name = item_data.get('name', 'Unknown Service')
                    
                    variations = item_data.get('variations', [])
                    for variation in variations:
                        variation_id = variation.get('id')
                        variation_data = variation.get('item_variation_data', {})
                        variation_name = variation_data.get('name', name)
                        
                        # Get expected duration (might be in milliseconds)
                        service_duration = variation_data.get('service_duration')
                        expected_minutes = None
                        
                        if service_duration:
                            # Convert from milliseconds to minutes
                            expected_minutes = service_duration / 60000
                        
                        service_catalog[variation_id] = {
                            'name': variation_name,
                            'parent_name': name,
                            'expected_duration_ms': service_duration,
                            'expected_minutes': expected_minutes
                        }
    except Exception as e:
        print(f"❌ Error loading catalog: {e}")
        return
    
    print(f"✅ Loaded catalog with {len(service_catalog)} service variations")
    
    # ==============================================================
    # GET LAINE'S FULL WEEK OF APPOINTMENTS
    # ==============================================================
    laine_id = "TMZx2T5T5arYJTm7"
    start_date = datetime(2025, 9, 1)
    end_date = datetime(2025, 9, 7)
    
    start_str = start_date.strftime('%Y-%m-%dT00:00:00Z')
    end_str = (end_date + timedelta(days=1) - timedelta(seconds=1)).strftime('%Y-%m-%dT23:59:59Z')
    
    # Get appointments
    laine_appointments = []
    cursor = None
    
    while True:
        url = f"{api_base_url}/v2/bookings?limit=200&start_at_min={start_str}&start_at_max={end_str}"
        if cursor:
            url += f"&cursor={cursor}"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                bookings = data.get('bookings', [])
                
                for apt in bookings:
                    segments = apt.get('appointment_segments', [])
                    for segment in segments:
                        if segment.get('team_member_id') == laine_id:
                            laine_appointments.append({
                                'start_at': apt.get('start_at'),
                                'segment': segment
                            })
                
                cursor = data.get('cursor')
                if not cursor:
                    break
            else:
                break
        except:
            break
    
    print(f"✅ Found {len(laine_appointments)} appointments for analysis")
    
    # ==============================================================
    # COMPARE SCHEDULED VS EXPECTED DURATIONS
    # ==============================================================
    print(f"\n📊 DURATION COMPARISON ANALYSIS")
    print("=" * 40)
    
    total_scheduled_minutes = 0
    total_expected_minutes = 0
    mismatches = []
    matches = 0
    no_catalog_data = 0
    
    print(f"{'SERVICE':<25} {'SCHEDULED':<10} {'EXPECTED':<10} {'DIFF':<8} {'STATUS'}")
    print("-" * 70)
    
    for apt in laine_appointments:
        segment = apt['segment']
        service_var_id = segment.get('service_variation_id', '')
        scheduled_minutes = segment.get('duration_minutes', 0)
        
        total_scheduled_minutes += scheduled_minutes
        
        if service_var_id in service_catalog:
            catalog_info = service_catalog[service_var_id]
            expected_minutes = catalog_info['expected_minutes']
            service_name = catalog_info['parent_name'][:20] + "..." if len(catalog_info['parent_name']) > 20 else catalog_info['parent_name']
            
            if expected_minutes:
                total_expected_minutes += expected_minutes
                diff = expected_minutes - scheduled_minutes
                
                if abs(diff) <= 1:  # Within 1 minute = match
                    status = "✅ MATCH"
                    matches += 1
                elif diff > 0:
                    status = "⬆️  UNDER"
                    mismatches.append({
                        'service': service_name,
                        'scheduled': scheduled_minutes,
                        'expected': expected_minutes,
                        'difference': diff,
                        'type': 'under_scheduled'
                    })
                else:
                    status = "⬇️  OVER"
                    mismatches.append({
                        'service': service_name,
                        'scheduled': scheduled_minutes,
                        'expected': expected_minutes,
                        'difference': diff,
                        'type': 'over_scheduled'
                    })
                
                print(f"{service_name:<25} {scheduled_minutes}min{'':<6} {expected_minutes:.0f}min{'':<6} {diff:+.0f}min{'':<4} {status}")
                
            else:
                print(f"{service_name:<25} {scheduled_minutes}min{'':<6} {'No data':<10} {'N/A':<8} ❓ NO DATA")
                total_expected_minutes += scheduled_minutes  # Use scheduled as fallback
                no_catalog_data += 1
        else:
            print(f"{'Unknown Service':<25} {scheduled_minutes}min{'':<6} {'Not found':<10} {'N/A':<8} ❌ NOT FOUND")
            total_expected_minutes += scheduled_minutes  # Use scheduled as fallback
            no_catalog_data += 1
    
    # ==============================================================
    # CALCULATE UTILIZATION WITH BOTH METHODS
    # ==============================================================
    print(f"\n🎯 UTILIZATION CALCULATION COMPARISON")
    print("=" * 40)
    
    scheduled_hours = total_scheduled_minutes / 60
    expected_hours = total_expected_minutes / 60
    work_week_hours = 40
    
    scheduled_utilization = (scheduled_hours / work_week_hours) * 100
    expected_utilization = (expected_hours / work_week_hours) * 100
    
    print(f"TOTAL DURATION COMPARISON:")
    print(f"  Scheduled duration: {total_scheduled_minutes} minutes ({scheduled_hours:.2f} hours)")
    print(f"  Expected duration: {total_expected_minutes:.0f} minutes ({expected_hours:.2f} hours)")
    print(f"  Difference: {total_expected_minutes - total_scheduled_minutes:.0f} minutes ({expected_hours - scheduled_hours:.2f} hours)")
    
    print(f"\nUTILIZATION CALCULATIONS:")
    print(f"  Our method (scheduled): {scheduled_utilization:.1f}%")
    print(f"  Square method (expected): {expected_utilization:.1f}%")
    print(f"  Square's actual figure: 60.0%")
    print(f"  Gap (vs Square): {abs(expected_utilization - 60.0):.1f}%")
    
    # ==============================================================
    # MISMATCH ANALYSIS
    # ==============================================================
    print(f"\n📋 MISMATCH SUMMARY")
    print("=" * 25)
    
    print(f"Appointment analysis:")
    print(f"  Perfect matches: {matches}")
    print(f"  Duration mismatches: {len(mismatches)}")
    print(f"  No catalog data: {no_catalog_data}")
    print(f"  Total appointments: {len(laine_appointments)}")
    
    if mismatches:
        under_scheduled = [m for m in mismatches if m['type'] == 'under_scheduled']
        over_scheduled = [m for m in mismatches if m['type'] == 'over_scheduled']
        
        print(f"\nMismatch breakdown:")
        print(f"  Under-scheduled: {len(under_scheduled)} (service needs more time)")
        print(f"  Over-scheduled: {len(over_scheduled)} (service needs less time)")
        
        if under_scheduled:
            print(f"\n  Top under-scheduled services:")
            sorted_under = sorted(under_scheduled, key=lambda x: x['difference'], reverse=True)
            for mismatch in sorted_under[:5]:
                print(f"    • {mismatch['service']}: {mismatch['scheduled']}min scheduled, {mismatch['expected']:.0f}min needed (+{mismatch['difference']:.0f}min)")
    
    # ==============================================================
    # CONCLUSION
    # ==============================================================
    print(f"\n🏆 CONCLUSION")
    print("=" * 15)
    
    if abs(expected_utilization - 60.0) < 5:
        print(f"✅ HYPOTHESIS CONFIRMED!")
        print(f"Square likely uses EXPECTED durations ({expected_utilization:.1f}%)")
        print(f"vs our SCHEDULED durations ({scheduled_utilization:.1f}%)")
        print(f"This explains the utilization gap!")
    else:
        print(f"❓ HYPOTHESIS PARTIALLY CONFIRMED")
        print(f"Expected duration method: {expected_utilization:.1f}%")
        print(f"Still {abs(expected_utilization - 60.0):.1f}% gap from Square's 60%")
        print(f"May need to check different time period or calculation method")
    
    return {
        'scheduled_utilization': scheduled_utilization,
        'expected_utilization': expected_utilization,
        'square_utilization': 60.0,
        'matches': matches,
        'mismatches': len(mismatches),
        'total_appointments': len(laine_appointments)
    }

if __name__ == "__main__":
    result = analyze_duration_mismatch()
    
    print(f"\n" + "=" * 50)
    print("⏰ DURATION MISMATCH ANALYSIS COMPLETE")
    
    if result:
        print(f"Scheduled method: {result['scheduled_utilization']:.1f}%")
        print(f"Expected method: {result['expected_utilization']:.1f}%")
        print(f"Square's figure: {result['square_utilization']:.1f}%")
        print(f"Duration matches: {result['matches']}/{result['total_appointments']}")
        
        if abs(result['expected_utilization'] - 60.0) < 5:
            print(f"\n🎯 SUCCESS: Utilization calculation method identified!")
        else:
            print(f"\n⚠️  Still investigating utilization calculation method")
    else:
        print(f"❌ ANALYSIS FAILED")