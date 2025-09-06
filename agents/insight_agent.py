"""
InsightAgent - Convert patterns into actionable tasks with dollar values

Responsibility: Transform analysis patterns into specific, actionable tasks with dollar values,
priority scoring, action scripts, and human context integration.

Author: Claude & Ray Hernandez
Created: 2024-09-06
"""

import logging
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import redis
from anthropic import Anthropic
from supabase import create_client, Client

from .base_agent import BaseAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2  
    HIGH = 3

@dataclass
class ActionableTask:
    """Structured task generated from insights"""
    title: str
    customer_name: str
    customer_id: str
    dollar_value: float
    priority: TaskPriority
    action_script: str
    expires_at: datetime
    insight_type: str
    confidence: float
    human_element: bool = False
    network_enhanced: bool = False
    expected_success_rate: Optional[float] = None

class InsightAgent(BaseAgent):
    """
    Convert patterns into actionable tasks with dollar values
    
    Key Features:
    - Convert insights to specific tasks
    - Calculate dollar impact and priority
    - Generate action scripts using Claude
    - Handle human context (health, personal issues)
    - Apply network learning enhancements
    - Task expiration management
    """
    
    def __init__(self, supabase_url: str, supabase_key: str, redis_url: str, 
                 anthropic_key: str):
        super().__init__("InsightAgent", supabase_url, supabase_key, redis_url)
        self.anthropic = Anthropic(api_key=anthropic_key)
        
    async def generate_tasks(self, insights: List[Dict[str, Any]]) -> List[ActionableTask]:
        """
        Convert insights to specific actionable tasks
        
        Process:
        1. Filter by confidence threshold (75%+)
        2. Calculate priority and dollar impact
        3. Generate action scripts using Claude
        4. Apply network learning enhancements
        5. Set expiration dates
        """
        try:
            await self._publish_status("analyzing", "insights", len(insights))
            
            tasks = []
            for insight in insights:
                # Skip low confidence insights
                if insight.get('confidence', 0) < 0.75:
                    continue
                    
                # Generate actionable task
                task = await self._create_task_from_insight(insight)
                if task:
                    tasks.append(task)
                    
            await self._publish_status("completed", "task_generation", len(tasks))
            
            # Store tasks in database
            await self._store_tasks(tasks)
            
            return tasks
            
        except Exception as e:
            logger.error(f"Task generation failed: {e}")
            await self._publish_status("failed", "task_generation", str(e))
            return []
    
    async def _create_task_from_insight(self, insight: Dict[str, Any]) -> Optional[ActionableTask]:
        """Create a specific actionable task from an insight"""
        try:
            # Calculate priority
            priority = self._calculate_priority(insight)
            
            # Generate action script using Claude
            action_script = await self._generate_action_script(insight)
            
            # Calculate expiration (7 days default, urgent tasks 3 days)
            days_to_expire = 3 if priority == TaskPriority.HIGH else 7
            expires_at = datetime.now() + timedelta(days=days_to_expire)
            
            # Create task
            task = ActionableTask(
                title=self._create_task_title(insight),
                customer_name=insight.get('customer_name', 'Unknown'),
                customer_id=insight.get('customer_id', ''),
                dollar_value=insight.get('dollar_impact', 0.0),
                priority=priority,
                action_script=action_script,
                expires_at=expires_at,
                insight_type=insight.get('type', 'unknown'),
                confidence=insight.get('confidence', 0.0),
                human_element=self._has_human_element(insight),
                network_enhanced=insight.get('network_enhanced', False),
                expected_success_rate=insight.get('expected_success_rate')
            )
            
            return task
            
        except Exception as e:
            logger.error(f"Failed to create task from insight: {e}")
            return None
    
    def _calculate_priority(self, insight: Dict[str, Any]) -> TaskPriority:
        """
        Score 1-3 based on impact and urgency
        
        Scoring factors:
        - Dollar impact (1 point per $1000)
        - Time sensitivity (weighted 2x)
        - Ease of execution (bonus)
        - Human element (1.5x multiplier)
        """
        score = 0
        
        # Dollar impact contribution (1 point per $1000)
        dollar_impact = insight.get('dollar_impact', 0)
        score += dollar_impact / 1000
        
        # Time sensitivity (weighted 2x)
        time_sensitivity = insight.get('time_sensitivity', 0)  # 0-1 scale
        score += time_sensitivity * 2
        
        # Ease of execution bonus
        ease = insight.get('ease_of_execution', 0)  # 0-1 scale
        score += ease
        
        # Human element multiplier (health, personal issues)
        if self._has_human_element(insight):
            score *= 1.5
            
        # Network learning confidence boost
        if insight.get('network_enhanced'):
            score *= 1.2
            
        # Convert to priority level
        if score >= 2.5:
            return TaskPriority.HIGH
        elif score >= 1.5:
            return TaskPriority.MEDIUM
        else:
            return TaskPriority.LOW
    
    async def _generate_action_script(self, insight: Dict[str, Any]) -> str:
        """Generate specific action script using Claude"""
        try:
            # Build context for script generation
            context = {
                'insight_type': insight.get('type'),
                'customer_name': insight.get('customer_name'),
                'dollar_impact': insight.get('dollar_impact'),
                'confidence': insight.get('confidence'),
                'pattern_details': insight.get('details', {}),
                'human_context': insight.get('human_context'),
                'network_context': insight.get('network_context')
            }
            
            # Create prompt for Claude
            prompt = self._build_script_prompt(context)
            
            # Generate script using Claude
            message = self.anthropic.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[{
                    "role": "user", 
                    "content": prompt
                }]
            )
            
            return message.content[0].text
            
        except Exception as e:
            logger.error(f"Script generation failed: {e}")
            return "Contact customer to discuss this opportunity."
    
    def _build_script_prompt(self, context: Dict[str, Any]) -> str:
        """Build Claude prompt for action script generation"""
        customer_name = context.get('customer_name', '[Customer]')
        insight_type = context.get('insight_type', 'general')
        dollar_impact = context.get('dollar_impact', 0)
        
        prompt = f"""
Generate a specific, actionable script for contacting {customer_name} about a {insight_type} opportunity worth ${dollar_impact:.0f}.

Context:
- Insight type: {insight_type}
- Dollar impact: ${dollar_impact:.0f}
- Confidence: {context.get('confidence', 0):.1%}
- Pattern details: {context.get('pattern_details', {})}

Requirements:
1. Personal, not generic
2. Specific action steps
3. Professional but warm tone
4. Include the dollar benefit
5. 2-3 sentences maximum
6. Ready to copy/paste

Human context: {context.get('human_context', 'None')}
Network learning: {context.get('network_context', 'None')}

Generate the script:
"""
        return prompt
    
    def _create_task_title(self, insight: Dict[str, Any]) -> str:
        """Create descriptive task title"""
        customer_name = insight.get('customer_name', 'Customer')
        insight_type = insight.get('type', 'opportunity')
        dollar_impact = insight.get('dollar_impact', 0)
        
        # Type-specific title templates
        if insight_type == 'churn_prevention':
            return f"Win back {customer_name} (${dollar_impact:.0f} at risk)"
        elif insight_type == 'modifier_opportunity':
            return f"Upsell {customer_name} on modifiers (+${dollar_impact:.0f})"
        elif insight_type == 'frequency_increase':
            return f"Increase {customer_name}'s visit frequency (+${dollar_impact:.0f})"
        elif insight_type == 'employee_coaching':
            return f"Coach staff on {customer_name} interactions (+${dollar_impact:.0f})"
        elif insight_type == 'review_response':
            return f"Respond to {customer_name}'s review (${dollar_impact:.0f} impact)"
        else:
            return f"Follow up with {customer_name} (${dollar_impact:.0f} opportunity)"
    
    def _has_human_element(self, insight: Dict[str, Any]) -> bool:
        """Detect if insight involves sensitive human context"""
        human_indicators = [
            'cancer', 'divorce', 'pregnancy', 'surgery', 'death', 'illness',
            'wedding', 'graduation', 'birthday', 'anniversary', 'family',
            'health', 'medical', 'personal', 'sensitive'
        ]
        
        # Check insight details and context
        details_text = json.dumps(insight.get('details', {})).lower()
        context_text = str(insight.get('human_context', '')).lower()
        
        for indicator in human_indicators:
            if indicator in details_text or indicator in context_text:
                return True
                
        return False
    
    async def _store_tasks(self, tasks: List[ActionableTask]) -> None:
        """Store generated tasks in Supabase"""
        try:
            # Convert tasks to database format
            task_records = []
            for task in tasks:
                record = {
                    'title': task.title,
                    'customer_name': task.customer_name,
                    'customer_id': task.customer_id,
                    'dollar_value': task.dollar_value,
                    'priority': task.priority.value,
                    'action_script': task.action_script,
                    'expires_at': task.expires_at.isoformat(),
                    'insight_type': task.insight_type,
                    'confidence': task.confidence,
                    'human_element': task.human_element,
                    'network_enhanced': task.network_enhanced,
                    'expected_success_rate': task.expected_success_rate,
                    'status': 'pending',
                    'created_at': datetime.now().isoformat()
                }
                task_records.append(record)
            
            # Batch insert tasks
            if task_records:
                result = self.supabase.table('tasks').insert(task_records).execute()
                logger.info(f"Stored {len(task_records)} tasks in database")
                
        except Exception as e:
            logger.error(f"Failed to store tasks: {e}")
    
    async def get_pending_tasks(self, account_id: str) -> List[Dict[str, Any]]:
        """Get all pending tasks for an account"""
        try:
            result = self.supabase.table('tasks').select('*').eq(
                'account_id', account_id
            ).eq('status', 'pending').order('priority', desc=True).execute()
            
            return result.data
            
        except Exception as e:
            logger.error(f"Failed to get pending tasks: {e}")
            return []
    
    async def complete_task(self, task_id: str, outcome: Dict[str, Any]) -> bool:
        """Mark task as completed and record outcome"""
        try:
            # Update task status
            result = self.supabase.table('tasks').update({
                'status': 'completed',
                'completed_at': datetime.now().isoformat(),
                'outcome': outcome
            }).eq('id', task_id).execute()
            
            # Publish completion for network learning
            await self.redis.publish('network_channel', json.dumps({
                'action': 'task_completed',
                'task_id': task_id,
                'outcome': outcome,
                'timestamp': datetime.now().isoformat()
            }))
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to complete task: {e}")
            return False
    
    async def expire_old_tasks(self) -> int:
        """Mark expired tasks as expired"""
        try:
            now = datetime.now().isoformat()
            
            result = self.supabase.table('tasks').update({
                'status': 'expired'
            }).lt('expires_at', now).eq('status', 'pending').execute()
            
            expired_count = len(result.data)
            if expired_count > 0:
                logger.info(f"Expired {expired_count} old tasks")
                
            return expired_count
            
        except Exception as e:
            logger.error(f"Failed to expire tasks: {e}")
            return 0
    
    async def get_task_metrics(self, account_id: str, days: int = 30) -> Dict[str, Any]:
        """Get task completion metrics"""
        try:
            # Calculate date range
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Get task counts by status
            result = self.supabase.table('tasks').select(
                'status, dollar_value, priority'
            ).eq('account_id', account_id).gte('created_at', start_date).execute()
            
            tasks = result.data
            
            # Calculate metrics
            metrics = {
                'total_tasks': len(tasks),
                'completed': len([t for t in tasks if t['status'] == 'completed']),
                'pending': len([t for t in tasks if t['status'] == 'pending']),
                'expired': len([t for t in tasks if t['status'] == 'expired']),
                'total_dollar_value': sum(t['dollar_value'] for t in tasks),
                'completed_dollar_value': sum(
                    t['dollar_value'] for t in tasks if t['status'] == 'completed'
                ),
                'high_priority': len([t for t in tasks if t['priority'] == 3]),
                'completion_rate': 0
            }
            
            # Calculate completion rate
            if metrics['total_tasks'] > 0:
                metrics['completion_rate'] = metrics['completed'] / metrics['total_tasks']
                
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get task metrics: {e}")
            return {}
    
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
    
    async def test_insight_agent():
        """Test InsightAgent functionality"""
        agent = InsightAgent(
            supabase_url=os.getenv('SUPABASE_URL'),
            supabase_key=os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
            redis_url=os.getenv('REDIS_URL'),
            anthropic_key=os.getenv('ANTHROPIC_API_KEY')
        )
        
        # Test insights
        test_insights = [
            {
                'type': 'churn_prevention',
                'customer_name': 'Sarah Johnson',
                'customer_id': 'cust_123',
                'dollar_impact': 2400.0,
                'confidence': 0.89,
                'time_sensitivity': 0.9,
                'ease_of_execution': 0.7,
                'details': {
                    'last_visit': '2024-08-01',
                    'typical_frequency': 'monthly',
                    'risk_factors': ['long_gap', 'price_sensitive']
                },
                'human_context': 'Recently went through divorce'
            },
            {
                'type': 'modifier_opportunity', 
                'customer_name': 'Jennifer Smith',
                'customer_id': 'cust_456',
                'dollar_impact': 480.0,
                'confidence': 0.82,
                'time_sensitivity': 0.3,
                'ease_of_execution': 0.9,
                'details': {
                    'never_adds_modifiers': True,
                    'high_base_service_value': True,
                    'employee_coaching_needed': 'Maria'
                }
            }
        ]
        
        # Generate tasks
        tasks = await agent.generate_tasks(test_insights)
        
        print(f"Generated {len(tasks)} actionable tasks:")
        for task in tasks:
            print(f"\n- {task.title}")
            print(f"  Priority: {task.priority.name}")
            print(f"  Value: ${task.dollar_value:.0f}")
            print(f"  Script: {task.action_script[:100]}...")
    
    # Run test
    asyncio.run(test_insight_agent())