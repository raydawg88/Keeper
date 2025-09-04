#!/usr/bin/env python3
"""
Square Data Sync Pipeline for Keeper
Pulls customers, payments, and transactions from Square API
"""
import os
import json
import uuid
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
import requests
import time

# Load environment variables
load_dotenv()

class SquareDataSync:
    """Handles data synchronization between Square API and Keeper database"""
    
    def __init__(self, account_id: str):
        """
        Initialize data sync for a specific Keeper account
        
        Args:
            account_id: Keeper account ID to sync data for
        """
        self.account_id = account_id
        
        # Supabase setup
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # Get account info and Square access token
        self.account_info = self._get_account_info()
        if not self.account_info:
            raise ValueError(f"Account {account_id} not found")
            
        self.access_token = self.account_info['square_access_token']
        self.square_merchant_id = self.account_info['square_merchant_id']
        
        # Square API setup
        self.api_base_url = 'https://connect.squareupsandbox.com'
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Square-Version': '2025-08-20',  # Latest version from documentation
            'Content-Type': 'application/json'
        }
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests (~10 QPS)
    
    def _get_account_info(self) -> Optional[Dict]:
        """Get account information from database"""
        try:
            result = self.supabase.table('accounts')\
                .select('*')\
                .eq('id', self.account_id)\
                .execute()
            
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            print(f"❌ Error getting account info: {e}")
            return None
    
    def _rate_limit(self):
        """Implement rate limiting to respect Square API limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_square_request(self, method: str, endpoint: str, params: Dict = None, json_data: Dict = None) -> Optional[Dict]:
        """
        Make a rate-limited request to Square API
        
        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint (e.g., '/v2/customers')
            params: URL parameters for GET requests
            json_data: JSON data for POST requests
            
        Returns:
            Response data or None if failed
        """
        self._rate_limit()
        
        url = f"{self.api_base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=json_data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                print("⚠️  Rate limited by Square API, implementing backoff...")
                time.sleep(2)  # Wait 2 seconds and try again
                return self._make_square_request(method, endpoint, params, json_data)
            else:
                print(f"❌ Square API error ({response.status_code}): {e}")
                return None
        except Exception as e:
            print(f"❌ Request error: {e}")
            return None
    
    def sync_customers(self) -> int:
        """
        Sync all customers from Square to Keeper database
        
        Returns:
            Number of customers synced
        """
        print("👥 Syncing customers from Square...")
        
        customers_synced = 0
        cursor = None
        
        while True:
            # Use ListCustomers endpoint with pagination
            params = {'limit': 100}  # Max 100 customers per request
            if cursor:
                params['cursor'] = cursor
            
            response = self._make_square_request('GET', '/v2/customers', params=params)
            
            if not response:
                break
            
            customers = response.get('customers', [])
            
            if not customers:
                break
            
            # Process customers in batch
            customer_records = []
            for customer in customers:
                customer_record = {
                    'id': str(uuid.uuid4()),
                    'account_id': self.account_id,
                    'square_customer_id': customer['id'],
                    'first_name': customer.get('given_name'),
                    'last_name': customer.get('family_name'),
                    'email': customer.get('email_address'),
                    'phone': customer.get('phone_number'),
                    'square_created_at': customer.get('created_at'),
                    'square_updated_at': customer.get('updated_at'),
                    'square_data': json.dumps(customer),
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'updated_at': datetime.now(timezone.utc).isoformat()
                }
                customer_records.append(customer_record)
            
            # Insert customers into database (use upsert to handle duplicates)
            try:
                self.supabase.table('customers')\
                    .upsert(customer_records, on_conflict='square_customer_id')\
                    .execute()
                
                customers_synced += len(customer_records)
                print(f"   ✅ Synced {len(customer_records)} customers (total: {customers_synced})")
                
            except Exception as e:
                print(f"   ❌ Error inserting customers: {e}")
                break
            
            # Check for more pages
            cursor = response.get('cursor')
            if not cursor:
                break
        
        print(f"✅ Customer sync complete: {customers_synced} customers synced")
        return customers_synced
    
    def sync_payments(self, days_back: int = 30) -> int:
        """
        Sync payments/transactions from Square to Keeper database
        
        Args:
            days_back: How many days back to sync payments
            
        Returns:
            Number of payments synced
        """
        print(f"💳 Syncing payments from Square (last {days_back} days)...")
        
        payments_synced = 0
        cursor = None
        
        # Calculate begin_time for filtering (days_back ago)
        from datetime import timedelta
        begin_time = datetime.now(timezone.utc) - timedelta(days=days_back)
        begin_time = begin_time.replace(hour=0, minute=0, second=0, microsecond=0)
        begin_time_str = begin_time.isoformat().replace('+00:00', 'Z')
        
        while True:
            # Use ListPayments endpoint with date filtering
            params = {
                'limit': 100,
                'begin_time': begin_time_str
            }
            if cursor:
                params['cursor'] = cursor
            
            response = self._make_square_request('GET', '/v2/payments', params=params)
            
            if not response:
                break
            
            payments = response.get('payments', [])
            
            if not payments:
                break
            
            # Process payments in batch
            payment_records = []
            for payment in payments:
                # Extract key information
                amount_money = payment.get('amount_money', {})
                tip_money = payment.get('tip_money', {})
                
                payment_record = {
                    'id': str(uuid.uuid4()),
                    'account_id': self.account_id,
                    'square_payment_id': payment['id'],
                    'square_order_id': payment.get('order_id'),
                    'amount_cents': amount_money.get('amount', 0),
                    'currency': amount_money.get('currency', 'USD'),
                    'tip_cents': tip_money.get('amount', 0) if tip_money else 0,
                    'status': payment.get('status'),
                    'square_created_at': payment.get('created_at'),
                    'square_updated_at': payment.get('updated_at'),
                    'square_data': json.dumps(payment),
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'updated_at': datetime.now(timezone.utc).isoformat()
                }
                
                # Try to link to customer if available
                customer_id = payment.get('buyer_email_address')
                if customer_id:
                    # Look up customer in our database
                    try:
                        customer_result = self.supabase.table('customers')\
                            .select('id')\
                            .eq('account_id', self.account_id)\
                            .eq('email', customer_id)\
                            .limit(1)\
                            .execute()
                        
                        if customer_result.data:
                            payment_record['customer_id'] = customer_result.data[0]['id']
                    except Exception:
                        pass  # Continue without customer linkage
                
                payment_records.append(payment_record)
            
            # Insert payments into database (use upsert to handle duplicates)
            try:
                self.supabase.table('transactions')\
                    .upsert(payment_records, on_conflict='square_payment_id')\
                    .execute()
                
                payments_synced += len(payment_records)
                print(f"   ✅ Synced {len(payment_records)} payments (total: {payments_synced})")
                
            except Exception as e:
                print(f"   ❌ Error inserting payments: {e}")
                break
            
            # Check for more pages
            cursor = response.get('cursor')
            if not cursor:
                break
        
        print(f"✅ Payment sync complete: {payments_synced} payments synced")
        return payments_synced
    
    def sync_all_data(self) -> Dict[str, int]:
        """
        Sync all data types from Square
        
        Returns:
            Dictionary with sync counts for each data type
        """
        print(f"🔄 Starting full data sync for account: {self.account_info['business_name']}")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Sync customers first (needed for payment customer linking)
        customers_count = self.sync_customers()
        
        # Sync payments/transactions
        payments_count = self.sync_payments()
        
        # Update account last sync timestamp
        try:
            self.supabase.table('accounts')\
                .update({'last_sync_at': datetime.now(timezone.utc).isoformat()})\
                .eq('id', self.account_id)\
                .execute()
        except Exception as e:
            print(f"⚠️  Could not update last_sync_at: {e}")
        
        sync_duration = datetime.now() - start_time
        
        results = {
            'customers': customers_count,
            'payments': payments_count,
            'duration_seconds': sync_duration.total_seconds()
        }
        
        print("=" * 60)
        print(f"🎉 Data sync complete!")
        print(f"   📊 Customers: {customers_count}")
        print(f"   💳 Payments: {payments_count}")
        print(f"   ⏱️  Duration: {sync_duration.total_seconds():.1f} seconds")
        
        return results

def test_data_sync():
    """Test data sync with our test account"""
    test_account_id = "27d755f9-87fd-40e8-a541-3a0478816395"
    
    try:
        sync_manager = SquareDataSync(test_account_id)
        results = sync_manager.sync_all_data()
        
        print(f"\n🎯 Data Sync Test Results:")
        print(f"   Account: {sync_manager.account_info['business_name']}")
        print(f"   Results: {results}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data sync test failed: {e}")
        return False

if __name__ == "__main__":
    test_data_sync()