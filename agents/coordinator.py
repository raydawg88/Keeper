"""
Agent Coordination System - Redis pub/sub for agent communication

Manages inter-agent communication, work coordination, and status tracking
for the 8-agent tournament system using Redis pub/sub messaging.

Author: Claude & Ray Hernandez
Created: 2024-09-06
"""

import logging
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum

import redis.asyncio as redis
from supabase import create_client, Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    IDLE = "idle"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

@dataclass
class AgentMessage:
    """Standard message format for inter-agent communication"""
    agent: str
    status: AgentStatus
    entity: str
    details: Any
    timestamp: datetime
    correlation_id: Optional[str] = None

@dataclass
class WorkflowState:
    """Tracks the state of a complete workflow execution"""
    account_id: str
    workflow_id: str
    agents_completed: List[str]
    agents_failed: List[str]
    agents_blocked: List[str]
    current_phase: str
    started_at: datetime
    completed_at: Optional[datetime] = None

class AgentCoordinator:
    """
    Coordinates the 8-agent tournament system using Redis pub/sub
    
    Features:
    - Agent status tracking and communication
    - Workflow orchestration and dependency management
    - Parallel execution coordination
    - Conflict resolution and locking
    - Performance monitoring and metrics
    - Error handling and recovery
    """
    
    def __init__(self, redis_url: str, supabase_url: str, supabase_key: str):
        self.redis = redis.from_url(redis_url)
        self.supabase = create_client(supabase_url, supabase_key)
        
        # Channel definitions
        self.AGENT_CHANNEL = 'agent_channel'
        self.NETWORK_CHANNEL = 'network_channel'
        self.WORKFLOW_CHANNEL = 'workflow_channel'
        
        # Agent registry
        self.agents = {
            'DataAgent': {'dependencies': [], 'parallel_safe': True},
            'MatchingAgent': {'dependencies': ['DataAgent'], 'parallel_safe': True},
            'ReviewAgent': {'dependencies': [], 'parallel_safe': True},
            'EmployeeAgent': {'dependencies': [], 'parallel_safe': True},
            'NetworkLearningAgent': {'dependencies': [], 'parallel_safe': True},
            'AnalysisAgent': {'dependencies': ['DataAgent', 'MatchingAgent'], 'parallel_safe': False},
            'InsightAgent': {'dependencies': ['AnalysisAgent'], 'parallel_safe': False},
            'ReportAgent': {'dependencies': ['InsightAgent'], 'parallel_safe': False}
        }
        
        # Active workflows
        self.workflows: Dict[str, WorkflowState] = {}
        
        # Message handlers
        self.handlers: Dict[str, List[Callable]] = {
            self.AGENT_CHANNEL: [],
            self.NETWORK_CHANNEL: [],
            self.WORKFLOW_CHANNEL: []
        }
        
    async def start_coordination(self):
        """Start the coordination system"""
        try:
            logger.info("🚀 Starting Agent Coordination System")
            
            # Start message listeners
            await asyncio.gather(
                self._listen_agent_channel(),
                self._listen_network_channel(),
                self._listen_workflow_channel(),
                self._monitor_workflows()
            )
            
        except Exception as e:
            logger.error(f"Coordination system failed: {e}")
    
    async def execute_workflow(self, account_id: str, workflow_type: str = "full_analysis") -> str:
        """
        Execute a complete agent workflow
        
        Workflow phases:
        1. Data Collection (DataAgent, ReviewAgent, EmployeeAgent in parallel)
        2. Analysis Preparation (MatchingAgent, NetworkLearningAgent in parallel)  
        3. Analysis Tournament (AnalysisAgent)
        4. Task Generation (InsightAgent)
        5. Report Generation (ReportAgent)
        """
        try:
            workflow_id = f"workflow_{account_id}_{int(datetime.now().timestamp())}"
            
            # Initialize workflow state
            workflow = WorkflowState(
                account_id=account_id,
                workflow_id=workflow_id,
                agents_completed=[],
                agents_failed=[],
                agents_blocked=[],
                current_phase="initialization",
                started_at=datetime.now()
            )
            
            self.workflows[workflow_id] = workflow
            
            # Publish workflow start
            await self._publish_workflow("workflow_started", workflow_id, {
                'account_id': account_id,
                'type': workflow_type
            })
            
            logger.info(f"🎯 Starting workflow {workflow_id} for account {account_id}")
            
            # Execute phases
            await self._execute_phase_1(workflow_id, account_id)  # Parallel data collection
            await self._execute_phase_2(workflow_id, account_id)  # Parallel analysis prep
            await self._execute_phase_3(workflow_id, account_id)  # Analysis tournament
            await self._execute_phase_4(workflow_id, account_id)  # Task generation
            await self._execute_phase_5(workflow_id, account_id)  # Report generation
            
            # Mark workflow complete
            workflow.completed_at = datetime.now()
            workflow.current_phase = "completed"
            
            await self._publish_workflow("workflow_completed", workflow_id, {
                'duration_seconds': (workflow.completed_at - workflow.started_at).total_seconds(),
                'agents_completed': workflow.agents_completed,
                'agents_failed': workflow.agents_failed
            })
            
            logger.info(f"✅ Workflow {workflow_id} completed successfully")
            
            return workflow_id
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            await self._publish_workflow("workflow_failed", workflow_id, {'error': str(e)})
            return ""
    
    async def _execute_phase_1(self, workflow_id: str, account_id: str):
        """Phase 1: Parallel data collection (DataAgent, ReviewAgent, EmployeeAgent)"""
        try:
            workflow = self.workflows[workflow_id]
            workflow.current_phase = "data_collection"
            
            logger.info(f"📊 Phase 1: Data Collection for {workflow_id}")
            
            # Execute agents in parallel
            tasks = [
                self._execute_agent("DataAgent", account_id, workflow_id),
                self._execute_agent("ReviewAgent", account_id, workflow_id),
                self._execute_agent("EmployeeAgent", account_id, workflow_id)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check results
            for i, result in enumerate(results):
                agent_name = ["DataAgent", "ReviewAgent", "EmployeeAgent"][i]
                if isinstance(result, Exception):
                    logger.error(f"❌ {agent_name} failed: {result}")
                    workflow.agents_failed.append(agent_name)
                else:
                    logger.info(f"✅ {agent_name} completed")
                    workflow.agents_completed.append(agent_name)
            
            # Check if critical agents failed
            if "DataAgent" in workflow.agents_failed:
                raise Exception("Critical agent DataAgent failed in Phase 1")
            
        except Exception as e:
            logger.error(f"Phase 1 failed: {e}")
            raise
    
    async def _execute_phase_2(self, workflow_id: str, account_id: str):
        """Phase 2: Parallel analysis preparation (MatchingAgent, NetworkLearningAgent)"""
        try:
            workflow = self.workflows[workflow_id]
            workflow.current_phase = "analysis_preparation"
            
            logger.info(f"🔄 Phase 2: Analysis Preparation for {workflow_id}")
            
            # Execute agents in parallel
            tasks = [
                self._execute_agent("MatchingAgent", account_id, workflow_id),
                self._execute_agent("NetworkLearningAgent", account_id, workflow_id)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check results
            for i, result in enumerate(results):
                agent_name = ["MatchingAgent", "NetworkLearningAgent"][i]
                if isinstance(result, Exception):
                    logger.error(f"❌ {agent_name} failed: {result}")
                    workflow.agents_failed.append(agent_name)
                else:
                    logger.info(f"✅ {agent_name} completed")
                    workflow.agents_completed.append(agent_name)
            
            # Check if critical agents failed
            if "MatchingAgent" in workflow.agents_failed:
                raise Exception("Critical agent MatchingAgent failed in Phase 2")
            
        except Exception as e:
            logger.error(f"Phase 2 failed: {e}")
            raise
    
    async def _execute_phase_3(self, workflow_id: str, account_id: str):
        """Phase 3: Analysis tournament (AnalysisAgent)"""
        try:
            workflow = self.workflows[workflow_id]
            workflow.current_phase = "analysis_tournament"
            
            logger.info(f"🏆 Phase 3: Analysis Tournament for {workflow_id}")
            
            result = await self._execute_agent("AnalysisAgent", account_id, workflow_id)
            
            if isinstance(result, Exception):
                logger.error(f"❌ AnalysisAgent failed: {result}")
                workflow.agents_failed.append("AnalysisAgent")
                raise Exception("Critical agent AnalysisAgent failed in Phase 3")
            else:
                logger.info(f"✅ AnalysisAgent completed")
                workflow.agents_completed.append("AnalysisAgent")
            
        except Exception as e:
            logger.error(f"Phase 3 failed: {e}")
            raise
    
    async def _execute_phase_4(self, workflow_id: str, account_id: str):
        """Phase 4: Task generation (InsightAgent)"""
        try:
            workflow = self.workflows[workflow_id]
            workflow.current_phase = "task_generation"
            
            logger.info(f"💡 Phase 4: Task Generation for {workflow_id}")
            
            result = await self._execute_agent("InsightAgent", account_id, workflow_id)
            
            if isinstance(result, Exception):
                logger.error(f"❌ InsightAgent failed: {result}")
                workflow.agents_failed.append("InsightAgent")
                raise Exception("Critical agent InsightAgent failed in Phase 4")
            else:
                logger.info(f"✅ InsightAgent completed")
                workflow.agents_completed.append("InsightAgent")
            
        except Exception as e:
            logger.error(f"Phase 4 failed: {e}")
            raise
    
    async def _execute_phase_5(self, workflow_id: str, account_id: str):
        """Phase 5: Report generation (ReportAgent)"""
        try:
            workflow = self.workflows[workflow_id]
            workflow.current_phase = "report_generation"
            
            logger.info(f"📋 Phase 5: Report Generation for {workflow_id}")
            
            result = await self._execute_agent("ReportAgent", account_id, workflow_id)
            
            if isinstance(result, Exception):
                logger.error(f"❌ ReportAgent failed: {result}")
                workflow.agents_failed.append("ReportAgent")
                # ReportAgent failure is not critical - workflow can complete
            else:
                logger.info(f"✅ ReportAgent completed")
                workflow.agents_completed.append("ReportAgent")
            
        except Exception as e:
            logger.error(f"Phase 5 failed: {e}")
            # Non-critical failure
    
    async def _execute_agent(self, agent_name: str, account_id: str, workflow_id: str) -> bool:
        """Execute a specific agent with proper coordination"""
        try:
            # Check for locks
            lock_key = f"agent_lock:{agent_name}:{account_id}"
            
            # Try to acquire lock
            lock_acquired = await self.redis.set(lock_key, workflow_id, nx=True, ex=300)  # 5 minute timeout
            
            if not lock_acquired:
                logger.warning(f"🔒 {agent_name} is locked by another workflow")
                return False
            
            try:
                # Publish agent start
                await self._publish_agent(agent_name, AgentStatus.ANALYZING, account_id, {
                    'workflow_id': workflow_id,
                    'phase': self.workflows[workflow_id].current_phase
                })
                
                # Import and execute the agent
                # This would import the actual agent class and call its main method
                # For now, simulate execution
                await asyncio.sleep(2)  # Simulate work
                
                # Publish agent completion
                await self._publish_agent(agent_name, AgentStatus.COMPLETED, account_id, {
                    'workflow_id': workflow_id,
                    'execution_time': 2.0
                })
                
                return True
                
            finally:
                # Release lock
                await self.redis.delete(lock_key)
            
        except Exception as e:
            # Publish agent failure
            await self._publish_agent(agent_name, AgentStatus.FAILED, account_id, {
                'workflow_id': workflow_id,
                'error': str(e)
            })
            
            raise e
    
    async def _listen_agent_channel(self):
        """Listen for agent status messages"""
        try:
            pubsub = self.redis.pubsub()
            await pubsub.subscribe(self.AGENT_CHANNEL)
            
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        await self._handle_agent_message(data)
                    except Exception as e:
                        logger.error(f"Agent message handling failed: {e}")
                        
        except Exception as e:
            logger.error(f"Agent channel listener failed: {e}")
    
    async def _listen_network_channel(self):
        """Listen for network learning events"""
        try:
            pubsub = self.redis.pubsub()
            await pubsub.subscribe(self.NETWORK_CHANNEL)
            
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        await self._handle_network_message(data)
                    except Exception as e:
                        logger.error(f"Network message handling failed: {e}")
                        
        except Exception as e:
            logger.error(f"Network channel listener failed: {e}")
    
    async def _listen_workflow_channel(self):
        """Listen for workflow coordination events"""
        try:
            pubsub = self.redis.pubsub()
            await pubsub.subscribe(self.WORKFLOW_CHANNEL)
            
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        await self._handle_workflow_message(data)
                    except Exception as e:
                        logger.error(f"Workflow message handling failed: {e}")
                        
        except Exception as e:
            logger.error(f"Workflow channel listener failed: {e}")
    
    async def _handle_agent_message(self, data: Dict[str, Any]):
        """Handle incoming agent status messages"""
        try:
            agent_name = data.get('agent')
            status = data.get('status')
            entity = data.get('entity')
            
            logger.info(f"📨 {agent_name}: {status} ({entity})")
            
            # Store agent status
            await self._store_agent_status(data)
            
            # Call registered handlers
            for handler in self.handlers[self.AGENT_CHANNEL]:
                try:
                    await handler(data)
                except Exception as e:
                    logger.error(f"Agent message handler failed: {e}")
                    
        except Exception as e:
            logger.error(f"Agent message processing failed: {e}")
    
    async def _handle_network_message(self, data: Dict[str, Any]):
        """Handle network learning events"""
        try:
            action = data.get('action')
            
            if action == 'pattern_learned':
                logger.info(f"🧠 New pattern learned: {data.get('pattern_id')}")
            elif action == 'pattern_applied':
                logger.info(f"🎯 Pattern applied: +{data.get('confidence_boost', 0):.1%} confidence")
            
            # Call registered handlers
            for handler in self.handlers[self.NETWORK_CHANNEL]:
                try:
                    await handler(data)
                except Exception as e:
                    logger.error(f"Network message handler failed: {e}")
                    
        except Exception as e:
            logger.error(f"Network message processing failed: {e}")
    
    async def _handle_workflow_message(self, data: Dict[str, Any]):
        """Handle workflow coordination events"""
        try:
            event_type = data.get('event_type')
            workflow_id = data.get('workflow_id')
            
            if event_type == 'workflow_started':
                logger.info(f"🚀 Workflow started: {workflow_id}")
            elif event_type == 'workflow_completed':
                logger.info(f"✅ Workflow completed: {workflow_id}")
                duration = data.get('details', {}).get('duration_seconds', 0)
                logger.info(f"   Duration: {duration:.1f}s")
            
            # Call registered handlers
            for handler in self.handlers[self.WORKFLOW_CHANNEL]:
                try:
                    await handler(data)
                except Exception as e:
                    logger.error(f"Workflow message handler failed: {e}")
                    
        except Exception as e:
            logger.error(f"Workflow message processing failed: {e}")
    
    async def _publish_agent(self, agent_name: str, status: AgentStatus, entity: str, details: Any):
        """Publish agent status message"""
        try:
            message = {
                'agent': agent_name,
                'status': status.value,
                'entity': entity,
                'details': details,
                'timestamp': datetime.now().isoformat()
            }
            
            await self.redis.publish(self.AGENT_CHANNEL, json.dumps(message))
            
        except Exception as e:
            logger.error(f"Agent message publishing failed: {e}")
    
    async def _publish_network(self, action: str, details: Dict[str, Any]):
        """Publish network learning event"""
        try:
            message = {
                'action': action,
                'details': details,
                'timestamp': datetime.now().isoformat()
            }
            
            await self.redis.publish(self.NETWORK_CHANNEL, json.dumps(message))
            
        except Exception as e:
            logger.error(f"Network message publishing failed: {e}")
    
    async def _publish_workflow(self, event_type: str, workflow_id: str, details: Dict[str, Any]):
        """Publish workflow event"""
        try:
            message = {
                'event_type': event_type,
                'workflow_id': workflow_id,
                'details': details,
                'timestamp': datetime.now().isoformat()
            }
            
            await self.redis.publish(self.WORKFLOW_CHANNEL, json.dumps(message))
            
        except Exception as e:
            logger.error(f"Workflow message publishing failed: {e}")
    
    async def _store_agent_status(self, status_data: Dict[str, Any]):
        """Store agent status in database for tracking"""
        try:
            self.supabase.table('agent_status').insert({
                'agent_name': status_data['agent'],
                'status': status_data['status'],
                'entity': status_data['entity'],
                'details': status_data['details'],
                'timestamp': status_data['timestamp']
            }).execute()
            
        except Exception as e:
            logger.error(f"Agent status storage failed: {e}")
    
    async def _monitor_workflows(self):
        """Monitor workflow health and performance"""
        try:
            while True:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Check for stalled workflows
                current_time = datetime.now()
                stalled_workflows = []
                
                for workflow_id, workflow in self.workflows.items():
                    if workflow.completed_at is None:
                        duration = (current_time - workflow.started_at).total_seconds()
                        if duration > 600:  # 10 minutes timeout
                            stalled_workflows.append(workflow_id)
                            logger.warning(f"⚠️ Workflow {workflow_id} stalled for {duration:.0f}s")
                
                # Cleanup old workflows
                old_workflows = [
                    wf_id for wf_id, workflow in self.workflows.items()
                    if workflow.completed_at and 
                    (current_time - workflow.completed_at).total_seconds() > 3600  # 1 hour
                ]
                
                for workflow_id in old_workflows:
                    del self.workflows[workflow_id]
                    
                if old_workflows:
                    logger.info(f"🧹 Cleaned up {len(old_workflows)} old workflows")
                    
        except Exception as e:
            logger.error(f"Workflow monitoring failed: {e}")
    
    def register_handler(self, channel: str, handler: Callable):
        """Register a message handler for a specific channel"""
        if channel in self.handlers:
            self.handlers[channel].append(handler)
            logger.info(f"📝 Registered handler for {channel}")
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a workflow"""
        if workflow_id in self.workflows:
            workflow = self.workflows[workflow_id]
            return {
                'workflow_id': workflow_id,
                'account_id': workflow.account_id,
                'current_phase': workflow.current_phase,
                'agents_completed': workflow.agents_completed,
                'agents_failed': workflow.agents_failed,
                'agents_blocked': workflow.agents_blocked,
                'started_at': workflow.started_at.isoformat(),
                'completed_at': workflow.completed_at.isoformat() if workflow.completed_at else None,
                'duration_seconds': (
                    (workflow.completed_at or datetime.now()) - workflow.started_at
                ).total_seconds()
            }
        return None
    
    async def cleanup(self):
        """Cleanup coordinator resources"""
        try:
            logger.info("🧹 Cleaning up coordinator resources")
            await self.redis.close()
            
        except Exception as e:
            logger.error(f"Coordinator cleanup failed: {e}")

# Example usage and testing
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def test_coordinator():
        """Test the coordination system"""
        coordinator = AgentCoordinator(
            redis_url=os.getenv('REDIS_URL'),
            supabase_url=os.getenv('SUPABASE_URL'),
            supabase_key=os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        )
        
        # Register test handlers
        async def agent_handler(data):
            print(f"Agent event: {data['agent']} -> {data['status']}")
        
        async def network_handler(data):
            print(f"Network event: {data['action']}")
        
        coordinator.register_handler(coordinator.AGENT_CHANNEL, agent_handler)
        coordinator.register_handler(coordinator.NETWORK_CHANNEL, network_handler)
        
        # Start a test workflow
        workflow_id = await coordinator.execute_workflow("test_account_123")
        print(f"Test workflow completed: {workflow_id}")
        
        # Get workflow status
        status = await coordinator.get_workflow_status(workflow_id)
        print(f"Workflow status: {status}")
        
        await coordinator.cleanup()
    
    # Run test
    asyncio.run(test_coordinator())