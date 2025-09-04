#!/usr/bin/env python3
"""
Multi-Model Insight Generation for Keeper
Uses Claude, GPT-4, and Gemini for comprehensive business analysis
"""
import os
import json
import asyncio
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
import google.generativeai as genai
from dataclasses import dataclass

# Load environment variables
load_dotenv()

@dataclass
class ModelInsight:
    """Insight from a specific AI model"""
    model_name: str
    insight_text: str
    confidence: float
    reasoning: str
    dollar_value: float
    action_items: List[str]

class MultiModelInsightEngine:
    """Generates insights using multiple AI models for validation"""
    
    def __init__(self):
        """Initialize all AI model clients"""
        
        # OpenAI setup
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Claude setup  
        self.claude_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        # Gemini setup
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # Banned obvious insights
        self.banned_insights = [
            "weekends are busier",
            "holidays affect sales", 
            "customers prefer discounts",
            "rain causes cancellations",
            "busy times have more sales"
        ]
    
    async def generate_gpt4_insights(self, business_data: Dict) -> List[ModelInsight]:
        """Generate insights using GPT-4"""
        
        prompt = f"""
        Analyze this spa/salon business data and find specific revenue opportunities with exact dollar values.

        Business Data:
        - Customers: {business_data.get('customer_count', 0)}
        - Transactions: {business_data.get('transaction_count', 0)}
        - Average Transaction: ${business_data.get('avg_transaction', 0):.2f}
        - Tip Rate: {business_data.get('tip_rate', 0):.1%}
        - Monthly Revenue: ${business_data.get('monthly_revenue', 0):.2f}

        CRITICAL REQUIREMENTS:
        1. Each insight must have a specific dollar value (minimum $100)
        2. Confidence must be 75% or higher
        3. NO obvious insights like "weekends are busier" 
        4. Provide specific, actionable steps
        5. Focus on: churn prevention, tip optimization, upselling, staff efficiency

        Return JSON format:
        {{
            "insights": [
                {{
                    "title": "specific insight title",
                    "description": "detailed explanation", 
                    "confidence": 0.85,
                    "dollar_value": 1500.0,
                    "reasoning": "why this opportunity exists",
                    "action_items": ["specific action 1", "specific action 2"]
                }}
            ]
        }}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500
            )
            
            result = json.loads(response.choices[0].message.content)
            
            insights = []
            for insight_data in result.get('insights', []):
                if not self._is_obvious_insight(insight_data.get('title', '')):
                    insights.append(ModelInsight(
                        model_name="GPT-4",
                        insight_text=insight_data.get('title', ''),
                        confidence=insight_data.get('confidence', 0.0),
                        reasoning=insight_data.get('reasoning', ''),
                        dollar_value=insight_data.get('dollar_value', 0.0),
                        action_items=insight_data.get('action_items', [])
                    ))
            
            return insights
            
        except Exception as e:
            print(f"❌ GPT-4 insight generation failed: {e}")
            return []
    
    async def generate_claude_insights(self, business_data: Dict) -> List[ModelInsight]:
        """Generate insights using Claude (superior reasoning)"""
        
        prompt = f"""
        You are an expert business analyst specializing in spa/salon revenue optimization. 
        Analyze this business data and identify high-value opportunities.

        Business Data:
        - Customer Count: {business_data.get('customer_count', 0)}
        - Transaction Count: {business_data.get('transaction_count', 0)}
        - Average Transaction: ${business_data.get('avg_transaction', 0):.2f}
        - Current Tip Rate: {business_data.get('tip_rate', 0):.1%}
        - Monthly Revenue: ${business_data.get('monthly_revenue', 0):.2f}

        Find opportunities worth $500+ each. Focus on:
        1. Customer retention patterns
        2. Service optimization 
        3. Staff performance improvements
        4. Revenue per customer enhancement

        Avoid obvious insights. Be specific about implementation and dollar impact.

        Provide 2-3 high-confidence insights in JSON format:
        {{
            "insights": [
                {{
                    "opportunity": "specific opportunity title",
                    "explanation": "detailed business reasoning",
                    "confidence_level": 0.88,
                    "annual_value": 3600.0,
                    "implementation": ["step 1", "step 2", "step 3"]
                }}
            ]
        }}
        """
        
        try:
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1500,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract JSON from Claude's response
            content = response.content[0].text
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            json_content = content[json_start:json_end]
            
            result = json.loads(json_content)
            
            insights = []
            for insight_data in result.get('insights', []):
                if not self._is_obvious_insight(insight_data.get('opportunity', '')):
                    insights.append(ModelInsight(
                        model_name="Claude-3-Sonnet",
                        insight_text=insight_data.get('opportunity', ''),
                        confidence=insight_data.get('confidence_level', 0.0),
                        reasoning=insight_data.get('explanation', ''),
                        dollar_value=insight_data.get('annual_value', 0.0),
                        action_items=insight_data.get('implementation', [])
                    ))
            
            return insights
            
        except Exception as e:
            print(f"❌ Claude insight generation failed: {e}")
            return []
    
    async def generate_gemini_insights(self, business_data: Dict) -> List[ModelInsight]:
        """Generate insights using Gemini (validation & backup)"""
        
        prompt = f"""
        Business Analysis Task: Spa/Salon Revenue Optimization

        Data Summary:
        Customers: {business_data.get('customer_count', 0)}
        Transactions: {business_data.get('transaction_count', 0)}
        Avg Transaction: ${business_data.get('avg_transaction', 0):.2f}
        Tip Rate: {business_data.get('tip_rate', 0):.1%}
        Monthly Revenue: ${business_data.get('monthly_revenue', 0):.2f}

        Identify 1-2 unique revenue opportunities not typically discovered by standard analysis.
        Each opportunity must be worth $1000+ annually.
        
        Requirements:
        - Specific dollar calculations
        - Confidence score (75%+ only)
        - Avoid generic business advice
        - Focus on data-driven insights

        Format as JSON:
        {{
            "opportunities": [
                {{
                    "insight": "specific insight description",
                    "value_calculation": "how you calculated the dollar amount", 
                    "confidence": 0.82,
                    "estimated_value": 2400.0,
                    "next_steps": ["action 1", "action 2"]
                }}
            ]
        }}
        """
        
        try:
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1000
                )
            )
            
            # Extract JSON from response
            content = response.text
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            json_content = content[json_start:json_end]
            
            result = json.loads(json_content)
            
            insights = []
            for insight_data in result.get('opportunities', []):
                if not self._is_obvious_insight(insight_data.get('insight', '')):
                    insights.append(ModelInsight(
                        model_name="Gemini-Pro",
                        insight_text=insight_data.get('insight', ''),
                        confidence=insight_data.get('confidence', 0.0),
                        reasoning=insight_data.get('value_calculation', ''),
                        dollar_value=insight_data.get('estimated_value', 0.0),
                        action_items=insight_data.get('next_steps', [])
                    ))
            
            return insights
            
        except Exception as e:
            print(f"❌ Gemini insight generation failed: {e}")
            return []
    
    def _is_obvious_insight(self, insight_text: str) -> bool:
        """Check if insight is obvious and should be filtered"""
        insight_lower = insight_text.lower()
        
        for banned in self.banned_insights:
            if banned in insight_lower:
                return True
        
        return False
    
    async def generate_multi_model_insights(self, business_data: Dict) -> Dict:
        """
        Generate insights using all three models and cross-validate
        
        Args:
            business_data: Dictionary with business metrics
            
        Returns:
            Dictionary with insights from all models and consensus
        """
        print("🤖 Generating multi-model insights...")
        print("=" * 50)
        
        # Run all models in parallel
        gpt4_task = self.generate_gpt4_insights(business_data)
        claude_task = self.generate_claude_insights(business_data)
        gemini_task = self.generate_gemini_insights(business_data)
        
        # Wait for all models to complete
        gpt4_insights, claude_insights, gemini_insights = await asyncio.gather(
            gpt4_task, claude_task, gemini_task, return_exceptions=True
        )
        
        # Handle any exceptions
        if isinstance(gpt4_insights, Exception):
            print(f"⚠️  GPT-4 failed: {gpt4_insights}")
            gpt4_insights = []
        
        if isinstance(claude_insights, Exception):
            print(f"⚠️  Claude failed: {claude_insights}")
            claude_insights = []
            
        if isinstance(gemini_insights, Exception):
            print(f"⚠️  Gemini failed: {gemini_insights}")
            gemini_insights = []
        
        # Combine and analyze insights
        all_insights = gpt4_insights + claude_insights + gemini_insights
        
        # Filter by confidence and value thresholds
        high_quality_insights = [
            insight for insight in all_insights
            if insight.confidence >= 0.75 and insight.dollar_value >= 500
        ]
        
        # Calculate consensus and total potential
        total_potential = sum(insight.dollar_value for insight in high_quality_insights)
        model_counts = {
            'GPT-4': len(gpt4_insights),
            'Claude': len(claude_insights), 
            'Gemini': len(gemini_insights)
        }
        
        results = {
            'total_insights': len(high_quality_insights),
            'total_potential_value': total_potential,
            'model_breakdown': model_counts,
            'insights_by_model': {
                'gpt4': gpt4_insights,
                'claude': claude_insights,
                'gemini': gemini_insights
            },
            'high_confidence_insights': high_quality_insights,
            'success': total_potential >= 3000  # $3000+ target
        }
        
        print(f"📊 Results Summary:")
        print(f"   GPT-4: {len(gpt4_insights)} insights")
        print(f"   Claude: {len(claude_insights)} insights") 
        print(f"   Gemini: {len(gemini_insights)} insights")
        print(f"   High Quality: {len(high_quality_insights)} insights")
        print(f"   Total Value: ${total_potential:,.2f}")
        
        if total_potential >= 3000:
            print(f"   🎯 SUCCESS: ${total_potential:,.2f} exceeds $3,000 target!")
        else:
            print(f"   ⚠️  Below target: ${total_potential:,.2f} (need $3,000+)")
        
        return results

async def test_multi_model_insights():
    """Test multi-model insight generation"""
    
    # Simulate spa business data
    test_business_data = {
        'customer_count': 250,
        'transaction_count': 800,
        'avg_transaction': 85.50,
        'tip_rate': 0.45,  # 45% tip rate
        'monthly_revenue': 12750.00
    }
    
    engine = MultiModelInsightEngine()
    results = await engine.generate_multi_model_insights(test_business_data)
    
    print(f"\n🎯 Multi-Model Test Results:")
    print(f"   Total Insights: {results['total_insights']}")
    print(f"   Potential Value: ${results['total_potential_value']:,.2f}")
    print(f"   Target Met: {'✅' if results['success'] else '❌'}")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_multi_model_insights())