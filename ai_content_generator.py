#!/usr/bin/env python3
"""
AI CONTENT GENERATOR - Personalized Scripts & Reports
Replaces ALL template dictionaries with AI-generated personalized content
Uses Claude Haiku/GPT-3.5 for cost-effective content generation
"""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import pandas as pd

try:
    import openai
    from anthropic import Anthropic
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()
    
except ImportError as e:
    print(f"Installing required packages: {e}")
    os.system("pip3 install --break-system-packages openai anthropic python-dotenv")
    import openai
    from anthropic import Anthropic
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()

@dataclass
class CustomerContext:
    """Complete customer context for personalized content generation"""
    customer_id: str
    name: str
    email: str
    phone: Optional[str] = None
    total_spent: float = 0.0
    visit_count: int = 0
    last_visit_date: Optional[datetime] = None
    favorite_services: List[str] = None
    favorite_staff: List[str] = None
    churn_risk: float = 0.0
    ltv: float = 0.0
    psychological_archetype: str = "UNKNOWN"
    psychological_state: str = "STABLE"
    visit_frequency: float = 0.0
    days_since_last_visit: int = 0
    spending_trend: str = "STABLE"
    service_preferences: Dict[str, float] = None
    business_type: str = "spa"  # spa, salon, restaurant, etc.

@dataclass
class BusinessContext:
    """Business context for content personalization"""
    business_name: str
    business_type: str
    staff_names: List[str]
    service_names: List[str]
    average_service_price: float
    location: str
    phone: str
    email: str

@dataclass
class ContentRequest:
    """Request for AI-generated content"""
    content_type: str  # 'retention_script', 'upsell_script', 'review_response', 'email', 'sms'
    customer_context: CustomerContext
    business_context: BusinessContext
    urgency: str = "medium"  # low, medium, high
    additional_context: Optional[str] = None
    max_length: int = 200

