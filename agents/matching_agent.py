"""
MatchingAgent - Fuzzy Matching Between Square and External Files

Responsibility: Fuzzy matching between Square and external files
Success Metrics:
- 97%+ match accuracy
- <60 seconds for 1000 records
- Preserve all external context

From agents-dropset.md specification
"""

import asyncio
import logging
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from fuzzywuzzy import fuzz, process
import pandas as pd
import redis
import os
from supabase import create_client, Client
import openai


class MatchingAgent:
    def __init__(self):
        self.name = "MatchingAgent"
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
        
        # OpenAI for embeddings (97%+ accuracy requirement)
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Matching thresholds
        self.exact_match_threshold = 100
        self.fuzzy_match_threshold = 85  # High threshold for 97%+ accuracy
        self.min_confidence_threshold = 0.97  # 97%+ requirement
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.name)
    
    def match_customers(self, square_customers: List[Dict], external_file: str) -> List[Dict[str, Any]]:
        """Match uploaded CSV to Square customers
        
        - Normalize names (lowercase, remove punctuation)
        - Try exact match first
        - Fuzzy match on name (threshold: 85%)
        - Validate with phone/email if available
        - Return match confidence scores
        """
        self.logger.info(f"Starting customer matching with external file: {external_file}")
        
        try:
            # Publish agent status
            self._publish_agent_status('analyzing', 'customer_matching')
            
            # Load external data
            external_data = self._load_external_file(external_file)
            if not external_data:
                raise ValueError("Could not load external file")
            
            # Normalize data for matching
            normalized_square = self._normalize_customers(square_customers)
            normalized_external = self._normalize_external_data(external_data)
            
            matches = []
            start_time = datetime.now()
            
            for ext_record in normalized_external:
                match_result = self._find_best_match(ext_record, normalized_square)
                
                if match_result:
                    matches.append({
                        'external_record': ext_record,
                        'square_customer': match_result['customer'],
                        'confidence_score': match_result['confidence'],
                        'match_method': match_result['method'],
                        'match_fields': match_result['fields']
                    })
            
            # Performance check
            processing_time = (datetime.now() - start_time).total_seconds()
            records_per_second = len(normalized_external) / processing_time if processing_time > 0 else 0
            
            self.logger.info(f"Matched {len(matches)} out of {len(normalized_external)} records")
            self.logger.info(f"Processing rate: {records_per_second:.1f} records/second")
            
            # Validate 97% accuracy target
            high_confidence_matches = len([m for m in matches if m['confidence_score'] >= self.min_confidence_threshold])
            accuracy_rate = high_confidence_matches / len(matches) if matches else 0
            
            self.logger.info(f"High confidence matches: {high_confidence_matches} ({accuracy_rate:.1%})")
            
            if accuracy_rate < 0.97:
                self.logger.warning(f"Accuracy rate {accuracy_rate:.1%} is below 97% target")
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Customer matching failed: {str(e)}")
            raise
    
    def merge_context(self, customer_id: str, external_data: Dict[str, Any]) -> bool:
        """Merge external context into customer record
        
        - Append to metadata field
        - Re-generate embedding
        - Flag sensitive info (health, personal)
        """
        self.logger.info(f"Merging external context for customer {customer_id}")
        
        try:
            # Get existing customer record
            customer_result = self.supabase.table('customers').select('*').eq('id', customer_id).single().execute()
            
            if not customer_result.data:
                raise ValueError(f"Customer {customer_id} not found")
            
            customer = customer_result.data
            
            # Merge external context
            existing_metadata = json.loads(customer.get('metadata', '{}'))
            
            # Flag sensitive information
            flagged_data = self._flag_sensitive_info(external_data)
            
            # Merge contexts
            merged_metadata = {
                **existing_metadata,
                'external_context': flagged_data,
                'context_merged_at': datetime.now().isoformat(),
                'context_source': 'external_upload'
            }
            
            # Generate new embedding with merged context
            embedding = self._generate_customer_embedding(customer, merged_metadata)
            
            # Update customer record
            update_result = self.supabase.table('customers').update({
                'metadata': json.dumps(merged_metadata),
                'embedding': embedding,
                'updated_at': datetime.now().isoformat()
            }).eq('id', customer_id).execute()
            
            if update_result.data:
                self.logger.info(f"Successfully merged context for customer {customer_id}")
                return True
            else:
                raise ValueError("Update failed")
                
        except Exception as e:
            self.logger.error(f"Context merge failed for customer {customer_id}: {str(e)}")
            return False
    
    def _load_external_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Load external CSV file"""
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format. Use CSV or Excel.")
            
            return df.to_dict('records')
            
        except Exception as e:
            self.logger.error(f"Error loading file {file_path}: {str(e)}")
            return []
    
    def _normalize_customers(self, customers: List[Dict]) -> List[Dict]:
        """Normalize Square customer data for matching"""
        normalized = []
        
        for customer in customers:
            normalized_customer = {
                'original': customer,
                'id': customer.get('id'),
                'normalized_name': self._normalize_name(
                    f"{customer.get('given_name', '')} {customer.get('family_name', '')}"
                ),
                'normalized_email': self._normalize_email(customer.get('email_address', '')),
                'normalized_phone': self._normalize_phone(customer.get('phone_number', '')),
                'search_text': self._create_search_text(customer)
            }
            normalized.append(normalized_customer)
        
        return normalized
    
    def _normalize_external_data(self, external_data: List[Dict]) -> List[Dict]:
        """Normalize external data for matching"""
        normalized = []
        
        for record in external_data:
            # Try to identify name columns
            name_fields = self._identify_name_fields(record)
            email_fields = self._identify_email_fields(record)
            phone_fields = self._identify_phone_fields(record)
            
            full_name = self._combine_name_fields(record, name_fields)
            
            normalized_record = {
                'original': record,
                'normalized_name': self._normalize_name(full_name),
                'normalized_email': self._normalize_email(self._get_first_valid(record, email_fields)),
                'normalized_phone': self._normalize_phone(self._get_first_valid(record, phone_fields)),
                'search_text': ' '.join([str(v) for v in record.values() if v and str(v).strip()])
            }
            normalized.append(normalized_record)
        
        return normalized
    
    def _find_best_match(self, external_record: Dict, square_customers: List[Dict]) -> Optional[Dict]:
        """Find best match using multi-stage approach"""
        
        # Stage 1: Exact name match
        exact_match = self._exact_name_match(external_record, square_customers)
        if exact_match:
            return exact_match
        
        # Stage 2: Fuzzy name match with email/phone validation
        fuzzy_match = self._fuzzy_match_with_validation(external_record, square_customers)
        if fuzzy_match:
            return fuzzy_match
        
        # Stage 3: Email exact match
        email_match = self._email_exact_match(external_record, square_customers)
        if email_match:
            return email_match
        
        # Stage 4: Phone exact match
        phone_match = self._phone_exact_match(external_record, square_customers)
        if phone_match:
            return phone_match
        
        return None
    
    def _exact_name_match(self, external_record: Dict, square_customers: List[Dict]) -> Optional[Dict]:
        """Check for exact name matches"""
        external_name = external_record['normalized_name']
        if not external_name or len(external_name) < 2:
            return None
        
        for customer in square_customers:
            if customer['normalized_name'] == external_name:
                return {
                    'customer': customer,
                    'confidence': 1.0,
                    'method': 'exact_name',
                    'fields': ['name']
                }
        
        return None
    
    def _fuzzy_match_with_validation(self, external_record: Dict, square_customers: List[Dict]) -> Optional[Dict]:
        """Fuzzy name match with email/phone validation"""
        external_name = external_record['normalized_name']
        if not external_name or len(external_name) < 2:
            return None
        
        # Get fuzzy matches above threshold
        customer_names = [c['normalized_name'] for c in square_customers]
        matches = process.extract(external_name, customer_names, limit=5)
        
        for match_name, score in matches:
            if score >= self.fuzzy_match_threshold:
                # Find the customer with this name
                matching_customer = next((c for c in square_customers if c['normalized_name'] == match_name), None)
                
                if matching_customer:
                    # Validate with email/phone if available
                    validation_score = self._validate_match(external_record, matching_customer)
                    
                    final_confidence = min((score / 100.0) * validation_score, 1.0)
                    
                    if final_confidence >= self.min_confidence_threshold:
                        return {
                            'customer': matching_customer,
                            'confidence': final_confidence,
                            'method': 'fuzzy_name_validated',
                            'fields': ['name', 'email', 'phone']
                        }
        
        return None
    
    def _email_exact_match(self, external_record: Dict, square_customers: List[Dict]) -> Optional[Dict]:
        """Exact email match"""
        external_email = external_record['normalized_email']
        if not external_email:
            return None
        
        for customer in square_customers:
            if customer['normalized_email'] and customer['normalized_email'] == external_email:
                return {
                    'customer': customer,
                    'confidence': 0.99,  # Slightly lower than exact name to prefer name matches
                    'method': 'exact_email',
                    'fields': ['email']
                }
        
        return None
    
    def _phone_exact_match(self, external_record: Dict, square_customers: List[Dict]) -> Optional[Dict]:
        """Exact phone match"""
        external_phone = external_record['normalized_phone']
        if not external_phone or len(external_phone) < 10:
            return None
        
        for customer in square_customers:
            if customer['normalized_phone'] and customer['normalized_phone'] == external_phone:
                return {
                    'customer': customer,
                    'confidence': 0.98,  # Slightly lower than email
                    'method': 'exact_phone',
                    'fields': ['phone']
                }
        
        return None
    
    def _validate_match(self, external_record: Dict, square_customer: Dict) -> float:
        """Validate fuzzy match with email/phone"""
        validation_score = 1.0
        validation_count = 0
        
        # Email validation
        if external_record['normalized_email'] and square_customer['normalized_email']:
            validation_count += 1
            if external_record['normalized_email'] == square_customer['normalized_email']:
                validation_score *= 1.0  # Perfect match
            else:
                validation_score *= 0.7  # Email mismatch penalty
        
        # Phone validation
        if external_record['normalized_phone'] and square_customer['normalized_phone']:
            validation_count += 1
            if external_record['normalized_phone'] == square_customer['normalized_phone']:
                validation_score *= 1.0  # Perfect match
            else:
                validation_score *= 0.7  # Phone mismatch penalty
        
        # If no validation data available, reduce confidence
        if validation_count == 0:
            validation_score *= 0.85
        
        return validation_score
    
    def _normalize_name(self, name: str) -> str:
        """Normalize name for comparison"""
        if not name:
            return ""
        
        # Convert to lowercase
        normalized = name.lower()
        
        # Remove punctuation and extra spaces
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Remove common prefixes/suffixes
        prefixes = ['mr', 'mrs', 'ms', 'dr', 'prof']
        suffixes = ['jr', 'sr', 'ii', 'iii', 'iv']
        
        words = normalized.split()
        words = [w for w in words if w not in prefixes and w not in suffixes]
        
        return ' '.join(words)
    
    def _normalize_email(self, email: str) -> str:
        """Normalize email address"""
        if not email:
            return ""
        
        return email.lower().strip()
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number"""
        if not phone:
            return ""
        
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', str(phone))
        
        # Handle US phone numbers
        if len(digits) == 11 and digits.startswith('1'):
            digits = digits[1:]
        
        return digits if len(digits) >= 10 else ""
    
    def _identify_name_fields(self, record: Dict) -> List[str]:
        """Identify potential name fields in external data"""
        name_keywords = ['name', 'first', 'last', 'given', 'family', 'fname', 'lname', 'cliente', 'customer']
        
        name_fields = []
        for key in record.keys():
            key_lower = str(key).lower()
            if any(keyword in key_lower for keyword in name_keywords):
                name_fields.append(key)
        
        return name_fields
    
    def _identify_email_fields(self, record: Dict) -> List[str]:
        """Identify potential email fields"""
        email_keywords = ['email', 'mail', 'correo', '@']
        
        email_fields = []
        for key in record.keys():
            key_lower = str(key).lower()
            if any(keyword in key_lower for keyword in email_keywords):
                email_fields.append(key)
        
        return email_fields
    
    def _identify_phone_fields(self, record: Dict) -> List[str]:
        """Identify potential phone fields"""
        phone_keywords = ['phone', 'tel', 'mobile', 'cell', 'numero', 'telefono']
        
        phone_fields = []
        for key in record.keys():
            key_lower = str(key).lower()
            if any(keyword in key_lower for keyword in phone_keywords):
                phone_fields.append(key)
        
        return phone_fields
    
    def _combine_name_fields(self, record: Dict, name_fields: List[str]) -> str:
        """Combine name fields into full name"""
        name_parts = []
        
        for field in name_fields:
            value = record.get(field, '')
            if value and str(value).strip():
                name_parts.append(str(value).strip())
        
        return ' '.join(name_parts)
    
    def _get_first_valid(self, record: Dict, fields: List[str]) -> str:
        """Get first valid value from fields"""
        for field in fields:
            value = record.get(field, '')
            if value and str(value).strip():
                return str(value).strip()
        
        return ""
    
    def _create_search_text(self, customer: Dict) -> str:
        """Create searchable text for customer"""
        parts = [
            customer.get('given_name', ''),
            customer.get('family_name', ''),
            customer.get('email_address', ''),
            customer.get('phone_number', '')
        ]
        
        return ' '.join([p for p in parts if p and str(p).strip()])
    
    def _flag_sensitive_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Flag sensitive information in external data"""
        sensitive_keywords = [
            'health', 'medical', 'diagnosis', 'prescription', 'surgery',
            'divorce', 'custody', 'legal', 'lawsuit', 'bankruptcy',
            'ssn', 'social security', 'insurance', 'credit', 'loan'
        ]
        
        flagged_data = {}
        
        for key, value in data.items():
            value_str = str(value).lower() if value else ""
            
            # Check if potentially sensitive
            is_sensitive = any(keyword in value_str or keyword in str(key).lower() 
                             for keyword in sensitive_keywords)
            
            flagged_data[key] = {
                'value': value,
                'sensitive': is_sensitive,
                'flagged_at': datetime.now().isoformat() if is_sensitive else None
            }
        
        return flagged_data
    
    def _generate_customer_embedding(self, customer: Dict, metadata: Dict) -> List[float]:
        """Generate embedding for customer with merged context"""
        try:
            # Combine customer data with metadata for embedding
            text_for_embedding = f"""
            Customer: {customer.get('given_name', '')} {customer.get('family_name', '')}
            Email: {customer.get('email_address', '')}
            Phone: {customer.get('phone_number', '')}
            Context: {json.dumps(metadata.get('external_context', {}))}
            """
            
            response = openai.Embedding.create(
                model="text-embedding-3-large",
                input=text_for_embedding.strip()
            )
            
            return response['data'][0]['embedding']
            
        except Exception as e:
            self.logger.error(f"Error generating embedding: {str(e)}")
            return []
    
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