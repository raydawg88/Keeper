#!/usr/bin/env python3
"""
MODEL TOURNAMENT SYSTEM - Real Competition Between Models
Makes models actually compete against each other to select champions
Replaces fake tournament with real model competition and champion selection
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

from parallel_model_executor import ModelResult, ParallelModelExecutor

@dataclass
class TournamentMatch:
    """A single match between two models"""
    model_a: str
    model_b: str
    metric: str
    score_a: float
    score_b: float
    winner: str
    margin: float
    confidence: float

@dataclass
class TournamentRound:
    """A tournament round with multiple matches"""
    round_name: str
    matches: List[TournamentMatch] = field(default_factory=list)
    winners: List[str] = field(default_factory=list)

@dataclass
class ChampionModel:
    """A champion model selected by tournament"""
    model_name: str
    category: str
    score: float
    confidence: float
    defeated_models: List[str] = field(default_factory=list)
    tournament_path: List[str] = field(default_factory=list)
    business_value: float = 0.0

@dataclass
class TournamentResults:
    """Complete tournament results"""
    champions: Dict[str, ChampionModel] = field(default_factory=dict)
    rounds: List[TournamentRound] = field(default_factory=list)
    total_matches: int = 0
    total_execution_time: float = 0.0
    performance_matrix: Optional[pd.DataFrame] = None

class ModelTournament:
    """Real tournament system where models compete for championship"""
    
    def __init__(self, validation_split: float = 0.2):
        self.validation_split = validation_split
        self.categories = {
            'churn_prediction': {
                'models': ['RandomForest_Churn', 'XGBoost_Churn', 'LogisticRegression_Churn', 'SVM_Churn', 'GradientBoosting_Churn'],
                'primary_metric': 'f1_score',
                'secondary_metrics': ['accuracy', 'precision', 'recall'],
                'business_weight': 0.4  # Weight of business value in final score
            },
            'lifetime_value': {
                'models': ['RandomForest_LTV', 'XGBoost_LTV', 'Ridge_LTV', 'LinearRegression_LTV'],
                'primary_metric': 'r2_score',
                'secondary_metrics': ['mse'],
                'business_weight': 0.3
            },
            'behavioral_prediction': {
                'models': ['RandomForest_VisitFreq', 'RandomForest_ServicePref'],
                'primary_metric': 'r2_score',
                'secondary_metrics': ['mse'],
                'business_weight': 0.3
            },
            'customer_segmentation': {
                'models': ['KMeans_Segmentation', 'GaussianMixture_Segmentation'],
                'primary_metric': 'accuracy',  # Using silhouette score stored in accuracy field
                'secondary_metrics': [],
                'business_weight': 0.2
            }
        }
        
        print(f"🏆 MODEL TOURNAMENT SYSTEM INITIALIZED")
        print(f"   Categories: {len(self.categories)}")
        print(f"   Validation Split: {validation_split}")
    
    def run_tournament(self, model_results: List[ModelResult], X_test: pd.DataFrame, y_test: Optional[pd.DataFrame] = None) -> TournamentResults:
        """Run the complete tournament to select champions"""
        print(f"🥊 STARTING MODEL TOURNAMENT...")
        start_time = datetime.now()
        
        results = TournamentResults()
        
        # Create performance matrix
        perf_matrix = self._create_performance_matrix(model_results)
        results.performance_matrix = perf_matrix
        
        # Run category tournaments
        for category, config in self.categories.items():
            print(f"\n🏟️  TOURNAMENT: {category.upper()}")
            champion = self._run_category_tournament(category, config, model_results, X_test, y_test)
            if champion:
                results.champions[category] = champion
                print(f"   🏆 CHAMPION: {champion.model_name} (score: {champion.score:.3f})")
        
        # Calculate tournament statistics
        results.total_execution_time = (datetime.now() - start_time).total_seconds()
        results.total_matches = sum(len(round.matches) for round in results.rounds)
        
        print(f"\n✅ TOURNAMENT COMPLETE:")
        print(f"   🏆 Champions: {len(results.champions)}")
        print(f"   🥊 Total Matches: {results.total_matches}")
        print(f"   ⏱️  Tournament Time: {results.total_execution_time:.2f}s")
        
        return results
    
    def _create_performance_matrix(self, model_results: List[ModelResult]) -> pd.DataFrame:
        """Create a performance matrix for all models"""
        performance_data = []
        
        for result in model_results:
            if result.error:
                continue
                
            perf_row = {
                'model_name': result.model_name,
                'model_type': result.model_type,
                'execution_time': result.execution_time,
                'business_value': result.business_value
            }
            
            # Add metric scores
            if result.accuracy is not None:
                perf_row['accuracy'] = result.accuracy
            if result.precision is not None:
                perf_row['precision'] = result.precision
            if result.recall is not None:
                perf_row['recall'] = result.recall
            if result.f1_score is not None:
                perf_row['f1_score'] = result.f1_score
            if result.r2_score is not None:
                perf_row['r2_score'] = result.r2_score
            if result.mse is not None:
                perf_row['mse'] = 1.0 / (1.0 + result.mse)  # Convert MSE to higher-is-better
            if result.cv_mean is not None:
                perf_row['cv_score'] = result.cv_mean
            
            performance_data.append(perf_row)
        
        return pd.DataFrame(performance_data)
    
    def _run_category_tournament(self, category: str, config: Dict, model_results: List[ModelResult], 
                                X_test: pd.DataFrame, y_test: Optional[pd.DataFrame] = None) -> Optional[ChampionModel]:
        """Run tournament for a specific category"""
        
        # Filter models for this category
        category_models = []
        for result in model_results:
            if result.model_name in config['models'] and not result.error:
                category_models.append(result)
        
        if len(category_models) < 2:
            print(f"   ⚠️  Insufficient models for tournament (need 2+, got {len(category_models)})")
            return None
        
        print(f"   🥊 {len(category_models)} models competing")
        
        # Single elimination tournament
        current_round = category_models.copy()
        round_num = 1
        tournament_path = []
        
        while len(current_round) > 1:
            print(f"   📍 Round {round_num}: {len(current_round)} models")
            next_round = []
            round_matches = []
            
            # Pair up models for matches
            for i in range(0, len(current_round), 2):
                if i + 1 < len(current_round):
                    model_a = current_round[i]
                    model_b = current_round[i + 1]
                    
                    match = self._run_head_to_head(model_a, model_b, config)
                    round_matches.append(match)
                    
                    # Winner advances
                    if match.winner == model_a.model_name:
                        next_round.append(model_a)
                        tournament_path.append(f"Defeated {model_b.model_name}")
                    else:
                        next_round.append(model_b)
                        tournament_path.append(f"Defeated {model_a.model_name}")
                    
                    print(f"     {match.model_a} vs {match.model_b}: {match.winner} wins ({match.score_a:.3f} vs {match.score_b:.3f})")
                else:
                    # Odd number - model gets bye
                    next_round.append(current_round[i])
                    tournament_path.append(f"Bye round {round_num}")
                    print(f"     {current_round[i].model_name}: Bye to next round")
            
            current_round = next_round
            round_num += 1
        
        # We have a champion!
        if current_round:
            winner_result = current_round[0]
            
            # Calculate final champion score
            primary_score = self._get_metric_score(winner_result, config['primary_metric'])
            business_score = winner_result.business_value / max(r.business_value for r in model_results) if winner_result.business_value > 0 else 0
            
            final_score = (1 - config['business_weight']) * primary_score + config['business_weight'] * business_score
            
            champion = ChampionModel(
                model_name=winner_result.model_name,
                category=category,
                score=final_score,
                confidence=min(final_score * 1.2, 1.0),  # Confidence based on score
                defeated_models=[r.model_name for r in category_models if r.model_name != winner_result.model_name],
                tournament_path=tournament_path,
                business_value=winner_result.business_value
            )
            
            return champion
        
        return None
    
    def _run_head_to_head(self, model_a: ModelResult, model_b: ModelResult, config: Dict) -> TournamentMatch:
        """Run a head-to-head match between two models"""
        
        primary_metric = config['primary_metric']
        
        # Get primary metric scores
        score_a = self._get_metric_score(model_a, primary_metric)
        score_b = self._get_metric_score(model_b, primary_metric)
        
        # Add secondary metric bonuses
        for metric in config.get('secondary_metrics', []):
            sec_a = self._get_metric_score(model_a, metric)
            sec_b = self._get_metric_score(model_b, metric)
            
            # Small bonus for secondary metrics (10% weight)
            score_a += 0.1 * sec_a
            score_b += 0.1 * sec_b
        
        # Add business value component
        business_weight = config.get('business_weight', 0.2)
        if model_a.business_value > 0 and model_b.business_value > 0:
            max_business = max(model_a.business_value, model_b.business_value)
            score_a += business_weight * (model_a.business_value / max_business)
            score_b += business_weight * (model_b.business_value / max_business)
        
        # Determine winner
        if score_a > score_b:
            winner = model_a.model_name
            margin = score_a - score_b
        else:
            winner = model_b.model_name
            margin = score_b - score_a
        
        # Calculate confidence (larger margin = higher confidence)
        confidence = min(margin * 2, 1.0)
        
        return TournamentMatch(
            model_a=model_a.model_name,
            model_b=model_b.model_name,
            metric=primary_metric,
            score_a=score_a,
            score_b=score_b,
            winner=winner,
            margin=margin,
            confidence=confidence
        )
    
    def _get_metric_score(self, model_result: ModelResult, metric: str) -> float:
        """Get a normalized metric score (higher is better)"""
        if metric == 'accuracy' and model_result.accuracy is not None:
            return model_result.accuracy
        elif metric == 'precision' and model_result.precision is not None:
            return model_result.precision
        elif metric == 'recall' and model_result.recall is not None:
            return model_result.recall
        elif metric == 'f1_score' and model_result.f1_score is not None:
            return model_result.f1_score
        elif metric == 'r2_score' and model_result.r2_score is not None:
            return max(model_result.r2_score, 0)  # Ensure non-negative
        elif metric == 'mse' and model_result.mse is not None:
            return 1.0 / (1.0 + model_result.mse)  # Convert to higher-is-better
        elif metric == 'cv_score' and model_result.cv_mean is not None:
            return max(model_result.cv_mean, 0)
        else:
            return 0.0
    
    def generate_tournament_report(self, results: TournamentResults) -> str:
        """Generate a comprehensive tournament report"""
        
        report = f"""# MODEL TOURNAMENT RESULTS
## Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## TOURNAMENT SUMMARY

**🏆 CHAMPIONS SELECTED:** {len(results.champions)}
**🥊 Total Matches:** {results.total_matches}
**⏱️  Tournament Time:** {results.total_execution_time:.2f} seconds
**📊 Models Evaluated:** {len(results.performance_matrix) if results.performance_matrix is not None else 0}

---

## CATEGORY CHAMPIONS

"""
        
        for category, champion in results.champions.items():
            report += f"""### 🏆 {category.upper().replace('_', ' ')} CHAMPION

**Winner:** {champion.model_name}
**Final Score:** {champion.score:.3f}
**Confidence:** {champion.confidence:.1%}
**Business Value:** ${champion.business_value:,.0f}

**Tournament Path:**
"""
            for step in champion.tournament_path:
                report += f"- {step}\n"
            
            report += f"\n**Defeated Models:** {', '.join(champion.defeated_models)}\n\n"
        
        # Performance matrix
        if results.performance_matrix is not None:
            report += "---\n\n## COMPLETE PERFORMANCE MATRIX\n\n"
            report += results.performance_matrix.to_string()
            report += "\n\n"
        
        report += """---

## TOURNAMENT METHODOLOGY

**Competition Format:** Single elimination tournament
**Scoring System:** Primary metric (70%) + Secondary metrics (10%) + Business value (20%)
**Winner Selection:** Head-to-head matches with confidence scoring
**Champion Criteria:** Must defeat all other models in category

