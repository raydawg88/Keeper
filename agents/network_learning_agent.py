"""
NetworkLearningAgent - Capture and apply collective intelligence

Responsibility: Capture successful patterns from task completions and apply network
intelligence to enhance insights for all customers. Every customer makes every other customer smarter.

Author: Claude & Ray Hernandez  
Created: 2024-09-06
"""

import logging
import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import redis
import numpy as np
from openai import AsyncOpenAI
from sklearn.metrics.pairwise import cosine_similarity
from supabase import create_client, Client

from .base_agent import BaseAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BusinessCategory(Enum):
    SPA = "spa"
    SALON = "salon" 
    FITNESS = "fitness"
    RESTAURANT = "restaurant"
    RETAIL = "retail"
    SERVICE = "service"
    HEALTHCARE = "healthcare"
    BEAUTY = "beauty"

@dataclass
class NetworkPattern:
    """Anonymized pattern for network learning"""
    id: str
    type: str
    business_category: BusinessCategory
    trigger_conditions: Dict[str, Any]
    action_taken: str
    success_rate: float
    occurrence_count: int
    total_revenue_impact: float
    embedding: List[float]
    created_at: datetime
    updated_at: datetime

@dataclass  
class PatternOutcome:
    """Outcome record for pattern validation"""
    success: bool
    revenue_impact: float
    customer_retained: bool = False
    implementation_difficulty: float = 0.0
    time_to_completion_days: int = 0

