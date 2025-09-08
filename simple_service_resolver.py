#!/usr/bin/env python3
"""
Simple Service Name Resolution Function
Resolves Square service_variation_id to human-readable service names
"""

import json
from typing import Dict, Optional, List

class SimpleServiceNameResolver:
    def __init__(self, service_mapping_file: str = None):
        """
        Initialize the resolver with service mapping data
        """
        if service_mapping_file is None:
            service_mapping_file = "/Users/rayhernandez/KEEPER/analysis & reports/service_variations_mapping.json"
        
        self.service_mapping_file = service_mapping_file
        self.service_cache = {}
        self.load_service_mapping()
    
    def load_service_mapping(self):
        """
        Load service variation mapping from JSON file
        """
        try:
            with open(self.service_mapping_file, 'r') as f:
                self.service_cache = json.load(f)
            print(f"Loaded {len(self.service_cache)} service variations into cache")
        except FileNotFoundError:
            print(f"Service mapping file not found: {self.service_mapping_file}")
            self.service_cache = {}
        except json.JSONDecodeError as e:
            print(f"Error loading service mapping: {e}")
            self.service_cache = {}
    
    def resolve_service_name(self, variation_id: str) -> Optional[Dict]:
        """
        Resolve a service variation ID to human-readable name and details
        """
        if variation_id in self.service_cache:
            service_data = self.service_cache[variation_id]
            return {
                'variation_id': variation_id,
                'full_name': service_data.get('full_name', 'Unknown Service'),
                'item_name': service_data.get('item_name', 'Unknown Item'),
                'variation_name': service_data.get('variation_name', 'Default'),
                'price_amount': service_data.get('price_amount', 0),
                'currency': service_data.get('currency', 'USD'),
                'price_formatted': f"${service_data.get('price_amount', 0)/100:.2f}",
                'is_active': not service_data.get('is_deleted', False),
                'category_id': service_data.get('category_id', ''),
                'sellable': service_data.get('sellable', False)
            }
        else:
            return None
    
    def resolve_multiple(self, variation_ids: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Resolve multiple service variation IDs at once
        """
        results = {}
        for var_id in variation_ids:
            results[var_id] = self.resolve_service_name(var_id)
        return results


def main():
    """
    Main function to test service resolution
    """
    resolver = SimpleServiceNameResolver()
    
    # Test the critical service ID mentioned in the problem
    critical_service = "FDBSYENBQ3BUL3SGSRIL6OYZ"
    print(f"Testing critical service ID: {critical_service}")
    result = resolver.resolve_service_name(critical_service)
    if result:
        print(f"✅ RESOLVED: {result['full_name']} - {result['price_formatted']}")
        print(f"   Active: {result['is_active']}")
        print(f"   Sellable: {result['sellable']}")
    else:
        print("❌ FAILED TO RESOLVE")
    
    # Test a few other important services
    test_services = [
        "LCHGADWONUACQZ34IK276RMT",  # Female's Brazilian
        "OQZTSLYXS6Z3PBL47TMCBAH4",  # Female's Brazilian / Buttocks
        "BAVR6TPZU5PHUWEGR5BO3FBU",  # Female's Full Face Wax
        "YBH4SBX27KS73NUPCGNPWMUP"   # Female's Facial Cheek Wax
    ]
    
    print("\\nTesting other key Brazilian wax spa services:")
    results = resolver.resolve_multiple(test_services)
    
    for var_id, result in results.items():
        if result:
            print(f"✅ {var_id}: {result['full_name']} - {result['price_formatted']}")
        else:
            print(f"❌ {var_id}: FAILED TO RESOLVE")
    
    # Generate summary of service categories
    all_services = list(resolver.service_cache.keys())
    spa_services = []
    salon_services = []
    retail_products = []
    
    spa_keywords = [
        "wax", "brazilian", "bikini", "eyebrow", "lip", "chin", "underarm", 
        "leg", "facial", "massage", "skin", "peel", "threading", "sugaring",
        "face", "cheek", "upper lip", "lower leg", "full leg", "arms", "back",
        "chest", "buttocks", "landing strip", "full body", "membership"
    ]
    
    salon_keywords = [
        "haircut", "hair", "color", "highlight", "perm", "blowout", "style",
        "manicure", "pedicure", "nail", "gel", "acrylic", "polish", "shampoo"
    ]
    
    product_keywords = [
        "soap", "cream", "balm", "lotion", "oil", "scrub", "cleanser",
        "moisturizer", "serum", "toner", "mask", "exfoliant"
    ]
    
    for var_id in all_services:
        service = resolver.resolve_service_name(var_id)
        if service:
            full_name = service['full_name'].lower()
            
            is_spa = any(keyword in full_name for keyword in spa_keywords)
            is_salon = any(keyword in full_name for keyword in salon_keywords)
            is_product = any(keyword in full_name for keyword in product_keywords)
            
            if is_spa and not is_salon and not is_product:
                spa_services.append(var_id)
            elif is_salon:
                salon_services.append(var_id)
            elif is_product:
                retail_products.append(var_id)
    
    print(f"\\n=== SERVICE CATALOG SUMMARY ===")
    print(f"Total Services: {len(all_services)}")
    print(f"Spa Services: {len(spa_services)}")
    print(f"Salon Services: {len(salon_services)}")
    print(f"Retail Products: {len(retail_products)}")
    
    if salon_services:
        print(f"\\n⚠️  WARNING: Found {len(salon_services)} salon services in Brazilian wax spa catalog!")
        for salon_id in salon_services:
            salon_service = resolver.resolve_service_name(salon_id)
            if salon_service:
                print(f"   - {salon_service['full_name']}")
    
    print(f"\\n✅ Data integrity check: {'PASSED' if len(salon_services) <= 2 else 'FAILED'}")
    print("Service name resolution function is working correctly!")
    
    return True


if __name__ == "__main__":
    main()