class AIContentGenerator:
    """Generate personalized content using AI instead of templates"""
    
    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None
        self._setup_ai_clients()
        self.cost_tracker = {'anthropic': 0.0, 'openai': 0.0}
        
        print("🤖 AI CONTENT GENERATOR INITIALIZED")
        print(f"   Claude Client: {'✅' if self.anthropic_client else '❌'}")
        print(f"   OpenAI Client: {'✅' if self.openai_client else '❌'}")
    
    def _setup_ai_clients(self):
        """Initialize AI clients with API keys"""
        # Claude (Anthropic) - Primary for cost-effectiveness
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key:
            try:
                self.anthropic_client = Anthropic(api_key=anthropic_key)
            except Exception as e:
                print(f"⚠️  Claude setup failed: {e}")
        
        # OpenAI - Fallback
        openai_key = os.getenv('OPENAI_API_KEY') 
        if openai_key:
            try:
                openai.api_key = openai_key
                self.openai_client = openai
            except Exception as e:
                print(f"⚠️  OpenAI setup failed: {e}")
    
    def generate_content(self, request: ContentRequest) -> str:
        """Generate personalized content based on request"""
        try:
            # Use Claude Haiku for cost-effectiveness (primary)
            if self.anthropic_client:
                return self._generate_with_claude(request)
            # Fallback to GPT-3.5 if Claude unavailable
            elif self.openai_client:
                return self._generate_with_openai(request)
            else:
                print("⚠️  No AI clients available, using fallback template")
                return self._generate_fallback_content(request)
                
        except Exception as e:
            print(f"⚠️  AI content generation failed: {e}")
            return self._generate_fallback_content(request)
    
    def _generate_with_claude(self, request: ContentRequest) -> str:
        """Generate content using Claude Haiku (cost-effective)"""
        prompt = self._create_prompt(request)
        
        print(f"🤖 CALLING CLAUDE API...")
        print(f"   Model: claude-3-haiku-20240307")
        print(f"   Customer: {request.customer_context.name}")
        print(f"   Content Type: {request.content_type}")
        print(f"   Prompt Length: {len(prompt)} chars")
        
        try:
            start_time = datetime.now()
            message = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",  # Most cost-effective model
                max_tokens=request.max_length + 50,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            api_time = (datetime.now() - start_time).total_seconds()
            
            content = message.content[0].text.strip()
            
            # Track costs (approximate)
            input_tokens = len(prompt) // 4  # Rough estimate
            output_tokens = len(content) // 4
            cost = (input_tokens * 0.00025 + output_tokens * 0.00125) / 1000  # Haiku pricing
            self.cost_tracker['anthropic'] += cost
            
            print(f"   ✅ Claude Response: {api_time:.3f}s")
            print(f"   📊 Tokens: ~{input_tokens} in, ~{output_tokens} out")
            print(f"   💰 Cost: ${cost:.6f}")
            
            return content
            
        except Exception as e:
            print(f"   ❌ Claude API failed: {e}")
            return self._generate_with_openai(request)
    
    def _generate_with_openai(self, request: ContentRequest) -> str:
        """Generate content using GPT-3.5 (fallback)"""
        prompt = self._create_prompt(request)
        
        print(f"🤖 CALLING OPENAI API...")
        print(f"   Model: gpt-3.5-turbo")
        print(f"   Customer: {request.customer_context.name}")
        print(f"   Content Type: {request.content_type}")
        print(f"   Prompt Length: {len(prompt)} chars")
        
        try:
            start_time = datetime.now()
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # Cost-effective model
                messages=[{"role": "user", "content": prompt}],
                max_tokens=request.max_length,
                temperature=0.7
            )
            api_time = (datetime.now() - start_time).total_seconds()
            
            content = response.choices[0].message.content.strip()
            
            # Track costs (approximate)
            cost = (response.usage.prompt_tokens * 0.0015 + response.usage.completion_tokens * 0.002) / 1000
            self.cost_tracker['openai'] += cost
            
            print(f"   ✅ OpenAI Response: {api_time:.3f}s")
            print(f"   📊 Tokens: {response.usage.prompt_tokens} in, {response.usage.completion_tokens} out")
            print(f"   💰 Cost: ${cost:.6f}")
            
            return content
            
        except Exception as e:
            print(f"   ❌ OpenAI API failed: {e}")
            return self._generate_fallback_content(request)
    
    def _create_prompt(self, request: ContentRequest) -> str:
        """Create AI prompt based on content request"""
        customer = request.customer_context
        business = request.business_context
        
        # Base context
        prompt = f"""You are a customer relationship expert for {business.business_name}, a {business.business_type}.

CUSTOMER PROFILE:
- Name: {customer.name}
- Total Spent: ${customer.total_spent:,.0f}
- Visits: {customer.visit_count}
- Last Visit: {customer.days_since_last_visit} days ago
- Churn Risk: {customer.churn_risk:.1%}
- Lifetime Value: ${customer.ltv:,.0f}
- Psychology: {customer.psychological_archetype} ({customer.psychological_state})
- Favorite Services: {', '.join(customer.favorite_services or ['None identified'])}
- Favorite Staff: {', '.join(customer.favorite_staff or ['None identified'])}
- Spending Trend: {customer.spending_trend}

BUSINESS CONTEXT:
- Business: {business.business_name}
- Staff: {', '.join(business.staff_names[:3])}
- Services: {', '.join(business.service_names[:5])}
- Location: {business.location}
- Phone: {business.phone}

"""
        
        # Content-specific prompts
        if request.content_type == 'retention_script':
            prompt += f"""Generate a personalized phone script to retain this customer who hasn't visited in {customer.days_since_last_visit} days.

REQUIREMENTS:
- {request.urgency.upper()} urgency
- Reference specific past services/staff they loved
- Include compelling reason to return (special offer, new service, staff request)
- Sound natural and conversational, not salesy
- Include specific next steps
- Max {request.max_length} characters

Generate ONLY the script - no explanations or headers."""

        elif request.content_type == 'upsell_script':
            prompt += f"""Generate a personalized upselling script for this customer during their next visit.

REQUIREMENTS:
- Based on their service history and preferences
- Reference their psychological profile ({customer.psychological_archetype})
- Suggest complementary services they haven't tried
- Natural conversation flow
- Max {request.max_length} characters

Generate ONLY the script - no explanations or headers."""

        elif request.content_type == 'review_response':
            prompt += f"""Generate a personalized response to this customer's review.

REVIEW CONTEXT: {request.additional_context or 'Positive review'}

REQUIREMENTS:
- Thank them specifically for their feedback
- Reference specific details if mentioned in review
- Professional but warm tone
- Include subtle invitation to return
- Max {request.max_length} characters

Generate ONLY the response - no explanations or headers."""

        elif request.content_type == 'email':
            prompt += f"""Generate a personalized email to re-engage this customer.

REQUIREMENTS:
- Subject line + email body
- Reference their history and preferences
- Clear call-to-action
- Professional email format
- Max {request.max_length} characters

Generate ONLY the email - no explanations or headers."""

        else:
            prompt += f"""Generate personalized {request.content_type} content for this customer.
Max {request.max_length} characters. No explanations - just the content."""

        return prompt
    
    def _generate_fallback_content(self, request: ContentRequest) -> str:
        """Generate basic content when AI is unavailable"""
        customer = request.customer_context
        
        if request.content_type == 'retention_script':
            return f"Hi {customer.name}, it's been {customer.days_since_last_visit} days since your last visit to {request.business_context.business_name}. We miss you and would love to schedule your next appointment. Can we book something for this week?"
        
        elif request.content_type == 'upsell_script':
            return f"Hi {customer.name}, based on your previous {customer.favorite_services[0] if customer.favorite_services else 'service'}, I think you'd love our complementary treatments. Would you like to hear about some options?"
        
        else:
            return f"Thank you {customer.name} for being a valued customer at {request.business_context.business_name}. We appreciate your business!"
    
    def generate_batch_content(self, requests: List[ContentRequest]) -> List[str]:
        """Generate content for multiple requests efficiently"""
        results = []
        
        print(f"🤖 Generating {len(requests)} personalized content pieces...")
        
        for i, request in enumerate(requests):
            try:
                content = self.generate_content(request)
                results.append(content)
                
                if (i + 1) % 10 == 0:
                    print(f"   ✅ Generated {i + 1}/{len(requests)} pieces")
                    
            except Exception as e:
                print(f"   ⚠️  Failed request {i + 1}: {e}")
                results.append(self._generate_fallback_content(request))
        
        print(f"✅ Batch generation complete:")
        print(f"   💰 Claude Cost: ${self.cost_tracker['anthropic']:.4f}")
        print(f"   💰 OpenAI Cost: ${self.cost_tracker['openai']:.4f}")
        print(f"   💰 Total Cost: ${sum(self.cost_tracker.values()):.4f}")
        
        return results
    
    def get_cost_summary(self) -> Dict[str, float]:
        """Get cost summary for AI usage"""
        return {
            'claude_cost': self.cost_tracker['anthropic'],
            'openai_cost': self.cost_tracker['openai'],
            'total_cost': sum(self.cost_tracker.values()),
            'average_cost_per_request': sum(self.cost_tracker.values()) / max(1, len(self.cost_tracker))
        }


