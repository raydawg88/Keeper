#!/usr/bin/env python3
"""
Service Name Resolution Function with Caching
Resolves Square service_variation_id to human-readable service names
"""

import json
import os
from typing import Dict, Optional, List, Tuple
from datetime import datetime
import psycopg2
from psycopg2.extras import DictCursor

class ServiceNameResolver:
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
        
        Args:
            variation_id: Square service variation ID
            
        Returns:
            Dict with service details or None if not found
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
            print(f"Service variation ID not found in cache: {variation_id}")
            return None
    
    def resolve_multiple(self, variation_ids: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Resolve multiple service variation IDs at once
        
        Args:
            variation_ids: List of Square service variation IDs
            
        Returns:
            Dict mapping variation_id to service details
        """
        results = {}
        for var_id in variation_ids:
            results[var_id] = self.resolve_service_name(var_id)
        return results
    
    def get_database_connection(self):
        """
        Get database connection using Supabase credentials
        """
        try:
            conn = psycopg2.connect(
                host="jlawmbqoykwgrjutrfsp.supabase.co",
                database="postgres",
                user="postgres",
                password="sb_secret_6ONiuNr9OL53Wwf5G28wqA_WJrYbp50",
                port="6543"
            )
            return conn
        except Exception as e:
            print(f"Database connection failed: {e}")
            return None
    
    def get_top_services_from_db(self, limit: int = 10) -> List[Tuple]:
        """
        Query database to get top service variations by appointment count
        """
        conn = self.get_database_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                query = """
                SELECT 
                    service_variation_id,
                    COUNT(*) as appointment_count,
                    MIN(start_at) as first_appointment,
                    MAX(start_at) as last_appointment,
                    COUNT(DISTINCT customer_id) as unique_customers
                FROM appointments 
                WHERE service_variation_id IS NOT NULL 
                    AND service_variation_id != ''
                GROUP BY service_variation_id 
                ORDER BY appointment_count DESC 
                LIMIT %s
                """
                cur.execute(query, (limit,))
                results = cur.fetchall()
                return [(row['service_variation_id'], row['appointment_count'], 
                        row['first_appointment'], row['last_appointment'], 
                        row['unique_customers']) for row in results]
        except Exception as e:
            print(f"Database query failed: {e}")
            return []
        finally:
            conn.close()
    
    def audit_top_services(self, limit: int = 10) -> Dict:
        """
        Audit top services from database with resolved names
        """
        print(f"Querying database for top {limit} services...")
        top_services = self.get_top_services_from_db(limit)
        
        if not top_services:
            return {"error": "No services found in database"}
        
        audit_results = {
            "timestamp": datetime.now().isoformat(),
            "total_services_found": len(top_services),
            "services": []
        }
        
        for var_id, count, first_appt, last_appt, unique_customers in top_services:
            service_details = self.resolve_service_name(var_id)
            
            service_audit = {
                "variation_id": var_id,
                "appointment_count": count,
                "unique_customers": unique_customers,
                "first_appointment": first_appt.isoformat() if first_appt else None,
                "last_appointment": last_appt.isoformat() if last_appt else None,
                "resolved_name": service_details['full_name'] if service_details else "UNRESOLVED",
                "price": service_details['price_formatted'] if service_details else "Unknown",
                "is_active": service_details['is_active'] if service_details else False,
                "is_spa_appropriate": self.is_spa_appropriate(service_details) if service_details else False
            }
            
            audit_results["services"].append(service_audit)
        
        return audit_results
    
    def is_spa_appropriate(self, service_details: Dict) -> bool:
        """
        Determine if service is appropriate for Brazilian wax spa
        """
        if not service_details:
            return False
        
        full_name = service_details['full_name'].lower()
        
        spa_keywords = [
            "wax", "brazilian", "bikini", "eyebrow", "lip", "chin", "underarm", 
            "leg", "facial", "massage", "skin", "peel", "threading", "sugaring",
            "face", "cheek", "upper lip", "lower leg", "full leg", "arms", "back",
            "chest", "buttocks", "landing strip", "full body", "membership"
        ]
        
        return any(keyword in full_name for keyword in spa_keywords)
    
    def generate_audit_report(self, limit: int = 10) -> str:
        """
        Generate comprehensive audit report
        """
        audit_data = self.audit_top_services(limit)
        
        if "error" in audit_data:
            return f"Error generating audit report: {audit_data['error']}"
        
        report = []
        report.append("# TOP SERVICES AUDIT REPORT")
        report.append(f"Generated: {audit_data['timestamp']}")
        report.append(f"Database Query Limit: {limit}")
        report.append(f"Services Found: {audit_data['total_services_found']}")
        report.append("")
        
        # Summary stats
        spa_appropriate = sum(1 for s in audit_data['services'] if s['is_spa_appropriate'])
        total_appointments = sum(s['appointment_count'] for s in audit_data['services'])
        
        report.append("## SUMMARY")
        report.append(f"Total Appointments: {total_appointments:,}")
        report.append(f"Spa-Appropriate Services: {spa_appropriate}/{len(audit_data['services'])}")
        report.append(f"Data Integrity: {'✅ GOOD' if spa_appropriate == len(audit_data['services']) else '⚠️ ISSUES FOUND'}")
        report.append("")
        
        # Detailed services
        report.append("## TOP SERVICES BREAKDOWN")
        report.append("| Rank | Service ID | Service Name | Appointments | Customers | Price | Spa Appropriate |")
        report.append("|------|------------|--------------|--------------|-----------|-------|-----------------|")
        
        for i, service in enumerate(audit_data['services'], 1):
            status = "✅" if service['is_spa_appropriate'] else "❌"
            report.append(f"| {i} | {service['variation_id'][:8]}... | {service['resolved_name'][:40]}{'...' if len(service['resolved_name']) > 40 else ''} | {service['appointment_count']:,} | {service['unique_customers']} | {service['price']} | {status} |")
        
        report.append("")
        report.append("## DETAILED SERVICE INFORMATION")
        
        for i, service in enumerate(audit_data['services'], 1):
            report.append(f"### {i}. {service['resolved_name']}")
            report.append(f"- **Variation ID**: {service['variation_id']}")
            report.append(f"- **Total Appointments**: {service['appointment_count']:,}")
            report.append(f"- **Unique Customers**: {service['unique_customers']}")
            report.append(f"- **Price**: {service['price']}")
            report.append(f"- **Active**: {'Yes' if service['is_active'] else 'No'}")
            report.append(f"- **Spa Appropriate**: {'✅ Yes' if service['is_spa_appropriate'] else '❌ No'}")
            
            if service['first_appointment']:
                report.append(f"- **First Appointment**: {service['first_appointment']}")
            if service['last_appointment']:
                report.append(f"- **Last Appointment**: {service['last_appointment']}")
            
            report.append("")
        
        return "\\n".join(report)


def main():
    """
    Main function to demonstrate service resolution
    """
    resolver = ServiceNameResolver()
    
    # Test the critical service ID mentioned in the problem
    critical_service = "FDBSYENBQ3BUL3SGSRIL6OYZ"
    print(f"\\nTesting critical service ID: {critical_service}")
    result = resolver.resolve_service_name(critical_service)
    if result:
        print(f"✅ RESOLVED: {result['full_name']} - {result['price_formatted']}")
    else:
        print("❌ FAILED TO RESOLVE")
    
    # Generate full audit report
    print("\\nGenerating audit report...")
    audit_report = resolver.generate_audit_report(10)
    
    # Save audit report
    output_file = "/Users/rayhernandez/KEEPER/analysis & reports/TOP_SERVICES_AUDIT_20250906.md"
    with open(output_file, 'w') as f:
        f.write(audit_report)
    
    print(f"Audit report saved to: {output_file}")
    
    return audit_report


if __name__ == "__main__":
    main()