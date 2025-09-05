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
        'Square-Version': '2024-07-17',
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
            reject(new Error(`Square API Error: ${res.statusCode} - ${responseData}`));
          }
        } catch (error) {
          reject(new Error(`Parse Error: ${error.message}`));
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

// Fetch Square locations
async function fetchSquareLocations() {
  try {
    console.log('Fetching Square locations...');
    const response = await makeSquareRequest('/v2/locations');
    return response.locations || [];
  } catch (error) {
    console.error('Error fetching locations:', error.message);
    return [];
  }
}

// Fetch Square customers
async function fetchSquareCustomers() {
  try {
    console.log('Fetching Square customers...');
    const response = await makeSquareRequest('/v2/customers');
    return response.customers || [];
  } catch (error) {
    console.error('Error fetching customers:', error.message);
    return [];
  }
}

// Fetch Square payments
async function fetchSquarePayments(limit = 100) {
  try {
    console.log('Fetching Square payments...');
    const params = new URLSearchParams({
      limit: limit.toString(),
      sort_order: 'DESC'
    });
    
    const response = await makeSquareRequest(`/v2/payments?${params}`);
    return response.payments || [];
  } catch (error) {
    console.error('Error fetching payments:', error.message);
    return [];
  }
}

// Create or update account in Supabase
async function createOrUpdateAccount(locations, merchantId) {
  try {
    console.log('Creating/updating account record...');
    
    const accountData = {
      square_merchant_id: merchantId,
      business_name: 'Bashful Beauty',
      business_category: 'spa'
    };

    // Try to find existing account first
    const { data: existingAccount, error: findError } = await supabase
      .from('accounts')
      .select('id')
      .eq('square_merchant_id', merchantId)
      .single();

    let accountId;

    if (existingAccount) {
      // Update existing account
      const { data, error } = await supabase
        .from('accounts')
        .update(accountData)
        .eq('id', existingAccount.id)
        .select('id')
        .single();
      
      if (error) throw error;
      accountId = data.id;
      console.log(`Updated existing account: ${accountId}`);
    } else {
      // Create new account
      const { data, error } = await supabase
        .from('accounts')
        .insert(accountData)
        .select('id')
        .single();
      
      if (error) throw error;
      accountId = data.id;
      console.log(`Created new account: ${accountId}`);
    }

    return accountId;
  } catch (error) {
    console.error('Error with account:', error.message);
    return null;
  }
}

// Sync customers to Supabase
async function syncCustomers(customers, accountId) {
  try {
    console.log(`Syncing ${customers.length} customers...`);
    let syncedCount = 0;
    let errors = 0;

    for (const customer of customers) {
      try {
        const customerData = {
          account_id: accountId,
          square_id: customer.id,
          name: `${customer.given_name || ''} ${customer.family_name || ''}`.trim() || null,
          email: customer.email_address || null,
          phone: customer.phone_number || null
        };

        // Check if customer exists
        const { data: existingCustomer } = await supabase
          .from('customers')
          .select('id')
          .eq('square_id', customer.id)
          .single();

        if (existingCustomer) {
          // Update existing customer
          const { error } = await supabase
            .from('customers')
            .update(customerData)
            .eq('id', existingCustomer.id);
          
          if (error) throw error;
        } else {
          // Insert new customer
          const { error } = await supabase
            .from('customers')
            .insert(customerData);
          
          if (error) throw error;
        }

        syncedCount++;
      } catch (error) {
        console.error(`Error syncing customer ${customer.id}:`, error.message);
        errors++;
      }
    }

    console.log(`Customers sync complete: ${syncedCount} synced, ${errors} errors`);
    return { synced: syncedCount, errors };
  } catch (error) {
    console.error('Error in customer sync:', error.message);
    return { synced: 0, errors: customers.length };
  }
}

// Sync payments to Supabase
async function syncPayments(payments, accountId) {
  try {
    console.log(`Syncing ${payments.length} payments...`);
    let syncedCount = 0;
    let errors = 0;

    for (const payment of payments) {
      try {
        // Find customer if exists
        let customerId = null;
        if (payment.buyer_email_address) {
          const { data: customer } = await supabase
            .from('customers')
            .select('id')
            .eq('email', payment.buyer_email_address)
            .eq('account_id', accountId)
            .single();
          
          if (customer) {
            customerId = customer.id;
          }
        }

        const transactionData = {
          account_id: accountId,
          customer_id: customerId,
          square_payment_id: payment.id,
          amount: payment.amount_money ? (payment.amount_money.amount / 100) : 0, // Convert cents to dollars
          timestamp: payment.created_at || new Date().toISOString()
        };

        // Check if payment exists
        const { data: existingPayment } = await supabase
          .from('transactions')
          .select('id')
          .eq('square_payment_id', payment.id)
          .single();

        if (existingPayment) {
          // Update existing payment
          const { error } = await supabase
            .from('transactions')
            .update(transactionData)
            .eq('id', existingPayment.id);
          
          if (error) throw error;
        } else {
          // Insert new payment
          const { error } = await supabase
            .from('transactions')
            .insert(transactionData);
          
          if (error) throw error;
        }

        syncedCount++;
      } catch (error) {
        console.error(`Error syncing payment ${payment.id}:`, error.message);
        errors++;
      }
    }

    console.log(`Payments sync complete: ${syncedCount} synced, ${errors} errors`);
    return { synced: syncedCount, errors };
  } catch (error) {
    console.error('Error in payment sync:', error.message);
    return { synced: 0, errors: payments.length };
  }
}

// Main sync function
async function syncSquareData() {
  console.log('Starting Square data sync for Bashful Beauty...');
  console.log(`Environment: ${SQUARE_ENVIRONMENT}`);
  console.log(`Using access token: ${SQUARE_ACCESS_TOKEN.substring(0, 10)}...`);
  
  const results = {
    locations: { count: 0 },
    customers: { synced: 0, errors: 0 },
    payments: { synced: 0, errors: 0 },
    account: null
  };

  try {
    // 1. Fetch Square locations
    const locations = await fetchSquareLocations();
    results.locations.count = locations.length;
    console.log(`Found ${locations.length} locations`);

    if (locations.length > 0) {
      console.log('Locations:', locations.map(l => `${l.name} (${l.id})`).join(', '));
    }

    // 2. Create/update account with merchant ID (using first location as reference)
    const merchantId = '40GJBMWKZ4FZS'; // As provided by user
    const accountId = await createOrUpdateAccount(locations, merchantId);
    results.account = accountId;

    if (!accountId) {
      throw new Error('Failed to create/update account record');
    }

    // 3. Fetch and sync customers
    const customers = await fetchSquareCustomers();
    if (customers.length > 0) {
      const customerResults = await syncCustomers(customers, accountId);
      results.customers = customerResults;
    }

    // 4. Fetch and sync payments
    const payments = await fetchSquarePayments();
    if (payments.length > 0) {
      const paymentResults = await syncPayments(payments, accountId);
      results.payments = paymentResults;
    }

    // Sync completed successfully

    console.log('\n=== SYNC COMPLETE ===');
    console.log(`Account ID: ${accountId}`);
    console.log(`Locations: ${results.locations.count}`);
    console.log(`Customers: ${results.customers.synced} synced, ${results.customers.errors} errors`);
    console.log(`Payments: ${results.payments.synced} synced, ${results.payments.errors} errors`);

  } catch (error) {
    console.error('Sync failed:', error.message);
    process.exit(1);
  }
}

// Run the sync
if (require.main === module) {
  syncSquareData();
}

module.exports = { syncSquareData };