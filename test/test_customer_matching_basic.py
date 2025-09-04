#!/usr/bin/env python3
"""
Test customer matching basic functionality without OpenAI API
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.lib.db.customer_matching import CustomerMatcher

def test_basic_matching_logic():
    """Test customer matching logic without API calls"""
    print("🧪 Testing Customer Matching Basic Logic")
    print("=" * 50)
    
    try:
        test_account_id = "27d755f9-87fd-40e8-a541-3a0478816395"
        matcher = CustomerMatcher(test_account_id)
        
        # Test customer text creation
        sample_customers = [
            {
                'first_name': 'John',
                'last_name': 'Smith', 
                'email': 'john.smith@email.com',
                'phone': '+1-555-123-4567'
            },
            {
                'first_name': 'Jane',
                'last_name': 'Doe',
                'email': 'jane.doe@gmail.com',
                'phone': '555.987.6543'
            },
            {
                'first_name': '',
                'last_name': '',
                'email': 'customer@spa.com',
                'phone': '(555) 111-2222'
            }
        ]
        
        print("📝 Testing customer text generation:")
        for i, customer in enumerate(sample_customers):
            customer_text = matcher._create_customer_text(customer)
            print(f"   Customer {i+1}: '{customer_text}'")
        
        # Test similarity calculation with mock vectors
        print("\n🎯 Testing similarity calculation:")
        mock_vec1 = [0.1, 0.2, 0.3, 0.4, 0.5]
        mock_vec2 = [0.1, 0.2, 0.3, 0.4, 0.5]  # Identical
        mock_vec3 = [0.5, 0.4, 0.3, 0.2, 0.1]  # Different
        
        similarity_identical = matcher._cosine_similarity(mock_vec1, mock_vec2)
        similarity_different = matcher._cosine_similarity(mock_vec1, mock_vec3)
        
        print(f"   Identical vectors: {similarity_identical:.3f} (should be 1.0)")
        print(f"   Different vectors: {similarity_different:.3f} (should be < 1.0)")
        
        # Test match explanation
        print("\n💡 Testing match explanation:")
        input_customer = sample_customers[0]
        matched_customer = {
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'john.smith@email.com',
            'phone': '5551234567'
        }
        
        reasons = matcher._explain_match(input_customer, matched_customer, 0.95)
        print(f"   Match reasons: {reasons}")
        
        print("\n✅ Basic matching logic tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Basic matching test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_basic_matching_logic()
    sys.exit(0 if success else 1)