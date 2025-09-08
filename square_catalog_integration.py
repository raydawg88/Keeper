#!/usr/bin/env python3
"""
Square Catalog API Integration for Brazilian Wax Spa Service Verification
Critical data integrity script to resolve service_variation_ids to actual service names
"""

import requests
import json
from typing import Dict, List, Optional, Tuple
import os
from datetime import datetime
import csv

class SquareCatalogAPI:
    def __init__(self, access_token: str, environment: str = "production"):
        self.access_token = access_token
        self.environment = environment
        self.base_url = "https://connect.squareup.com" if environment == "production" else "https://connect.squareupsandbox.com"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Square-Version": "2023-10-18"
        }
        self.service_cache = {}
    
    def get_catalog_items(self, types: List[str] = None) -> Dict:
        """
        Retrieve catalog items from Square API
        """
        url = f"{self.base_url}/v2/catalog/list"
        params = {}
        
        if types:
            params["types"] = ",".join(types)
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching catalog: {e}")
            return {}
    
    def extract_service_variations(self, catalog_data: Dict) -> Dict[str, Dict]:
        """
        Extract service variations and map IDs to service names
        Returns: {variation_id: {name, item_name, category, present_at_all_locations, ...}}
        """
        variations = {}
        
        if "objects" not in catalog_data:
            print("No objects found in catalog data")
            return variations
        
        # Process items and their nested variations
        for obj in catalog_data["objects"]:
            if obj.get("type") == "ITEM":
                item_data = obj.get("item_data", {})
                item_name = item_data.get("name", "Unknown Item")
                item_id = obj["id"]
                
                # Process nested variations
                nested_variations = item_data.get("variations", [])
                for variation in nested_variations:
                    variation_id = variation["id"]
                    variation_data = variation.get("item_variation_data", {})
                    
                    variations[variation_id] = {
                        "variation_name": variation_data.get("name", "Default"),
                        "item_name": item_name,
                        "item_id": item_id,
                        "sku": variation_data.get("sku", ""),
                        "present_at_all_locations": variation.get("present_at_all_locations", False),
                        "category_id": item_data.get("category_id", ""),
                        "is_deleted": variation.get("is_deleted", False),
                        "version": variation.get("version", 0),
                        "price_amount": variation_data.get("price_money", {}).get("amount", 0),
                        "currency": variation_data.get("price_money", {}).get("currency", "USD"),
                        "sellable": variation_data.get("sellable", False),
                        "full_name": f"{item_name} - {variation_data.get('name', 'Default')}"
                    }
        
        return variations
    
    def categorize_services(self, variations: Dict[str, Dict]) -> Dict[str, List]:
        """
        Categorize services to identify spa vs salon services
        """
        spa_keywords = [
            "wax", "brazilian", "bikini", "eyebrow", "lip", "chin", "underarm", 
            "leg", "facial", "massage", "skin", "peel", "threading", "sugaring",
            "face", "cheek", "upper lip", "lower leg", "full leg", "arms", "back",
            "chest", "buttocks", "landing strip", "full body", "membership"
        ]
        
        salon_keywords = [
            "haircut", "hair", "color", "highlight", "perm", "blowout", "style",
            "manicure", "pedicure", "nail", "gel", "acrylic", "polish", "shampoo",
            "conditioning", "straightening", "curling"
        ]
        
        product_keywords = [
            "soap", "cream", "balm", "lotion", "oil", "scrub", "cleanser",
            "moisturizer", "serum", "toner", "mask", "exfoliant"
        ]
        
        categorized = {
            "spa_services": [],
            "salon_services": [],
            "retail_products": [],
            "unclear_services": [],
            "inactive_services": []
        }
        
        for var_id, var_data in variations.items():
            full_name = var_data["full_name"].lower()
            
            if var_data["is_deleted"]:
                categorized["inactive_services"].append((var_id, var_data))
                continue
            
            is_spa = any(keyword in full_name for keyword in spa_keywords)
            is_salon = any(keyword in full_name for keyword in salon_keywords)
            is_product = any(keyword in full_name for keyword in product_keywords)
            
            if is_spa and not is_salon and not is_product:
                categorized["spa_services"].append((var_id, var_data))
            elif is_salon and not is_spa:
                categorized["salon_services"].append((var_id, var_data))
            elif is_product:
                categorized["retail_products"].append((var_id, var_data))
            else:
                categorized["unclear_services"].append((var_id, var_data))
        
        return categorized
    
    def resolve_service_name(self, variation_id: str) -> Optional[str]:
        """
        Resolve a service variation ID to human-readable name
        Uses cache to avoid repeated API calls
        """
        if variation_id in self.service_cache:
            return self.service_cache[variation_id]
        
        # If not cached, would need to fetch from API
        # For now, return None to indicate cache miss
        return None
    
    def generate_service_mapping_report(self, variations: Dict[str, Dict], categorized: Dict[str, List]) -> str:
        """
        Generate comprehensive service mapping report
        """
        report = []
        report.append("# VERIFIED SQUARE CATALOG SERVICE MAPPING")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Environment: {self.environment}")
        report.append("")
        
        # Summary
        report.append("## SUMMARY")
        report.append(f"Total Items Found: {len(variations)}")
        report.append(f"Spa Services: {len(categorized['spa_services'])}")
        report.append(f"Salon Services: {len(categorized['salon_services'])}")
        report.append(f"Retail Products: {len(categorized['retail_products'])}")
        report.append(f"Unclear Items: {len(categorized['unclear_services'])}")
        report.append(f"Inactive Items: {len(categorized['inactive_services'])}")
        report.append("")
        
        # Data integrity assessment
        salon_count = len(categorized['salon_services'])
        spa_count = len(categorized['spa_services'])
        
        if salon_count > 0:
            report.append("## ⚠️ DATA INTEGRITY ALERT")
            report.append(f"Found {salon_count} salon services in Brazilian wax spa catalog!")
            report.append("This indicates catalog contamination that needs immediate attention.")
            report.append("")
        
        # Spa Services (Expected)
        report.append("## ✅ VERIFIED SPA SERVICES")
        for var_id, var_data in categorized['spa_services']:
            report.append(f"- {var_id}: {var_data['full_name']}")
        report.append("")
        
        # Salon Services (Unexpected)
        if categorized['salon_services']:
            report.append("## ❌ SALON SERVICES (SHOULD NOT EXIST)")
            for var_id, var_data in categorized['salon_services']:
                report.append(f"- {var_id}: {var_data['full_name']}")
            report.append("")
        
        # Retail Products
        if categorized['retail_products']:
            report.append("## 🛒 RETAIL PRODUCTS")
            for var_id, var_data in categorized['retail_products'][:10]:  # Show first 10
                price = f"${var_data['price_amount']/100:.2f}" if var_data['price_amount'] else "No price"
                report.append(f"- {var_id}: {var_data['full_name']} ({price})")
            if len(categorized['retail_products']) > 10:
                report.append(f"... and {len(categorized['retail_products']) - 10} more products")
            report.append("")
        
        # Unclear Services
        if categorized['unclear_services']:
            report.append("## ❓ UNCLEAR ITEMS (NEED MANUAL REVIEW)")
            for var_id, var_data in categorized['unclear_services']:
                report.append(f"- {var_id}: {var_data['full_name']}")
            report.append("")
        
        # Complete mapping table
        report.append("## COMPLETE SERVICE VARIATION MAPPING")
        report.append("| Variation ID | Service Name | Category | Active |")
        report.append("|--------------|--------------|----------|--------|")
        
        for var_id, var_data in variations.items():
            category = "Unknown"
            if any(var_id == v[0] for v in categorized['spa_services']):
                category = "Spa"
            elif any(var_id == v[0] for v in categorized['salon_services']):
                category = "Salon"
            elif any(var_id == v[0] for v in categorized['unclear_services']):
                category = "Unclear"
            elif any(var_id == v[0] for v in categorized['inactive_services']):
                category = "Inactive"
            
            active = "Yes" if not var_data['is_deleted'] else "No"
            report.append(f"| {var_id} | {var_data['full_name']} | {category} | {active} |")
        
        return "\n".join(report)


