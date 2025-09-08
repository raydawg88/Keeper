#!/usr/bin/env python3
"""
EMERGENCY DATABASE AUDIT SCRIPT
Critical investigation to identify source of wrong service data in Bashful Beauty reports
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json

# Load environment variables
load_dotenv()

def audit_database():
    """Emergency audit of Bashful Beauty database to identify data contamination"""
    
    # Get credentials from environment
    url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not url or not service_key:
        print("❌ CRITICAL: Missing Supabase credentials")
        return False
    
    try:
        supabase: Client = create_client(url, service_key)
        account_id = "b491de6e-7d5b-4e0e-b1cd-625c6c4f7d81"
        
        print("🚨 EMERGENCY DATABASE AUDIT - BASHFUL BEAUTY")
        print("=" * 60)
        print(f"Account ID: {account_id}")
        print(f"Database: {url}")
        print("=" * 60)
        
        # 1. VERIFY ACCOUNT EXISTS AND BUSINESS NAME
        print("\n1. VERIFYING ACCOUNT DETAILS:")
        print("-" * 40)
        
        try:
            account_result = supabase.table('accounts').select('*').eq('id', account_id).execute()
            if account_result.data:
                account = account_result.data[0]
                print(f"✅ Account found: {account['business_name']}")
                print(f"   Category: {account.get('business_category', 'N/A')}")
                print(f"   Created: {account.get('created_at', 'N/A')}")
            else:
                print(f"❌ CRITICAL: Account {account_id} not found!")
                return False
        except Exception as e:
            print(f"❌ Account query failed: {str(e)}")
        
        # 2. CHECK SQUARE MERCHANT DATA
        print("\n2. CHECKING SQUARE MERCHANT DATA:")
        print("-" * 40)
        
        try:
            merchant_result = supabase.table('square_merchants').select('*').eq('account_id', account_id).execute()
            if merchant_result.data:
                merchant = merchant_result.data[0]
                print(f"✅ Square Merchant: {merchant['business_name']}")
                print(f"   Merchant ID: {merchant['id']}")
                print(f"   Status: {merchant['status']}")
                print(f"   Country: {merchant['country']}")
            else:
                print("⚠️  No Square merchant data found")
        except Exception as e:
            print(f"❌ Square merchant query failed: {str(e)}")
        
        # 3. CHECK FOR APPOINTMENTS TABLE AND DATA
        print("\n3. CHECKING APPOINTMENTS DATA:")
        print("-" * 40)
        
        try:
            # Check if appointments table exists and has data
            appointments_result = supabase.table('appointments').select('*').eq('account_id', account_id).limit(10).execute()
            if appointments_result.data:
                print(f"✅ Found {len(appointments_result.data)} appointment records")
                for i, apt in enumerate(appointments_result.data[:5]):
                    print(f"   Sample {i+1}: {apt.get('service_variation_id', 'N/A')} - {apt.get('status', 'N/A')}")
            else:
                print("⚠️  No appointments found in appointments table")
        except Exception as e:
            print(f"❌ Appointments query failed: {str(e)}")
        
        # 4. CHECK SQUARE ORDERS FOR SERVICE DATA
        print("\n4. CHECKING SQUARE ORDERS FOR SERVICE DATA:")
        print("-" * 40)
        
        try:
            orders_result = supabase.table('square_orders').select('*').eq('account_id', account_id).limit(20).execute()
            if orders_result.data:
                print(f"✅ Found {len(orders_result.data)} order records")
                
                # Extract line items to see actual services
                all_services = []
                for order in orders_result.data:
                    if order.get('line_items'):
                        try:
                            if isinstance(order['line_items'], str):
                                line_items = json.loads(order['line_items'])
                            else:
                                line_items = order['line_items']
                            
                            for item in line_items:
                                service_name = item.get('name', 'Unknown')
                                if service_name not in all_services:
                                    all_services.append(service_name)
                        except:
                            pass
                
                print(f"   ACTUAL SERVICES FOUND IN DATABASE:")
                for i, service in enumerate(all_services[:20]):
                    print(f"     {i+1}. {service}")
                
                if len(all_services) > 20:
                    print(f"     ... and {len(all_services) - 20} more services")
                    
            else:
                print("⚠️  No orders found in square_orders table")
        except Exception as e:
            print(f"❌ Orders query failed: {str(e)}")
        
        # 5. CHECK FOR CATALOG ITEMS (SERVICES)
        print("\n5. CHECKING FOR CATALOG/SERVICE DATA:")
        print("-" * 40)
        
        # Check if there are any catalog or service tables
        try:
            # Try to find any table that might contain service definitions
            tables_to_check = ['square_catalog_items', 'services', 'catalog_items', 'square_items']
            for table_name in tables_to_check:
                try:
                    result = supabase.table(table_name).select('*').eq('account_id', account_id).limit(5).execute()
                    if result.data:
                        print(f"✅ Found data in {table_name}: {len(result.data)} records")
                        for item in result.data[:3]:
                            print(f"   Sample: {item}")
                except:
                    continue
        except Exception as e:
            print(f"❌ Catalog check failed: {str(e)}")
        
        # 6. CHECK PAYMENT DATA FOR SERVICE PATTERNS
        print("\n6. ANALYZING PAYMENT PATTERNS:")
        print("-" * 40)
        
        try:
            payments_result = supabase.table('square_payments').select('*').eq('account_id', account_id).limit(100).execute()
            if payments_result.data:
                print(f"✅ Found {len(payments_result.data)} payment records")
                
                # Analyze amounts to see if they match Brazilian wax pricing
                amounts = [float(p['amount_money']) for p in payments_result.data if p.get('amount_money')]
                if amounts:
                    avg_amount = sum(amounts) / len(amounts)
                    min_amount = min(amounts)
                    max_amount = max(amounts)
                    
                    print(f"   Average transaction: ${avg_amount:.2f}")
                    print(f"   Range: ${min_amount:.2f} - ${max_amount:.2f}")
                    
                    # Brazilian wax services typically range $30-150
                    if 30 <= avg_amount <= 150:
                        print("   ✅ Transaction amounts consistent with Brazilian wax spa")
                    else:
                        print("   ⚠️  Transaction amounts may not match expected spa services")
                        
            else:
                print("⚠️  No payments found")
        except Exception as e:
            print(f"❌ Payments analysis failed: {str(e)}")
        
        # 7. FINAL DIAGNOSIS
        print("\n" + "=" * 60)
        print("🔍 DIAGNOSIS:")
        print("=" * 60)
        
        print("\n⚠️  CRITICAL FINDINGS:")
        print("1. Need to verify if wrong service names (Manicure, Styling, Coloring, Haircut)")
        print("   actually exist in the database or were AI-generated")
        print("2. Bashful Beauty should only have Brazilian wax-related services")
        print("3. Previous reports may have used synthetic/fake data instead of real queries")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    audit_database()