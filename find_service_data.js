const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
);

const ACCOUNT_ID = 'b491de6e-7d5b-4e0e-b1cd-625c6c4f7d81';

async function findServiceData() {
  console.log('🔍 FINDING SERVICE DATA LOCATION');
  console.log('=================================');

  try {
    // Get all table names in the database
    console.log('1. LISTING ALL TABLES...');
    const { data: tables, error: tableError } = await supabase
      .rpc('get_table_names');
    
    if (tableError) {
      console.log('❌ Error getting table names:', tableError.message);
      
      // Alternative method - try common table names
      console.log('\n📋 CHECKING COMMON TABLE NAMES...');
      const commonTables = [
        'appointments', 'customers', 'transactions', 'bookings', 
        'catalog_items', 'orders', 'order_items', 'payments',
        'variations', 'categories', 'items', 'modifiers',
        'services', 'service_types', 'service_variations'
      ];
      
      for (const table of commonTables) {
        try {
          const { data, error, count } = await supabase
            .from(table)
            .select('*', { count: 'exact' })
            .limit(1);
          
          if (!error) {
            console.log(`✅ ${table}: ${count} records`);
            if (data && data.length > 0) {
              console.log('Sample columns:', Object.keys(data[0]).join(', '));
            }
          }
        } catch (e) {
          // Table doesn't exist, skip
        }
      }
    }

    // Check appointments table more thoroughly for service info
    console.log('\n2. DEEP DIVE INTO APPOINTMENTS...');
    console.log('----------------------------------');
    
    const { data: appointments, error: appointmentsError } = await supabase
      .from('appointments')
      .select('*')
      .eq('account_id', ACCOUNT_ID)
      .limit(10);
    
    if (appointmentsError) {
      console.log('❌ Error querying appointments:', appointmentsError.message);
    } else if (appointments && appointments.length > 0) {
      console.log(`📊 Sample appointments with service info:`);
      appointments.forEach((appt, index) => {
        console.log(`\n${index + 1}. Appointment ID: ${appt.square_booking_id}`);
        console.log(`   Service Variation ID: ${appt.service_variation_id}`);
        console.log(`   Duration: ${appt.duration_minutes} minutes`);
        console.log(`   Status: ${appt.status}`);
        console.log(`   Date: ${appt.start_at}`);
        if (appt.service_name) console.log(`   Service Name: ${appt.service_name}`);
        if (appt.service_type) console.log(`   Service Type: ${appt.service_type}`);
      });
    }

    // Check if service variations are stored in Square catalog format
    console.log('\n3. CHECKING FOR SQUARE CATALOG DATA...');
    console.log('---------------------------------------');
    
    // Look for any tables that might contain Square catalog items
    const catalogTables = ['catalog_items', 'square_catalog', 'items', 'variations'];
    
    for (const table of catalogTables) {
      try {
        const { data, error, count } = await supabase
          .from(table)
          .select('*', { count: 'exact' })
          .eq('account_id', ACCOUNT_ID)
          .limit(5);
        
        if (!error && data) {
          console.log(`\n✅ Found ${table} table with ${count} records:`);
          data.forEach((item, index) => {
            console.log(`${index + 1}. ${JSON.stringify(item, null, 2)}`);
          });
        }
      } catch (e) {
        // Table doesn't exist, continue
      }
    }

    // Check transactions for service-related data
    console.log('\n4. ANALYZING TRANSACTIONS FOR SERVICE DATA...');
    console.log('----------------------------------------------');
    
    const { data: transactions, error: transError } = await supabase
      .from('transactions')
      .select('*')
      .eq('account_id', ACCOUNT_ID)
      .not('square_data', 'is', null)
      .limit(5);
    
    if (transError) {
      console.log('❌ Error querying transactions:', transError.message);
    } else if (transactions && transactions.length > 0) {
      console.log('📊 Transactions with Square data:');
      transactions.forEach((trans, index) => {
        console.log(`\n${index + 1}. Transaction: ${trans.square_payment_id}`);
        console.log(`   Amount: $${trans.amount || trans.amount_cents/100}`);
        if (trans.square_data) {
          try {
            const squareData = typeof trans.square_data === 'string' ? 
              JSON.parse(trans.square_data) : trans.square_data;
            console.log(`   Square Data Keys: ${Object.keys(squareData).join(', ')}`);
            
            // Look for line items or order details
            if (squareData.line_items || squareData.order?.line_items) {
              const lineItems = squareData.line_items || squareData.order.line_items;
              console.log('   Line Items:');
              lineItems.forEach((item, i) => {
                console.log(`     ${i+1}. ${item.name || item.catalog_object_id || 'Unknown'}`);
                if (item.variation_name) console.log(`        Variation: ${item.variation_name}`);
                if (item.category_name) console.log(`        Category: ${item.category_name}`);
              });
            }
          } catch (e) {
            console.log('   Square Data (raw):', trans.square_data);
          }
        }
      });
    }

    // Get unique service variation IDs from appointments
    console.log('\n5. ANALYZING SERVICE VARIATIONS...');
    console.log('-----------------------------------');
    
    const { data: variationIds, error: varError } = await supabase
      .from('appointments')
      .select('service_variation_id')
      .eq('account_id', ACCOUNT_ID)
      .not('service_variation_id', 'is', null);
    
    if (varError) {
      console.log('❌ Error getting variation IDs:', varError.message);
    } else if (variationIds && variationIds.length > 0) {
      const uniqueVariations = [...new Set(variationIds.map(v => v.service_variation_id))];
      console.log(`📊 Found ${uniqueVariations.length} unique service variations:`);
      uniqueVariations.slice(0, 20).forEach((variation, index) => {
        console.log(`${index + 1}. ${variation}`);
      });
      
      if (uniqueVariations.length > 20) {
        console.log(`... and ${uniqueVariations.length - 20} more`);
      }
    }

    console.log('\n🔍 SERVICE DATA INVESTIGATION COMPLETE');
    console.log('=====================================');
    
  } catch (error) {
    console.error('💥 Critical error during service investigation:', error);
  }
}

findServiceData();