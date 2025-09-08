#!/usr/bin/env python3
"""
FIX BOOKINGS API WITH PROPER PAGINATION
- Get ALL 55,236 appointments, not just 10
- Implement proper pagination with cursors
- Show exact API calls being made
- Verify Laine has 7,212 appointments
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def fix_bookings_pagination():
    """Fix bookings API with proper pagination to get all 55,236 appointments"""
    
    print("📅 FIX: BOOKINGS API WITH PROPER PAGINATION")
    print("=" * 70)
    print("TARGET: Get ALL 55,236 appointments (not just 10!)")
    
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
    
    all_bookings = []
    cursor = None
    page = 1
    max_pages = 300  # Safety limit (55,236 / 200 = ~276 pages)
    
    print(f"\n🌐 IMPLEMENTING PROPER PAGINATION:")
    print(f"- Using limit=200 per page")
    print(f"- Expected pages: ~276 (55,236 ÷ 200)")
    print(f"- Safety limit: {max_pages} pages")
    
    while page <= max_pages:
        # Build URL with proper pagination
        url = f"{api_base_url}/v2/bookings?limit=200"
        if cursor:
            url += f"&cursor={cursor}"
        
        print(f"\n📡 PAGE {page} - EXACT API CALL:")
        print(f"URL: {url}")
        print(f"Headers: Authorization: Bearer {access_token[:20]}...")
        print(f"Method: GET")
        
        try:
            response = requests.get(url, headers=headers)
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ API ERROR: {response.status_code}")
                print(f"Response: {response.text}")
                break
            
            data = response.json()
            bookings = data.get('bookings', [])
            cursor = data.get('cursor')
            
            print(f"✅ Retrieved {len(bookings)} bookings from page {page}")
            print(f"Cursor for next page: {cursor[:20] + '...' if cursor else 'None (last page)'}")
            
            # Add to our collection
            all_bookings.extend(bookings)
            
            print(f"📊 Running Total: {len(all_bookings)} appointments")
            
            # Show sample data from this page
            if bookings:
                sample = bookings[0]
                customer_id = sample.get('customer_id', 'N/A')
                start_at = sample.get('start_at', 'N/A')
                status = sample.get('booking_status', 'N/A')
                print(f"Sample: Customer {customer_id[:10]}..., Status: {status}, Start: {start_at[:10]}")
            
            # Check if we're done
            if not cursor or len(bookings) == 0:
                print(f"🏁 PAGINATION COMPLETE - No more pages")
                break
                
            page += 1
            
        except Exception as e:
            print(f"❌ CONNECTION ERROR: {e}")
            break
    
    # FINAL RESULTS
    print(f"\n🎯 FINAL BOOKINGS RESULTS:")
    print("=" * 50)
    print(f"Total Appointments Retrieved: {len(all_bookings):,}")
    print(f"Expected Appointments: 55,236")
    print(f"Data Coverage: {(len(all_bookings) / 55236) * 100:.2f}%")
    print(f"Pages Processed: {page - 1}")
    
    if len(all_bookings) < 50000:
        print(f"⚠️  WARNING: Still missing {55236 - len(all_bookings):,} appointments")
        print(f"Possible issues:")
        print(f"- Date range filtering (only future appointments?)")
        print(f"- Status filtering (only active appointments?)")
        print(f"- Location filtering (missing locations?)")
        print(f"- Permission restrictions")
    
    # Analyze by team member (check Laine's 7,212 appointments)
    if all_bookings:
        print(f"\n👥 APPOINTMENTS BY TEAM MEMBER:")
        print("-" * 40)
        
        team_member_counts = {}
        for booking in all_bookings:
            # Look for team member in appointment segments
            segments = booking.get('appointment_segments', [])
            for segment in segments:
                team_member_id = segment.get('team_member_id')
                if team_member_id:
                    team_member_counts[team_member_id] = team_member_counts.get(team_member_id, 0) + 1
        
        # Sort by count
        sorted_members = sorted(team_member_counts.items(), key=lambda x: x[1], reverse=True)
        
        print(f"Team Members Found: {len(sorted_members)}")
        for member_id, count in sorted_members[:10]:  # Top 10
            print(f"  {member_id}: {count:,} appointments")
        
        # Look specifically for Laine
        laine_found = False
        for member_id, count in sorted_members:
            # Check if this could be Laine (look for someone with ~7,212)
            if 7000 <= count <= 7500:
                print(f"🎯 POSSIBLE LAINE: {member_id} with {count:,} appointments")
                laine_found = True
        
        if not laine_found:
            print(f"❌ LAINE NOT FOUND: No team member with ~7,212 appointments")
    
    # Save results
    print(f"\n💾 SAVING RESULTS...")
    output_file = f"/tmp/square_bookings_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            'pagination_info': {
                'total_appointments': len(all_bookings),
                'expected_appointments': 55236,
                'coverage_percent': (len(all_bookings) / 55236) * 100,
                'pages_processed': page - 1,
                'team_members_found': len(team_member_counts) if all_bookings else 0
            },
            'team_member_counts': team_member_counts if all_bookings else {},
            'bookings': all_bookings[:100],  # Save first 100 for analysis
            'sample_booking': all_bookings[0] if all_bookings else None
        }, f, indent=2)
    
    print(f"✅ Results saved to: {output_file}")
    
    return len(all_bookings), team_member_counts if all_bookings else {}

if __name__ == "__main__":
    total_appointments, team_counts = fix_bookings_pagination()
    
    print(f"\n" + "=" * 70)
    if total_appointments >= 50000:
        print("🎉 BOOKINGS API FIX: SUCCESS!")
        print(f"✅ Retrieved {total_appointments:,} appointments")
        print(f"✅ Proper pagination implemented")
    else:
        print("⚠️  BOOKINGS API FIX: PARTIAL SUCCESS")
        print(f"Retrieved {total_appointments:,} appointments")
        print(f"Still need investigation for full 55,236")
    
    print(f"\n📋 NEXT: Fix Subscriptions, Timecards, Cash Drawer APIs")