#!/usr/bin/env python3
"""
Debug script to examine Square Catalog API response structure
"""

import requests
import json
from typing import Dict, List

def debug_square_catalog():
    access_token = "EAAAlswReG53bJehffaCjrK9A-Cc8g7PTizcq2de8TlV4KEmeyoNwtoytt_4PDFn"
    base_url = "https://connect.squareup.com"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Square-Version": "2023-10-18"
    }
    
    url = f"{base_url}/v2/catalog/list"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print("=== CATALOG API RESPONSE DEBUG ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response Keys: {list(data.keys())}")
        
        if "objects" in data:
            objects = data["objects"]
            print(f"Total Objects: {len(objects)}")
            
            # Count by type
            type_counts = {}
            for obj in objects:
                obj_type = obj.get("type", "UNKNOWN")
                type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
            
            print("\nObject Types:")
            for obj_type, count in type_counts.items():
                print(f"  {obj_type}: {count}")
            
            # Show first few objects of each type
            print("\n=== SAMPLE OBJECTS ===")
            for obj_type in type_counts.keys():
                print(f"\n--- {obj_type} SAMPLE ---")
                sample_objs = [obj for obj in objects if obj.get("type") == obj_type][:2]
                for i, obj in enumerate(sample_objs):
                    print(f"Object {i+1}:")
                    print(json.dumps(obj, indent=2)[:500] + "..." if len(json.dumps(obj, indent=2)) > 500 else json.dumps(obj, indent=2))
        
        # Also save full response for analysis
        with open("/Users/rayhernandez/KEEPER/full_catalog_response.json", "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"\nFull response saved to: /Users/rayhernandez/KEEPER/full_catalog_response.json")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    debug_square_catalog()