"""
ReviewAgent - Online Review Monitoring and Analysis

Responsibility: Monitor and analyze online reviews across multiple platforms
Success Metrics:
- Daily review collection from Google, Yelp, Facebook
- Sentiment analysis and entity extraction
- Issue detection and response recommendations
- Competitive intelligence gathering

From agents-dropset.md specification
Comprehensive review monitoring for reputation management
"""

import logging
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import redis
import os
from supabase import create_client, Client
import anthropic
import openai
from dataclasses import dataclass


@dataclass
class Review:
    """Review data structure"""
    platform: str
    review_id: str
    author: str
    rating: int
    text: str
    date: datetime
    url: Optional[str] = None
    response: Optional[str] = None


@dataclass
class ReviewAnalysis:
    """Review analysis results"""
    sentiment_score: float  # -1 to 1
    sentiment_label: str    # positive, negative, neutral
    entities: Dict[str, List[str]]  # employees, services, competitors
    issues: List[str]
    action_items: List[str]
    priority: str          # high, medium, low
    requires_response: bool


class ReviewAgent:
    def __init__(self):
        self.name = "ReviewAgent"
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
        
        # AI clients for analysis
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Review monitoring configuration
        self.platforms = ['google', 'yelp', 'facebook']
        self.sentiment_threshold = -0.3  # Reviews below this need immediate attention
        self.response_time_threshold = 24  # Hours to respond to reviews
        
        # Common service keywords for entity extraction
        self.service_keywords = [
            'massage', 'facial', 'pedicure', 'manicure', 'waxing', 'eyebrow', 'lash',
            'hair', 'color', 'cut', 'style', 'blowout', 'treatment', 'spa', 'relaxation',
            'deep tissue', 'swedish', 'hot stone', 'aromatherapy', 'prenatal'
        ]
        
        # Competitor detection patterns
        self.competitor_patterns = [
            r'went to (\w+\s+\w+) instead',
            r'(\w+\s+\w+) is better',
            r'prefer (\w+\s+\w+)',
            r'switched to (\w+\s+\w+)'
        ]
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.name)
    
    def scrape_reviews(self, account_id: str) -> List[Dict[str, Any]]:
        """Daily review collection from all platforms"""
        self.logger.info(f"Starting review collection for account {account_id}")
        
        try:
            # Publish agent status
            self._publish_agent_status('scraping_reviews', account_id)
            
            all_reviews = []
            business_info = self._get_business_info(account_id)
            
            if not business_info:
                raise ValueError("No business information available for review scraping")
            
            # Scrape from each platform
            for platform in self.platforms:
                try:
                    self.logger.info(f"Scraping {platform} reviews...")
                    
                    if platform == 'google':
                        reviews = self._scrape_google_business(business_info)
                    elif platform == 'yelp':
                        reviews = self._scrape_yelp(business_info)
                    elif platform == 'facebook':
                        reviews = self._scrape_facebook(business_info)
                    else:
                        continue
                    
                    all_reviews.extend(reviews)
                    self.logger.info(f"Found {len(reviews)} new reviews on {platform}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to scrape {platform}: {str(e)}")
                    continue
            
            # Analyze each review
            analyzed_reviews = []
            for review in all_reviews:
                try:
                    analysis = self._analyze_review(review)
                    analyzed_reviews.append({
                        'review': review,
                        'analysis': analysis
                    })
                except Exception as e:
                    self.logger.error(f"Failed to analyze review: {str(e)}")
                    continue
            
            # Store reviews and analyses
            self._store_reviews(account_id, analyzed_reviews)
            
            # Generate summary insights
            summary_insights = self._generate_review_insights(analyzed_reviews)
            
            self.logger.info(f"Review collection completed: {len(analyzed_reviews)} reviews analyzed")
            
            return summary_insights
            
        except Exception as e:
            self.logger.error(f"Review scraping failed for account {account_id}: {str(e)}")
            raise
    
    def _scrape_google_business(self, business_info: Dict[str, Any]) -> List[Review]:
        """Scrape Google Business reviews (placeholder implementation)"""
        # In production, would use Google My Business API or web scraping
        # For now, return mock data structure
        
        reviews = []
        # Mock implementation - would integrate with Google API
        self.logger.info("Google Business review scraping (mock implementation)")
        
        # Would implement actual Google scraping logic here
        mock_reviews = [
            {
                'platform': 'google',
                'review_id': 'google_123',
                'author': 'Sarah M.',
                'rating': 5,
                'text': 'Amazing massage! Lisa was fantastic and really helped with my back pain.',
                'date': datetime.now() - timedelta(days=1),
                'url': 'https://maps.google.com/review/123'
            }
        ]
        
        for review_data in mock_reviews:
            reviews.append(Review(**review_data))
        
        return reviews
    
    def _scrape_yelp(self, business_info: Dict[str, Any]) -> List[Review]:
        """Scrape Yelp reviews (placeholder implementation)"""
        reviews = []
        # Mock implementation - would integrate with Yelp API
        self.logger.info("Yelp review scraping (mock implementation)")
        
        mock_reviews = [
            {
                'platform': 'yelp',
                'review_id': 'yelp_456',
                'author': 'Jessica K.',
                'rating': 2,
                'text': 'Disappointed with my facial. The room was too cold and Jennifer seemed rushed. Not worth the price.',
                'date': datetime.now() - timedelta(days=2),
                'url': 'https://yelp.com/biz/business/review/456'
            }
        ]
        
        for review_data in mock_reviews:
            reviews.append(Review(**review_data))
        
        return reviews
    
    def _scrape_facebook(self, business_info: Dict[str, Any]) -> List[Review]:
        """Scrape Facebook reviews (placeholder implementation)"""
        reviews = []
        # Mock implementation - would integrate with Facebook Graph API
        self.logger.info("Facebook review scraping (mock implementation)")
        
        mock_reviews = [
            {
                'platform': 'facebook',
                'review_id': 'fb_789',
                'author': 'Mike D.',
                'rating': 4,
                'text': 'Great spa experience overall. The massage was relaxing but parking was difficult.',
                'date': datetime.now() - timedelta(days=3),
                'url': 'https://facebook.com/business/reviews/789'
            }
        ]
        
        for review_data in mock_reviews:
            reviews.append(Review(**review_data))
        
        return reviews
    
    def _analyze_review(self, review: Review) -> ReviewAnalysis:
        """Comprehensive review analysis using AI"""
        try:
            # Sentiment analysis
            sentiment = self._analyze_sentiment(review.text)
            
            # Entity extraction
            entities = self._extract_entities(review.text)
            
            # Issue detection
            issues = self._detect_issues(review.text, review.rating)
            
            # Priority assessment
            priority = self._assess_priority(sentiment, review.rating, issues)
            
            # Response requirement
            requires_response = self._requires_response(sentiment, review.rating, issues)
            
            # Action items generation
            action_items = self._generate_action_items(review, sentiment, issues, entities)
            
            return ReviewAnalysis(
                sentiment_score=sentiment['score'],
                sentiment_label=sentiment['label'],
                entities=entities,
                issues=issues,
                action_items=action_items,
                priority=priority,
                requires_response=requires_response
            )
            
        except Exception as e:
            self.logger.error(f"Review analysis failed: {str(e)}")
            return ReviewAnalysis(
                sentiment_score=0.0,
                sentiment_label='neutral',
                entities={},
                issues=['analysis_failed'],
                action_items=['manual_review_required'],
                priority='medium',
                requires_response=False
            )
    
    def _analyze_sentiment(self, review_text: str) -> Dict[str, Any]:
        """Analyze sentiment using Claude"""
        try:
            prompt = f"""Analyze the sentiment of this business review. Provide:
1. A sentiment score from -1.0 (very negative) to 1.0 (very positive)
2. A sentiment label: positive, negative, or neutral
3. Key emotional indicators

Review: "{review_text}"

Respond in JSON format:
{{
    "score": 0.0,
    "label": "neutral",
    "emotions": ["emotion1", "emotion2"],
    "confidence": 0.0
}}"""
            
            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = json.loads(response.content[0].text.strip())
            return result
            
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {str(e)}")
            # Fallback to basic keyword-based sentiment
            return self._basic_sentiment_analysis(review_text)
    
    def _basic_sentiment_analysis(self, review_text: str) -> Dict[str, Any]:
        """Fallback sentiment analysis using keywords"""
        positive_words = ['great', 'amazing', 'excellent', 'wonderful', 'fantastic', 'love', 'perfect', 'outstanding']
        negative_words = ['terrible', 'awful', 'horrible', 'disappointing', 'rude', 'dirty', 'expensive', 'worst']
        
        text_lower = review_text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return {'score': 0.6, 'label': 'positive', 'emotions': ['satisfaction'], 'confidence': 0.7}
        elif negative_count > positive_count:
            return {'score': -0.6, 'label': 'negative', 'emotions': ['dissatisfaction'], 'confidence': 0.7}
        else:
            return {'score': 0.0, 'label': 'neutral', 'emotions': ['neutral'], 'confidence': 0.5}
    
    def _extract_entities(self, review_text: str) -> Dict[str, List[str]]:
        """Extract employees, services, and competitors from review text"""
        entities = {
            'employees': [],
            'services': [],
            'competitors': [],
            'issues': []
        }
        
        try:
            # Employee name extraction (common first names)
            employee_patterns = [
                r'\\b([A-Z][a-z]+)\\s+(?:was|is|did|gave|provided)',
                r'(?:with|by)\\s+([A-Z][a-z]+)\\s+(?:who|and|was)',
                r'([A-Z][a-z]+)\\s+(?:really|was very|seemed)'
            ]
            
            for pattern in employee_patterns:
                matches = re.findall(pattern, review_text, re.IGNORECASE)
                entities['employees'].extend([match for match in matches if len(match) > 2])
            
            # Service extraction
            text_lower = review_text.lower()
            for service in self.service_keywords:
                if service in text_lower:
                    entities['services'].append(service)
            
            # Competitor extraction
            for pattern in self.competitor_patterns:
                matches = re.findall(pattern, review_text, re.IGNORECASE)
                entities['competitors'].extend(matches)
            
            # Issue extraction
            issue_keywords = [
                'cold', 'rushed', 'dirty', 'expensive', 'rude', 'unprofessional',
                'late', 'cancelled', 'parking', 'noisy', 'uncomfortable'
            ]
            
            for issue in issue_keywords:
                if issue in text_lower:
                    entities['issues'].append(issue)
            
            # Remove duplicates
            for key in entities:
                entities[key] = list(set(entities[key]))
            
        except Exception as e:
            self.logger.error(f"Entity extraction failed: {str(e)}")
        
        return entities
    
    def _detect_issues(self, review_text: str, rating: int) -> List[str]:
        """Detect specific business issues from review text"""
        issues = []
        text_lower = review_text.lower()
        
        try:
            # Service quality issues
            if any(word in text_lower for word in ['rushed', 'hurried', 'quick']):
                issues.append('service_rushed')
            
            if any(word in text_lower for word in ['dirty', 'unclean', 'messy']):
                issues.append('cleanliness_issue')
            
            if any(word in text_lower for word in ['cold', 'freezing', 'too hot']):
                issues.append('temperature_issue')
            
            if any(word in text_lower for word in ['rude', 'unprofessional', 'attitude']):
                issues.append('staff_attitude')
            
            if any(word in text_lower for word in ['expensive', 'overpriced', 'too much']):
                issues.append('pricing_concern')
            
            if any(word in text_lower for word in ['parking', 'park']):
                issues.append('parking_difficulty')
            
            if any(word in text_lower for word in ['cancelled', 'cancel', 'reschedule']):
                issues.append('scheduling_issue')
            
            if any(word in text_lower for word in ['wait', 'waiting', 'late']):
                issues.append('timing_issue')
            
            # Low rating without specific issues mentioned
            if rating <= 2 and not issues:
                issues.append('general_dissatisfaction')
            
        except Exception as e:
            self.logger.error(f"Issue detection failed: {str(e)}")
        
        return issues
    
    def _assess_priority(self, sentiment: Dict[str, Any], rating: int, issues: List[str]) -> str:
        """Assess review priority for response and action"""
        # High priority criteria
        if (sentiment['score'] < -0.5 or rating <= 2 or 
            any(issue in ['staff_attitude', 'cleanliness_issue'] for issue in issues)):
            return 'high'
        
        # Medium priority criteria
        if (sentiment['score'] < 0 or rating == 3 or 
            len(issues) > 0):
            return 'medium'
        
        # Low priority (positive reviews)
        return 'low'
    
    def _requires_response(self, sentiment: Dict[str, Any], rating: int, issues: List[str]) -> bool:
        """Determine if review requires a response"""
        # Always respond to negative reviews
        if sentiment['score'] < -0.2 or rating <= 3:
            return True
        
        # Respond to reviews mentioning specific issues
        critical_issues = ['staff_attitude', 'cleanliness_issue', 'service_rushed']
        if any(issue in critical_issues for issue in issues):
            return True
        
        return False
    
    def _generate_action_items(self, review: Review, sentiment: Dict[str, Any], 
                             issues: List[str], entities: Dict[str, List[str]]) -> List[str]:
        """Generate specific action items based on review analysis"""
        action_items = []
        
        try:
            # Response actions
            if sentiment['score'] < -0.2:
                action_items.append(f"Respond to {review.platform} review by {review.author} within 24 hours")
            
            # Staff-specific actions
            if entities['employees']:
                employee = entities['employees'][0]
                if 'staff_attitude' in issues:
                    action_items.append(f"Schedule coaching session with {employee} regarding customer service")
                elif sentiment['score'] > 0.5:
                    action_items.append(f"Recognize {employee} for excellent customer service")
            
            # Service improvement actions
            if 'service_rushed' in issues:
                action_items.append("Review scheduling to ensure adequate time between appointments")
            
            if 'cleanliness_issue' in issues:
                action_items.append("Implement enhanced cleaning checklist and staff training")
            
            if 'temperature_issue' in issues:
                action_items.append("Check and adjust room temperature controls")
            
            if 'pricing_concern' in issues:
                action_items.append("Review pricing strategy and value communication")
            
            if 'parking_difficulty' in issues:
                action_items.append("Provide clear parking instructions or explore valet options")
            
            # Competitor mentions
            if entities['competitors']:
                competitor = entities['competitors'][0]
                action_items.append(f"Research competitive analysis against {competitor}")
            
            # Positive reinforcement
            if sentiment['score'] > 0.7 and review.rating >= 4:
                action_items.append("Share positive feedback with team for motivation")
                if entities['services']:
                    service = entities['services'][0]
                    action_items.append(f"Highlight {service} as a standout service in marketing")
            
        except Exception as e:
            self.logger.error(f"Action item generation failed: {str(e)}")
            action_items.append("Manual review and action planning required")
        
        return action_items
    
    def _generate_review_insights(self, analyzed_reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate summary insights from all reviews"""
        insights = []
        
        try:
            if not analyzed_reviews:
                return insights
            
            # Overall sentiment analysis
            sentiments = [r['analysis'].sentiment_score for r in analyzed_reviews]
            avg_sentiment = sum(sentiments) / len(sentiments)
            
            # Rating analysis
            ratings = [r['review'].rating for r in analyzed_reviews]
            avg_rating = sum(ratings) / len(ratings)
            
            # Issue frequency analysis
            all_issues = []
            for r in analyzed_reviews:
                all_issues.extend(r['analysis'].issues)
            
            issue_counts = {}
            for issue in all_issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
            
            # Most mentioned employees
            all_employees = []
            for r in analyzed_reviews:
                all_employees.extend(r['analysis'].entities.get('employees', []))
            
            employee_mentions = {}
            for employee in all_employees:
                employee_mentions[employee] = employee_mentions.get(employee, 0) + 1
            
            # Generate insights
            insights.append({
                'type': 'review_summary',
                'title': f'Review Analysis Summary - {len(analyzed_reviews)} Reviews',
                'description': f'Average sentiment: {avg_sentiment:.2f}, Average rating: {avg_rating:.1f}/5',
                'metrics': {
                    'total_reviews': len(analyzed_reviews),
                    'average_sentiment': avg_sentiment,
                    'average_rating': avg_rating,
                    'positive_reviews': len([r for r in analyzed_reviews if r['analysis'].sentiment_score > 0.2]),
                    'negative_reviews': len([r for r in analyzed_reviews if r['analysis'].sentiment_score < -0.2]),
                    'response_required': len([r for r in analyzed_reviews if r['analysis'].requires_response])
                },
                'top_issues': sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5],
                'mentioned_employees': sorted(employee_mentions.items(), key=lambda x: x[1], reverse=True)[:5]
            })
            
            # Issue-specific insights
            if issue_counts:
                top_issue, count = max(issue_counts.items(), key=lambda x: x[1])
                insights.append({
                    'type': 'top_issue',
                    'title': f'Most Common Issue: {top_issue.replace("_", " ").title()}',
                    'description': f'Mentioned in {count} out of {len(analyzed_reviews)} reviews ({count/len(analyzed_reviews)*100:.1f}%)',
                    'issue': top_issue,
                    'frequency': count,
                    'percentage': count / len(analyzed_reviews) * 100,
                    'priority': 'high' if count / len(analyzed_reviews) > 0.3 else 'medium'
                })
            
            # Employee performance insights
            if employee_mentions:
                top_employee, mentions = max(employee_mentions.items(), key=lambda x: x[1])
                insights.append({
                    'type': 'employee_recognition',
                    'title': f'Most Mentioned Employee: {top_employee}',
                    'description': f'{top_employee} was mentioned in {mentions} reviews',
                    'employee': top_employee,
                    'mention_count': mentions,
                    'recommendation': 'Review individual mentions for performance feedback'
                })
            
        except Exception as e:
            self.logger.error(f"Review insights generation failed: {str(e)}")
        
        return insights
    
    def generate_response_template(self, review: Review, analysis: ReviewAnalysis) -> str:
        """Generate AI-powered personalized review response"""
        try:
            # Import AI content generator
            from ai_content_generator import AIContentGenerator, CustomerContext, BusinessContext, ContentRequest
            
            # Initialize AI generator (cached)
            if not hasattr(self, '_ai_generator'):
                self._ai_generator = AIContentGenerator()
                self._business_context = BusinessContext(
                    business_name="Bashful Beauty",
                    business_type="spa",
                    staff_names=["Jennifer", "Maria", "Lisa"],
                    service_names=["Brazilian Wax", "Facial", "Body Wax"],
                    average_service_price=85.0,
                    location="Downtown",
                    phone="555-BASHFUL",
                    email="info@bashfulbeauty.com"
                )
            
            # Create customer context from review
            customer_context = CustomerContext(
                customer_id=review.author,
                name=review.author,
                email="",
                psychological_archetype="UNKNOWN",
                psychological_state="STABLE"
            )
            
            # Prepare review context for AI
            review_context = f"{review.rating}-star review: {review.content}"
            if analysis.entities.get('employees'):
                review_context += f" (Mentioned staff: {', '.join(analysis.entities['employees'])})"
            if analysis.entities.get('services'):
                review_context += f" (Services: {', '.join(analysis.entities['services'])})"
            if analysis.issues:
                review_context += f" (Issues: {', '.join(analysis.issues)})"
            
            # Generate AI response
            request = ContentRequest(
                content_type='review_response',
                customer_context=customer_context,
                business_context=self._business_context,
                additional_context=review_context,
                max_length=200
            )
            
            ai_response = self._ai_generator.generate_content(request)
            
            self.logger.info(f"Generated AI review response for {review.author}")
            return ai_response
            
        except Exception as e:
            self.logger.error(f"AI review response generation failed: {str(e)}")
            
            # Fallback to simple template
            if analysis.sentiment_score >= 0:
                return f"Thank you so much for your {review.rating}-star review, {review.author}! We appreciate your business and look forward to serving you again!"
            else:
                return f"Thank you for your feedback, {review.author}. We sincerely apologize that your experience didn't meet expectations. Please contact us so we can make this right."
    
    def _get_business_info(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get business information for review scraping"""
        try:
            result = self.supabase.table('accounts').select('*').eq('id', account_id).single().execute()
            
            if result.data:
                return {
                    'business_name': result.data.get('business_name'),
                    'locations': result.data.get('locations', [])
                }
            
        except Exception as e:
            self.logger.error(f"Failed to get business info: {str(e)}")
        
        return None
    
    def _store_reviews(self, account_id: str, analyzed_reviews: List[Dict[str, Any]]):
        """Store reviews and analyses in database"""
        try:
            for item in analyzed_reviews:
                review = item['review']
                analysis = item['analysis']
                
                # Store review
                review_record = {
                    'account_id': account_id,
                    'platform': review.platform,
                    'review_id': review.review_id,
                    'author': review.author,
                    'rating': review.rating,
                    'review_text': review.text,
                    'review_date': review.date.isoformat(),
                    'url': review.url,
                    'sentiment_score': analysis.sentiment_score,
                    'sentiment_label': analysis.sentiment_label,
                    'entities': json.dumps(analysis.entities),
                    'issues': json.dumps(analysis.issues),
                    'action_items': json.dumps(analysis.action_items),
                    'priority': analysis.priority,
                    'requires_response': analysis.requires_response,
                    'created_at': datetime.now().isoformat()
                }
                
                # Store in reviews table (would need to create this table)
                # For now, store in agent_logs
                self.supabase.table('agent_logs').insert({
                    'account_id': account_id,
                    'agent_name': self.name,
                    'action_type': 'review_analysis',
                    'entity_type': 'review',
                    'entity_id': review.review_id,
                    'decision': review_record,
                    'confidence': analysis.sentiment_score if analysis.sentiment_score >= 0 else -analysis.sentiment_score,
                    'created_at': datetime.now().isoformat()
                }).execute()
                
            self.logger.info(f"Stored {len(analyzed_reviews)} reviews for account {account_id}")
            
        except Exception as e:
            self.logger.error(f"Error storing reviews: {str(e)}")
    
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