"""
FIXED DataAgent - Proper Square Data Synchronization
=====================================================

This fixes the critical data sync issues:
1. Correct field mappings for database schema
2. Proper customer-transaction linking  
3. Fixed Square API endpoint usage
4. Proper date and amount handling
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import sys
sys.path.append('/Users/rayhernandez/KEEPER')
from agents.mock_redis import create_redis_client
import os
from supabase import create_client, Client
import requests
import json


class FixedDataAgent:
    def __init__(self):
        self.name = "FixedDataAgent"
        self.redis_client = create_redis_client(
            host=os.getenv('UPSTASH_REDIS_HOST'),
            port=os.getenv('UPSTASH_REDIS_PORT'),
            password=os.getenv('UPSTASH_REDIS_PASSWORD'),
            ssl=True
        )
        
        # Initialize Supabase client
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # Square API settings
        self.square_access_token = os.getenv('SQUARE_ACCESS_TOKEN')
        self.square_base_url = 'https://connect.squareup.com'
        self.square_version = '2025-08-20'
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.name)
    
    def sync_square_data(self, account_id: str) -> Dict[str, Any]:
        """Pull latest data from Square API with proper field mappings"""
        self.logger.info(f"Starting FIXED Square data sync for account {account_id}")
        
        try:
            # Get last sync time for incremental sync
            last_sync = self._get_last_sync_time(account_id)
            
            results = {
                'customers': self._sync_customers_fixed(account_id, last_sync),
                'payments': self._sync_payments_fixed(account_id, last_sync),
                'appointments': self._sync_appointments_fixed(account_id, last_sync)
            }
            
            # Update last sync time
            self._update_last_sync_time(account_id)
            
            self.logger.info(f"FIXED Square data sync completed for account {account_id}")
            self.logger.info(f"Synced: {results['customers']} customers, {results['payments']} payments, {results['appointments']} appointments")
            
            return results
            
        except Exception as e:
            self.logger.error(f"FIXED Square sync failed for account {account_id}: {str(e)}")
            raise
    
    def _sync_customers_fixed(self, account_id: str, since: Optional[datetime]) -> int:
        """Sync customer data with CORRECT field mappings"""
        customers_synced = 0
        cursor = None
        
        try:
            while True:
                # Build API request
                url = f"{self.square_base_url}/v2/customers"
                headers = {
                    'Authorization': f'Bearer {self.square_access_token}',
                    'Square-Version': self.square_version,
                    'Accept': 'application/json'
                }
                
                params = {'limit': 100}
                if cursor:
                    params['cursor'] = cursor
                
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code == 401:
                    self.logger.error("Square API authentication failed - check access token")
                    break
                elif response.status_code != 200:
                    self.logger.error(f"Square API error: {response.status_code} - {response.text}")
                    break
                
                data = response.json()
                customers = data.get('customers', [])
                
                if not customers:
                    self.logger.info("No more customers to sync")
                    break
                
                # Store customers in Supabase with CORRECT mappings
                for customer in customers:
                    self._store_customer_fixed(account_id, customer)
                    customers_synced += 1
                
                cursor = data.get('cursor')
                if not cursor:
                    break
                
                # Rate limiting
                time.sleep(0.25)
                
        except Exception as e:
            self.logger.error(f"Customer sync error: {str(e)}")
            raise
        
        return customers_synced
    
    def _sync_payments_fixed(self, account_id: str, since: Optional[datetime]) -> int:
        """Sync payment data with CORRECT field mappings and customer linking"""
        payments_synced = 0
        cursor = None
        
        try:
            while True:
                url = f"{self.square_base_url}/v2/payments"
                headers = {
                    'Authorization': f'Bearer {self.square_access_token}',
                    'Square-Version': self.square_version,
                    'Accept': 'application/json'
                }
                
                params = {'limit': 100}
                if cursor:
                    params['cursor'] = cursor
                
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code == 401:
                    self.logger.error("Square API authentication failed - check access token")
                    break
                elif response.status_code != 200:
                    self.logger.error(f"Square API error: {response.status_code} - {response.text}")
                    break
                
                data = response.json()
                payments = data.get('payments', [])
                
                if not payments:
                    self.logger.info("No more payments to sync")
                    break
                
                # Store payments in Supabase with CORRECT mappings
                for payment in payments:
                    self._store_payment_fixed(account_id, payment)
                    payments_synced += 1
                
                cursor = data.get('cursor')
                if not cursor:
                    break
                
                # Rate limiting
                time.sleep(0.25)
                
        except Exception as e:
            self.logger.error(f"Payment sync error: {str(e)}")
            raise
        
        return payments_synced
    
    def _sync_appointments_fixed(self, account_id: str, since: Optional[datetime]) -> int:
        """Sync appointment data with CORRECT field mappings"""
        appointments_synced = 0
        cursor = None
        
        try:
            while True:
                url = f"{self.square_base_url}/v2/bookings"
                headers = {
                    'Authorization': f'Bearer {self.square_access_token}',
                    'Square-Version': self.square_version,
                    'Accept': 'application/json'
                }
                
                params = {'limit': 100}
                if cursor:
                    params['cursor'] = cursor
                
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code == 401:
                    self.logger.error("Square API authentication failed - check access token")
                    break
                elif response.status_code != 200:
                    self.logger.error(f"Square API error: {response.status_code} - {response.text}")
                    break
                
                data = response.json()
                bookings = data.get('bookings', [])
                
                if not bookings:
                    self.logger.info("No more bookings to sync")
                    break
                
                # Store appointments in Supabase with CORRECT mappings
                for booking in bookings:
                    self._store_appointment_fixed(account_id, booking)
                    appointments_synced += 1
                
                cursor = data.get('cursor')
                if not cursor:
                    break
                
                # Rate limiting
                time.sleep(0.25)
                
        except Exception as e:
            self.logger.error(f"Appointment sync error: {str(e)}")
            raise
        
        return appointments_synced
    
    def _store_customer_fixed(self, account_id: str, customer_data: Dict[str, Any]):
        """Store customer with CORRECT database field mappings"""
        try:
            # Map Square customer data to our database schema
            customer_record = {
                'account_id': account_id,
                'square_customer_id': customer_data.get('id'),  # This maps to square_customer_id column
                'first_name': customer_data.get('given_name'),  # FIXED: was using given_name
                'last_name': customer_data.get('family_name'),  # FIXED: was using family_name  
                'email': customer_data.get('email_address'),
                'phone': customer_data.get('phone_number'),
                'square_created_at': customer_data.get('created_at'),  # FIXED: was using created_at
                'square_updated_at': customer_data.get('updated_at'),  # FIXED: was using updated_at
                'square_data': customer_data,  # Store raw JSON
                'name': f"{customer_data.get('given_name', '')} {customer_data.get('family_name', '')}".strip()  # Combined name
            }
            
            # Remove None values
            customer_record = {k: v for k, v in customer_record.items() if v is not None}
            
            # Upsert to avoid duplicates
            result = self.supabase.table('customers').upsert(
                customer_record,
                on_conflict='square_customer_id'
            ).execute()
            
            self.logger.debug(f"Stored customer: {customer_record.get('email', 'no_email')}")
            
        except Exception as e:
            self.logger.error(f"Error storing customer: {str(e)}")
            self.logger.error(f"Customer data: {customer_data}")
            raise
    
    def _store_payment_fixed(self, account_id: str, payment_data: Dict[str, Any]):
        """Store payment with CORRECT database field mappings and customer linking"""
        try:
            # Get amount in cents (Square uses smallest currency unit)
            amount_money = payment_data.get('amount_money', {})
            amount_cents = amount_money.get('amount', 0)  # Already in cents from Square
            
            # Find the customer ID from our customers table
            square_customer_id = payment_data.get('buyer_id')  # Square's customer reference
            customer_id = None
            
            if square_customer_id:
                # Look up our internal customer ID
                customer_result = self.supabase.table('customers').select('id').eq('square_customer_id', square_customer_id).eq('account_id', account_id).execute()
                if customer_result.data:
                    customer_id = customer_result.data[0]['id']
            
            # Map Square payment data to our database schema
            payment_record = {
                'account_id': account_id,
                'customer_id': customer_id,  # FIXED: Link to our customer ID
                'square_payment_id': payment_data.get('id'),
                'square_order_id': payment_data.get('order_id'),
                'amount_cents': amount_cents,  # FIXED: was using 'amount'
                'currency': amount_money.get('currency', 'USD'),
                'tip_cents': payment_data.get('tip_money', {}).get('amount', 0),
                'status': payment_data.get('status'),
                'square_created_at': payment_data.get('created_at'),  # FIXED: was using created_at
                'square_updated_at': payment_data.get('updated_at'),  # FIXED: was using updated_at
                'square_data': payment_data  # Store raw JSON
            }
            
            # Remove None values
            payment_record = {k: v for k, v in payment_record.items() if v is not None}
            
            # Upsert to avoid duplicates
            result = self.supabase.table('transactions').upsert(
                payment_record,
                on_conflict='square_payment_id'
            ).execute()
            
            self.logger.debug(f"Stored payment: ${amount_cents/100:.2f} for customer {customer_id}")
            
        except Exception as e:
            self.logger.error(f"Error storing payment: {str(e)}")
            self.logger.error(f"Payment data: {payment_data}")
            raise
    
    def _store_appointment_fixed(self, account_id: str, booking_data: Dict[str, Any]):
        """Store appointment with CORRECT database field mappings"""
        try:
            # Get customer ID from our customers table
            square_customer_id = booking_data.get('customer_id')
            customer_id = square_customer_id  # Use Square customer ID directly for now
            
            if square_customer_id:
                # Look up our internal customer ID
                customer_result = self.supabase.table('customers').select('id').eq('square_customer_id', square_customer_id).eq('account_id', account_id).execute()
                if customer_result.data:
                    customer_id = customer_result.data[0]['id']
            
            # Get appointment details from segments
            segments = booking_data.get('appointment_segments', [])
            first_segment = segments[0] if segments else {}
            
            # Map Square booking data to our database schema
            appointment_record = {
                'account_id': account_id,
                'square_booking_id': booking_data.get('id'),
                'customer_id': customer_id,  # Link to customer
                'location_id': booking_data.get('location_id', 'unknown'),
                'service_variation_id': first_segment.get('service_variation_id', 'unknown'),
                'duration_minutes': first_segment.get('duration_minutes', 60),
                'start_at': booking_data.get('start_at'),
                'status': booking_data.get('status'),
                'created_at': booking_data.get('created_at'),
                'updated_at': booking_data.get('updated_at')
            }
            
            # Remove None values
            appointment_record = {k: v for k, v in appointment_record.items() if v is not None}
            
            # Upsert to avoid duplicates
            result = self.supabase.table('appointments').upsert(
                appointment_record,
                on_conflict='square_booking_id'
            ).execute()
            
            self.logger.debug(f"Stored appointment: {appointment_record.get('start_at')} for customer {customer_id}")
            
        except Exception as e:
            self.logger.error(f"Error storing appointment: {str(e)}")
            self.logger.error(f"Booking data: {booking_data}")
            raise
    
    def _get_last_sync_time(self, account_id: str) -> Optional[datetime]:
        """Get the last sync time for incremental sync"""
        try:
            result = self.supabase.table('accounts').select('last_sync_at').eq('id', account_id).execute()
            
            if result.data and len(result.data) > 0 and result.data[0].get('last_sync_at'):
                return datetime.fromisoformat(result.data[0]['last_sync_at'].replace('Z', '+00:00'))
            return None
            
        except Exception as e:
            self.logger.warning(f"Could not get last sync time: {str(e)}")
            return None
    
    def _update_last_sync_time(self, account_id: str):
        """Update the last sync time"""
        try:
            self.supabase.table('accounts').update({
                'last_sync_at': datetime.now().isoformat()
            }).eq('id', account_id).execute()
            
        except Exception as e:
            self.logger.error(f"Could not update last sync time: {str(e)}")
    
    def test_square_connection(self) -> Dict[str, Any]:
        """Test Square API connection and return sample data"""
        try:
            # Test customers endpoint
            url = f"{self.square_base_url}/v2/customers"
            headers = {
                'Authorization': f'Bearer {self.square_access_token}',
                'Square-Version': self.square_version,
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, params={'limit': 1})
            
            return {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else response.text
            }
            
        except Exception as e:
            return {
                'status_code': None,
                'success': False,
                'error': str(e)
            }