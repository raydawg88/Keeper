#!/usr/bin/env python3
"""
MAP TEAM MEMBER IDs TO REAL NAMES
- We have IDs like TMZx2T5T5arYJTm7 from appointments
- Need to show "Laine Duttlinger" instead of cryptic IDs
- Check Team Members API for name mapping
- Cross-reference with appointment data to show real names
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def map_team_member_ids_to_names():
    """Map team member IDs from appointments to real names"""
    
    print("👥 MAP TEAM MEMBER IDs TO REAL NAMES")
    print("=" * 60)
    print("GOAL: Convert TMZx2T5T5arYJTm7 → 'Laine Duttlinger'")
    print("SOURCE: Team Members API + Appointment data cross-reference")
    
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
    
    # STEP 1: Get team members with names from Team Members API
    print(f"\n📡 STEP 1: GET TEAM MEMBERS WITH NAMES")
    print(f"URL: {api_base_url}/v2/team-members/search")
    print(f"Method: POST")
    
    team_member_names = {}
    
    try:
        search_body = {"limit": 50}
        response = requests.post(f"{api_base_url}/v2/team-members/search", 
                               headers=headers, 
                               json=search_body)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            team_members = data.get('team_members', [])
            
            print(f"✅ SUCCESS! Found {len(team_members)} team members")
            
            # Build ID to name mapping
            for member in team_members:
                member_id = member.get('id')
                given_name = member.get('given_name', '')
                family_name = member.get('family_name', '')
                full_name = f"{given_name} {family_name}".strip()
                status = member.get('status', 'UNKNOWN')
                
                if member_id:
                    team_member_names[member_id] = {
                        'name': full_name or 'Unknown Name',
                        'given_name': given_name,
                        'family_name': family_name,
                        'status': status,
                        'is_owner': member.get('is_owner', False)
                    }
                    
                    print(f"  {member_id}: {full_name} ({status})")
            
        else:
            print(f"❌ ERROR: {response.text}")
            return {}
            
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")
        return {}
    
    # STEP 2: Load appointment data from our checkpoint
    print(f"\n📊 STEP 2: LOAD APPOINTMENT DATA")
    
    appointment_team_counts = {}
    try:
        # Try to load from our checkpoint file
        checkpoint_files = [
            '/tmp/square_appointments_30k_final.json',
            '/tmp/square_appointments_checkpoint_10590.json'
        ]
        
        for checkpoint_file in checkpoint_files:
            try:
                with open(checkpoint_file, 'r') as f:
                    checkpoint_data = json.load(f)
                    
                # Look for team member counts
                if 'historical_team_counts' in checkpoint_data:
                    appointment_team_counts.update(checkpoint_data['historical_team_counts'])
                    print(f"✅ Loaded historical team counts from {checkpoint_file}")
                    break
                    
            except FileNotFoundError:
                continue
        
        if not appointment_team_counts:
            print("⚠️  No appointment checkpoint found, will use Team Members API data only")
            
    except Exception as e:
        print(f"⚠️  Could not load appointment data: {e}")
    
    # STEP 3: Create comprehensive mapping with appointment counts
    print(f"\n📋 STEP 3: CREATE COMPREHENSIVE ID-TO-NAME MAPPING")
    print("=" * 60)
    
    print(f"{'ID':<25} {'NAME':<20} {'STATUS':<10} {'APPOINTMENTS':<12} {'ROLE'}")
    print("-" * 80)
    
    # Combine team member data with appointment counts
    all_team_members = {}
    
    for member_id, member_info in team_member_names.items():
        appointment_count = appointment_team_counts.get(member_id, 0)
        
        all_team_members[member_id] = {
            'name': member_info['name'],
            'status': member_info['status'],
            'appointments': appointment_count,
            'is_owner': member_info['is_owner']
        }
        
        # Show in formatted table
        name = member_info['name'][:20]
        status = member_info['status'][:10]  
        role = "OWNER" if member_info['is_owner'] else "STAFF"
        
        print(f"{member_id:<25} {name:<20} {status:<10} {appointment_count:<12,} {role}")
    
    # STEP 4: Identify key staff members
    print(f"\n🎯 STEP 4: IDENTIFY KEY STAFF MEMBERS")
    print("=" * 50)
    
    # Look for Laine Duttlinger specifically
    laine_candidates = []
    for member_id, info in all_team_members.items():
        name = info['name'].lower()
        if 'laine' in name or 'duttlinger' in name:
            laine_candidates.append((member_id, info))
            print(f"🎯 FOUND LAINE: {member_id} = {info['name']} ({info['appointments']:,} appointments)")
    
    # Show top performers by appointment count
    print(f"\n🏆 TOP PERFORMERS BY APPOINTMENTS:")
    sorted_by_appointments = sorted(all_team_members.items(), 
                                   key=lambda x: x[1]['appointments'], 
                                   reverse=True)[:10]
    
    for i, (member_id, info) in enumerate(sorted_by_appointments, 1):
        if info['appointments'] > 0:
            print(f"  {i}. {info['name']}: {info['appointments']:,} appointments ({info['status']})")
            
            # Check if this matches expected Laine count (~7,212)
            if 6000 <= info['appointments'] <= 8000:
                print(f"     ⭐ LIKELY LAINE: Expected ~7,212 appointments")
    
    # STEP 5: Save mapping for future use
    print(f"\n💾 STEP 5: SAVE ID-TO-NAME MAPPING")
    
    mapping_file = "/tmp/team_member_id_name_mapping.json"
    with open(mapping_file, 'w') as f:
        json.dump({
            'mapping_info': {
                'created_at': datetime.now().isoformat(),
                'total_team_members': len(all_team_members),
                'active_members': len([m for m in all_team_members.values() if m['status'] == 'ACTIVE']),
                'with_appointments': len([m for m in all_team_members.values() if m['appointments'] > 0])
            },
            'id_to_name_mapping': all_team_members,
            'laine_candidates': [{'id': id, 'info': info} for id, info in laine_candidates] if laine_candidates else []
        }, f, indent=2)
    
    print(f"✅ Mapping saved to: {mapping_file}")
    
    # VERIFICATION
    print(f"\n✅ VERIFICATION:")
    print(f"Team members mapped: {len(all_team_members)}")
    print(f"With appointment data: {len([m for m in all_team_members.values() if m['appointments'] > 0])}")
    print(f"Laine candidates found: {len(laine_candidates)}")
    
    return all_team_members, laine_candidates

if __name__ == "__main__":
    mapping, laine_candidates = map_team_member_ids_to_names()
    
    print(f"\n" + "=" * 60)
    if mapping:
        print("🎉 TEAM MEMBER ID MAPPING: SUCCESS!")
        print("✅ IDs mapped to real names")
        print("✅ Appointment counts included") 
        print("✅ Status and roles identified")
        
        if laine_candidates:
            print(f"✅ Laine Duttlinger candidates: {len(laine_candidates)}")
        else:
            print("⚠️  Laine Duttlinger not found by name")
            print("    (May be under different name in system)")
    else:
        print("❌ TEAM MEMBER MAPPING: FAILED!")
        print("⚠️  Could not retrieve team member names")