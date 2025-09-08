#!/usr/bin/env python3
"""
INCREMENTAL DATA LOADER - High Performance Data Loading
Replaces the 31-minute full data load with sub-second incremental updates
Only loads changed data since last run + maintains cached calculations
"""

import os
import json
import pickle
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

try:
    from supabase import create_client, Client
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"Installing required packages: {e}")
    os.system("pip3 install supabase pandas numpy")
    from supabase import create_client, Client
    import pandas as pd
    import numpy as np

@dataclass
class IncrementalStats:
    """Statistics about incremental data loading"""
    customers_loaded: int = 0
    appointments_loaded: int = 0
    transactions_loaded: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    load_time_seconds: float = 0.0
    total_customers: int = 0

class IncrementalDataLoader:
    """High-performance incremental data loader for Keeper Intelligence"""
    
    def __init__(self, account_id: str, cache_dir: str = "/tmp/keeper_cache"):
        self.account_id = account_id
        self.cache_dir = cache_dir
        self.supabase = self._init_supabase()
        self._ensure_cache_dir()
        
        # Thread-safe cache
        self._cache_lock = threading.Lock()
        self._customer_cache = {}
        self._rfm_cache = {}
        self._ltv_cache = {}
        
        print(f"🚀 INCREMENTAL LOADER INITIALIZED")
        print(f"   Account: {account_id}")
        print(f"   Cache Dir: {cache_dir}")
    
    def _init_supabase(self) -> Client:
        """Initialize Supabase client with environment variables"""
        supabase_url = os.getenv('SUPABASE_URL', 'https://jlawmbqoykwgrjutrfsp.supabase.co')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY', 'sb_secret_6ONiuNr9OL53Wwf5G28wqA_WJrYbp50')
        return create_client(supabase_url, supabase_key)
    
    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(f"{self.cache_dir}/models", exist_ok=True)
        os.makedirs(f"{self.cache_dir}/features", exist_ok=True)
    
    def get_last_sync_time(self) -> Optional[datetime]:
        """Get the last sync timestamp from cache"""
        cache_file = f"{self.cache_dir}/last_sync_{self.account_id}.json"
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    return datetime.fromisoformat(data['last_sync'])
        except Exception:
            pass
        return None
    
    def update_last_sync_time(self, sync_time: Optional[datetime] = None):
        """Update the last sync timestamp"""
        if sync_time is None:
            sync_time = datetime.utcnow()
            
        cache_file = f"{self.cache_dir}/last_sync_{self.account_id}.json"
        with open(cache_file, 'w') as f:
            json.dump({
                'last_sync': sync_time.isoformat(),
                'account_id': self.account_id
            }, f)
    
    def load_incremental_data(self, full_refresh: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, IncrementalStats]:
        """
        Load only changed data since last sync
        Returns: (customers_df, appointments_df, transactions_df, stats)
        """
        start_time = datetime.utcnow()
        stats = IncrementalStats()
        
        print(f"📊 LOADING {'FULL' if full_refresh else 'INCREMENTAL'} DATA...")
        
        # Get last sync time
        last_sync = None if full_refresh else self.get_last_sync_time()
        if last_sync:
            print(f"   📅 Loading changes since: {last_sync}")
        else:
            print(f"   🔄 Full refresh mode")
        
        # Load data in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                'customers': executor.submit(self._load_customers_incremental, last_sync),
                'appointments': executor.submit(self._load_appointments_incremental, last_sync),
                'transactions': executor.submit(self._load_transactions_incremental, last_sync)
            }
            
            results = {}
            for name, future in futures.items():
                try:
                    results[name] = future.result()
                except Exception as e:
                    print(f"❌ Error loading {name}: {e}")
                    results[name] = pd.DataFrame()
        
        customers_df = results['customers']
        appointments_df = results['appointments']
        transactions_df = results['transactions']
        
        # Update statistics
        stats.customers_loaded = len(customers_df)
        stats.appointments_loaded = len(appointments_df)
        stats.transactions_loaded = len(transactions_df)
        stats.load_time_seconds = (datetime.utcnow() - start_time).total_seconds()
        
        # Get total customer count for reference
        try:
            count_response = self.supabase.table('customers')\
                .select('id', count='exact')\
                .eq('account_id', self.account_id)\
                .execute()
            stats.total_customers = count_response.count or 0
        except:
            stats.total_customers = len(customers_df)
        
        # Update sync time
        self.update_last_sync_time()
        
        print(f"✅ INCREMENTAL LOAD COMPLETE:")
        print(f"   📈 Customers: {stats.customers_loaded:,} ({'new/changed' if not full_refresh else 'total'})")
        print(f"   📅 Appointments: {stats.appointments_loaded:,}")
        print(f"   💰 Transactions: {stats.transactions_loaded:,}")
        print(f"   ⏱️  Load Time: {stats.load_time_seconds:.2f} seconds")
        
        return customers_df, appointments_df, transactions_df, stats
    
    def _load_customers_incremental(self, since: Optional[datetime]) -> pd.DataFrame:
        """Load customers with optional incremental filtering"""
        try:
            query = self.supabase.table('customers')\
                .select('*')\
                .eq('account_id', self.account_id)
            
            # Add incremental filter if provided
            if since:
                query = query.gte('updated_at', since.isoformat())
            
            response = query.execute()
            
            if response.data:
                return pd.DataFrame(response.data)
            
        except Exception as e:
            print(f"⚠️  Customer loading error: {e}")
        
        return pd.DataFrame()
    
    def _load_appointments_incremental(self, since: Optional[datetime]) -> pd.DataFrame:
        """Load appointments with optional incremental filtering"""
        try:
            query = self.supabase.table('appointments')\
                .select('*')\
                .eq('account_id', self.account_id)
            
            # Add incremental filter if provided
            if since:
                query = query.gte('updated_at', since.isoformat())
            
            response = query.execute()
            
            if response.data:
                return pd.DataFrame(response.data)
            
        except Exception as e:
            print(f"⚠️  Appointment loading error: {e}")
        
        return pd.DataFrame()
    
    def _load_transactions_incremental(self, since: Optional[datetime]) -> pd.DataFrame:
        """Load transactions with optional incremental filtering"""
        try:
            query = self.supabase.table('transactions')\
                .select('*')\
                .eq('account_id', self.account_id)
            
            # Add incremental filter if provided  
            if since:
                query = query.gte('updated_at', since.isoformat())
            
            response = query.execute()
            
            if response.data:
                return pd.DataFrame(response.data)
            
        except Exception as e:
            print(f"⚠️  Transaction loading error: {e}")
        
        return pd.DataFrame()
    
    def get_cached_features(self, customer_ids: List[str]) -> Dict[str, Dict]:
        """Get cached RFM scores, LTV calculations, etc. for given customers"""
        cached_features = {}
        
        with self._cache_lock:
            for customer_id in customer_ids:
                cache_key = f"features_{customer_id}"
                cache_file = f"{self.cache_dir}/features/{cache_key}.pkl"
                
                if os.path.exists(cache_file):
                    try:
                        with open(cache_file, 'rb') as f:
                            cached_features[customer_id] = pickle.load(f)
                    except Exception:
                        pass
        
        return cached_features
    
    def cache_features(self, customer_features: Dict[str, Dict]):
        """Cache computed features for customers"""
        with self._cache_lock:
            for customer_id, features in customer_features.items():
                cache_key = f"features_{customer_id}"
                cache_file = f"{self.cache_dir}/features/{cache_key}.pkl"
                
                try:
                    with open(cache_file, 'wb') as f:
                        pickle.dump(features, f)
                except Exception as e:
                    print(f"⚠️  Failed to cache features for {customer_id}: {e}")
    
    def invalidate_customer_cache(self, customer_ids: List[str]):
        """Invalidate cached features for specific customers"""
        with self._cache_lock:
            for customer_id in customer_ids:
                cache_key = f"features_{customer_id}"
                cache_file = f"{self.cache_dir}/features/{cache_key}.pkl"
                
                if os.path.exists(cache_file):
                    try:
                        os.remove(cache_file)
                    except Exception:
                        pass
    
    def get_cached_models(self) -> Dict[str, Any]:
        """Load pre-trained models from cache"""
        cached_models = {}
        models_dir = f"{self.cache_dir}/models"
        
        for model_file in os.listdir(models_dir):
            if model_file.endswith('.pkl'):
                model_name = model_file.replace('.pkl', '')
                try:
                    with open(f"{models_dir}/{model_file}", 'rb') as f:
                        cached_models[model_name] = pickle.load(f)
                except Exception as e:
                    print(f"⚠️  Failed to load cached model {model_name}: {e}")
        
        return cached_models
    
    def cache_models(self, models: Dict[str, Any]):
        """Cache trained models"""
        models_dir = f"{self.cache_dir}/models"
        
        for model_name, model in models.items():
            try:
                with open(f"{models_dir}/{model_name}.pkl", 'wb') as f:
                    pickle.dump(model, f)
            except Exception as e:
                print(f"⚠️  Failed to cache model {model_name}: {e}")
    
    def should_retrain_models(self, max_age_hours: int = 168) -> bool:  # Default: 1 week
        """Check if models need retraining based on age"""
        models_dir = f"{self.cache_dir}/models"
        
        if not os.path.exists(models_dir) or not os.listdir(models_dir):
            return True
        
        # Check age of model files
        oldest_model_time = None
        for model_file in os.listdir(models_dir):
            if model_file.endswith('.pkl'):
                model_path = f"{models_dir}/{model_file}"
                model_time = datetime.fromtimestamp(os.path.getmtime(model_path))
                
                if oldest_model_time is None or model_time < oldest_model_time:
                    oldest_model_time = model_time
        
        if oldest_model_time:
            age_hours = (datetime.now() - oldest_model_time).total_seconds() / 3600
            return age_hours > max_age_hours
        
        return True
    
    def clear_cache(self):
        """Clear all cached data"""
        import shutil
        try:
            shutil.rmtree(self.cache_dir)
            self._ensure_cache_dir()
            print("✅ Cache cleared")
        except Exception as e:
            print(f"⚠️  Cache clear failed: {e}")