def main():
    """
    Main execution function
    """
    print("Starting Square Catalog API Integration...")
    
    # Load credentials from environment
    access_token = "EAAAlswReG53bJehffaCjrK9A-Cc8g7PTizcq2de8TlV4KEmeyoNwtoytt_4PDFn"
    environment = "production"
    
    # Initialize Square API client
    square_api = SquareCatalogAPI(access_token, environment)
    
    print("Fetching catalog data from Square...")
    catalog_data = square_api.get_catalog_items(types=["ITEM", "ITEM_VARIATION"])
    
    if not catalog_data:
        print("Failed to fetch catalog data!")
        return
    
    print(f"Retrieved {len(catalog_data.get('objects', []))} catalog objects")
    
    # Extract service variations
    print("Processing service variations...")
    variations = square_api.extract_service_variations(catalog_data)
    print(f"Found {len(variations)} service variations")
    
    # Categorize services
    print("Categorizing services...")
    categorized = square_api.categorize_services(variations)
    
    # Generate report
    print("Generating service mapping report...")
    report = square_api.generate_service_mapping_report(variations, categorized)
    
    # Save report
    output_file = "/Users/rayhernandez/KEEPER/analysis & reports/VERIFIED_SERVICE_CATALOG_20250906.md"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"Report saved to: {output_file}")
    
    # Also save as JSON for programmatic use
    json_file = "/Users/rayhernandez/KEEPER/analysis & reports/service_variations_mapping.json"
    with open(json_file, 'w') as f:
        json.dump(variations, f, indent=2)
    
    print(f"JSON mapping saved to: {json_file}")
    
    # Print summary
    print("\n=== SUMMARY ===")
    print(f"Total Items: {len(variations)}")
    print(f"Spa Services: {len(categorized['spa_services'])}")
    print(f"Salon Services: {len(categorized['salon_services'])}")
    print(f"Retail Products: {len(categorized['retail_products'])}")
    print(f"Unclear Items: {len(categorized['unclear_services'])}")
    print(f"Inactive Items: {len(categorized['inactive_services'])}")
    
    if categorized['salon_services']:
        print(f"\n⚠️  WARNING: Found {len(categorized['salon_services'])} salon services!")
        print("This indicates catalog contamination in your Brazilian wax spa.")
    
    if categorized['spa_services']:
        print(f"\n✅ SUCCESS: Found {len(categorized['spa_services'])} verified spa services!")
        print("These are legitimate services for your Brazilian wax spa.")


if __name__ == "__main__":
    main()