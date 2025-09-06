"""
EmployeeAgent - Staff Performance Tracking

Responsibility: Staff performance analysis and optimization recommendations
Success Metrics:
- Track revenue per hour for all staff
- Identify retention and performance issues
- Compare against team averages
- Generate actionable coaching recommendations

From agents-dropset.md specification
Comprehensive staff analysis for operational excellence
"""

import logging
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import redis
import os
from supabase import create_client, Client
from collections import defaultdict


class EmployeeAgent:
    def __init__(self):
        self.name = "EmployeeAgent"
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
        
        # Performance thresholds
        self.min_revenue_per_hour = 50    # Minimum acceptable RPH
        self.min_retention_rate = 0.65    # 65% client retention minimum
        self.min_modifier_rate = 0.15     # 15% modifier attach rate minimum
        self.min_tip_percentage = 0.18    # 18% average tip minimum
        self.max_cancellation_rate = 0.10 # 10% max cancellation rate
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.name)
    
    def analyze_employee_performance(self, account_id: str, employee_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Complete employee analysis for individual or all staff"""
        self.logger.info(f"Starting employee performance analysis for account {account_id}")
        
        try:
            # Publish agent status
            self._publish_agent_status('analyzing_employees', account_id)
            
            # Load employee and transaction data
            data = self._load_employee_data(account_id)
            if not data:
                raise ValueError("No employee data available for analysis")
            
            analyses = []
            
            if employee_id:
                # Analyze single employee
                analysis = self._analyze_single_employee(account_id, employee_id, data)
                if analysis:
                    analyses.append(analysis)
            else:
                # Analyze all employees
                employees = self._get_employees_from_data(data)
                for emp_id in employees:
                    analysis = self._analyze_single_employee(account_id, emp_id, data)
                    if analysis:
                        analyses.append(analysis)
            
            # Generate comparative insights
            if len(analyses) > 1:
                team_insights = self._generate_team_insights(analyses)
                analyses.extend(team_insights)
            
            # Store analysis results
            self._store_employee_analyses(account_id, analyses)
            
            self.logger.info(f"Employee analysis completed: {len(analyses)} insights generated")
            
            return analyses
            
        except Exception as e:
            self.logger.error(f"Employee analysis failed for account {account_id}: {str(e)}")
            raise
    
    def _analyze_single_employee(self, account_id: str, employee_id: str, data: Dict[str, pd.DataFrame]) -> Optional[Dict[str, Any]]:
        """Analyze performance metrics for a single employee"""
        try:
            # Calculate core performance metrics
            metrics = {
                'revenue_per_hour': self._calculate_rph(employee_id, data),
                'client_retention': self._retention_rate(employee_id, data),
                'modifier_attach': self._modifier_success(employee_id, data),
                'average_ticket': self._avg_transaction(employee_id, data),
                'tip_percentage': self._tip_analysis(employee_id, data),
                'cancellation_rate': self._cancellations(employee_id, data),
                'total_revenue': self._total_revenue(employee_id, data),
                'hours_worked': self._hours_worked(employee_id, data),
                'customer_count': self._customer_count(employee_id, data),
                'appointments_completed': self._appointments_completed(employee_id, data)
            }
            
            # Skip if insufficient data
            if metrics['appointments_completed'] < 5:
                return None
            
            # Compare to team average
            team_comparison = self._compare_to_team(employee_id, metrics, data)
            
            # Generate performance assessment
            performance_grade = self._grade_performance(metrics, team_comparison)
            
            # Create specific recommendations
            recommendations = self._generate_recommendations(employee_id, metrics, team_comparison)
            
            return {
                'employee_id': employee_id,
                'employee_name': self._get_employee_name(employee_id, data),
                'metrics': metrics,
                'team_comparison': team_comparison,
                'performance_grade': performance_grade,
                'recommendations': recommendations,
                'analysis_date': datetime.now().isoformat(),
                'account_id': account_id
            }
            
        except Exception as e:
            self.logger.error(f"Single employee analysis failed for {employee_id}: {str(e)}")
            return None
    
    def _calculate_rph(self, employee_id: str, data: Dict[str, pd.DataFrame]) -> float:
        """Calculate revenue per hour for employee"""
        try:
            transactions = data.get('transactions', pd.DataFrame())
            appointments = data.get('appointments', pd.DataFrame())
            
            # Get employee transactions
            emp_transactions = transactions[transactions.get('employee_id') == employee_id]
            emp_appointments = appointments[appointments.get('employee_id') == employee_id]
            
            if len(emp_transactions) == 0 or len(emp_appointments) == 0:
                return 0.0
            
            total_revenue = emp_transactions['amount'].sum()
            total_hours = emp_appointments['duration_minutes'].sum() / 60  # Convert to hours
            
            return round(total_revenue / total_hours, 2) if total_hours > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"RPH calculation failed for {employee_id}: {str(e)}")
            return 0.0
    
    def _retention_rate(self, employee_id: str, data: Dict[str, pd.DataFrame]) -> float:
        """Calculate client retention rate for employee"""
        try:
            transactions = data.get('transactions', pd.DataFrame())
            emp_transactions = transactions[transactions.get('employee_id') == employee_id]
            
            if len(emp_transactions) == 0:
                return 0.0
            
            # Group by customer to find repeat visits
            customer_visits = emp_transactions.groupby('customer_id').size()
            repeat_customers = (customer_visits > 1).sum()
            total_customers = len(customer_visits)
            
            return round(repeat_customers / total_customers, 3) if total_customers > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Retention rate calculation failed for {employee_id}: {str(e)}")
            return 0.0
    
    def _modifier_success(self, employee_id: str, data: Dict[str, pd.DataFrame]) -> float:
        """Calculate modifier attachment rate for employee"""
        try:
            transactions = data.get('transactions', pd.DataFrame())
            emp_transactions = transactions[transactions.get('employee_id') == employee_id]
            
            if len(emp_transactions) == 0:
                return 0.0
            
            # Count transactions with modifiers vs total
            transactions_with_modifiers = 0
            total_transactions = len(emp_transactions)
            
            for _, transaction in emp_transactions.iterrows():
                if transaction.get('square_data'):
                    try:
                        square_data = json.loads(transaction['square_data'])
                        line_items = square_data.get('line_items', [])
                        
                        has_modifier = any('modifier' in item.get('name', '').lower() 
                                         for item in line_items)
                        if has_modifier:
                            transactions_with_modifiers += 1
                    except (json.JSONDecodeError, KeyError):
                        continue
            
            return round(transactions_with_modifiers / total_transactions, 3) if total_transactions > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Modifier success calculation failed for {employee_id}: {str(e)}")
            return 0.0
    
    def _avg_transaction(self, employee_id: str, data: Dict[str, pd.DataFrame]) -> float:
        """Calculate average transaction value for employee"""
        try:
            transactions = data.get('transactions', pd.DataFrame())
            emp_transactions = transactions[transactions.get('employee_id') == employee_id]
            
            if len(emp_transactions) == 0:
                return 0.0
            
            return round(emp_transactions['amount'].mean(), 2)
            
        except Exception as e:
            self.logger.error(f"Average transaction calculation failed for {employee_id}: {str(e)}")
            return 0.0
    
    def _tip_analysis(self, employee_id: str, data: Dict[str, pd.DataFrame]) -> float:
        """Calculate average tip percentage for employee"""
        try:
            transactions = data.get('transactions', pd.DataFrame())
            emp_transactions = transactions[transactions.get('employee_id') == employee_id]
            
            if len(emp_transactions) == 0:
                return 0.0
            
            # Extract tip data from Square transaction data
            tips = []
            subtotals = []
            
            for _, transaction in emp_transactions.iterrows():
                if transaction.get('square_data'):
                    try:
                        square_data = json.loads(transaction['square_data'])
                        
                        # Get tip amount
                        tip_amount = 0
                        for tender in square_data.get('tenders', []):
                            tip_amount += tender.get('tip_money', {}).get('amount', 0) / 100  # Convert cents
                        
                        # Get subtotal
                        subtotal = square_data.get('total_money', {}).get('amount', 0) / 100 - tip_amount
                        
                        if subtotal > 0:
                            tips.append(tip_amount)
                            subtotals.append(subtotal)
                    except (json.JSONDecodeError, KeyError):
                        continue
            
            if not tips or not subtotals:
                return 0.0
            
            total_tips = sum(tips)
            total_subtotal = sum(subtotals)
            
            return round(total_tips / total_subtotal, 3) if total_subtotal > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Tip analysis failed for {employee_id}: {str(e)}")
            return 0.0
    
    def _cancellations(self, employee_id: str, data: Dict[str, pd.DataFrame]) -> float:
        """Calculate cancellation rate for employee"""
        try:
            appointments = data.get('appointments', pd.DataFrame())
            emp_appointments = appointments[appointments.get('employee_id') == employee_id]
            
            if len(emp_appointments) == 0:
                return 0.0
            
            cancelled = emp_appointments[emp_appointments.get('status') == 'CANCELLED']
            
            return round(len(cancelled) / len(emp_appointments), 3)
            
        except Exception as e:
            self.logger.error(f"Cancellation rate calculation failed for {employee_id}: {str(e)}")
            return 0.0
    
    def _total_revenue(self, employee_id: str, data: Dict[str, pd.DataFrame]) -> float:
        """Calculate total revenue generated by employee"""
        try:
            transactions = data.get('transactions', pd.DataFrame())
            emp_transactions = transactions[transactions.get('employee_id') == employee_id]
            
            return round(emp_transactions['amount'].sum(), 2) if len(emp_transactions) > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Total revenue calculation failed for {employee_id}: {str(e)}")
            return 0.0
    
    def _hours_worked(self, employee_id: str, data: Dict[str, pd.DataFrame]) -> float:
        """Calculate total hours worked by employee"""
        try:
            appointments = data.get('appointments', pd.DataFrame())
            emp_appointments = appointments[appointments.get('employee_id') == employee_id]
            
            if len(emp_appointments) == 0:
                return 0.0
            
            total_minutes = emp_appointments['duration_minutes'].sum()
            return round(total_minutes / 60, 1)  # Convert to hours
            
        except Exception as e:
            self.logger.error(f"Hours worked calculation failed for {employee_id}: {str(e)}")
            return 0.0
    
    def _customer_count(self, employee_id: str, data: Dict[str, pd.DataFrame]) -> int:
        """Calculate unique customer count for employee"""
        try:
            transactions = data.get('transactions', pd.DataFrame())
            emp_transactions = transactions[transactions.get('employee_id') == employee_id]
            
            return emp_transactions['customer_id'].nunique() if len(emp_transactions) > 0 else 0
            
        except Exception as e:
            self.logger.error(f"Customer count calculation failed for {employee_id}: {str(e)}")
            return 0
    
    def _appointments_completed(self, employee_id: str, data: Dict[str, pd.DataFrame]) -> int:
        """Calculate completed appointments count for employee"""
        try:
            appointments = data.get('appointments', pd.DataFrame())
            emp_appointments = appointments[appointments.get('employee_id') == employee_id]
            
            completed = emp_appointments[emp_appointments.get('status') != 'CANCELLED']
            return len(completed)
            
        except Exception as e:
            self.logger.error(f"Appointments completed calculation failed for {employee_id}: {str(e)}")
            return 0
    
    def _compare_to_team(self, employee_id: str, metrics: Dict[str, Any], data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Compare employee metrics to team averages"""
        try:
            # Get all employees
            employees = self._get_employees_from_data(data)
            
            # Calculate team averages (excluding current employee)
            other_employees = [emp for emp in employees if emp != employee_id]
            
            if not other_employees:
                return {'team_size': 1, 'position': 'only_employee'}
            
            team_metrics = {}
            for metric in ['revenue_per_hour', 'client_retention', 'modifier_attach', 
                          'average_ticket', 'tip_percentage', 'cancellation_rate']:
                
                values = []
                for emp in other_employees:
                    if metric == 'revenue_per_hour':
                        val = self._calculate_rph(emp, data)
                    elif metric == 'client_retention':
                        val = self._retention_rate(emp, data)
                    elif metric == 'modifier_attach':
                        val = self._modifier_success(emp, data)
                    elif metric == 'average_ticket':
                        val = self._avg_transaction(emp, data)
                    elif metric == 'tip_percentage':
                        val = self._tip_analysis(emp, data)
                    elif metric == 'cancellation_rate':
                        val = self._cancellations(emp, data)
                    else:
                        continue
                    
                    if val > 0:  # Only include non-zero values
                        values.append(val)
                
                if values:
                    team_metrics[f'team_avg_{metric}'] = np.mean(values)
                    team_metrics[f'vs_team_{metric}'] = (metrics[metric] - np.mean(values)) / np.mean(values) if np.mean(values) > 0 else 0
                else:
                    team_metrics[f'team_avg_{metric}'] = 0
                    team_metrics[f'vs_team_{metric}'] = 0
            
            team_metrics['team_size'] = len(employees)
            
            return team_metrics
            
        except Exception as e:
            self.logger.error(f"Team comparison failed for {employee_id}: {str(e)}")
            return {'team_size': 1, 'error': 'comparison_failed'}
    
    def _grade_performance(self, metrics: Dict[str, Any], team_comparison: Dict[str, Any]) -> Dict[str, Any]:
        """Grade employee performance across key metrics"""
        try:
            grades = {}
            overall_score = 0
            
            # Grade each metric
            grade_weights = {
                'revenue_per_hour': 0.25,
                'client_retention': 0.20,
                'modifier_attach': 0.15,
                'average_ticket': 0.15,
                'tip_percentage': 0.15,
                'cancellation_rate': 0.10
            }
            
            for metric, weight in grade_weights.items():
                if metric == 'cancellation_rate':
                    # Lower is better for cancellation rate
                    if metrics[metric] <= self.max_cancellation_rate * 0.5:
                        grade = 'A'
                        score = 4.0
                    elif metrics[metric] <= self.max_cancellation_rate * 0.75:
                        grade = 'B'
                        score = 3.0
                    elif metrics[metric] <= self.max_cancellation_rate:
                        grade = 'C'
                        score = 2.0
                    else:
                        grade = 'D'
                        score = 1.0
                else:
                    # Higher is better for other metrics
                    vs_team = team_comparison.get(f'vs_team_{metric}', 0)
                    
                    if vs_team > 0.25:  # 25% above team average
                        grade = 'A'
                        score = 4.0
                    elif vs_team > 0.1:  # 10% above team average
                        grade = 'B'
                        score = 3.0
                    elif vs_team > -0.1:  # Within 10% of team average
                        grade = 'C'
                        score = 2.0
                    else:  # Below team average
                        grade = 'D'
                        score = 1.0
                
                grades[metric] = grade
                overall_score += score * weight
            
            # Convert overall score to letter grade
            if overall_score >= 3.5:
                overall_grade = 'A'
            elif overall_score >= 2.5:
                overall_grade = 'B'
            elif overall_score >= 1.5:
                overall_grade = 'C'
            else:
                overall_grade = 'D'
            
            return {
                'individual_grades': grades,
                'overall_score': round(overall_score, 2),
                'overall_grade': overall_grade
            }
            
        except Exception as e:
            self.logger.error(f"Performance grading failed: {str(e)}")
            return {'overall_grade': 'Unknown', 'error': 'grading_failed'}
    
    def _generate_recommendations(self, employee_id: str, metrics: Dict[str, Any], team_comparison: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific performance improvement recommendations"""
        recommendations = []
        
        try:
            # Revenue per hour recommendations
            if metrics['revenue_per_hour'] < self.min_revenue_per_hour:
                recommendations.append({
                    'category': 'revenue_optimization',
                    'priority': 'high',
                    'issue': f"Revenue per hour (${metrics['revenue_per_hour']:.2f}) below minimum (${self.min_revenue_per_hour})",
                    'recommendation': 'Focus on upselling premium services and improving service efficiency',
                    'action_items': [
                        'Review service menu and pricing strategy',
                        'Train on consultative selling techniques',
                        'Track time per service and identify bottlenecks'
                    ]
                })
            
            # Client retention recommendations
            if metrics['client_retention'] < self.min_retention_rate:
                recommendations.append({
                    'category': 'client_retention',
                    'priority': 'high',
                    'issue': f"Client retention ({metrics['client_retention']:.1%}) below minimum ({self.min_retention_rate:.1%})",
                    'recommendation': 'Improve client experience and follow-up processes',
                    'action_items': [
                        'Review recent client feedback and complaints',
                        'Implement post-service follow-up calls',
                        'Shadow high-retention team members',
                        'Focus on building personal relationships with clients'
                    ]
                })
            
            # Modifier attachment recommendations
            if metrics['modifier_attach'] < self.min_modifier_rate:
                recommendations.append({
                    'category': 'upselling',
                    'priority': 'medium',
                    'issue': f"Modifier attachment rate ({metrics['modifier_attach']:.1%}) below minimum ({self.min_modifier_rate:.1%})",
                    'recommendation': 'Improve upselling skills and product knowledge',
                    'action_items': [
                        'Practice consultative selling techniques',
                        'Learn about all available add-on services',
                        'Role-play upselling scenarios',
                        'Track successful upselling strategies from team'
                    ]
                })
            
            # Tip percentage recommendations
            if metrics['tip_percentage'] < self.min_tip_percentage:
                recommendations.append({
                    'category': 'service_quality',
                    'priority': 'medium',
                    'issue': f"Average tip percentage ({metrics['tip_percentage']:.1%}) below minimum ({self.min_tip_percentage:.1%})",
                    'recommendation': 'Enhance client service experience and relationship building',
                    'action_items': [
                        'Focus on exceptional customer service',
                        'Improve communication and listening skills',
                        'Create memorable client experiences',
                        'Ask for feedback to understand client preferences'
                    ]
                })
            
            # Cancellation rate recommendations
            if metrics['cancellation_rate'] > self.max_cancellation_rate:
                recommendations.append({
                    'category': 'scheduling_efficiency',
                    'priority': 'high',
                    'issue': f"Cancellation rate ({metrics['cancellation_rate']:.1%}) above maximum ({self.max_cancellation_rate:.1%})",
                    'recommendation': 'Improve scheduling practices and client communication',
                    'action_items': [
                        'Send appointment reminders 24-48 hours in advance',
                        'Confirm appointments day-of',
                        'Be flexible with rescheduling requests',
                        'Analyze cancellation patterns to identify issues'
                    ]
                })
            
            # Team comparison insights
            worst_metric = None
            worst_performance = 0
            
            for metric in ['revenue_per_hour', 'client_retention', 'modifier_attach', 'average_ticket', 'tip_percentage']:
                vs_team = team_comparison.get(f'vs_team_{metric}', 0)
                if vs_team < worst_performance:
                    worst_performance = vs_team
                    worst_metric = metric
            
            if worst_metric and worst_performance < -0.2:  # 20% below team average
                recommendations.append({
                    'category': 'peer_learning',
                    'priority': 'high',
                    'issue': f"Significantly underperforming team average in {worst_metric.replace('_', ' ')}",
                    'recommendation': 'Partner with top-performing team member for mentoring',
                    'action_items': [
                        f'Shadow top performer in {worst_metric.replace("_", " ")}',
                        'Schedule weekly coaching sessions with manager',
                        'Set specific improvement goals with timeline',
                        'Review successful strategies from top performers'
                    ]
                })
            
            # If no issues found, provide positive reinforcement
            if not recommendations:
                recommendations.append({
                    'category': 'positive_reinforcement',
                    'priority': 'low',
                    'issue': 'No significant performance issues identified',
                    'recommendation': 'Continue excellent work and consider mentoring opportunities',
                    'action_items': [
                        'Maintain current performance standards',
                        'Consider mentoring newer team members',
                        'Explore advanced training opportunities',
                        'Share successful strategies with team'
                    ]
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Recommendation generation failed for {employee_id}: {str(e)}")
            return [{
                'category': 'error',
                'priority': 'low',
                'issue': 'Unable to generate specific recommendations',
                'recommendation': 'Manual review recommended'
            }]
    
    def _generate_team_insights(self, analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate team-level insights and comparisons"""
        team_insights = []
        
        try:
            if len(analyses) < 2:
                return team_insights
            
            # Find top and bottom performers
            by_rph = sorted(analyses, key=lambda x: x['metrics']['revenue_per_hour'], reverse=True)
            by_retention = sorted(analyses, key=lambda x: x['metrics']['client_retention'], reverse=True)
            by_modifiers = sorted(analyses, key=lambda x: x['metrics']['modifier_attach'], reverse=True)
            
            top_rph = by_rph[0]
            bottom_rph = by_rph[-1]
            
            # Revenue gap analysis
            rph_gap = top_rph['metrics']['revenue_per_hour'] - bottom_rph['metrics']['revenue_per_hour']
            if rph_gap > 20:  # Significant gap
                team_insights.append({
                    'type': 'team_revenue_gap',
                    'title': f"Revenue Per Hour Gap: ${rph_gap:.2f}",
                    'description': f"{top_rph['employee_name']} generates ${rph_gap:.2f}/hour more than {bottom_rph['employee_name']}. Cross-training opportunity.",
                    'priority': 'high',
                    'top_performer': top_rph['employee_name'],
                    'improvement_candidate': bottom_rph['employee_name'],
                    'potential_revenue_gain': rph_gap * bottom_rph['metrics']['hours_worked'],
                    'recommendations': [
                        f"Have {top_rph['employee_name']} mentor {bottom_rph['employee_name']}",
                        "Analyze service delivery differences",
                        "Implement best practices sharing sessions"
                    ]
                })
            
            # Retention leader insights
            retention_leader = by_retention[0]
            if retention_leader['metrics']['client_retention'] > 0.8:  # High retention
                team_insights.append({
                    'type': 'retention_excellence',
                    'title': f"Retention Leader: {retention_leader['employee_name']}",
                    'description': f"{retention_leader['employee_name']} maintains {retention_leader['metrics']['client_retention']:.1%} client retention. Model for team.",
                    'priority': 'medium',
                    'exemplar': retention_leader['employee_name'],
                    'retention_rate': retention_leader['metrics']['client_retention'],
                    'recommendations': [
                        f"Document {retention_leader['employee_name']}'s client relationship strategies",
                        "Create retention training based on their methods",
                        "Have them share best practices in team meetings"
                    ]
                })
            
            # Modifier champion insights
            modifier_champion = by_modifiers[0]
            if modifier_champion['metrics']['modifier_attach'] > 0.25:  # High attachment rate
                team_insights.append({
                    'type': 'upselling_champion',
                    'title': f"Upselling Champion: {modifier_champion['employee_name']}",
                    'description': f"{modifier_champion['employee_name']} achieves {modifier_champion['metrics']['modifier_attach']:.1%} modifier attachment rate.",
                    'priority': 'medium',
                    'champion': modifier_champion['employee_name'],
                    'modifier_rate': modifier_champion['metrics']['modifier_attach'],
                    'recommendations': [
                        f"Record {modifier_champion['employee_name']}'s upselling conversations",
                        "Create upselling script templates",
                        "Implement team upselling challenges"
                    ]
                })
            
            return team_insights
            
        except Exception as e:
            self.logger.error(f"Team insights generation failed: {str(e)}")
            return []
    
    def _load_employee_data(self, account_id: str) -> Dict[str, pd.DataFrame]:
        """Load employee-related data for analysis"""
        data = {}
        
        try:
            # Load transactions with employee data
            transactions_result = self.supabase.table('transactions').select('*').eq('account_id', account_id).execute()
            if transactions_result.data:
                data['transactions'] = pd.DataFrame(transactions_result.data)
            
            # Load appointments with employee data
            appointments_result = self.supabase.table('appointments').select('*').eq('account_id', account_id).execute()
            if appointments_result.data:
                data['appointments'] = pd.DataFrame(appointments_result.data)
            
            # Load customer data for relationship analysis
            customers_result = self.supabase.table('customers').select('*').eq('account_id', account_id).execute()
            if customers_result.data:
                data['customers'] = pd.DataFrame(customers_result.data)
            
            self.logger.info(f"Loaded employee data for account {account_id}: "
                           f"{len(data.get('transactions', []))} transactions, "
                           f"{len(data.get('appointments', []))} appointments, "
                           f"{len(data.get('customers', []))} customers")
            
        except Exception as e:
            self.logger.error(f"Error loading employee data: {str(e)}")
        
        return data
    
    def _get_employees_from_data(self, data: Dict[str, pd.DataFrame]) -> List[str]:
        """Extract unique employee IDs from transaction/appointment data"""
        try:
            employees = set()
            
            if 'transactions' in data and not data['transactions'].empty:
                emp_ids = data['transactions']['employee_id'].dropna().unique()
                employees.update(emp_ids)
            
            if 'appointments' in data and not data['appointments'].empty:
                emp_ids = data['appointments']['employee_id'].dropna().unique()
                employees.update(emp_ids)
            
            # Filter out 'unknown' or invalid IDs
            valid_employees = [emp for emp in employees if emp != 'unknown' and emp]
            
            return list(valid_employees)
            
        except Exception as e:
            self.logger.error(f"Error extracting employee IDs: {str(e)}")
            return []
    
    def _get_employee_name(self, employee_id: str, data: Dict[str, pd.DataFrame]) -> str:
        """Get employee name from ID (placeholder - would integrate with employee management system)"""
        # In real implementation, would look up from employee table
        # For now, return formatted ID
        return f"Employee_{employee_id[-4:]}" if len(employee_id) > 4 else f"Employee_{employee_id}"
    
    def _store_employee_analyses(self, account_id: str, analyses: List[Dict[str, Any]]):
        """Store employee analysis results in database"""
        try:
            for analysis in analyses:
                analysis_record = {
                    'account_id': account_id,
                    'employee_id': analysis.get('employee_id'),
                    'analysis_type': 'performance_review',
                    'metrics': json.dumps(analysis.get('metrics', {})),
                    'team_comparison': json.dumps(analysis.get('team_comparison', {})),
                    'performance_grade': json.dumps(analysis.get('performance_grade', {})),
                    'recommendations': json.dumps(analysis.get('recommendations', [])),
                    'analysis_date': analysis.get('analysis_date'),
                    'created_at': datetime.now().isoformat()
                }
                
                # Store in agent_logs table (or create employee_analyses table)
                self.supabase.table('agent_logs').insert({
                    'account_id': account_id,
                    'agent_name': self.name,
                    'action_type': 'employee_analysis',
                    'entity_type': 'employee',
                    'entity_id': analysis.get('employee_id'),
                    'decision': analysis_record,
                    'confidence': analysis.get('performance_grade', {}).get('overall_score', 0) / 4.0,  # Convert to 0-1 scale
                    'created_at': datetime.now().isoformat()
                }).execute()
                
            self.logger.info(f"Stored {len(analyses)} employee analyses for account {account_id}")
            
        except Exception as e:
            self.logger.error(f"Error storing employee analyses: {str(e)}")
    
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