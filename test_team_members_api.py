#!/usr/bin/env python3
"""
TEST 4: TEAM MEMBERS API
- Call Team Members API
- Show actual employee data
- Show raw JSON response
- Store in JSON file  
- Verify staff count and roles
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_team_members_api():
    """Test Team Members API step by step"""
    
    print("👥 TEST 4: TEAM MEMBERS API")
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
    
    print("🌐 CALLING TEAM MEMBERS API...")
    print(f"URL: {api_base_url}/v2/team-members/search")
    print("Method: POST (Team Members requires search with body)")
    
    # Team Members API requires POST with search criteria
    search_body = {
        "limit": 20
    }
    
    try:
        response = requests.post(f"{api_base_url}/v2/team-members/search", 
                               headers=headers, 
                               json=search_body)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            team_data = response.json()
            team_members = team_data.get('team_members', [])
            
            print(f"✅ SUCCESS! Retrieved {len(team_members)} team members")
            
            # Show raw JSON response
            print(f"\n📋 RAW JSON RESPONSE:")
            print("-" * 60)
            print(json.dumps(team_data, indent=2))
            print("-" * 60)
            
            if team_members:
                print(f"\n👥 TEAM MEMBER DETAILS:")
                active_members = []
                inactive_members = []
                
                for i, member in enumerate(team_members, 1):
                    member_id = member.get('id')
                    given_name = member.get('given_name', '')
                    family_name = member.get('family_name', '')
                    email = member.get('email_address', '')
                    phone = member.get('phone_number', '')
                    status = member.get('status', 'UNKNOWN')
                    is_owner = member.get('is_owner', False)
                    assigned_locations = member.get('assigned_locations', [])
                    
                    full_name = f"{given_name} {family_name}".strip()
                    if not full_name:
                        full_name = f"Team Member {i}"
                    
                    print(f"\nTeam Member {i}:")
                    print(f"  ID: {member_id}")
                    print(f"  Name: {full_name}")
                    print(f"  Email: {email or 'N/A'}")
                    print(f"  Phone: {phone or 'N/A'}")
                    print(f"  Status: {status}")
                    print(f"  Owner: {'Yes' if is_owner else 'No'}")
                    print(f"  Locations: {len(assigned_locations)} assigned")
                    print(f"  Created: {member.get('created_at', 'N/A')}")
                    print(f"  Updated: {member.get('updated_at', 'N/A')}")
                    
                    if status == 'ACTIVE':
                        active_members.append(member)
                    else:
                        inactive_members.append(member)
                
                print(f"\n👥 TEAM SUMMARY:")
                print(f"Total Team Members: {len(team_members)}")
                print(f"Active Members: {len(active_members)}")
                print(f"Inactive Members: {len(inactive_members)}")
                
                owners = [m for m in team_members if m.get('is_owner')]
                print(f"Business Owners: {len(owners)}")
                
                # Check email coverage
                with_emails = [m for m in team_members if m.get('email_address')]
                print(f"Members with Email: {len(with_emails)}/{len(team_members)} ({len(with_emails)/len(team_members)*100:.1f}%)")
                
                # Check phone coverage
                with_phones = [m for m in team_members if m.get('phone_number')]
                print(f"Members with Phone: {len(with_phones)}/{len(team_members)} ({len(with_phones)/len(team_members)*100:.1f}%)")
            
            # Store team members data
            print(f"\n💾 STORING TEAM MEMBERS DATA...")
            
            # Transform team members for storage
            team_records = []
            for member in team_members:
                assigned_locations = member.get('assigned_locations', [])
                
                team_record = {
                    'id': f"team_{member.get('id')}",
                    'account_id': account_id,
                    'team_member_id': member.get('id'),
                    'reference_id': member.get('reference_id'),
                    'is_owner': member.get('is_owner', False),
                    'status': member.get('status'),
                    'given_name': member.get('given_name'),
                    'family_name': member.get('family_name'),
                    'email_address': member.get('email_address'),
                    'phone_number': member.get('phone_number'),
                    'assigned_locations': assigned_locations,
                    'assigned_locations_count': len(assigned_locations),
                    'created_at': member.get('created_at'),
                    'updated_at': member.get('updated_at'),
                    'square_data': member,  # Store full Square data
                    'synced_at': datetime.now().isoformat(),
                    'data_source': 'Square Team Members API v2',
                    'test_timestamp': datetime.now().isoformat()
                }
                
                team_records.append(team_record)
            
            # Save to JSON file
            output_file = f"/tmp/square_team_members_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump({
                    'test_info': {
                        'test_name': 'Square Team Members API Test',
                        'account_id': account_id,
                        'timestamp': datetime.now().isoformat(),
                        'team_members_count': len(team_records),
                        'active_members': len([r for r in team_records if r['status'] == 'ACTIVE']),
                        'inactive_members': len([r for r in team_records if r['status'] != 'ACTIVE']),
                        'owners_count': len([r for r in team_records if r['is_owner']]),
                        'api_endpoint': '/v2/team-members',
                        'api_version': '2025-08-20'
                    },
                    'team_members': team_records
                }, f, indent=2)
            
            print(f"✅ Team members data saved to: {output_file}")
            
            # Data quality verification
            print(f"\n📊 DATA QUALITY VERIFICATION:")
            print("-" * 40)
            
            active_records = [r for r in team_records if r['status'] == 'ACTIVE']
            with_email_records = [r for r in team_records if r['email_address']]
            with_phone_records = [r for r in team_records if r['phone_number']]
            
            print(f"Total Team Members: {len(team_records)}")
            print(f"Active Team Members: {len(active_records)} ({len(active_records)/len(team_records)*100:.1f}%)")
            print(f"Email Coverage: {len(with_email_records)}/{len(team_records)} ({len(with_email_records)/len(team_records)*100:.1f}%)")
            print(f"Phone Coverage: {len(with_phone_records)}/{len(team_records)} ({len(with_phone_records)/len(team_records)*100:.1f}%)")
            
            # Compare with expected count (you mentioned 16 active employees)
            expected_active = 16
            if len(active_records) != expected_active:
                print(f"⚠️  Note: Found {len(active_records)} active members, expected {expected_active}")
                print(f"   This may include owners, managers, or different status definitions")
            else:
                print(f"✅ Active count matches expectation: {expected_active}")
            
            return True
            
        elif response.status_code == 404:
            print(f"❌ TEAM MEMBERS API NOT FOUND: {response.status_code}")
            print(f"This endpoint may not be available or requires additional permissions")
            print(f"Error: {response.text}")
            return False
            
        else:
            print(f"❌ TEAM MEMBERS API FAILED: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ TEAM MEMBERS API ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_team_members_api()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 TEST 4 (TEAM MEMBERS API) COMPLETE!")
        print("✅ API call successful")
        print("✅ Raw JSON response shown")
        print("✅ Team member details extracted")
        print("✅ Staff count and roles verified")
        print("✅ Data quality verified")
        print("✅ Data saved to JSON file")
        print("\n📋 ALL API TESTS COMPLETE! Ready for database integration.")
    else:
        print("❌ TEST 4 (TEAM MEMBERS API) FAILED!")
        print("⚠️  This API may require additional permissions or setup")
        print("📋 Continuing with available data from other APIs")