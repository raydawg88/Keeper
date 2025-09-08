const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
);

const ACCOUNT_ID = 'b491de6e-7d5b-4e0e-b1cd-625c6c4f7d81';

async function investigateDataIntegrity() {
  console.log('🔍 CRITICAL DATA INTEGRITY INVESTIGATION');
  console.log('========================================');
  console.log(`Target Account ID: ${ACCOUNT_ID}`);
  console.log('');

  try {
    // 1. VERIFY ACCOUNT DATA
    console.log('1. VERIFYING ACCOUNT DATA...');
    console.log('----------------------------');
    
    // Check if there's an accounts table
    const { data: accounts, error: accountError } = await supabase
      .from('accounts')
      .select('*')
      .eq('id', ACCOUNT_ID);
    
    if (accountError) {
      console.log('❌ Error querying accounts table:', accountError.message);
    } else if (accounts && accounts.length > 0) {
      console.log('✅ Found account data:');
      console.log(JSON.stringify(accounts[0], null, 2));
    } else {
      console.log('⚠️  No account data found in accounts table');
    }

    // Check all tables for account_id column
    console.log('\n2. CHECKING TABLE STRUCTURES...');
    console.log('--------------------------------');
    
    const tables = ['customers', 'transactions', 'appointments', 'services', 'service_types'];
    for (const table of tables) {
      console.log(`\nChecking ${table} table:`);
      const { data, error, count } = await supabase
        .from(table)
        .select('*', { count: 'exact' })
        .eq('account_id', ACCOUNT_ID)
        .limit(5);
      
      if (error) {
        console.log(`❌ Error querying ${table}:`, error.message);
      } else {
        console.log(`📊 Found ${count} records in ${table} for account ${ACCOUNT_ID}`);
        if (data && data.length > 0) {
          console.log('Sample record:');
          console.log(JSON.stringify(data[0], null, 2));
        }
      }
    }

    // 3. AUDIT ALL SERVICES
    console.log('\n3. AUDITING ALL SERVICES...');
    console.log('----------------------------');
    
    const { data: services, error: servicesError } = await supabase
      .from('services')
      .select('*')
      .eq('account_id', ACCOUNT_ID);
    
    if (servicesError) {
      console.log('❌ Error querying services:', servicesError.message);
    } else if (services) {
      console.log(`📊 Total services found: ${services.length}`);
      console.log('\n🔍 ALL SERVICES IN DATABASE:');
      services.forEach((service, index) => {
        console.log(`${index + 1}. ${service.name} (${service.service_type || 'No type'})`);
      });
      
      // Flag suspicious services for a Brazilian wax spa
      const suspiciousServices = services.filter(service => {
        const name = service.name.toLowerCase();
        return name.includes('haircut') || 
               name.includes('manicure') || 
               name.includes('pedicure') || 
               name.includes('massage') || 
               name.includes('facial') ||
               name.includes('hair') ||
               name.includes('nail');
      });
      
      if (suspiciousServices.length > 0) {
        console.log('\n🚨 SUSPICIOUS SERVICES FOR BRAZILIAN WAX SPA:');
        suspiciousServices.forEach(service => {
          console.log(`❌ ${service.name} - ${service.service_type}`);
        });
      }
      
      // Check for expected Brazilian wax services
      const expectedServices = services.filter(service => {
        const name = service.name.toLowerCase();
        return name.includes('brazilian') || 
               name.includes('wax') || 
               name.includes('bikini') ||
               name.includes('full body') ||
               name.includes('eyebrow');
      });
      
      if (expectedServices.length > 0) {
        console.log('\n✅ EXPECTED SERVICES FOR BRAZILIAN WAX SPA:');
        expectedServices.forEach(service => {
          console.log(`✅ ${service.name} - ${service.service_type}`);
        });
      }
    }

    // 4. CHECK SERVICE TYPES
    console.log('\n4. CHECKING SERVICE TYPES...');
    console.log('-----------------------------');
    
    const { data: serviceTypes, error: serviceTypesError } = await supabase
      .from('service_types')
      .select('*')
      .eq('account_id', ACCOUNT_ID);
    
    if (serviceTypesError) {
      console.log('❌ Error querying service_types:', serviceTypesError.message);
    } else if (serviceTypes) {
      console.log(`📊 Total service types: ${serviceTypes.length}`);
      console.log('\n🔍 ALL SERVICE TYPES:');
      serviceTypes.forEach((type, index) => {
        console.log(`${index + 1}. ${type.name}`);
      });
    }

    // 5. VALIDATE CUSTOMER SAMPLE
    console.log('\n5. CUSTOMER DATA SAMPLE...');
    console.log('---------------------------');
    
    const { data: customers, error: customersError } = await supabase
      .from('customers')
      .select('*')
      .eq('account_id', ACCOUNT_ID)
      .limit(10);
    
    if (customersError) {
      console.log('❌ Error querying customers:', customersError.message);
    } else if (customers) {
      console.log(`📊 Sample of ${customers.length} customers:`);
      customers.forEach((customer, index) => {
        console.log(`${index + 1}. ${customer.name || customer.first_name + ' ' + customer.last_name}`);
        if (customer.phone) console.log(`   Phone: ${customer.phone}`);
        if (customer.email) console.log(`   Email: ${customer.email}`);
        console.log('');
      });
    }

    // 6. CHECK RECENT TRANSACTIONS WITH SERVICES
    console.log('\n6. RECENT TRANSACTIONS WITH SERVICES...');
    console.log('----------------------------------------');
    
    const { data: recentTransactions, error: transactionsError } = await supabase
      .from('transactions')
      .select(`
        *,
        customers(name, first_name, last_name),
        services(name, service_type)
      `)
      .eq('account_id', ACCOUNT_ID)
      .order('created_at', { ascending: false })
      .limit(20);
    
    if (transactionsError) {
      console.log('❌ Error querying transactions:', transactionsError.message);
    } else if (recentTransactions) {
      console.log(`📊 ${recentTransactions.length} recent transactions:`);
      recentTransactions.forEach((transaction, index) => {
        const customerName = transaction.customers?.name || 
                           `${transaction.customers?.first_name || ''} ${transaction.customers?.last_name || ''}`.trim() ||
                           'Unknown Customer';
        const serviceName = transaction.services?.name || 'No service linked';
        console.log(`${index + 1}. ${customerName} - ${serviceName} - $${transaction.total_amount || 0}`);
      });
    }

    // 7. CHECK SQUARE BUSINESS INFO (if available)
    console.log('\n7. CHECKING FOR BUSINESS INFO...');
    console.log('---------------------------------');
    
    // Look for any business or account info tables
    const { data: businessInfo, error: businessError } = await supabase
      .from('business_info')
      .select('*')
      .eq('account_id', ACCOUNT_ID);
    
    if (businessError && !businessError.message.includes('does not exist')) {
      console.log('❌ Error querying business_info:', businessError.message);
    } else if (businessInfo && businessInfo.length > 0) {
      console.log('✅ Found business info:');
      console.log(JSON.stringify(businessInfo[0], null, 2));
    } else {
      console.log('⚠️  No business_info table or data found');
    }

    console.log('\n🔍 INVESTIGATION COMPLETE');
    console.log('=========================');
    
  } catch (error) {
    console.error('💥 Critical error during investigation:', error);
  }
}

investigateDataIntegrity();