def test_ai_content_generator():
    """Test the AI content generator with sample data"""
    print("🧪 TESTING AI CONTENT GENERATOR")
    print("=" * 50)
    
    # Create sample customer context
    customer = CustomerContext(
        customer_id="cust_123",
        name="Sarah Chen",
        email="sarah.chen@example.com",
        phone="555-0123",
        total_spent=2450.0,
        visit_count=12,
        last_visit_date=datetime.now() - timedelta(days=47),
        days_since_last_visit=47,
        favorite_services=["Brazilian Wax", "Facial"],
        favorite_staff=["Jennifer", "Maria"],
        churn_risk=0.73,
        ltv=3200.0,
        psychological_archetype="LOYALIST",
        psychological_state="PAIN",
        spending_trend="DECLINING"
    )
    
    # Create business context
    business = BusinessContext(
        business_name="Bashful Beauty",
        business_type="spa",
        staff_names=["Jennifer", "Maria", "Lisa"],
        service_names=["Brazilian Wax", "Facial", "Body Wax", "Eyebrow Wax"],
        average_service_price=85.0,
        location="Downtown",
        phone="555-BASHFUL",
        email="info@bashfulbeauty.com"
    )
    
    generator = AIContentGenerator()
    
    # Test different content types
    test_requests = [
        ContentRequest(
            content_type="retention_script",
            customer_context=customer,
            business_context=business,
            urgency="high",
            max_length=300
        ),
        ContentRequest(
            content_type="upsell_script", 
            customer_context=customer,
            business_context=business,
            max_length=200
        ),
        ContentRequest(
            content_type="review_response",
            customer_context=customer,
            business_context=business,
            additional_context="5-star review mentioning Jennifer's excellent service",
            max_length=150
        )
    ]
    
    # Generate content
    print("\n🤖 GENERATING PERSONALIZED CONTENT...")
    results = generator.generate_batch_content(test_requests)
    
    print("\n📝 RESULTS:")
    content_types = ["Retention Script", "Upsell Script", "Review Response"]
    
    for i, (content_type, result) in enumerate(zip(content_types, results)):
        print(f"\n{i+1}. {content_type}:")
        print(f"   {result}")
    
    # Cost summary
    costs = generator.get_cost_summary()
    print(f"\n💰 COST ANALYSIS:")
    print(f"   Total Cost: ${costs['total_cost']:.4f}")
    print(f"   Per Request: ${costs['total_cost']/len(test_requests):.4f}")
    
    print("\n✅ AI CONTENT GENERATOR TEST COMPLETE")
    
    return results


if __name__ == "__main__":
    test_ai_content_generator()