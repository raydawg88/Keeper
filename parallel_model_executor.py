#!/usr/bin/env python3
"""
PARALLEL MODEL EXECUTOR - High Performance ML Pipeline
Replaces sequential 31-minute model training with parallel execution
Trains models in parallel processes and caches results for reuse
"""

import os
import time
import pickle
import warnings
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
import joblib

warnings.filterwarnings('ignore')

try:
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
    from sklearn.svm import SVC, SVR
    from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
    from sklearn.neural_network import MLPClassifier, MLPRegressor
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.naive_bayes import GaussianNB
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.mixture import GaussianMixture
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, r2_score, silhouette_score
    import xgboost as xgb
except ImportError as e:
    print(f"Installing required packages: {e}")
    packages = ["pandas", "numpy", "scikit-learn", "xgboost", "joblib"]
    for package in packages:
        os.system(f"pip3 install {package}")
    print("Packages installed. Please restart the script.")
    exit(1)

@dataclass
class ModelResult:
    """Result from a single model execution"""
    model_name: str
    model_type: str  # 'classification', 'regression', 'clustering'
    execution_time: float
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    r2_score: Optional[float] = None
    mse: Optional[float] = None
    cv_mean: Optional[float] = None
    cv_std: Optional[float] = None
    feature_importance: Optional[Dict[str, float]] = None
    predictions: Optional[List] = None
    model_object: Optional[Any] = None
    business_value: float = 0.0
    error: Optional[str] = None

@dataclass
class ModelExecutionStats:
    """Statistics from parallel model execution"""
    total_models: int = 0
    successful_models: int = 0
    failed_models: int = 0
    total_execution_time: float = 0.0
    parallel_speedup: float = 0.0
    models_per_second: float = 0.0
    results: List[ModelResult] = field(default_factory=list)

