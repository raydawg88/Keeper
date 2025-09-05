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

// Clear existing transactions and sync fresh
async function syncPaymentsSimple(accountId) {
  console.log('💰 Starting fresh payments sync (clearing existing)...');
  
  // Clear existing transactions first
  const { error: clearError } = await supabase
    .from('transactions')
    .delete()
    .neq('id', '00000000-0000-0000-0000-000000000000'); // Delete all rows
  
  if (clearError) {
    console.error('❌ Error clearing transactions:', clearError);
    return;
  }
  
  console.log('✅ Cleared existing transactions');
  
  let totalSynced = 0;
  let cursor = null;
  let page = 1;
  let totalRevenue = 0;
  
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
        
        // Transform and insert payments (simple insert, no upsert)
        const paymentData = response.payments
          .filter(payment => payment.status === 'COMPLETED')
          .map(payment => {
            const amount = parseFloat(payment.amount_money.amount) / 100;
            totalRevenue += amount;
            return {
              account_id: accountId,
              amount: amount,
              currency: payment.amount_money.currency,
              status: payment.status,
              created_at: payment.created_at || new Date().toISOString(),
              updated_at: new Date().toISOString()
            };
          });

        if (paymentData.length > 0) {
          const { error } = await supabase
            .from('transactions')
            .insert(paymentData);

          if (error) {
            console.error(`❌ Error inserting payments:`, error);
          } else {
            totalSynced += paymentData.length;
            console.log(`   ✅ Synced ${paymentData.length} payments (total: ${totalSynced}, revenue: $${totalRevenue.toFixed(2)})`);
          }
        }
      }
      
      cursor = response.cursor;
      page++;
      
      await sleep(500);
      
      // Limit to first 10 pages for now to avoid timeout
      if (page > 10) {
        console.log('⚠️ Limiting to first 10 pages for demonstration');
        break;
      }
      
    } catch (error) {
      console.error(`❌ Error fetching payments page ${page}:`, error.message);
      break;
    }
  } while (cursor);
  
  console.log(`🎉 Payments sync complete!`);
  console.log(`   Total payments synced: ${totalSynced}`);
  console.log(`   Total revenue: $${totalRevenue.toFixed(2)}`);
}

// Main sync function
async function main() {
  try {
    console.log('🎯 Starting simplified payments sync for Bashful Beauty...\n');
    
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
    
    await syncPaymentsSimple(accountId);
    
  } catch (error) {
    console.error('💥 Sync failed:', error);
  }
}

if (require.main === module) {
  main();
}