def test_incremental_loader():
    """Test the incremental loader performance"""
    print("🧪 TESTING INCREMENTAL LOADER")
    print("=" * 50)
    
    account_id = "b491de6e-7d5b-4e0e-b1cd-625c6c4f7d81"
    loader = IncrementalDataLoader(account_id)
    
    # Test full load
    print("\n1. FULL LOAD TEST")
    customers, appointments, transactions, stats = loader.load_incremental_data(full_refresh=True)
    print(f"Full load took {stats.load_time_seconds:.2f} seconds")
    
    # Test incremental load (should be much faster)
    print("\n2. INCREMENTAL LOAD TEST")
    customers, appointments, transactions, stats = loader.load_incremental_data(full_refresh=False)
    print(f"Incremental load took {stats.load_time_seconds:.2f} seconds")
    
    # Test cache functionality
    if not customers.empty:
        print("\n3. CACHE TEST")
        sample_ids = customers['id'].head(5).tolist()
        
        # Cache some features
        sample_features = {
            customer_id: {
                'rfm_score': 75.5,
                'ltv': 1250.0,
                'churn_risk': 0.23
            } for customer_id in sample_ids
        }
        loader.cache_features(sample_features)
        
        # Retrieve cached features
        cached = loader.get_cached_features(sample_ids)
        print(f"Cached {len(cached)} customer features successfully")
    
    print("\n✅ INCREMENTAL LOADER TESTS COMPLETE")

if __name__ == "__main__":
    test_incremental_loader()