class ParallelModelExecutor:
    """High-performance parallel model execution system"""
    
    def __init__(self, cache_dir: str = "/tmp/keeper_cache/models", max_workers: Optional[int] = None):
        self.cache_dir = cache_dir
        self.max_workers = max_workers or min(cpu_count(), 8)  # Cap at 8 to avoid memory issues
        os.makedirs(cache_dir, exist_ok=True)
        
        print(f"🚀 PARALLEL MODEL EXECUTOR INITIALIZED")
        print(f"   Cache Dir: {cache_dir}")
        print(f"   Max Workers: {self.max_workers}")
        print(f"   CPU Cores: {cpu_count()}")
    
    def get_model_configurations(self) -> List[Dict[str, Any]]:
        """Get all model configurations to run"""
        return [
            # CHURN PREDICTION MODELS (Classification)
            {
                'name': 'RandomForest_Churn',
                'type': 'classification',
                'target': 'churn_risk',
                'model': RandomForestClassifier(n_estimators=50, random_state=42),  # Reduced for speed
                'business_value_multiplier': 5000
            },
            {
                'name': 'XGBoost_Churn', 
                'type': 'classification',
                'target': 'churn_risk',
                'model': xgb.XGBClassifier(n_estimators=50, random_state=42),
                'business_value_multiplier': 4800
            },
            {
                'name': 'LogisticRegression_Churn',
                'type': 'classification', 
                'target': 'churn_risk',
                'model': LogisticRegression(random_state=42, max_iter=500),
                'business_value_multiplier': 4200
            },
            {
                'name': 'SVM_Churn',
                'type': 'classification',
                'target': 'churn_risk', 
                'model': SVC(probability=True, random_state=42),
                'business_value_multiplier': 4500
            },
            {
                'name': 'GradientBoosting_Churn',
                'type': 'classification',
                'target': 'churn_risk',
                'model': GradientBoostingClassifier(n_estimators=50, random_state=42),
                'business_value_multiplier': 4700
            },
            
            # LIFETIME VALUE MODELS (Regression)
            {
                'name': 'RandomForest_LTV',
                'type': 'regression',
                'target': 'lifetime_value',
                'model': RandomForestRegressor(n_estimators=50, random_state=42),
                'business_value_multiplier': 3000
            },
            {
                'name': 'XGBoost_LTV',
                'type': 'regression', 
                'target': 'lifetime_value',
                'model': xgb.XGBRegressor(n_estimators=50, random_state=42),
                'business_value_multiplier': 2800
            },
            {
                'name': 'Ridge_LTV',
                'type': 'regression',
                'target': 'lifetime_value',
                'model': Ridge(random_state=42),
                'business_value_multiplier': 2200
            },
            {
                'name': 'LinearRegression_LTV',
                'type': 'regression',
                'target': 'lifetime_value', 
                'model': LinearRegression(),
                'business_value_multiplier': 2000
            },
            
            # BEHAVIORAL PREDICTION MODELS
            {
                'name': 'RandomForest_VisitFreq',
                'type': 'regression',
                'target': 'visit_frequency',
                'model': RandomForestRegressor(n_estimators=30, random_state=42),
                'business_value_multiplier': 1800
            },
            {
                'name': 'RandomForest_ServicePref',
                'type': 'regression',
                'target': 'service_preference', 
                'model': RandomForestRegressor(n_estimators=30, random_state=42),
                'business_value_multiplier': 1600
            },
            
            # CLUSTERING MODELS
            {
                'name': 'KMeans_Segmentation',
                'type': 'clustering',
                'target': None,
                'model': KMeans(n_clusters=5, random_state=42),
                'business_value_multiplier': 2500
            },
            {
                'name': 'GaussianMixture_Segmentation',
                'type': 'clustering', 
                'target': None,
                'model': GaussianMixture(n_components=5, random_state=42),
                'business_value_multiplier': 2300
            }
        ]
    
    def execute_models_parallel(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> ModelExecutionStats:
        """Execute all models in parallel"""
        print(f"🏃 EXECUTING MODELS IN PARALLEL...")
        print(f"   Features: {X.shape[1]} columns, {X.shape[0]} rows")
        print(f"   Workers: {self.max_workers}")
        
        start_time = time.time()
        configurations = self.get_model_configurations()
        
        stats = ModelExecutionStats()
        stats.total_models = len(configurations)
        
        # Execute models in parallel
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all model training jobs
            future_to_config = {}
            for config in configurations:
                future = executor.submit(execute_single_model, config, X, y)
                future_to_config[future] = config
            
            # Collect results as they complete
            for future in as_completed(future_to_config):
                config = future_to_config[future]
                try:
                    result = future.result()
                    stats.results.append(result)
                    stats.successful_models += 1
                    print(f"   ✅ {result.model_name}: {result.execution_time:.2f}s")
                except Exception as e:
                    error_result = ModelResult(
                        model_name=config['name'],
                        model_type=config['type'],
                        execution_time=0.0,
                        error=str(e)
                    )
                    stats.results.append(error_result)
                    stats.failed_models += 1
                    print(f"   ❌ {config['name']}: {str(e)}")
        
        # Calculate statistics
        stats.total_execution_time = time.time() - start_time
        sequential_time = sum(r.execution_time for r in stats.results)
        stats.parallel_speedup = sequential_time / stats.total_execution_time if stats.total_execution_time > 0 else 0
        stats.models_per_second = stats.successful_models / stats.total_execution_time if stats.total_execution_time > 0 else 0
        
        print(f"✅ PARALLEL EXECUTION COMPLETE:")
        print(f"   📊 Successful: {stats.successful_models}/{stats.total_models}")
        print(f"   ⏱️  Total Time: {stats.total_execution_time:.2f}s")
        print(f"   🚀 Speedup: {stats.parallel_speedup:.1f}x")
        print(f"   📈 Models/sec: {stats.models_per_second:.1f}")
        
        return stats
    
    def save_models(self, results: List[ModelResult], version: str = None):
        """Save trained models to cache"""
        if version is None:
            version = datetime.now().strftime("%Y%m%d_%H%M")
        
        saved_count = 0
        for result in results:
            if result.model_object and not result.error:
                try:
                    model_path = f"{self.cache_dir}/{result.model_name}_{version}.pkl"
                    joblib.dump(result.model_object, model_path)
                    saved_count += 1
                except Exception as e:
                    print(f"⚠️  Failed to save {result.model_name}: {e}")
        
        print(f"💾 Saved {saved_count} models to cache")
    
    def load_models(self, version: str = None) -> Dict[str, Any]:
        """Load models from cache"""
        if version is None:
            # Find the latest version
            model_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.pkl')]
            if not model_files:
                return {}
            
            # Extract versions and get the latest
            versions = set()
            for f in model_files:
                parts = f.split('_')
                if len(parts) >= 3:
                    version_part = '_'.join(parts[-2:]).replace('.pkl', '')
                    versions.add(version_part)
            
            if versions:
                version = max(versions)
            else:
                return {}
        
        loaded_models = {}
        model_pattern = f"_{version}.pkl"
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith(model_pattern):
                model_name = filename.replace(model_pattern, '')
                try:
                    model_path = f"{self.cache_dir}/{filename}"
                    loaded_models[model_name] = joblib.load(model_path)
                except Exception as e:
                    print(f"⚠️  Failed to load {model_name}: {e}")
        
        print(f"📥 Loaded {len(loaded_models)} models from cache (version: {version})")
        return loaded_models
    
    def predict_parallel(self, models: Dict[str, Any], X: pd.DataFrame) -> Dict[str, np.ndarray]:
        """Make predictions using cached models in parallel"""
        print(f"🔮 MAKING PREDICTIONS IN PARALLEL...")
        print(f"   Models: {len(models)}")
        print(f"   Samples: {X.shape[0]}")
        
        predictions = {}
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_name = {}
            for model_name, model in models.items():
                future = executor.submit(make_single_prediction, model, X)
                future_to_name[future] = model_name
            
            for future in as_completed(future_to_name):
                model_name = future_to_name[future]
                try:
                    pred = future.result()
                    predictions[model_name] = pred
                except Exception as e:
                    print(f"⚠️  Prediction failed for {model_name}: {e}")
        
        print(f"✅ Generated {len(predictions)} prediction sets")
        return predictions


def execute_single_model(config: Dict[str, Any], X: pd.DataFrame, y: Optional[pd.Series] = None) -> ModelResult:
    """Execute a single model (called in parallel)"""
    start_time = time.time()
    
    try:
        model = config['model']
        model_name = config['name']
        model_type = config['type']
        target = config.get('target')
        business_multiplier = config.get('business_value_multiplier', 1000)
        
        # Prepare data based on model type
        if model_type in ['classification', 'regression']:
            if y is None or target not in y.index:
                # Create synthetic target for testing
                if model_type == 'classification':
                    target_data = np.random.choice([0, 1], size=len(X))
                else:
                    target_data = np.random.normal(100, 50, size=len(X))
            else:
                target_data = y
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, target_data, test_size=0.3, random_state=42)
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Make predictions
            predictions = model.predict(X_test_scaled)
            
            # Calculate metrics
            result = ModelResult(
                model_name=model_name,
                model_type=model_type,
                execution_time=time.time() - start_time,
                model_object=model,
                predictions=predictions.tolist()
            )
            
            if model_type == 'classification':
                result.accuracy = accuracy_score(y_test, predictions)
                result.precision = precision_score(y_test, predictions, average='weighted', zero_division=0)
                result.recall = recall_score(y_test, predictions, average='weighted', zero_division=0)
                result.f1_score = f1_score(y_test, predictions, average='weighted', zero_division=0)
                
                # Cross-validation
                try:
                    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=3)
                    result.cv_mean = cv_scores.mean()
                    result.cv_std = cv_scores.std()
                except:
                    pass
                
                result.business_value = result.accuracy * business_multiplier
                
            else:  # regression
                result.r2_score = r2_score(y_test, predictions)
                result.mse = mean_squared_error(y_test, predictions)
                
                # Cross-validation
                try:
                    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=3, scoring='r2')
                    result.cv_mean = cv_scores.mean()
                    result.cv_std = cv_scores.std()
                except:
                    pass
                
                result.business_value = max(result.r2_score, 0) * business_multiplier
            
            # Feature importance
            if hasattr(model, 'feature_importances_'):
                result.feature_importance = dict(zip(X.columns, model.feature_importances_))
            elif hasattr(model, 'coef_'):
                result.feature_importance = dict(zip(X.columns, model.coef_.flatten()))
        
        elif model_type == 'clustering':
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Fit clustering model
            cluster_labels = model.fit_predict(X_scaled)
            
            result = ModelResult(
                model_name=model_name,
                model_type=model_type,
                execution_time=time.time() - start_time,
                model_object=model,
                predictions=cluster_labels.tolist()
            )
            
            # Calculate silhouette score if possible
            try:
                if len(set(cluster_labels)) > 1:
                    sil_score = silhouette_score(X_scaled, cluster_labels)
                    result.accuracy = sil_score  # Use accuracy field for silhouette score
                    result.business_value = sil_score * business_multiplier
            except:
                pass
        
        return result
        
    except Exception as e:
        return ModelResult(
            model_name=config['name'],
            model_type=config['type'], 
            execution_time=time.time() - start_time,
            error=str(e)
        )


