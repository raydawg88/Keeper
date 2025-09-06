"""
ReportAgent - McKinsey-style narrative report generation

Responsibility: Generate professional narrative reports combining insights, metrics, 
and recommendations in McKinsey-style format with PDF output capability.

Author: Claude & Ray Hernandez
Created: 2024-09-06
"""

import logging
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

import redis
from anthropic import Anthropic
from supabase import create_client, Client
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from io import BytesIO
import base64

from .base_agent import BaseAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ReportMetrics:
    """Core business metrics for reporting"""
    total_revenue: float
    customer_count: int
    transaction_count: int
    avg_transaction_value: float
    customer_retention_rate: float
    revenue_per_customer: float
    modifier_attachment_rate: float
    appointment_utilization: float
    employee_performance_avg: float
    review_sentiment_avg: float

@dataclass
class InsightSummary:
    """Summary of insights for reporting"""
    total_insights: int
    high_priority_insights: int
    total_dollar_impact: float
    avg_confidence: float
    completion_rate: float
    network_enhanced_count: int

class ReportAgent(BaseAgent):
    """
    Generate narrative reports in McKinsey-style format
    
    Features:
    - Daily operational summaries
    - Weekly strategic analysis
    - Monthly trend reports  
    - Annual employee reviews
    - PDF generation with charts
    - Executive summary format
    - Data visualization integration
    - Professional presentation ready
    """
    
    def __init__(self, supabase_url: str, supabase_key: str, redis_url: str, 
                 anthropic_key: str):
        super().__init__("ReportAgent", supabase_url, supabase_key, redis_url)
        self.anthropic = Anthropic(api_key=anthropic_key)
        
        # Set up plotting style
        plt.style.use('seaborn-v0_8-whitegrid')
        sns.set_palette("husl")
        
    async def generate_daily_report(self, account_id: str) -> Dict[str, Any]:
        """
        Generate daily operational summary
        
        Content:
        - New insights discovered
        - Tasks completed and impact
        - Key metric changes  
        - Priority alerts
        """
        try:
            await self._publish_status("generating", "daily_report", account_id)
            
            # Gather today's data
            today = datetime.now().date()
            context = await self._gather_daily_context(account_id, today)
            
            # Generate narrative using Claude
            narrative = await self._generate_daily_narrative(context)
            
            # Create report structure
            report = {
                'type': 'daily',
                'account_id': account_id,
                'date': today.isoformat(),
                'title': f"Daily Operations Summary - {today.strftime('%B %d, %Y')}",
                'narrative': narrative,
                'metrics': context['metrics'],
                'insights': context['insights'], 
                'tasks': context['tasks'],
                'alerts': context['alerts'],
                'generated_at': datetime.now().isoformat()
            }
            
            # Store report
            await self._store_report(report)
            
            await self._publish_status("completed", "daily_report", len(context['insights']))
            
            return report
            
        except Exception as e:
            logger.error(f"Daily report generation failed: {e}")
            await self._publish_status("failed", "daily_report", str(e))
            return {}
    
    async def generate_weekly_report(self, account_id: str) -> Dict[str, Any]:
        """
        Generate McKinsey-style weekly strategic analysis
        
        Content:
        - Executive summary
        - Key insights and patterns
        - Financial impact analysis
        - Strategic recommendations
        - Performance trends
        """
        try:
            await self._publish_status("generating", "weekly_report", account_id)
            
            # Gather week's data
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
            context = await self._gather_weekly_context(account_id, start_date, end_date)
            
            # Generate charts
            chart_paths = await self._create_weekly_charts(context)
            
            # Generate McKinsey-style narrative
            narrative = await self._generate_weekly_narrative(context)
            
            # Create comprehensive report
            report = {
                'type': 'weekly',
                'account_id': account_id,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'title': f"Weekly Strategic Analysis - {start_date.strftime('%b %d')} to {end_date.strftime('%b %d, %Y')}",
                'executive_summary': narrative['executive_summary'],
                'key_insights': narrative['key_insights'],
                'financial_analysis': narrative['financial_analysis'],
                'recommendations': narrative['recommendations'],
                'performance_trends': narrative['performance_trends'],
                'charts': chart_paths,
                'raw_data': context,
                'generated_at': datetime.now().isoformat()
            }
            
            # Generate PDF version
            pdf_path = await self._generate_pdf_report(report)
            report['pdf_path'] = pdf_path
            
            # Store report
            await self._store_report(report)
            
            await self._publish_status("completed", "weekly_report", f"PDF: {pdf_path}")
            
            return report
            
        except Exception as e:
            logger.error(f"Weekly report generation failed: {e}")
            await self._publish_status("failed", "weekly_report", str(e))
            return {}
    
    async def generate_monthly_report(self, account_id: str) -> Dict[str, Any]:
        """
        Generate monthly comparison with trends
        
        Content:
        - Month-over-month analysis
        - Trend identification
        - Customer behavior changes
        - Revenue optimization opportunities
        - Employee performance analysis
        """
        try:
            await self._publish_status("generating", "monthly_report", account_id)
            
            # Gather month's data plus previous month for comparison
            end_date = datetime.now().date()
            start_date = end_date.replace(day=1)  # First of current month
            prev_start = (start_date - timedelta(days=1)).replace(day=1)  # First of previous month
            prev_end = start_date - timedelta(days=1)  # Last of previous month
            
            current_context = await self._gather_monthly_context(account_id, start_date, end_date)
            previous_context = await self._gather_monthly_context(account_id, prev_start, prev_end)
            
            # Generate comparison charts
            chart_paths = await self._create_monthly_charts(current_context, previous_context)
            
            # Generate trend analysis narrative
            narrative = await self._generate_monthly_narrative(current_context, previous_context)
            
            # Create comprehensive report
            report = {
                'type': 'monthly',
                'account_id': account_id,
                'current_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'comparison_period': {
                    'start_date': prev_start.isoformat(), 
                    'end_date': prev_end.isoformat()
                },
                'title': f"Monthly Analysis - {start_date.strftime('%B %Y')}",
                'executive_summary': narrative['executive_summary'],
                'performance_comparison': narrative['performance_comparison'],
                'trend_analysis': narrative['trend_analysis'],
                'customer_insights': narrative['customer_insights'],
                'revenue_opportunities': narrative['revenue_opportunities'],
                'employee_analysis': narrative['employee_analysis'],
                'strategic_recommendations': narrative['strategic_recommendations'],
                'charts': chart_paths,
                'current_data': current_context,
                'comparison_data': previous_context,
                'generated_at': datetime.now().isoformat()
            }
            
            # Generate PDF version
            pdf_path = await self._generate_pdf_report(report)
            report['pdf_path'] = pdf_path
            
            # Store report
            await self._store_report(report)
            
            await self._publish_status("completed", "monthly_report", f"PDF: {pdf_path}")
            
            return report
            
        except Exception as e:
            logger.error(f"Monthly report generation failed: {e}")
            await self._publish_status("failed", "monthly_report", str(e))
            return {}
    
    async def annual_employee_review(self, account_id: str, employee_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive annual employee review
        
        Content:
        - 12 months of performance metrics
        - Comparison to team averages
        - Growth trajectory analysis
        - Specific wins and improvement areas
        - Recommended actions and goals
        """
        try:
            await self._publish_status("generating", "employee_review", employee_id)
            
            # Gather 12 months of employee data
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=365)
            
            employee_data = await self._gather_employee_data(account_id, employee_id, start_date, end_date)
            team_data = await self._gather_team_data(account_id, start_date, end_date)
            
            # Generate performance charts
            chart_paths = await self._create_employee_charts(employee_data, team_data)
            
            # Generate review narrative
            narrative = await self._generate_employee_narrative(employee_data, team_data)
            
            # Create comprehensive review
            review = {
                'type': 'employee_review',
                'account_id': account_id,
                'employee_id': employee_id,
                'review_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'title': f"Annual Performance Review - {employee_data.get('employee_name', 'Employee')}",
                'executive_summary': narrative['executive_summary'],
                'performance_metrics': narrative['performance_metrics'],
                'team_comparison': narrative['team_comparison'],
                'growth_analysis': narrative['growth_analysis'],
                'achievements': narrative['achievements'],
                'improvement_areas': narrative['improvement_areas'],
                'goals_recommendations': narrative['goals_recommendations'],
                'charts': chart_paths,
                'raw_data': employee_data,
                'team_benchmarks': team_data,
                'generated_at': datetime.now().isoformat()
            }
            
            # Generate PDF version
            pdf_path = await self._generate_pdf_report(review)
            review['pdf_path'] = pdf_path
            
            # Store review
            await self._store_report(review)
            
            await self._publish_status("completed", "employee_review", f"PDF: {pdf_path}")
            
            return review
            
        except Exception as e:
            logger.error(f"Employee review generation failed: {e}")
            await self._publish_status("failed", "employee_review", str(e))
            return {}
    
    async def _gather_daily_context(self, account_id: str, date) -> Dict[str, Any]:
        """Gather data for daily report"""
        try:
            date_str = date.isoformat()
            
            # Get today's insights
            insights_result = self.supabase.table('insights').select('*').eq(
                'account_id', account_id
            ).gte('created_at', f"{date_str}T00:00:00").lte(
                'created_at', f"{date_str}T23:59:59"
            ).execute()
            
            # Get today's completed tasks
            tasks_result = self.supabase.table('tasks').select('*').eq(
                'account_id', account_id
            ).eq('status', 'completed').gte('completed_at', f"{date_str}T00:00:00").execute()
            
            # Get recent transactions
            transactions_result = self.supabase.table('transactions').select('*').eq(
                'account_id', account_id
            ).gte('created_at', f"{date_str}T00:00:00").execute()
            
            # Calculate daily metrics
            transactions = transactions_result.data
            daily_revenue = sum(t.get('total_money', 0) for t in transactions)
            transaction_count = len(transactions)
            
            # Get alerts (high priority tasks, negative reviews, etc.)
            alerts = []
            
            # High priority tasks
            priority_tasks = self.supabase.table('tasks').select('*').eq(
                'account_id', account_id
            ).eq('priority', 3).eq('status', 'pending').execute()
            
            if priority_tasks.data:
                alerts.append(f"{len(priority_tasks.data)} high-priority tasks require attention")
            
            return {
                'date': date_str,
                'insights': insights_result.data,
                'tasks': tasks_result.data,
                'transactions': transactions,
                'metrics': {
                    'daily_revenue': daily_revenue,
                    'transaction_count': transaction_count,
                    'avg_transaction': daily_revenue / max(transaction_count, 1),
                    'insights_generated': len(insights_result.data),
                    'tasks_completed': len(tasks_result.data)
                },
                'alerts': alerts
            }
            
        except Exception as e:
            logger.error(f"Daily context gathering failed: {e}")
            return {}
    
    async def _generate_daily_narrative(self, context: Dict[str, Any]) -> str:
        """Generate daily narrative using Claude"""
        try:
            prompt = f"""
Generate a concise daily operations summary for a business owner.

Data Summary:
- Date: {context['date']}
- Daily Revenue: ${context['metrics']['daily_revenue']:,.2f}
- Transactions: {context['metrics']['transaction_count']}
- New Insights: {context['metrics']['insights_generated']}
- Tasks Completed: {context['metrics']['tasks_completed']}
- Alerts: {len(context['alerts'])}

Key Insights Generated:
{self._format_insights_for_prompt(context['insights'][:5])}

Tasks Completed Today:
{self._format_tasks_for_prompt(context['tasks'][:5])}

Alerts:
{chr(10).join(context['alerts'][:3])}

Generate a 2-3 paragraph executive summary that:
1. Highlights the day's key performance
2. Summarizes most important insights and their impact
3. Notes any urgent items requiring attention
4. Maintains professional, data-driven tone

Focus on actionable insights and dollar impacts.
"""
            
            message = self.anthropic.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text
            
        except Exception as e:
            logger.error(f"Daily narrative generation failed: {e}")
            return "Unable to generate daily narrative."
    
    async def _gather_weekly_context(self, account_id: str, start_date, end_date) -> Dict[str, Any]:
        """Gather comprehensive weekly data"""
        try:
            start_str = start_date.isoformat()
            end_str = end_date.isoformat()
            
            # Get all insights for the week
            insights_result = self.supabase.table('insights').select('*').eq(
                'account_id', account_id
            ).gte('created_at', f"{start_str}T00:00:00").lte(
                'created_at', f"{end_str}T23:59:59"
            ).execute()
            
            # Get tasks and their outcomes
            tasks_result = self.supabase.table('tasks').select('*').eq(
                'account_id', account_id
            ).gte('created_at', f"{start_str}T00:00:00").execute()
            
            # Get transactions
            transactions_result = self.supabase.table('transactions').select('*').eq(
                'account_id', account_id
            ).gte('created_at', f"{start_str}T00:00:00").lte(
                'created_at', f"{end_str}T23:59:59"
            ).execute()
            
            # Get customers
            customers_result = self.supabase.table('customers').select('*').eq(
                'account_id', account_id
            ).execute()
            
            # Calculate weekly metrics
            transactions = transactions_result.data
            weekly_revenue = sum(t.get('total_money', 0) for t in transactions)
            
            insights = insights_result.data
            tasks = tasks_result.data
            
            completed_tasks = [t for t in tasks if t['status'] == 'completed']
            
            metrics = ReportMetrics(
                total_revenue=weekly_revenue,
                customer_count=len(customers_result.data),
                transaction_count=len(transactions),
                avg_transaction_value=weekly_revenue / max(len(transactions), 1),
                customer_retention_rate=self._calculate_retention_rate(customers_result.data),
                revenue_per_customer=weekly_revenue / max(len(customers_result.data), 1),
                modifier_attachment_rate=self._calculate_modifier_rate(transactions),
                appointment_utilization=0.85,  # Placeholder
                employee_performance_avg=0.78,  # Placeholder
                review_sentiment_avg=0.82  # Placeholder
            )
            
            insight_summary = InsightSummary(
                total_insights=len(insights),
                high_priority_insights=len([i for i in insights if i.get('priority') == 'high']),
                total_dollar_impact=sum(i.get('dollar_impact', 0) for i in insights),
                avg_confidence=sum(i.get('confidence', 0) for i in insights) / max(len(insights), 1),
                completion_rate=len(completed_tasks) / max(len(tasks), 1),
                network_enhanced_count=len([i for i in insights if i.get('network_enhanced')])
            )
            
            return {
                'period': {'start': start_str, 'end': end_str},
                'metrics': metrics,
                'insight_summary': insight_summary,
                'insights': insights,
                'tasks': tasks,
                'transactions': transactions,
                'customers': customers_result.data
            }
            
        except Exception as e:
            logger.error(f"Weekly context gathering failed: {e}")
            return {}
    
    async def _generate_weekly_narrative(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate McKinsey-style weekly narrative"""
        try:
            metrics = context['metrics']
            insights = context['insight_summary']
            
            base_prompt = f"""
Generate a McKinsey-style weekly business analysis with the following structure.

BUSINESS PERFORMANCE DATA:
- Revenue: ${metrics.total_revenue:,.2f}
- Transactions: {metrics.transaction_count:,}
- Average Transaction: ${metrics.avg_transaction_value:.2f}
- Customers: {metrics.customer_count:,}
- Revenue per Customer: ${metrics.revenue_per_customer:.2f}

INSIGHT ANALYSIS:
- Total Insights: {insights.total_insights}
- High Priority: {insights.high_priority_insights}
- Total Dollar Impact: ${insights.total_dollar_impact:,.2f}
- Average Confidence: {insights.avg_confidence:.1%}
- Network Enhanced: {insights.network_enhanced_count}

Top Insights:
{self._format_insights_for_prompt(context['insights'][:5])}

Generate professional, data-driven analysis for each section:
"""
            
            sections = {
                'executive_summary': "Write a 2-3 sentence executive summary highlighting the week's key performance and most critical finding.",
                'key_insights': "Analyze the top 3-5 insights, focusing on dollar impact and implementation priority.",
                'financial_analysis': "Provide revenue analysis with specific recommendations for improvement.",
                'recommendations': "List 3-4 specific, actionable recommendations based on the data.",
                'performance_trends': "Identify emerging patterns and their business implications."
            }
            
            narratives = {}
            
            for section, instruction in sections.items():
                section_prompt = f"{base_prompt}\n\nFOCUS: {instruction}\n\nProvide professional analysis:"
                
                message = self.anthropic.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=800,
                    messages=[{"role": "user", "content": section_prompt}]
                )
                
                narratives[section] = message.content[0].text
                
                # Brief delay to respect rate limits
                await asyncio.sleep(0.5)
            
            return narratives
            
        except Exception as e:
            logger.error(f"Weekly narrative generation failed: {e}")
            return {}
    
    async def _create_weekly_charts(self, context: Dict[str, Any]) -> List[str]:
        """Create visualization charts for weekly report"""
        try:
            chart_paths = []
            
            # Revenue trend chart
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Sample daily data (in real implementation, query daily transactions)
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            daily_revenue = [800, 950, 1200, 1100, 1400, 1600, 900]  # Sample data
            
            ax.plot(days, daily_revenue, marker='o', linewidth=3, markersize=8)
            ax.set_title('Daily Revenue Trend', fontsize=16, fontweight='bold')
            ax.set_ylabel('Revenue ($)', fontsize=12)
            ax.grid(True, alpha=0.3)
            
            # Format y-axis as currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            revenue_chart_path = f'/tmp/weekly_revenue_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            plt.savefig(revenue_chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            chart_paths.append(revenue_chart_path)
            
            # Insight impact chart
            fig, ax = plt.subplots(figsize=(10, 6))
            
            insights = context.get('insights', [])
            if insights:
                insight_types = {}
                for insight in insights:
                    itype = insight.get('type', 'other')
                    impact = insight.get('dollar_impact', 0)
                    if itype in insight_types:
                        insight_types[itype] += impact
                    else:
                        insight_types[itype] = impact
                
                types = list(insight_types.keys())
                impacts = list(insight_types.values())
                
                bars = ax.bar(types, impacts, color=sns.color_palette("husl", len(types)))
                ax.set_title('Insight Impact by Type', fontsize=16, fontweight='bold')
                ax.set_ylabel('Dollar Impact ($)', fontsize=12)
                ax.tick_params(axis='x', rotation=45)
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'${height:,.0f}', ha='center', va='bottom')
            
            insights_chart_path = f'/tmp/weekly_insights_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            plt.savefig(insights_chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            chart_paths.append(insights_chart_path)
            
            return chart_paths
            
        except Exception as e:
            logger.error(f"Weekly chart creation failed: {e}")
            return []
    
    async def _generate_pdf_report(self, report: Dict[str, Any]) -> str:
        """Generate PDF version of report"""
        try:
            # Create PDF file path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_path = f'/tmp/{report["type"]}_report_{timestamp}.pdf'
            
            # Create PDF document
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor='darkblue',
                alignment=1  # Center alignment
            )
            story.append(Paragraph(report['title'], title_style))
            story.append(Spacer(1, 0.5*inch))
            
            # Executive Summary
            if 'executive_summary' in report:
                story.append(Paragraph("Executive Summary", styles['Heading2']))
                story.append(Paragraph(report['executive_summary'], styles['Normal']))
                story.append(Spacer(1, 0.3*inch))
            
            # Add sections based on report type
            if report['type'] == 'weekly':
                sections = [
                    ('Key Insights', report.get('key_insights', '')),
                    ('Financial Analysis', report.get('financial_analysis', '')),
                    ('Recommendations', report.get('recommendations', '')),
                    ('Performance Trends', report.get('performance_trends', ''))
                ]
            elif report['type'] == 'monthly':
                sections = [
                    ('Performance Comparison', report.get('performance_comparison', '')),
                    ('Trend Analysis', report.get('trend_analysis', '')),
                    ('Revenue Opportunities', report.get('revenue_opportunities', '')),
                    ('Strategic Recommendations', report.get('strategic_recommendations', ''))
                ]
            else:
                sections = [('Content', report.get('narrative', ''))]
            
            for section_title, section_content in sections:
                if section_content:
                    story.append(Paragraph(section_title, styles['Heading2']))
                    story.append(Paragraph(section_content, styles['Normal']))
                    story.append(Spacer(1, 0.3*inch))
            
            # Add charts if available
            if 'charts' in report and report['charts']:
                story.append(PageBreak())
                story.append(Paragraph("Data Visualizations", styles['Heading2']))
                
                for chart_path in report['charts']:
                    if Path(chart_path).exists():
                        img = Image(chart_path, width=6*inch, height=3.6*inch)
                        story.append(img)
                        story.append(Spacer(1, 0.3*inch))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF report generated: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return ""
    
    def _format_insights_for_prompt(self, insights: List[Dict[str, Any]]) -> str:
        """Format insights for Claude prompt"""
        if not insights:
            return "No insights available."
            
        formatted = []
        for insight in insights:
            formatted.append(f"- {insight.get('type', 'Unknown')}: ${insight.get('dollar_impact', 0):,.0f} impact ({insight.get('confidence', 0):.0%} confidence)")
        
        return '\n'.join(formatted)
    
    def _format_tasks_for_prompt(self, tasks: List[Dict[str, Any]]) -> str:
        """Format tasks for Claude prompt"""
        if not tasks:
            return "No tasks completed."
            
        formatted = []
        for task in tasks:
            formatted.append(f"- {task.get('title', 'Unknown task')}: ${task.get('dollar_value', 0):,.0f}")
        
        return '\n'.join(formatted)
    
    def _calculate_retention_rate(self, customers: List[Dict[str, Any]]) -> float:
        """Calculate customer retention rate"""
        # Simplified calculation - in real implementation, analyze visit patterns
        return 0.78  # Placeholder
    
    def _calculate_modifier_rate(self, transactions: List[Dict[str, Any]]) -> float:
        """Calculate modifier attachment rate"""
        # Simplified calculation - in real implementation, analyze modifiers
        return 0.43  # Placeholder
    
    async def _store_report(self, report: Dict[str, Any]) -> bool:
        """Store report in database"""
        try:
            result = self.supabase.table('reports').insert({
                'account_id': report['account_id'],
                'type': report['type'],
                'title': report['title'],
                'content': report,
                'generated_at': report['generated_at']
            }).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Report storage failed: {e}")
            return False
    
    async def get_recent_reports(self, account_id: str, report_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent reports for an account"""
        try:
            query = self.supabase.table('reports').select('*').eq('account_id', account_id)
            
            if report_type:
                query = query.eq('type', report_type)
            
            result = query.order('generated_at', desc=True).limit(10).execute()
            
            return result.data
            
        except Exception as e:
            logger.error(f"Report retrieval failed: {e}")
            return []
    
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
    
    async def test_report_agent():
        """Test ReportAgent functionality"""
        agent = ReportAgent(
            supabase_url=os.getenv('SUPABASE_URL'),
            supabase_key=os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
            redis_url=os.getenv('REDIS_URL'),
            anthropic_key=os.getenv('ANTHROPIC_API_KEY')
        )
        
        # Test daily report generation
        daily_report = await agent.generate_daily_report('test_account')
        print(f"Generated daily report: {len(daily_report.get('narrative', ''))} chars")
        
        # Test weekly report generation
        weekly_report = await agent.generate_weekly_report('test_account')
        print(f"Generated weekly report with PDF: {weekly_report.get('pdf_path', 'None')}")
        
        # Get recent reports
        reports = await agent.get_recent_reports('test_account')
        print(f"Found {len(reports)} recent reports")
    
    # Run test
    asyncio.run(test_report_agent())