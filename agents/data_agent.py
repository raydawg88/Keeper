"""
DataAgent - Square Data Synchronization and Storage

Responsibility: Square data synchronization and storage
Success Metrics:
- 100% data accuracy
- <5 minute sync time
- Zero duplicate records

Triggers:
- Hourly cron
- Manual sync request
- After OAuth connection

From agents-dropset.md specification
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import redis
import os
from supabase import create_client, Client
import requests
import json


class DataAgent:
    def __init__(self):
        self.name = "DataAgent"
        self.redis_client = redis.Redis(
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
        """Pull latest data from Square API
        
        - Fetch new/updated customers
        - Fetch payments since last sync
        - Fetch appointments
        - Fetch modifiers
        - Store raw in raw_square_data
        - Publish: "square_sync_complete"
        """
        self.logger.info(f"Starting Square data sync for account {account_id}")
        
        try:
            # Publish agent status
            self._publish_agent_status('analyzing', account_id)
            
            # Get last sync time for incremental sync
            last_sync = self._get_last_sync_time(account_id)
            
            results = {
                'customers': self._sync_customers(account_id, last_sync),
                'payments': self._sync_payments(account_id, last_sync),
                'appointments': self._sync_appointments(account_id, last_sync),
                'modifiers': self._sync_modifiers(account_id, last_sync)
            }
            
            # Update last sync time
            self._update_last_sync_time(account_id)
            
            # Publish completion
            self._publish_completion(account_id, results)
            
            self.logger.info(f"Square data sync completed for account {account_id}")
            return results
            
        except Exception as e:
            self.logger.error(f"Square sync failed for account {account_id}: {str(e)}")
            raise
    
    def backfill_historical(self, account_id: str, months: int = 12) -> Dict[str, Any]:
        """Initial historical data import
        
        - Paginate through all endpoints
        - Handle rate limits
        - Store with timestamps
        """
        self.logger.info(f"Starting historical backfill for account {account_id} ({months} months)")
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            
            results = {
                'customers': self._backfill_customers(account_id, start_date, end_date),
                'payments': self._backfill_payments(account_id, start_date, end_date),
                'appointments': self._backfill_appointments(account_id, start_date, end_date),
                'modifiers': self._backfill_modifiers(account_id, start_date, end_date)
            }
            
            self.logger.info(f"Historical backfill completed for account {account_id}")
            return results
            
        except Exception as e:
            self.logger.error(f"Historical backfill failed for account {account_id}: {str(e)}")
            raise
    
    def _sync_customers(self, account_id: str, since: Optional[datetime]) -> int:
        """Sync customer data from Square"""
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
                if since:
                    params['updated_at'] = {'min': since.isoformat() + 'Z'}
                
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code != 200:
                    self.logger.error(f"Square API error: {response.status_code} - {response.text}")
                    break
                
                data = response.json()
                customers = data.get('customers', [])
                
                if not customers:
                    break
                
                # Store customers in Supabase
                for customer in customers:
                    self._store_customer(account_id, customer)
                    customers_synced += 1
                
                cursor = data.get('cursor')
                if not cursor:
                    break
                
                # Rate limiting
                await asyncio.sleep(0.25)
                
        except Exception as e:
            self.logger.error(f"Customer sync error: {str(e)}")
            raise
        
        return customers_synced
    
    def _sync_payments(self, account_id: str, since: Optional[datetime]) -> int:
        """Sync payment data from Square"""
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
                if since:
                    params['updated_at'] = {'min': since.isoformat() + 'Z'}
                
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code != 200:
                    self.logger.error(f"Square API error: {response.status_code} - {response.text}")
                    break
                
                data = response.json()
                payments = data.get('payments', [])
                
                if not payments:
                    break
                
                # Store payments in Supabase
                for payment in payments:
                    self._store_payment(account_id, payment)
                    payments_synced += 1
                
                cursor = data.get('cursor')
                if not cursor:
                    break
                
                # Rate limiting
                await asyncio.sleep(0.25)
                
        except Exception as e:
            self.logger.error(f"Payment sync error: {str(e)}")
            raise
        
        return payments_synced
    
    def _sync_appointments(self, account_id: str, since: Optional[datetime]) -> int:
        """Sync appointment data from Square"""
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
                if since:
                    params['updated_at_min'] = since.isoformat() + 'Z'
                
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code != 200:
                    self.logger.error(f"Square API error: {response.status_code} - {response.text}")
                    break
                
                data = response.json()
                bookings = data.get('bookings', [])
                
                if not bookings:
                    break
                
                # Store appointments in Supabase
                for booking in bookings:
                    self._store_appointment(account_id, booking)
                    appointments_synced += 1
                
                cursor = data.get('cursor')
                if not cursor:
                    break
                
                # Rate limiting
                await asyncio.sleep(0.25)
                
        except Exception as e:
            self.logger.error(f"Appointment sync error: {str(e)}")
            raise
        
        return appointments_synced
    
    def _sync_modifiers(self, account_id: str, since: Optional[datetime]) -> int:
        """Sync modifier data from Square"""
        # For now, modifiers are extracted from orders/payments
        # This method can be expanded based on specific Square API endpoints
        return 0
    
    def _store_customer(self, account_id: str, customer_data: Dict[str, Any]):
        """Store customer in Supabase"""
        try:
            # Prepare customer data for storage
            customer_record = {
                'account_id': account_id,
                'square_customer_id': customer_data.get('id'),
                'given_name': customer_data.get('given_name'),
                'family_name': customer_data.get('family_name'),
                'email': customer_data.get('email_address'),
                'phone': customer_data.get('phone_number'),
                'square_data': json.dumps(customer_data),
                'created_at': customer_data.get('created_at'),
                'updated_at': customer_data.get('updated_at')
            }
            
            # Upsert to avoid duplicates
            self.supabase.table('customers').upsert(
                customer_record,
                on_conflict='square_customer_id'
            ).execute()
            
        except Exception as e:
            self.logger.error(f"Error storing customer: {str(e)}")
            raise
    
    def _store_payment(self, account_id: str, payment_data: Dict[str, Any]):
        """Store payment in Supabase"""
        try:
            # Prepare payment data for storage
            payment_record = {
                'account_id': account_id,
                'square_payment_id': payment_data.get('id'),
                'amount': payment_data.get('amount_money', {}).get('amount', 0),
                'currency': payment_data.get('amount_money', {}).get('currency', 'USD'),
                'status': payment_data.get('status'),
                'square_data': json.dumps(payment_data),
                'created_at': payment_data.get('created_at'),
                'updated_at': payment_data.get('updated_at')
            }
            
            # Upsert to avoid duplicates
            self.supabase.table('transactions').upsert(
                payment_record,
                on_conflict='square_payment_id'
            ).execute()
            
        except Exception as e:
            self.logger.error(f"Error storing payment: {str(e)}")
            raise
    
    def _store_appointment(self, account_id: str, booking_data: Dict[str, Any]):
        """Store appointment in Supabase"""
        try:
            # Prepare appointment data for storage
            appointment_record = {
                'account_id': account_id,
                'square_booking_id': booking_data.get('id'),
                'customer_id': booking_data.get('customer_id', 'unknown'),
                'location_id': booking_data.get('location_id', 'unknown'),
                'service_variation_id': booking_data.get('appointment_segments', [{}])[0].get('service_variation_id', 'unknown'),
                'duration_minutes': booking_data.get('appointment_segments', [{}])[0].get('duration_minutes', 60),
                'start_at': booking_data.get('start_at'),
                'status': booking_data.get('status'),
                'created_at': booking_data.get('created_at'),
                'updated_at': booking_data.get('updated_at')
            }
            
            # Upsert to avoid duplicates
            self.supabase.table('appointments').upsert(
                appointment_record,
                on_conflict='square_booking_id'
            ).execute()
            
        except Exception as e:
            self.logger.error(f"Error storing appointment: {str(e)}")
            raise
    
    def _get_last_sync_time(self, account_id: str) -> Optional[datetime]:
        """Get the last sync time for incremental sync"""
        try:
            result = self.supabase.table('accounts').select('last_sync_at').eq('id', account_id).single().execute()
            
            if result.data and result.data.get('last_sync_at'):
                return datetime.fromisoformat(result.data['last_sync_at'].replace('Z', '+00:00'))
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
    
    def _publish_agent_status(self, status: str, entity_id: str):
        """Publish agent status to Redis"""
        try:
            message = {
                'agent': self.name,
                'status': status,
                'entity': entity_id,
                'timestamp': datetime.now().isoformat()
            }
            
            self.redis_client.publish('agent_channel', json.dumps(message))
            
        except Exception as e:
            self.logger.error(f"Could not publish status: {str(e)}")
    
    def _publish_completion(self, account_id: str, results: Dict[str, Any]):
        """Publish sync completion event"""
        try:
            message = {
                'agent': self.name,
                'event': 'square_sync_complete',
                'account_id': account_id,
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
            self.redis_client.publish('agent_channel', json.dumps(message))
            
        except Exception as e:
            self.logger.error(f"Could not publish completion: {str(e)}")
    
    def _backfill_customers(self, account_id: str, start_date: datetime, end_date: datetime) -> int:
        """Backfill historical customer data"""
        # Implementation for historical customer backfill
        # Similar to _sync_customers but with date range filtering
        return 0
    
    def _backfill_payments(self, account_id: str, start_date: datetime, end_date: datetime) -> int:
        """Backfill historical payment data"""
        # Implementation for historical payment backfill
        # Similar to _sync_payments but with date range filtering
        return 0
    
    def _backfill_appointments(self, account_id: str, start_date: datetime, end_date: datetime) -> int:
        """Backfill historical appointment data"""
        # Implementation for historical appointment backfill
        # Similar to _sync_appointments but with date range filtering
        return 0
    
    def _backfill_modifiers(self, account_id: str, start_date: datetime, end_date: datetime) -> int:
        """Backfill historical modifier data"""
        # Implementation for historical modifier backfill
        return 0