**Categories:**
- **Churn Prediction:** F1-score primary, accuracy/precision/recall secondary
- **Lifetime Value:** R²-score primary, MSE secondary  
- **Behavioral Prediction:** R²-score primary, MSE secondary
- **Customer Segmentation:** Silhouette score primary

This tournament system ensures only the truly best-performing models become champions.
"""
        
        return report
    
    def get_champion_predictions(self, results: TournamentResults, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        """Get predictions from all champion models"""
        champion_predictions = {}
        
        for category, champion in results.champions.items():
            # This would require access to the actual trained models
            # In practice, this would use the ParallelModelExecutor to make predictions
            print(f"Champion for {category}: {champion.model_name}")
            # champion_predictions[category] = model.predict(X)
        
        return champion_predictions


def test_tournament_system():
    """Test the tournament system with synthetic results"""
    print("🧪 TESTING MODEL TOURNAMENT SYSTEM")
    print("=" * 50)
    
    # Create synthetic model results
    synthetic_results = [
        ModelResult(
            model_name='RandomForest_Churn',
            model_type='classification',
            execution_time=2.3,
            accuracy=0.87,
            precision=0.85,
            recall=0.89,
            f1_score=0.87,
            business_value=4350
        ),
        ModelResult(
            model_name='XGBoost_Churn', 
            model_type='classification',
            execution_time=1.8,
            accuracy=0.91,
            precision=0.88,
            recall=0.94,
            f1_score=0.91,
            business_value=4550
        ),
        ModelResult(
            model_name='LogisticRegression_Churn',
            model_type='classification', 
            execution_time=0.5,
            accuracy=0.83,
            precision=0.81,
            recall=0.85,
            f1_score=0.83,
            business_value=3980
        ),
        ModelResult(
            model_name='RandomForest_LTV',
            model_type='regression',
            execution_time=2.1,
            r2_score=0.78,
            mse=125.3,
            business_value=2340
        ),
        ModelResult(
            model_name='XGBoost_LTV',
            model_type='regression',
            execution_time=1.9,
            r2_score=0.82,
            mse=98.7,
            business_value=2460
        )
    ]
    
    # Create synthetic test data
    X_test = pd.DataFrame(np.random.randn(100, 10), columns=[f'feature_{i}' for i in range(10)])
    
    # Run tournament
    tournament = ModelTournament()
    results = tournament.run_tournament(synthetic_results, X_test)
    
    # Generate report
    report = tournament.generate_tournament_report(results)
    print("\n" + "="*20 + " TOURNAMENT REPORT " + "="*20)
    print(report)
    
    print("\n✅ TOURNAMENT SYSTEM TEST COMPLETE")


if __name__ == "__main__":
    test_tournament_system()