class NetworkLearningAgent(BaseAgent):
    """
    Capture and apply collective intelligence across all customers
    
    Core Principle: "Every customer makes every other customer smarter"
    
    Key Features:
    - Capture successful patterns from task completions
    - Anonymize but preserve actionable intelligence
    - Apply network knowledge to enhance new insights
    - Generate embeddings for similarity matching
    - Track pattern success rates across network
    - Provide confidence boosts based on proven approaches
    """
    
    def __init__(self, supabase_url: str, supabase_key: str, redis_url: str, 
                 openai_key: str):
        super().__init__("NetworkLearningAgent", supabase_url, supabase_key, redis_url)
        self.openai = AsyncOpenAI(api_key=openai_key)
        
        # Success rate thresholds
        self.MIN_SUCCESS_RATE = 0.60  # 60% minimum for recommendations
        self.MIN_OCCURRENCES = 3      # At least 3 data points
        self.CONFIDENCE_BOOST_MAX = 0.30  # Maximum 30% confidence boost
        
    async def capture_successful_pattern(self, account_id: str, insight: Dict[str, Any], 
                                       outcome: PatternOutcome) -> bool:
        """
        Capture successful pattern for network learning
        
        Process:
        1. Anonymize the pattern while preserving intelligence
        2. Generate embedding for similarity matching
        3. Check for existing similar patterns
        4. Update or create pattern record
        5. Notify network of new learning
        """
        try:
            await self._publish_status("analyzing", "pattern_capture", account_id)
            
            # Only capture successful patterns
            if not outcome.success:
                logger.info(f"Skipping failed pattern capture: {insight.get('type')}")
                return False
                
            # Get business category
            business_category = await self._get_business_category(account_id)
            
            # Create anonymized pattern
            anonymized_pattern = await self._anonymize_pattern(insight, outcome, business_category)
            
            # Generate embedding
            embedding = await self._create_pattern_embedding(anonymized_pattern)
            
            # Check for existing similar pattern
            existing_pattern = await self._find_similar_pattern(embedding, anonymized_pattern['type'])
            
            if existing_pattern and existing_pattern['similarity'] > 0.95:
                # Update existing pattern
                updated = await self._update_pattern_success(existing_pattern['id'], outcome)
                if updated:
                    await self._publish_network_learning("pattern_updated", existing_pattern['id'])
                return updated
            else:
                # Create new network pattern
                pattern_id = await self._create_network_pattern(anonymized_pattern, embedding)
                if pattern_id:
                    await self._publish_network_learning("pattern_learned", pattern_id)
                return pattern_id is not None
                
        except Exception as e:
            logger.error(f"Pattern capture failed: {e}")
            await self._publish_status("failed", "pattern_capture", str(e))
            return False
    
    async def apply_network_knowledge(self, account_id: str, new_insight: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance insight with network intelligence
        
        Process:
        1. Generate embedding for the new insight
        2. Search for similar successful patterns
        3. Apply confidence boosts and proven approaches
        4. Add network context to insight
        """
        try:
            await self._publish_status("analyzing", "network_enhancement", account_id)
            
            # Get business category
            business_category = await self._get_business_category(account_id)
            
            # Search for similar patterns
            similar_patterns = await self._search_patterns(
                new_insight, 
                business_category,
                min_success_rate=self.MIN_SUCCESS_RATE,
                min_occurrences=self.MIN_OCCURRENCES
            )
            
            if similar_patterns:
                # Find best matching pattern
                best_pattern = max(similar_patterns, key=lambda x: x['success_rate'] * x['similarity'])
                
                # Calculate confidence boost
                confidence_boost = min(
                    best_pattern['success_rate'] * self.CONFIDENCE_BOOST_MAX,
                    self.CONFIDENCE_BOOST_MAX
                )
                
                # Enhance the insight
                enhanced_insight = new_insight.copy()
                enhanced_insight['network_enhanced'] = True
                enhanced_insight['confidence'] *= (1 + confidence_boost)
                enhanced_insight['proven_approach'] = best_pattern['action_template']
                enhanced_insight['expected_success_rate'] = best_pattern['success_rate']
                enhanced_insight['network_context'] = (
                    f"This approach worked {best_pattern['success_rate']*100:.0f}% of the time "
                    f"across {best_pattern['occurrence_count']} similar cases in {business_category.value} businesses"
                )
                enhanced_insight['similarity_score'] = best_pattern['similarity']
                
                await self._publish_status("completed", "network_enhancement", 
                                         f"Enhanced with {confidence_boost:.1%} boost")
                
                return enhanced_insight
            else:
                # No similar patterns found
                logger.info(f"No network patterns found for insight type: {new_insight.get('type')}")
                return new_insight
                
        except Exception as e:
            logger.error(f"Network enhancement failed: {e}")
            return new_insight
    
    async def _anonymize_pattern(self, insight: Dict[str, Any], outcome: PatternOutcome, 
                                business_category: BusinessCategory) -> Dict[str, Any]:
        """Anonymize pattern while preserving intelligence"""
        # Remove all PII
        anonymized = {
            'type': insight.get('type'),
            'business_category': business_category.value,
            'trigger_conditions': self._anonymize_conditions(insight.get('details', {})),
            'action_taken': self._anonymize_action(insight.get('action_script', '')),
            'outcome_metrics': {
                'success': outcome.success,
                'revenue_impact': outcome.revenue_impact,
                'customer_retained': outcome.customer_retained,
                'implementation_difficulty': outcome.implementation_difficulty,
                'time_to_completion_days': outcome.time_to_completion_days
            },
            'confidence': insight.get('confidence', 0),
            'dollar_impact': insight.get('dollar_impact', 0)
        }
        
        return anonymized
    
    def _anonymize_conditions(self, conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize trigger conditions while preserving patterns"""
        anonymized = {}
        
        for key, value in conditions.items():
            if key in ['customer_name', 'customer_id', 'email', 'phone']:
                continue  # Skip PII
            elif key in ['last_visit', 'created_date']:
                # Convert dates to relative patterns
                if isinstance(value, str) and 'T' in value:
                    try:
                        date = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        days_ago = (datetime.now() - date).days
                        anonymized[f'{key}_days_ago'] = days_ago
                    except:
                        pass
            elif isinstance(value, (int, float, bool)):
                anonymized[key] = value
            elif isinstance(value, str) and len(value) < 100:
                # Keep short descriptive strings
                anonymized[key] = self._hash_sensitive_content(value)
        
        return anonymized
    
    def _anonymize_action(self, action: str) -> str:
        """Anonymize action script while preserving structure"""
        if not action:
            return ""
            
        # Replace names with placeholders
        import re
        
        # Replace potential names with [CUSTOMER]
        action = re.sub(r'\b[A-Z][a-z]+\b', '[CUSTOMER]', action)
        
        # Replace phone numbers
        action = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', action)
        
        # Replace email addresses  
        action = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', action)
        
        return action
    
    def _hash_sensitive_content(self, content: str) -> str:
        """Hash potentially sensitive content"""
        return hashlib.md5(content.lower().encode()).hexdigest()[:8]
    
    async def _create_pattern_embedding(self, pattern: Dict[str, Any]) -> List[float]:
        """Generate embedding for pattern similarity matching"""
        try:
            # Create text representation for embedding
            text_parts = [
                f"type: {pattern.get('type', '')}",
                f"category: {pattern.get('business_category', '')}",
                f"conditions: {json.dumps(pattern.get('trigger_conditions', {}))}",
                f"action: {pattern.get('action_taken', '')}"
            ]
            
            text = " | ".join(text_parts)
            
            # Generate embedding using OpenAI
            response = await self.openai.embeddings.create(
                model="text-embedding-3-large",
                input=text,
                dimensions=1536  # Reduced dimensions for performance
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return [0.0] * 1536  # Return zero embedding
    
    async def _find_similar_pattern(self, embedding: List[float], pattern_type: str) -> Optional[Dict[str, Any]]:
        """Find most similar existing pattern"""
        try:
            # Get existing patterns of same type
            result = self.supabase.table('network_patterns').select('*').eq(
                'type', pattern_type
            ).execute()
            
            if not result.data:
                return None
            
            best_similarity = 0
            best_match = None
            
            for pattern in result.data:
                if pattern['embedding']:
                    # Calculate cosine similarity
                    similarity = cosine_similarity(
                        [embedding], 
                        [pattern['embedding']]
                    )[0][0]
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = pattern
                        best_match['similarity'] = similarity
            
            return best_match
            
        except Exception as e:
            logger.error(f"Pattern search failed: {e}")
            return None
    
    async def _update_pattern_success(self, pattern_id: str, outcome: PatternOutcome) -> bool:
        """Update existing pattern with new outcome"""
        try:
            # Get current pattern
            result = self.supabase.table('network_patterns').select('*').eq('id', pattern_id).execute()
            
            if not result.data:
                return False
                
            pattern = result.data[0]
            
            # Update success metrics
            current_successes = pattern['occurrence_count'] * pattern['success_rate']
            new_successes = current_successes + (1 if outcome.success else 0)
            new_count = pattern['occurrence_count'] + 1
            new_success_rate = new_successes / new_count
            
            # Update revenue impact
            new_revenue = pattern['total_revenue_impact'] + outcome.revenue_impact
            
            # Update pattern
            update_result = self.supabase.table('network_patterns').update({
                'success_rate': new_success_rate,
                'occurrence_count': new_count,
                'total_revenue_impact': new_revenue,
                'updated_at': datetime.now().isoformat()
            }).eq('id', pattern_id).execute()
            
            return len(update_result.data) > 0
            
        except Exception as e:
            logger.error(f"Pattern update failed: {e}")
            return False
    
    async def _create_network_pattern(self, pattern: Dict[str, Any], embedding: List[float]) -> Optional[str]:
        """Create new network pattern"""
        try:
            # Prepare pattern record
            pattern_record = {
                'type': pattern['type'],
                'business_category': pattern['business_category'],
                'trigger_conditions': pattern['trigger_conditions'],
                'action_taken': pattern['action_taken'],
                'success_rate': 1.0 if pattern['outcome_metrics']['success'] else 0.0,
                'occurrence_count': 1,
                'total_revenue_impact': pattern['outcome_metrics']['revenue_impact'],
                'embedding': embedding,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Insert pattern
            result = self.supabase.table('network_patterns').insert(pattern_record).execute()
            
            if result.data:
                pattern_id = result.data[0]['id']
                logger.info(f"Created network pattern: {pattern_id}")
                return pattern_id
            
            return None
            
        except Exception as e:
            logger.error(f"Pattern creation failed: {e}")
            return None
    
    async def _search_patterns(self, insight: Dict[str, Any], business_category: BusinessCategory,
                              min_success_rate: float = 0.60, min_occurrences: int = 3) -> List[Dict[str, Any]]:
        """Search for similar patterns with minimum thresholds"""
        try:
            # Generate embedding for search
            search_embedding = await self._create_pattern_embedding({
                'type': insight.get('type'),
                'business_category': business_category.value,
                'trigger_conditions': insight.get('details', {}),
                'action_taken': insight.get('action_script', '')
            })
            
            # Get patterns above thresholds
            result = self.supabase.table('network_patterns').select('*').gte(
                'success_rate', min_success_rate
            ).gte('occurrence_count', min_occurrences).execute()
            
            if not result.data:
                return []
            
            # Calculate similarities and filter
            similar_patterns = []
            for pattern in result.data:
                if pattern['embedding'] and pattern['type'] == insight.get('type'):
                    similarity = cosine_similarity(
                        [search_embedding], 
                        [pattern['embedding']]
                    )[0][0]
                    
                    if similarity > 0.7:  # 70% similarity threshold
                        pattern['similarity'] = similarity
                        pattern['action_template'] = pattern['action_taken']
                        similar_patterns.append(pattern)
            
            return similar_patterns
            
        except Exception as e:
            logger.error(f"Pattern search failed: {e}")
            return []
    
    async def _get_business_category(self, account_id: str) -> BusinessCategory:
        """Determine business category from account data"""
        try:
            result = self.supabase.table('accounts').select('business_name, business_type').eq(
                'id', account_id
            ).execute()
            
            if result.data:
                business_name = result.data[0].get('business_name', '').lower()
                business_type = result.data[0].get('business_type', '').lower()
                
                # Keyword mapping
                if any(word in business_name + business_type for word in ['spa', 'massage', 'wellness']):
                    return BusinessCategory.SPA
                elif any(word in business_name + business_type for word in ['salon', 'hair', 'nail']):
                    return BusinessCategory.SALON
                elif any(word in business_name + business_type for word in ['fitness', 'gym', 'yoga']):
                    return BusinessCategory.FITNESS
                elif any(word in business_name + business_type for word in ['restaurant', 'cafe', 'food']):
                    return BusinessCategory.RESTAURANT
                elif any(word in business_name + business_type for word in ['retail', 'shop', 'store']):
                    return BusinessCategory.RETAIL
                elif any(word in business_name + business_type for word in ['beauty', 'cosmetic']):
                    return BusinessCategory.BEAUTY
                elif any(word in business_name + business_type for word in ['medical', 'health', 'clinic']):
                    return BusinessCategory.HEALTHCARE
                    
            return BusinessCategory.SERVICE  # Default
            
        except Exception as e:
            logger.error(f"Business category detection failed: {e}")
            return BusinessCategory.SERVICE
    
    async def get_network_stats(self) -> Dict[str, Any]:
        """Get network learning statistics"""
        try:
            # Get pattern counts
            result = self.supabase.table('network_patterns').select('*').execute()
            patterns = result.data
            
            if not patterns:
                return {'total_patterns': 0}
            
            # Calculate stats
            stats = {
                'total_patterns': len(patterns),
                'by_business_category': {},
                'by_pattern_type': {},
                'average_success_rate': 0,
                'total_revenue_impact': 0,
                'high_performing_patterns': 0
            }
            
            total_success = 0
            for pattern in patterns:
                # By category
                category = pattern['business_category']
                if category not in stats['by_business_category']:
                    stats['by_business_category'][category] = 0
                stats['by_business_category'][category] += 1
                
                # By type
                pattern_type = pattern['type']
                if pattern_type not in stats['by_pattern_type']:
                    stats['by_pattern_type'][pattern_type] = 0
                stats['by_pattern_type'][pattern_type] += 1
                
                # Aggregates
                total_success += pattern['success_rate']
                stats['total_revenue_impact'] += pattern['total_revenue_impact']
                
                if pattern['success_rate'] >= 0.8 and pattern['occurrence_count'] >= 5:
                    stats['high_performing_patterns'] += 1
            
            stats['average_success_rate'] = total_success / len(patterns)
            
            return stats
            
        except Exception as e:
            logger.error(f"Network stats failed: {e}")
            return {}
    
    async def validate_patterns(self, days_back: int = 30) -> Dict[str, Any]:
        """Validate pattern accuracy by checking recent outcomes"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
            
            # Get recent tasks with network enhancement
            result = self.supabase.table('tasks').select('*').gte(
                'created_at', cutoff_date
            ).eq('network_enhanced', True).execute()
            
            network_tasks = result.data
            
            if not network_tasks:
                return {'validation_count': 0}
            
            # Calculate validation metrics
            completed_tasks = [t for t in network_tasks if t['status'] == 'completed']
            successful_tasks = [t for t in completed_tasks if t.get('outcome', {}).get('success')]
            
            validation_stats = {
                'validation_count': len(network_tasks),
                'completed_count': len(completed_tasks),
                'success_count': len(successful_tasks),
                'validation_rate': len(successful_tasks) / len(completed_tasks) if completed_tasks else 0,
                'average_predicted_success': np.mean([t['expected_success_rate'] for t in network_tasks if t.get('expected_success_rate')]) if network_tasks else 0,
                'actual_success_rate': len(successful_tasks) / len(completed_tasks) if completed_tasks else 0
            }
            
            return validation_stats
            
        except Exception as e:
            logger.error(f"Pattern validation failed: {e}")
            return {}
    
    async def _publish_network_learning(self, action: str, pattern_id: str):
        """Publish network learning event"""
        try:
            message = {
                'agent': self.name,
                'action': action,
                'pattern_id': pattern_id,
                'timestamp': datetime.now().isoformat()
            }
            
            await self.redis.publish('network_channel', json.dumps(message))
            
        except Exception as e:
            logger.error(f"Failed to publish network learning: {e}")
    
    async def _publish_status(self, status: str, entity: str, details: Any = None):
        """Publish agent status via Redis"""
        try:
            message = {
                'agent': self.name,
                'status': status,
                'entity': entity,
                'details': details,
                'timestamp': datetime.now().isoformat()
            }
            
            await self.redis.publish('agent_channel', json.dumps(message))
            
        except Exception as e:
            logger.error(f"Failed to publish status: {e}")

# Example usage and testing
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def test_network_learning():
        """Test NetworkLearningAgent functionality"""
        agent = NetworkLearningAgent(
            supabase_url=os.getenv('SUPABASE_URL'),
            supabase_key=os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
            redis_url=os.getenv('REDIS_URL'),
            openai_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Test pattern capture
        test_insight = {
            'type': 'churn_prevention',
            'customer_id': 'test_123',
            'dollar_impact': 1200.0,
            'confidence': 0.85,
            'details': {
                'last_visit_days_ago': 45,
                'typical_frequency': 'monthly',
                'risk_factors': ['long_gap', 'competitor_mention']
            },
            'action_script': 'Call Sarah to offer 20% discount on next visit'
        }
        
        test_outcome = PatternOutcome(
            success=True,
            revenue_impact=1200.0,
            customer_retained=True,
            implementation_difficulty=0.3,
            time_to_completion_days=2
        )
        
        # Capture pattern
        captured = await agent.capture_successful_pattern('test_account', test_insight, test_outcome)
        print(f"Pattern captured: {captured}")
        
        # Apply network knowledge
        new_insight = {
            'type': 'churn_prevention',
            'customer_id': 'new_123',
            'dollar_impact': 800.0,
            'confidence': 0.60,
            'details': {
                'last_visit_days_ago': 40,
                'typical_frequency': 'monthly'
            }
        }
        
        enhanced = await agent.apply_network_knowledge('test_account', new_insight)
        print(f"Enhanced insight confidence: {enhanced['confidence']:.2f}")
        print(f"Network enhanced: {enhanced.get('network_enhanced', False)}")
        
        # Get network stats
        stats = await agent.get_network_stats()
        print(f"Network stats: {stats}")
    
    # Run test
    asyncio.run(test_network_learning())