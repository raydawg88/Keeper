#!/usr/bin/env node

const https = require('https');
const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: '.env' });

// Configuration
const SQUARE_ACCESS_TOKEN = process.env.SQUARE_ACCESS_TOKEN;
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

// Sync payments for a specific year with pagination - FIXED VERSION
async function syncPaymentsForYear(accountId, year) {
  console.log(`💰 Syncing payments for ${year}...`);
  let totalSynced = 0;
  let totalRevenue = 0;
  let cursor = null;
  let page = 1;
  
  const startDate = `${year}-01-01T00:00:00Z`;
  const endDate = `${year}-12-31T23:59:59Z`;
  
  do {
    try {
      console.log(`   📄 Page ${page}...`);
      
      let endpoint = `/v2/payments?begin_time=${startDate}&end_time=${endDate}&limit=100`;
      if (cursor) {
        endpoint += `&cursor=${encodeURIComponent(cursor)}`;
      }
      
      const response = await makeSquareRequest(endpoint);
      
      if (response.payments && response.payments.length > 0) {
        // Transform payment data - USING ONLY EXISTING COLUMNS
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
              updated_at: payment.updated_at || new Date().toISOString()
            };
          });

        if (paymentData.length > 0) {
          // Insert in batches
          const BATCH_SIZE = 100;
          for (let i = 0; i < paymentData.length; i += BATCH_SIZE) {
            const batch = paymentData.slice(i, i + BATCH_SIZE);
            
            const { error } = await supabase
              .from('transactions')
              .insert(batch);

            if (error) {
              console.error(`   ❌ Error inserting ${year} batch:`, error.message);
            } else {
              totalSynced += batch.length;
            }
            
            await sleep(100); // Faster rate limiting
          }
        }
      }
      
      cursor = response.cursor;
      page++;
      
      await sleep(200); // Faster between pages
      
    } catch (error) {
      console.error(`   ❌ Error fetching ${year} page ${page}:`, error.message);
      break;
    }
  } while (cursor);
  
  console.log(`   ✅ ${year}: ${totalSynced} payments, $${totalRevenue.toFixed(2)} revenue`);
  return { count: totalSynced, revenue: totalRevenue };
}

// Clear existing transactions
async function clearExistingTransactions() {
  console.log('🧹 Clearing existing transactions...');
  const { error } = await supabase
    .from('transactions')
    .delete()
    .neq('id', '00000000-0000-0000-0000-000000000000');
  
  if (error) {
    console.error('❌ Error clearing transactions:', error);
    return false;
  }
  
  console.log('✅ Existing transactions cleared');
  return true;
}

// Main function - OPTIMIZED VERSION
async function syncAllHistoricalPaymentsFixed() {
  try {
    console.log('🎯 Starting FIXED historical payment sync (2017-2025)...\n');
    
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
    
    // Clear existing data
    const cleared = await clearExistingTransactions();
    if (!cleared) return;
    
    // Sync each year - OPTIMIZED ORDER (most recent first for immediate value)
    const years = [2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017];
    let grandTotal = { count: 0, revenue: 0 };
    
    console.log('🚀 Syncing 8 years of payment history (recent first)...\n');
    
    for (const year of years) {
      const yearResult = await syncPaymentsForYear(accountId, year);
      grandTotal.count += yearResult.count;
      grandTotal.revenue += yearResult.revenue;
      
      // Progress indicator
      const progress = ((years.indexOf(year) + 1) / years.length * 100).toFixed(0);
      console.log(`   📈 Progress: ${progress}% complete (${grandTotal.count.toLocaleString()} payments, $${grandTotal.revenue.toLocaleString()})\n`);
      
      // Pause between years
      await sleep(500);
    }
    
    // Final summary with business intelligence insights
    console.log('🏁 HISTORICAL SYNC COMPLETE!');
    console.log('='.repeat(60));
    console.log(`🎉 BASHFUL BEAUTY - 8 YEAR BUSINESS INTELLIGENCE SUMMARY`);
    console.log('='.repeat(60));
    console.log(`📊 Total Transactions: ${grandTotal.count.toLocaleString()}`);
    console.log(`💰 Total Revenue: $${grandTotal.revenue.toLocaleString('en-US', { maximumFractionDigits: 2 })}`);
    console.log(`📅 Time Period: 2017-2025 (8 years)`);
    console.log(`📈 Average Annual Revenue: $${Math.round(grandTotal.revenue / 8).toLocaleString()}`);
    console.log(`💵 Average Transaction: $${Math.round(grandTotal.revenue / grandTotal.count)}`);
    console.log(`📊 Transactions per Year: ${Math.round(grandTotal.count / 8).toLocaleString()}`);
    console.log('='.repeat(60));
    console.log('✨ Ready for advanced business analytics and insights!');
    console.log('🎯 Next: Create appointments table and build BI dashboard');
    console.log('='.repeat(60));
    
  } catch (error) {
    console.error('💥 Historical sync failed:', error);
  }
}

// Run the complete sync
if (require.main === module) {
  syncAllHistoricalPaymentsFixed();
}

module.exports = { syncAllHistoricalPaymentsFixed };