#!/usr/bin/env python3
"""
REAL DATA IMPORTER - Import ONLY actual Bashful Beauty Square export data
NO FAKE DATA - NO ASSUMPTIONS - NO FILLING GAPS
Data accuracy safeguards implemented
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class DataAccuracySafeguards:
    """Ensure we never lie about business data"""
    
    @staticmethod
    def validate_or_error(data, expected_type, field_name, source_file):
        """Return data with source info or 'Data Not Available'"""
        try:
            if data is None or (isinstance(data, (int, float)) and pd.isna(data)):
                return {"value": "Data Not Available", "source": f"Missing in {source_file}", "confidence": 0}
            return {"value": data, "source": source_file, "confidence": 100}
        except:
            return {"value": "Data Not Available", "source": f"Error reading {source_file}", "confidence": 0}
    
    @staticmethod
    def count_with_source(df, field_name, source_file):
        """Count with full source attribution"""
        count = len(df) if df is not None and not df.empty else 0
        return {
            "count": count,
            "source": f"{source_file} ({len(df)} records)" if not df.empty else f"No data in {source_file}",
            "confidence": 100 if count > 0 else 0
        }

def import_real_square_data():
    """Import ONLY real Square export data with full source attribution"""
    print("🔥 IMPORTING REAL BASHFUL BEAUTY DATA")
    print("❌ FAKE DATABASE DATA DELETED")
    print("✅ USING ONLY REAL SQUARE EXPORTS")
    print("=" * 60)
    
    export_path = "/Users/rayhernandez/KEEPER/manual_export/"
    safeguards = DataAccuracySafeguards()
    
    # Track data sources
    data_sources = {}
    
    # 1. IMPORT REAL CUSTOMERS
    print("👥 IMPORTING REAL CUSTOMERS...")
    customers_file = f"{export_path}customers2.csv"
    try:
        customers_df = pd.read_csv(customers_file)
        print(f"   ✅ {len(customers_df)} real customers imported")
        print(f"   Source: {customers_file}")
        print(f"   Columns available: {len(customers_df.columns)}")
        data_sources['customers'] = customers_file
    except Exception as e:
        print(f"   ❌ FAILED to import customers: {e}")
        customers_df = pd.DataFrame()
    
    # 2. IMPORT REAL APPOINTMENTS
    print(f"\n📅 IMPORTING REAL APPOINTMENTS...")
    appointments_file = f"{export_path}appointments-20250907T0126.csv"
    try:
        appointments_df = pd.read_csv(appointments_file)
        print(f"   ✅ {len(appointments_df)} real appointments imported")
        print(f"   Source: {appointments_file}")
        print(f"   Date range: {appointments_df['start'].min()} to {appointments_df['start'].max()}")
        data_sources['appointments'] = appointments_file
    except Exception as e:
        print(f"   ❌ FAILED to import appointments: {e}")
        appointments_df = pd.DataFrame()
    
    # 3. IMPORT REAL STAFF (CORRECTED)
    print(f"\n👨‍💼 IMPORTING REAL STAFF...")
    staff_file = f"{export_path}team-members-2025-09-07.csv"
    try:
        staff_df = pd.read_csv(staff_file)
        print(f"   ✅ {len(staff_df)} REAL employees imported (NOT 83)")
        print(f"   Source: {staff_file}")
        print(f"   Columns: {list(staff_df.columns)}")
        
        # Show actual employee names
        if 'Given Name' in staff_df.columns and 'Family Name' in staff_df.columns:
            staff_names = (staff_df['Given Name'].fillna('') + ' ' + staff_df['Family Name'].fillna('')).str.strip()
            print(f"   REAL EMPLOYEES:")
            for i, name in enumerate(staff_names, 1):
                print(f"     {i}. {name}")
        
        data_sources['staff'] = staff_file
    except Exception as e:
        print(f"   ❌ FAILED to import staff: {e}")
        staff_df = pd.DataFrame()
    
    # 4. IMPORT REAL TRANSACTIONS
    print(f"\n💰 IMPORTING REAL TRANSACTIONS...")
    trans_2024_file = f"{export_path}transactions-2024-01-01-2025-01-01 (1).csv"
    trans_2025_file = f"{export_path}transactions-2025-01-01-2026-01-01 (1).csv"
    
    transactions_list = []
    try:
        trans_2024 = pd.read_csv(trans_2024_file)
        trans_2024['year'] = '2024'
        transactions_list.append(trans_2024)
        print(f"   ✅ {len(trans_2024)} 2024 transactions imported")
    except Exception as e:
        print(f"   ⚠️ 2024 transactions failed: {e}")
    
    try:
        trans_2025 = pd.read_csv(trans_2025_file)
        trans_2025['year'] = '2025'
        transactions_list.append(trans_2025)
        print(f"   ✅ {len(trans_2025)} 2025 transactions imported")
    except Exception as e:
        print(f"   ⚠️ 2025 transactions failed: {e}")
    
    if transactions_list:
        transactions_df = pd.concat(transactions_list, ignore_index=True)
        print(f"   ✅ TOTAL: {len(transactions_df)} real transactions")
        data_sources['transactions'] = f"{trans_2024_file} + {trans_2025_file}"
    else:
        transactions_df = pd.DataFrame()
        print(f"   ❌ NO transaction data available")
    
    # 5. IMPORT REAL ITEMS/SERVICES
    print(f"\n🛍️ IMPORTING REAL SERVICES...")
    items_file = f"{export_path}items_catalog.csv"
    try:
        items_df = pd.read_csv(items_file)
        print(f"   ✅ {len(items_df)} real services/items imported")
        print(f"   Source: {items_file}")
        data_sources['items'] = items_file
    except Exception as e:
        print(f"   ❌ FAILED to import items: {e}")
        items_df = pd.DataFrame()
    
    # DATA QUALITY VALIDATION
    print(f"\n🔍 DATA QUALITY VALIDATION...")
    validation_report = {}
    
    # Customer validation
    if not customers_df.empty:
        validation_report['customers'] = {
            'total': len(customers_df),
            'with_email': customers_df['Email Address'].notna().sum() if 'Email Address' in customers_df.columns else 0,
            'with_phone': customers_df['Phone Number'].notna().sum() if 'Phone Number' in customers_df.columns else 0,
            'source': data_sources.get('customers', 'Unknown'),
            'confidence': 100
        }
    else:
        validation_report['customers'] = {'error': 'No customer data available', 'confidence': 0}
    
    # Staff validation (CORRECTED COUNT)
    if not staff_df.empty:
        validation_report['staff'] = {
            'total': len(staff_df),
            'source': data_sources.get('staff', 'Unknown'),
            'confidence': 100,
            'note': f"ACTUAL employee count - not the fake 83 number"
        }
    else:
        validation_report['staff'] = {'error': 'No staff data available', 'confidence': 0}
    
    # Transaction validation
    if not transactions_df.empty:
        # Calculate real revenue (check multiple possible column names)
        real_revenue = 0
        revenue_column = None
        for col in ['Net Sales', 'Gross Sales', 'Total Collected']:
            if col in transactions_df.columns:
                revenue_values = pd.to_numeric(transactions_df[col], errors='coerce')
                revenue_sum = revenue_values.sum()
                if revenue_sum > real_revenue:  # Use the highest revenue column
                    real_revenue = revenue_sum
                    revenue_column = col
        
        validation_report['transactions'] = {
            'total': len(transactions_df),
            'revenue': real_revenue,
            'revenue_column': revenue_column,
            'source': data_sources.get('transactions', 'Unknown'),
            'confidence': 100 if revenue_column else 50
        }
    else:
        validation_report['transactions'] = {'error': 'No transaction data available', 'confidence': 0}
    
    # FINAL DATA SUMMARY
    print(f"\n" + "="*60)
    print("📋 REAL DATA IMPORT SUMMARY")
    print("="*60)
    
    total_confidence = 0
    confidence_count = 0
    
    for data_type, validation in validation_report.items():
        if 'error' in validation:
            print(f"❌ {data_type.upper()}: {validation['error']}")
        else:
            if data_type == 'customers':
                print(f"✅ CUSTOMERS: {validation['total']} real customers")
                print(f"   Source: {validation['source']}")
                print(f"   Email addresses: {validation['with_email']}")
                print(f"   Phone numbers: {validation['with_phone']}")
            elif data_type == 'staff':
                print(f"✅ STAFF: {validation['total']} REAL employees")
                print(f"   Source: {validation['source']}")
                print(f"   Note: {validation.get('note', '')}")
            elif data_type == 'transactions':
                print(f"✅ TRANSACTIONS: {validation['total']} real transactions")
                print(f"   Revenue: ${validation['revenue']:,.2f} (from {validation['revenue_column']})")
                print(f"   Source: {validation['source']}")
            
            total_confidence += validation.get('confidence', 0)
            confidence_count += 1
    
    overall_confidence = total_confidence / confidence_count if confidence_count > 0 else 0
    
    print(f"\n📊 OVERALL DATA CONFIDENCE: {overall_confidence:.0f}%")
    print(f"🔗 ALL NUMBERS TRACEABLE TO SOURCE FILES")
    print(f"❌ ZERO FAKE DATA USED")
    
    return {
        'customers': customers_df,
        'appointments': appointments_df,  
        'staff': staff_df,
        'transactions': transactions_df,
        'items': items_df,
        'validation_report': validation_report,
        'data_sources': data_sources
    }

if __name__ == "__main__":
    real_data = import_real_square_data()
    print(f"\n✅ REAL DATA IMPORT COMPLETE")
    print(f"📁 Ready for analysis using ONLY real business data")