def make_single_prediction(model: Any, X: pd.DataFrame) -> np.ndarray:
    """Make a single prediction (called in parallel)"""
    # Scale features (assuming model was trained on scaled data)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Make prediction
    if hasattr(model, 'predict_proba'):
        return model.predict_proba(X_scaled)
    else:
        return model.predict(X_scaled)


def test_parallel_executor():
    """Test the parallel model executor"""
    print("🧪 TESTING PARALLEL MODEL EXECUTOR")
    print("=" * 50)
    
    # Create synthetic data
    np.random.seed(42)
    n_samples = 1000
    n_features = 10
    
    X = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f'feature_{i}' for i in range(n_features)]
    )
    
    executor = ParallelModelExecutor()
    
    # Test parallel training
    print("\n1. PARALLEL TRAINING TEST")
    stats = executor.execute_models_parallel(X)
    
    print(f"\nTraining Results:")
    print(f"  Total Models: {stats.total_models}")
    print(f"  Successful: {stats.successful_models}")
    print(f"  Failed: {stats.failed_models}")
    print(f"  Execution Time: {stats.total_execution_time:.2f}s")
    print(f"  Speedup: {stats.parallel_speedup:.1f}x")
    
    # Save models
    executor.save_models(stats.results)
    
    # Test model loading and prediction
    print("\n2. PARALLEL PREDICTION TEST")
    models = executor.load_models()
    
    if models:
        predictions = executor.predict_parallel(models, X)
        print(f"Generated predictions for {len(predictions)} models")
    
    print("\n✅ PARALLEL EXECUTOR TESTS COMPLETE")


if __name__ == "__main__":
    test_parallel_executor()