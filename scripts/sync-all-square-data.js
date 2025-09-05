#!/usr/bin/env node

const https = require('https');
const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: '.env' });

// Configuration
const SQUARE_ACCESS_TOKEN = process.env.SQUARE_ACCESS_TOKEN || 'EAAAlnr4NgdhtBbcMt_Cz9zyufGUFuIlA19ibdvtoMRYmGnbLj90SdezKXj3Nnz6';
const SQUARE_ENVIRONMENT = process.env.SQUARE_ENVIRONMENT || 'production';
const SQUARE_BASE_URL = SQUARE_ENVIRONMENT === 'production' 
  ? 'https://connect.squareup.com'
  : 'https://connect.squareupsandbox.com';

// Supabase client
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
);

// Helper function to make Square API requests
function makeSquareRequest(endpoint, method = 'GET', data = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(`${SQUARE_BASE_URL}${endpoint}`);
    
    const options = {
      hostname: url.hostname,
      port: 443,
      path: url.pathname + url.search,
      method: method,
      headers: {
        'Square-Version': '2025-08-20',
        'Authorization': `Bearer ${SQUARE_ACCESS_TOKEN}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    };

    const req = https.request(options, (res) => {
      let responseData = '';

      res.on('data', (chunk) => {
        responseData += chunk;
      });

      res.on('end', () => {
        try {
          const parsedData = JSON.parse(responseData);
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(parsedData);
          } else {
            reject(new Error(`Square API error: ${res.statusCode} - ${JSON.stringify(parsedData)}`));
          }
        } catch (error) {
          reject(new Error(`Failed to parse response: ${error.message}`));
        }
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    if (data) {
      req.write(JSON.stringify(data));
    }

    req.end();
  });
}

// Sleep function for rate limiting
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Sync all customers with pagination
async function syncAllCustomers(accountId) {
  console.log('🚀 Starting complete customer sync...');
  let allCustomers = [];
  let cursor = null;
  let page = 1;
  let totalSynced = 0;
  
  do {
    try {
      console.log(`📄 Fetching customer page ${page}...`);
      
      let endpoint = '/v2/customers?limit=100';
      if (cursor) {
        endpoint += `&cursor=${encodeURIComponent(cursor)}`;
      }
      
      const response = await makeSquareRequest(endpoint);
      
      if (response.customers && response.customers.length > 0) {
        console.log(`   Found ${response.customers.length} customers on page ${page}`);
        
        // Transform and batch insert customers
        const customerData = response.customers.map(customer => ({
          account_id: accountId,
          square_customer_id: customer.id,
          name: `${customer.given_name || ''} ${customer.family_name || ''}`.trim() || 'Unknown',
          email: customer.email_address || null,
          phone: customer.phone_number || null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }));

        // Insert in batches to avoid overwhelming Supabase
        const BATCH_SIZE = 50;
        for (let i = 0; i < customerData.length; i += BATCH_SIZE) {
          const batch = customerData.slice(i, i + BATCH_SIZE);
          
          const { error } = await supabase
            .from('customers')
            .upsert(batch, { 
              onConflict: 'square_customer_id',
              ignoreDuplicates: false 
            });

          if (error) {
            console.error(`❌ Error inserting customer batch:`, error);
          } else {
            totalSynced += batch.length;
            console.log(`   ✅ Synced ${batch.length} customers (total: ${totalSynced})`);
          }
          
          // Rate limiting - pause between batches
          await sleep(200);
        }
        
        allCustomers.push(...response.customers);
      }
      
      cursor = response.cursor;
      page++;
      
      // Rate limiting - pause between pages
      await sleep(500);
      
    } catch (error) {
      console.error(`❌ Error fetching customers page ${page}:`, error.message);
      break;
    }
  } while (cursor);
  
  console.log(`🎉 Customer sync complete! Total customers synced: ${totalSynced}`);
  return allCustomers;
}

// Sync all payments with pagination
async function syncAllPayments(accountId) {
  console.log('💰 Starting complete payments sync...');
  let allPayments = [];
  let cursor = null;
  let page = 1;
  let totalSynced = 0;
  
  do {
    try {
      console.log(`📄 Fetching payments page ${page}...`);
      
      let endpoint = '/v2/payments?limit=100';
      if (cursor) {
        endpoint += `&cursor=${encodeURIComponent(cursor)}`;
      }
      
      const response = await makeSquareRequest(endpoint);
      
      if (response.payments && response.payments.length > 0) {
        console.log(`   Found ${response.payments.length} payments on page ${page}`);
        
        // Transform and batch insert payments
        const paymentData = response.payments
          .filter(payment => payment.status === 'COMPLETED')
          .map(payment => ({
            account_id: accountId,
            square_payment_id: payment.id,
            amount: parseFloat(payment.amount_money.amount) / 100, // Convert from cents
            currency: payment.amount_money.currency,
            status: payment.status,
            created_at: payment.created_at || new Date().toISOString(),
            updated_at: new Date().toISOString()
          }));

        if (paymentData.length > 0) {
          // Insert in batches
          const BATCH_SIZE = 50;
          for (let i = 0; i < paymentData.length; i += BATCH_SIZE) {
            const batch = paymentData.slice(i, i + BATCH_SIZE);
            
            const { error } = await supabase
              .from('transactions')
              .upsert(batch, { 
                onConflict: 'square_payment_id',
                ignoreDuplicates: false 
              });

            if (error) {
              console.error(`❌ Error inserting payment batch:`, error);
            } else {
              totalSynced += batch.length;
              console.log(`   ✅ Synced ${batch.length} payments (total: ${totalSynced})`);
            }
            
            await sleep(200);
          }
        }
        
        allPayments.push(...response.payments);
      }
      
      cursor = response.cursor;
      page++;
      
      await sleep(500);
      
    } catch (error) {
      console.error(`❌ Error fetching payments page ${page}:`, error.message);
      break;
    }
  } while (cursor);
  
  console.log(`🎉 Payments sync complete! Total payments synced: ${totalSynced}`);
  return allPayments;
}

// Main sync function
async function syncAllSquareData() {
  try {
    console.log('🎯 Starting complete Square data sync for Bashful Beauty...\n');
    
    // Get account info
    const { data: accounts } = await supabase
      .from('accounts')
      .select('id')
      .eq('business_name', 'Bashful Beauty')
      .single();
    
    if (!accounts) {
      console.error('❌ Bashful Beauty account not found in database');
      return;
    }
    
    const accountId = accounts.id;
    console.log(`📊 Using account ID: ${accountId}\n`);
    
    // Sync all customers
    const customers = await syncAllCustomers(accountId);
    console.log(`📈 Total customers retrieved: ${customers.length}\n`);
    
    // Sync all payments
    const payments = await syncAllPayments(accountId);
    console.log(`📈 Total payments retrieved: ${payments.length}\n`);
    
    // Final summary
    console.log('🏁 SYNC SUMMARY:');
    console.log(`   Customers: ${customers.length} retrieved`);
    console.log(`   Payments: ${payments.length} retrieved`);
    console.log('   Status: Complete ✅');
    
  } catch (error) {
    console.error('💥 Sync failed:', error);
  }
}

// Run the sync
if (require.main === module) {
  syncAllSquareData();
}

module.exports = { syncAllSquareData };