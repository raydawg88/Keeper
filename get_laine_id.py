#!/usr/bin/env python3
"""
Get Laine Duttlinger's team member ID
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_laine_id():
    """Find Laine Duttlinger's team member ID"""
    
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
    
    # Get all team members
    try:
        search_body = {"limit": 100}
        response = requests.post(f"{api_base_url}/v2/team-members/search", 
                               headers=headers, 
                               json=search_body)
        
        if response.status_code == 200:
            data = response.json()
            all_team_members = data.get('team_members', [])
            
            print(f"Found {len(all_team_members)} team members:")
            
            laine_id = None
            for member in all_team_members:
                given_name = member.get('given_name', '')
                family_name = member.get('family_name', '')
                full_name = f"{given_name} {family_name}".strip()
                member_id = member.get('id')
                status = member.get('status', 'Unknown')
                
                print(f"  {full_name} ({member_id}) - {status}")
                
                if 'laine' in full_name.lower() and 'duttlinger' in full_name.lower():
                    laine_id = member_id
                    print(f"  ✅ FOUND LAINE: {laine_id}")
            
            return laine_id
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    laine_id = get_laine_id()
    if laine_id:
        print(f"\n✅ Laine Duttlinger ID: {laine_id}")
    else:
        print(f"\n❌ Could not find Laine Duttlinger")