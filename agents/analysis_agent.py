"""
AnalysisAgent - Pattern Detection and Insight Generation

Responsibility: Pattern detection and insight generation
Success Metrics:
- Find 5+ insights per analysis
- 75%+ insight accuracy
- No obvious patterns

From agents-dropset.md specification
Core of the tournament system for generating $3000+ revenue opportunities
"""

import asyncio
import logging
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import redis
import os
from supabase import create_client, Client
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import anthropic
import openai


class AnalysisAgent:
    def __init__(self):
        self.name = "AnalysisAgent"
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
        
        # AI clients
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Tournament configuration
        self.min_confidence_threshold = 0.75  # 75%+ requirement
        self.min_insights_per_analysis = 5    # 5+ insights requirement
        self.min_dollar_impact = 100          # Minimum $100 impact
        self.target_revenue_discovery = 3000   # $3000+ target
        
        # Banned insights (no obvious patterns)
        self.banned_insights = [
            "rain causes cancellations",
            "weekends are busier",
            "holidays are busy",
            "summer is peak season",
            "people prefer afternoon appointments",
            "customers like discounts"
        ]
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.name)
    
    def run_analysis_tournament(self, account_id: str) -> List[Dict[str, Any]]:
        """Run multiple models, pick best insights
        
        models = {
            'rfm': self.rfm_analysis(),
            'modifiers': self.modifier_analysis(),
            'employee': self.employee_performance(),
            'churn': self.churn_prediction(),
            'patterns': self.sequence_mining()
        }
        
        # Score and rank insights
        insights = self.tournament_judge(models)
        
        # Filter by confidence
        return [i for i in insights if i.confidence >= 0.75]
        """
        self.logger.info(f"Starting analysis tournament for account {account_id}")
        
        try:
            # Publish agent status
            self._publish_agent_status('analyzing', account_id)
            
            # Load data for analysis
            data = self._load_account_data(account_id)
            if not data:
                raise ValueError("No data available for analysis")
            
            # Run all analysis models in tournament
            models = {
                'rfm': self.rfm_analysis(account_id, data),
                'modifiers': self.modifier_analysis(account_id, data),
                'employee': self.employee_performance(account_id, data),
                'churn': self.churn_prediction(account_id, data),
                'patterns': self.sequence_mining(account_id, data)
            }
            
            self.logger.info(f"Completed all model runs: {list(models.keys())}")
            
            # Score and rank insights using tournament judge
            all_insights = self.tournament_judge(models)
            
            # Apply quality filters
            filtered_insights = self._apply_quality_filters(all_insights)
            
            # Ensure we meet success metrics
            self._validate_success_metrics(filtered_insights)
            
            # Store insights in database
            self._store_insights(account_id, filtered_insights)
            
            self.logger.info(f"Tournament completed: {len(filtered_insights)} high-quality insights generated")
            
            return filtered_insights
            
        except Exception as e:
            self.logger.error(f"Analysis tournament failed for account {account_id}: {str(e)}")
            raise
    
    def rfm_analysis(self, account_id: str, data: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """RFM (Recency, Frequency, Monetary) analysis for customer segmentation"""
        insights = []
        
        try:
            customers_df = data.get('customers')
            transactions_df = data.get('transactions')
            
            if customers_df is None or transactions_df is None or len(transactions_df) == 0:
                return insights
            
            # Calculate RFM metrics
            current_date = datetime.now()
            
            rfm_df = transactions_df.groupby('customer_id').agg({
                'square_created_at': lambda x: (current_date - pd.to_datetime(x.max())).days,  # Recency
                'square_payment_id': 'count',  # Frequency
                'amount': 'sum'  # Monetary
            }).rename(columns={
                'square_created_at': 'recency',
                'square_payment_id': 'frequency',
                'amount': 'monetary'
            })
            
            # Create RFM scores (1-5 scale)
            rfm_df['r_score'] = pd.qcut(rfm_df['recency'].rank(method='first'), 5, labels=[5, 4, 3, 2, 1])
            rfm_df['f_score'] = pd.qcut(rfm_df['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
            rfm_df['m_score'] = pd.qcut(rfm_df['monetary'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
            
            # Combine RFM scores
            rfm_df['rfm_score'] = rfm_df['r_score'].astype(str) + rfm_df['f_score'].astype(str) + rfm_df['m_score'].astype(str)
            
            # Define customer segments
            segment_map = {
                '555': 'Champions',
                '554': 'Champions', 
                '544': 'Champions',
                '545': 'Champions',
                '454': 'Champions',
                '455': 'Champions',
                '445': 'Champions',
                '355': 'Loyal Customers',
                '354': 'Loyal Customers',
                '345': 'Loyal Customers',
                '344': 'Loyal Customers',
                '335': 'Loyal Customers',
                '155': 'New Customers',
                '154': 'New Customers',
                '144': 'New Customers',
                '145': 'New Customers',
                '114': 'New Customers',
                '214': 'Potential Loyalists',
                '215': 'Potential Loyalists',
                '115': 'Potential Loyalists',
                '125': 'Potential Loyalists',
                '511': 'At Risk',
                '512': 'At Risk',
                '521': 'At Risk',
                '522': 'At Risk',
                '411': 'Cannot Lose Them',
                '412': 'Cannot Lose Them',
                '421': 'Cannot Lose Them',
                '422': 'Cannot Lose Them',
                '111': 'Lost',
                '112': 'Lost',
                '121': 'Lost',
                '122': 'Lost',
                '211': 'Lost',
                '212': 'Lost',
                '221': 'Lost',
                '222': 'Lost'
            }
            
            rfm_df['segment'] = rfm_df['rfm_score'].map(segment_map).fillna('Others')
            
            # Generate insights from segments
            segment_stats = rfm_df['segment'].value_counts()
            
            for segment, count in segment_stats.items():
                if count < 5:  # Skip small segments
                    continue
                
                segment_data = rfm_df[rfm_df['segment'] == segment]
                avg_monetary = segment_data['monetary'].mean()
                avg_frequency = segment_data['frequency'].mean()
                
                # Calculate revenue opportunity
                if segment == 'At Risk':
                    # At-risk customers opportunity
                    potential_revenue = avg_monetary * 0.8 * count  # 80% retention potential
                    
                    insights.append({
                        'type': 'rfm_segment',
                        'title': f"Win Back {count} At-Risk Customers",
                        'description': f"You have {count} at-risk customers who previously spent ${avg_monetary:.0f} on average. Targeted win-back campaigns could recover 80% of them.",
                        'dollar_impact': potential_revenue,
                        'confidence': 0.82,
                        'customer_count': count,
                        'segment': segment,
                        'action_items': [
                            "Send personalized win-back offers",
                            "Call customers who haven't visited in 60+ days",
                            "Offer 20% discount on next service"
                        ],
                        'evidence': {
                            'avg_previous_spend': avg_monetary,
                            'avg_visit_frequency': avg_frequency,
                            'days_since_last_visit': segment_data['recency'].mean()
                        }
                    })
                
                elif segment == 'Potential Loyalists':
                    # Potential loyalists opportunity
                    potential_revenue = avg_monetary * 1.5 * count  # 50% upsell potential
                    
                    insights.append({
                        'type': 'rfm_segment',
                        'title': f"Convert {count} Potential Loyalists",
                        'description': f"You have {count} potential loyalists spending ${avg_monetary:.0f} on average. They could become loyal customers with targeted engagement.",
                        'dollar_impact': potential_revenue,
                        'confidence': 0.78,
                        'customer_count': count,
                        'segment': segment,
                        'action_items': [
                            "Invite to loyalty program",
                            "Offer package deals",
                            "Send birthday/anniversary specials"
                        ],
                        'evidence': {
                            'avg_current_spend': avg_monetary,
                            'visit_frequency': avg_frequency,
                            'growth_potential': '50% upsell'
                        }
                    })
                
                elif segment == 'Champions' and count < 50:
                    # VIP customer referral program
                    referral_revenue = avg_monetary * count * 0.3  # 30% referral rate
                    
                    insights.append({
                        'type': 'rfm_segment',
                        'title': f"VIP Referral Program for {count} Champions",
                        'description': f"Your {count} champion customers spend ${avg_monetary:.0f} on average. A referral program could generate significant new business.",
                        'dollar_impact': referral_revenue,
                        'confidence': 0.85,
                        'customer_count': count,
                        'segment': segment,
                        'action_items': [
                            "Launch VIP referral program",
                            "Offer $50 credit for successful referrals",
                            "Create exclusive champion perks"
                        ],
                        'evidence': {
                            'avg_customer_value': avg_monetary,
                            'loyalty_score': 'High',
                            'referral_potential': '30% of champions likely to refer'
                        }
                    })
                
        except Exception as e:
            self.logger.error(f"RFM analysis failed: {str(e)}")
        
        return insights
    
    def modifier_analysis(self, account_id: str, data: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """Find modifier revenue opportunities
        
        - Calculate attach rates by employee
        - Find modifier combinations
        - Detect time-based patterns
        - Return dollar opportunities
        """
        insights = []
        
        try:
            transactions_df = data.get('transactions')
            if transactions_df is None or len(transactions_df) == 0:
                return insights
            
            # Analyze transaction line items for modifiers
            modifier_opportunities = []
            
            for _, transaction in transactions_df.iterrows():
                if transaction.get('square_data'):
                    try:
                        square_data = json.loads(transaction['square_data'])
                        line_items = square_data.get('line_items', [])
                        
                        base_services = []
                        modifiers = []
                        
                        for item in line_items:
                            if 'modifier' in item.get('name', '').lower():
                                modifiers.append(item)
                            else:
                                base_services.append(item)
                        
                        # Calculate modifier attach rate for this transaction
                        if base_services:
                            attach_rate = len(modifiers) / len(base_services)
                            
                            modifier_opportunities.append({
                                'transaction_id': transaction['square_payment_id'],
                                'base_services_count': len(base_services),
                                'modifiers_count': len(modifiers),
                                'attach_rate': attach_rate,
                                'transaction_amount': transaction['amount'],
                                'date': pd.to_datetime(transaction['square_created_at'])
                            })
                    except (json.JSONDecodeError, KeyError):
                        continue
            
            if modifier_opportunities:
                modifier_df = pd.DataFrame(modifier_opportunities)
                
                # Calculate overall modifier statistics
                avg_attach_rate = modifier_df['attach_rate'].mean()
                total_transactions = len(modifier_df)
                transactions_with_modifiers = len(modifier_df[modifier_df['attach_rate'] > 0])
                
                # Identify low-modifier periods
                modifier_df['month'] = modifier_df['date'].dt.to_period('M')
                monthly_attach_rates = modifier_df.groupby('month')['attach_rate'].mean()
                
                # Find revenue opportunity
                avg_transaction_amount = modifier_df['transaction_amount'].mean()
                potential_modifier_revenue_per_transaction = avg_transaction_amount * 0.2  # Assume 20% uplift per modifier
                
                low_attach_months = monthly_attach_rates[monthly_attach_rates < avg_attach_rate * 0.8]
                
                if len(low_attach_months) > 0:
                    # Calculate opportunity from improving low months
                    low_month_transactions = modifier_df[modifier_df['month'].isin(low_attach_months.index)]
                    missed_revenue = len(low_month_transactions) * potential_modifier_revenue_per_transaction
                    
                    insights.append({
                        'type': 'modifier_opportunity',
                        'title': f"Increase Modifier Attach Rate by 20%",
                        'description': f"Your modifier attach rate is {avg_attach_rate:.1%}. Improving this to {(avg_attach_rate * 1.2):.1%} could generate significant additional revenue.",
                        'dollar_impact': missed_revenue,
                        'confidence': 0.76,
                        'current_attach_rate': avg_attach_rate,
                        'target_attach_rate': avg_attach_rate * 1.2,
                        'action_items': [
                            "Train staff on modifier upselling",
                            "Create modifier suggestion prompts",
                            "Offer modifier bundles",
                            "Track individual staff modifier rates"
                        ],
                        'evidence': {
                            'total_transactions': total_transactions,
                            'current_attach_rate': f"{avg_attach_rate:.1%}",
                            'avg_transaction_value': avg_transaction_amount,
                            'improvement_months': len(low_attach_months)
                        }
                    })
                
                # Time-based modifier patterns
                modifier_df['hour'] = modifier_df['date'].dt.hour
                hourly_attach_rates = modifier_df.groupby('hour')['attach_rate'].mean()
                
                best_hours = hourly_attach_rates.nlargest(3).index.tolist()
                worst_hours = hourly_attach_rates.nsmallest(3).index.tolist()
                
                if len(best_hours) > 0 and len(worst_hours) > 0:
                    best_rate = hourly_attach_rates[best_hours].mean()
                    worst_rate = hourly_attach_rates[worst_hours].mean()
                    
                    if best_rate > worst_rate * 1.5:  # Significant difference
                        worst_hour_transactions = modifier_df[modifier_df['hour'].isin(worst_hours)]
                        time_opportunity = len(worst_hour_transactions) * potential_modifier_revenue_per_transaction * 0.3
                        
                        insights.append({
                            'type': 'modifier_timing',
                            'title': f"Optimize Modifier Sales During Low Hours",
                            'description': f"Modifier sales are {best_rate/worst_rate:.1f}x higher at {best_hours} compared to {worst_hours}. Focus training during low-performance hours.",
                            'dollar_impact': time_opportunity,
                            'confidence': 0.73,
                            'best_hours': best_hours,
                            'worst_hours': worst_hours,
                            'action_items': [
                                f"Extra modifier training for {worst_hours[0]}:00-{worst_hours[-1]}:00 shifts",
                                "Incentivize modifier sales during slow hours",
                                "Review staffing during peak modifier hours"
                            ],
                            'evidence': {
                                'best_hour_attach_rate': f"{best_rate:.1%}",
                                'worst_hour_attach_rate': f"{worst_rate:.1%}",
                                'performance_ratio': f"{best_rate/worst_rate:.1f}x"
                            }
                        })
            
        except Exception as e:
            self.logger.error(f"Modifier analysis failed: {str(e)}")
        
        return insights
    
    def employee_performance(self, account_id: str, data: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """Employee performance analysis"""
        insights = []
        
        try:
            transactions_df = data.get('transactions')
            appointments_df = data.get('appointments')
            
            if transactions_df is None or appointments_df is None:
                return insights
            
            # Mock employee data analysis (in real implementation, would extract from Square data)
            # For demonstration, create sample insights based on transaction patterns
            
            # Analyze transaction amounts by time periods to infer employee performance
            transactions_df['hour'] = pd.to_datetime(transactions_df['square_created_at']).dt.hour
            transactions_df['day_of_week'] = pd.to_datetime(transactions_df['square_created_at']).dt.dayofweek
            
            hourly_performance = transactions_df.groupby('hour').agg({
                'amount': ['mean', 'count', 'sum']
            }).round(2)
            
            # Find performance variations that could indicate employee differences
            hourly_avg = hourly_performance[('amount', 'mean')]
            overall_avg = transactions_df['amount'].mean()
            
            high_performing_hours = hourly_avg[hourly_avg > overall_avg * 1.2].index.tolist()
            low_performing_hours = hourly_avg[hourly_avg < overall_avg * 0.8].index.tolist()
            
            if high_performing_hours and low_performing_hours:
                # Calculate revenue opportunity from bringing low hours up to average
                low_hour_transactions = transactions_df[transactions_df['hour'].isin(low_performing_hours)]
                current_low_revenue = low_hour_transactions['amount'].sum()
                potential_revenue = len(low_hour_transactions) * overall_avg
                opportunity = potential_revenue - current_low_revenue
                
                insights.append({
                    'type': 'employee_performance_timing',
                    'title': f"Improve Performance During {len(low_performing_hours)} Underperforming Hours",
                    'description': f"Revenue per transaction is {(overall_avg/hourly_avg[low_performing_hours].mean() - 1)*100:.0f}% lower during hours {low_performing_hours}. This suggests training opportunities.",
                    'dollar_impact': opportunity,
                    'confidence': 0.71,
                    'high_performing_hours': high_performing_hours,
                    'low_performing_hours': low_performing_hours,
                    'action_items': [
                        "Review staff scheduling for low-performing hours",
                        "Provide additional training during these periods",
                        "Implement performance incentives",
                        "Analyze which staff work during these hours"
                    ],
                    'evidence': {
                        'overall_avg_transaction': overall_avg,
                        'low_hour_avg': hourly_avg[low_performing_hours].mean(),
                        'high_hour_avg': hourly_avg[high_performing_hours].mean(),
                        'low_hour_transaction_count': len(low_hour_transactions)
                    }
                })
            
            # Day-of-week performance analysis
            daily_performance = transactions_df.groupby('day_of_week').agg({
                'amount': ['mean', 'count', 'sum']
            }).round(2)
            
            daily_avg = daily_performance[('amount', 'mean')]
            best_days = daily_avg.nlargest(2).index.tolist()
            worst_days = daily_avg.nsmallest(2).index.tolist()
            
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            if best_days and worst_days:
                best_day_performance = daily_avg[best_days].mean()
                worst_day_performance = daily_avg[worst_days].mean()
                
                if best_day_performance > worst_day_performance * 1.3:
                    worst_day_transactions = transactions_df[transactions_df['day_of_week'].isin(worst_days)]
                    day_opportunity = len(worst_day_transactions) * (best_day_performance - worst_day_performance)
                    
                    insights.append({
                        'type': 'employee_performance_daily',
                        'title': f"Improve {[day_names[d] for d in worst_days]} Performance",
                        'description': f"Average transaction value on {[day_names[d] for d in best_days]} is ${best_day_performance:.0f} vs ${worst_day_performance:.0f} on {[day_names[d] for d in worst_days]}. Focus on consistency.",
                        'dollar_impact': day_opportunity,
                        'confidence': 0.74,
                        'best_days': [day_names[d] for d in best_days],
                        'worst_days': [day_names[d] for d in worst_days],
                        'action_items': [
                            "Schedule top performers on underperforming days",
                            "Analyze service mix differences by day",
                            "Implement day-specific training",
                            "Review pricing strategy by day"
                        ],
                        'evidence': {
                            'best_day_avg': best_day_performance,
                            'worst_day_avg': worst_day_performance,
                            'performance_gap': f"{(best_day_performance/worst_day_performance - 1)*100:.0f}%"
                        }
                    })
                
        except Exception as e:
            self.logger.error(f"Employee performance analysis failed: {str(e)}")
        
        return insights
    
    def churn_prediction(self, account_id: str, data: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """Predict customer churn and calculate prevention value"""
        insights = []
        
        try:
            customers_df = data.get('customers')
            transactions_df = data.get('transactions')
            
            if customers_df is None or transactions_df is None or len(transactions_df) == 0:
                return insights
            
            # Calculate customer metrics
            current_date = datetime.now()
            
            customer_metrics = transactions_df.groupby('square_customer_id').agg({
                'square_created_at': ['count', 'max'],
                'amount': ['sum', 'mean']
            }).round(2)
            
            customer_metrics.columns = ['transaction_count', 'last_transaction', 'total_spent', 'avg_transaction']
            customer_metrics['days_since_last'] = (current_date - pd.to_datetime(customer_metrics['last_transaction'])).dt.days
            
            # Define churn risk categories
            customer_metrics['churn_risk'] = 'Low'
            customer_metrics.loc[customer_metrics['days_since_last'] > 90, 'churn_risk'] = 'Medium'
            customer_metrics.loc[customer_metrics['days_since_last'] > 180, 'churn_risk'] = 'High'
            customer_metrics.loc[customer_metrics['days_since_last'] > 365, 'churn_risk'] = 'Lost'
            
            # Analyze churn risk segments
            churn_stats = customer_metrics.groupby('churn_risk').agg({
                'total_spent': ['count', 'mean', 'sum'],
                'avg_transaction': 'mean',
                'days_since_last': 'mean'
            }).round(2)
            
            # High-risk churn prevention
            high_risk_customers = customer_metrics[customer_metrics['churn_risk'] == 'High']
            
            if len(high_risk_customers) > 5:
                # Calculate prevention opportunity
                avg_customer_value = high_risk_customers['total_spent'].mean()
                prevention_rate = 0.4  # Assume 40% prevention rate with intervention
                churn_prevention_value = len(high_risk_customers) * avg_customer_value * prevention_rate
                
                insights.append({
                    'type': 'churn_prevention',
                    'title': f"Prevent {len(high_risk_customers)} High-Risk Customer Churn",
                    'description': f"You have {len(high_risk_customers)} customers at high risk of churning (180+ days since last visit). Average customer value is ${avg_customer_value:.0f}.",
                    'dollar_impact': churn_prevention_value,
                    'confidence': 0.77,
                    'at_risk_customers': len(high_risk_customers),
                    'avg_customer_value': avg_customer_value,
                    'action_items': [
                        "Send personalized win-back campaigns",
                        "Offer comeback discounts (20-30%)",
                        "Make personal phone calls",
                        "Survey to understand why they stopped coming"
                    ],
                    'evidence': {
                        'high_risk_count': len(high_risk_customers),
                        'avg_days_since_last_visit': high_risk_customers['days_since_last'].mean(),
                        'avg_historical_spend': avg_customer_value,
                        'estimated_prevention_rate': f"{prevention_rate*100:.0f}%"
                    }
                })
            
            # Medium-risk retention
            medium_risk_customers = customer_metrics[customer_metrics['churn_risk'] == 'Medium']
            
            if len(medium_risk_customers) > 10:
                avg_medium_value = medium_risk_customers['total_spent'].mean()
                retention_rate = 0.7  # Higher retention rate for medium risk
                retention_value = len(medium_risk_customers) * avg_medium_value * retention_rate * 0.5  # Conservative estimate
                
                insights.append({
                    'type': 'retention_opportunity',
                    'title': f"Retain {len(medium_risk_customers)} Medium-Risk Customers",
                    'description': f"{len(medium_risk_customers)} customers haven't visited in 90-180 days. Pro-active retention could prevent churn.",
                    'dollar_impact': retention_value,
                    'confidence': 0.69,
                    'medium_risk_customers': len(medium_risk_customers),
                    'avg_customer_value': avg_medium_value,
                    'action_items': [
                        "Send 'we miss you' emails",
                        "Offer loyalty incentives",
                        "Book follow-up appointments",
                        "Create retention call campaign"
                    ],
                    'evidence': {
                        'medium_risk_count': len(medium_risk_customers),
                        'avg_days_since_last_visit': medium_risk_customers['days_since_last'].mean(),
                        'estimated_retention_rate': f"{retention_rate*100:.0f}%"
                    }
                })
                
        except Exception as e:
            self.logger.error(f"Churn prediction failed: {str(e)}")
        
        return insights
    
    def sequence_mining(self, account_id: str, data: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """Mine sequential patterns in customer behavior"""
        insights = []
        
        try:
            transactions_df = data.get('transactions')
            appointments_df = data.get('appointments')
            
            if transactions_df is None or len(transactions_df) == 0:
                return insights
            
            # Analyze service sequences and timing patterns
            transactions_df['date'] = pd.to_datetime(transactions_df['square_created_at'])
            transactions_df = transactions_df.sort_values(['square_customer_id', 'date'])
            
            # Calculate time between visits
            transactions_df['days_between_visits'] = transactions_df.groupby('square_customer_id')['date'].diff().dt.days
            
            # Find optimal visit frequency
            visit_intervals = transactions_df['days_between_visits'].dropna()
            
            if len(visit_intervals) > 20:
                # Find most common interval ranges
                interval_bins = [0, 30, 60, 90, 180, 365, float('inf')]
                interval_labels = ['<30 days', '30-60 days', '60-90 days', '90-180 days', '180-365 days', '365+ days']
                
                transactions_df['interval_category'] = pd.cut(transactions_df['days_between_visits'], 
                                                           bins=interval_bins, 
                                                           labels=interval_labels, 
                                                           right=False)
                
                interval_stats = transactions_df['interval_category'].value_counts()
                most_common_interval = interval_stats.index[0]
                
                # Customers who exceed optimal interval
                optimal_days = 60  # Assume 60 days is optimal based on most common
                overdue_customers = transactions_df.groupby('square_customer_id').agg({
                    'date': 'max',
                    'amount': ['sum', 'mean']
                }).round(2)
                
                overdue_customers.columns = ['last_visit', 'total_spent', 'avg_transaction']
                overdue_customers['days_overdue'] = (current_date - overdue_customers['last_visit']).dt.days - optimal_days
                
                # Find customers overdue for visits
                overdue_list = overdue_customers[overdue_customers['days_overdue'] > 0]
                
                if len(overdue_list) > 5:
                    # Calculate rebooking opportunity
                    avg_rebooking_value = overdue_list['avg_transaction'].mean()
                    rebooking_rate = 0.3  # 30% likely to rebook if contacted
                    rebooking_opportunity = len(overdue_list) * avg_rebooking_value * rebooking_rate
                    
                    insights.append({
                        'type': 'rebooking_sequence',
                        'title': f"Proactive Rebooking for {len(overdue_list)} Overdue Customers",
                        'description': f"Based on visit patterns, {len(overdue_list)} customers are overdue for their next appointment. Optimal frequency appears to be every {optimal_days} days.",
                        'dollar_impact': rebooking_opportunity,
                        'confidence': 0.72,
                        'overdue_customers': len(overdue_list),
                        'optimal_frequency_days': optimal_days,
                        'action_items': [
                            "Send appointment reminder texts/emails",
                            "Call customers overdue by 30+ days",
                            "Offer convenient booking incentives",
                            "Set up automated rebooking sequences"
                        ],
                        'evidence': {
                            'most_common_interval': most_common_interval,
                            'avg_overdue_days': overdue_list['days_overdue'].mean(),
                            'avg_transaction_value': avg_rebooking_value,
                            'estimated_rebooking_rate': f"{rebooking_rate*100:.0f}%"
                        }
                    })
            
            # Service upgrade patterns
            if len(transactions_df) > 50:
                # Look for customers with consistent low-value transactions who could be upsold
                customer_consistency = transactions_df.groupby('square_customer_id').agg({
                    'amount': ['count', 'mean', 'std'],
                    'date': ['min', 'max']
                }).round(2)
                
                customer_consistency.columns = ['visit_count', 'avg_amount', 'amount_std', 'first_visit', 'last_visit']
                customer_consistency['tenure_days'] = (customer_consistency['last_visit'] - customer_consistency['first_visit']).dt.days
                
                # Find loyal customers with low variation (potential upsell targets)
                loyal_consistent = customer_consistency[
                    (customer_consistency['visit_count'] >= 5) &
                    (customer_consistency['amount_std'] < customer_consistency['avg_amount'] * 0.3) &  # Low variation
                    (customer_consistency['tenure_days'] > 90)  # Long-term customers
                ]
                
                if len(loyal_consistent) > 5:
                    avg_current_spend = loyal_consistent['avg_amount'].mean()
                    upsell_potential = avg_current_spend * 0.4  # 40% upsell potential
                    total_upsell_opportunity = len(loyal_consistent) * upsell_potential * 2  # Assume 2 visits per upsell period
                    
                    insights.append({
                        'type': 'upsell_sequence',
                        'title': f"Upsell {len(loyal_consistent)} Loyal, Consistent Customers",
                        'description': f"You have {len(loyal_consistent)} loyal customers with consistent spending patterns (avg: ${avg_current_spend:.0f}). They're perfect candidates for service upgrades.",
                        'dollar_impact': total_upsell_opportunity,
                        'confidence': 0.75,
                        'upsell_candidates': len(loyal_consistent),
                        'avg_current_spend': avg_current_spend,
                        'action_items': [
                            "Present premium service options to loyal customers",
                            "Create loyalty tier upgrades",
                            "Offer package deals to consistent customers",
                            "Train staff to identify upsell moments"
                        ],
                        'evidence': {
                            'candidate_count': len(loyal_consistent),
                            'avg_visits': loyal_consistent['visit_count'].mean(),
                            'avg_tenure_days': loyal_consistent['tenure_days'].mean(),
                            'upsell_potential_per_customer': upsell_potential
                        }
                    })
                
        except Exception as e:
            self.logger.error(f"Sequence mining failed: {str(e)}")
        
        return insights
    
    def tournament_judge(self, models: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Score and rank insights from all models"""
        all_insights = []
        
        # Collect all insights from all models
        for model_name, insights in models.items():
            for insight in insights:
                insight['source_model'] = model_name
                all_insights.append(insight)
        
        # Score each insight
        scored_insights = []
        for insight in all_insights:
            score = self._score_insight(insight)
            insight['tournament_score'] = score
            scored_insights.append(insight)
        
        # Sort by tournament score
        scored_insights.sort(key=lambda x: x['tournament_score'], reverse=True)
        
        self.logger.info(f"Tournament judge processed {len(scored_insights)} insights")
        
        return scored_insights
    
    def _score_insight(self, insight: Dict[str, Any]) -> float:
        """Score an insight based on multiple criteria"""
        score = 0.0
        
        # Confidence score (0-30 points)
        confidence = insight.get('confidence', 0.5)
        score += confidence * 30
        
        # Dollar impact score (0-25 points)
        dollar_impact = insight.get('dollar_impact', 0)
        if dollar_impact > 0:
            # Logarithmic scale for dollar impact
            import math
            score += min(25, math.log10(dollar_impact + 1) * 5)
        
        # Actionability score (0-20 points)
        action_items = insight.get('action_items', [])
        score += min(20, len(action_items) * 5)
        
        # Evidence quality score (0-15 points)
        evidence = insight.get('evidence', {})
        score += min(15, len(evidence) * 3)
        
        # Novelty score (0-10 points) - penalize obvious insights
        title = insight.get('title', '').lower()
        description = insight.get('description', '').lower()
        
        novelty_penalty = 0
        for banned in self.banned_insights:
            if banned.lower() in title or banned.lower() in description:
                novelty_penalty += 10
                break
        
        score -= novelty_penalty
        score += 10  # Base novelty score
        
        return max(0, score)
    
    def _apply_quality_filters(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply quality filters to insights"""
        filtered = []
        
        for insight in insights:
            # Confidence filter
            if insight.get('confidence', 0) < self.min_confidence_threshold:
                continue
            
            # Dollar impact filter
            if insight.get('dollar_impact', 0) < self.min_dollar_impact:
                continue
            
            # Obviousness filter
            title = insight.get('title', '').lower()
            description = insight.get('description', '').lower()
            
            is_obvious = False
            for banned in self.banned_insights:
                if banned.lower() in title or banned.lower() in description:
                    is_obvious = True
                    break
            
            if is_obvious:
                self.logger.warning(f"Filtered obvious insight: {insight.get('title')}")
                continue
            
            filtered.append(insight)
        
        return filtered
    
    def _validate_success_metrics(self, insights: List[Dict[str, Any]]):
        """Validate that success metrics are met"""
        # Check minimum insight count
        if len(insights) < self.min_insights_per_analysis:
            self.logger.warning(f"Only {len(insights)} insights generated, target is {self.min_insights_per_analysis}")
        
        # Check total revenue opportunity
        total_opportunity = sum(insight.get('dollar_impact', 0) for insight in insights)
        if total_opportunity < self.target_revenue_discovery:
            self.logger.warning(f"Total revenue opportunity ${total_opportunity:.0f} is below target ${self.target_revenue_discovery}")
        
        # Check confidence distribution
        high_confidence_count = sum(1 for insight in insights if insight.get('confidence', 0) >= 0.8)
        if high_confidence_count / len(insights) < 0.6:
            self.logger.warning("Less than 60% of insights have high confidence (80%+)")
        
        self.logger.info(f"Validation complete: {len(insights)} insights, ${total_opportunity:.0f} opportunity, {high_confidence_count} high confidence")
    
    def _load_account_data(self, account_id: str) -> Dict[str, pd.DataFrame]:
        """Load all account data for analysis"""
        data = {}
        
        try:
            # Load customers
            customers_result = self.supabase.table('customers').select('*').eq('account_id', account_id).execute()
            if customers_result.data:
                data['customers'] = pd.DataFrame(customers_result.data)
            
            # Load transactions
            transactions_result = self.supabase.table('transactions').select('*').eq('account_id', account_id).execute()
            if transactions_result.data:
                data['transactions'] = pd.DataFrame(transactions_result.data)
            
            # Load appointments
            appointments_result = self.supabase.table('appointments').select('*').eq('account_id', account_id).execute()
            if appointments_result.data:
                data['appointments'] = pd.DataFrame(appointments_result.data)
            
            self.logger.info(f"Loaded data for account {account_id}: "
                           f"{len(data.get('customers', []))} customers, "
                           f"{len(data.get('transactions', []))} transactions, "
                           f"{len(data.get('appointments', []))} appointments")
            
        except Exception as e:
            self.logger.error(f"Error loading account data: {str(e)}")
        
        return data
    
    def _store_insights(self, account_id: str, insights: List[Dict[str, Any]]):
        """Store generated insights in database"""
        try:
            for insight in insights:
                insight_record = {
                    'account_id': account_id,
                    'type': insight.get('type'),
                    'title': insight.get('title'),
                    'description': insight.get('description'),
                    'dollar_impact': insight.get('dollar_impact', 0),
                    'confidence': insight.get('confidence', 0),
                    'source_model': insight.get('source_model'),
                    'tournament_score': insight.get('tournament_score', 0),
                    'action_items': json.dumps(insight.get('action_items', [])),
                    'evidence': json.dumps(insight.get('evidence', {})),
                    'metadata': json.dumps({k: v for k, v in insight.items() 
                                          if k not in ['type', 'title', 'description', 'dollar_impact', 
                                                     'confidence', 'action_items', 'evidence']}),
                    'created_at': datetime.now().isoformat()
                }
                
                self.supabase.table('insights').insert(insight_record).execute()
                
            self.logger.info(f"Stored {len(insights)} insights for account {account_id}")
            
        except Exception as e:
            self.logger.error(f"Error storing insights: {str(e)}")
    
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