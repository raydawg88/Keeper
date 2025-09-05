#!/usr/bin/env node

const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: '.env' });

// Supabase client
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
);

async function verifySync() {
  console.log('Verifying synced data in Supabase...\n');

  try {
    // 1. Check accounts
    const { data: accounts, error: accountsError } = await supabase
      .from('accounts')
      .select('*')
      .eq('business_name', 'Bashful Beauty');

    if (accountsError) throw accountsError;

    console.log('=== ACCOUNTS ===');
    console.log(`Found ${accounts.length} account(s):`);
    accounts.forEach(account => {
      console.log(`  - ID: ${account.id}`);
      console.log(`  - Business: ${account.business_name}`);
      console.log(`  - Square Merchant ID: ${account.square_merchant_id}`);
      console.log(`  - Category: ${account.business_category}`);
      console.log(`  - Created: ${account.created_at}`);
    });

    if (accounts.length === 0) {
      throw new Error('No accounts found!');
    }

    const accountId = accounts[0].id;

    // 2. Check customers
    const { data: customers, error: customersError } = await supabase
      .from('customers')
      .select('*')
      .eq('account_id', accountId);

    if (customersError) throw customersError;

    console.log(`\n=== CUSTOMERS ===`);
    console.log(`Found ${customers.length} customers`);
    
    // Show sample customers
    const sampleCustomers = customers.slice(0, 5);
    sampleCustomers.forEach((customer, index) => {
      console.log(`  ${index + 1}. ${customer.name || 'No name'} (${customer.square_id})`);
      console.log(`     Email: ${customer.email || 'No email'}`);
      console.log(`     Phone: ${customer.phone || 'No phone'}`);
    });
    
    if (customers.length > 5) {
      console.log(`     ... and ${customers.length - 5} more customers`);
    }

    // Customer statistics
    const customersWithEmail = customers.filter(c => c.email).length;
    const customersWithPhone = customers.filter(c => c.phone).length;
    const customersWithName = customers.filter(c => c.name && c.name.trim()).length;
    
    console.log(`\n  Statistics:`);
    console.log(`    - With names: ${customersWithName}/${customers.length} (${Math.round(customersWithName/customers.length*100)}%)`);
    console.log(`    - With emails: ${customersWithEmail}/${customers.length} (${Math.round(customersWithEmail/customers.length*100)}%)`);
    console.log(`    - With phones: ${customersWithPhone}/${customers.length} (${Math.round(customersWithPhone/customers.length*100)}%)`);

    // 3. Check transactions
    const { data: transactions, error: transactionsError } = await supabase
      .from('transactions')
      .select('*')
      .eq('account_id', accountId)
      .order('timestamp', { ascending: false });

    if (transactionsError) throw transactionsError;

    console.log(`\n=== TRANSACTIONS ===`);
    console.log(`Found ${transactions.length} transactions`);

    if (transactions.length > 0) {
      // Calculate total revenue
      const totalRevenue = transactions.reduce((sum, tx) => sum + (parseFloat(tx.amount) || 0), 0);
      
      console.log(`  Total Revenue: $${totalRevenue.toFixed(2)}`);
      
      // Show sample transactions
      const sampleTransactions = transactions.slice(0, 5);
      console.log(`\n  Recent Transactions:`);
      sampleTransactions.forEach((tx, index) => {
        console.log(`    ${index + 1}. $${parseFloat(tx.amount || 0).toFixed(2)} on ${new Date(tx.timestamp).toLocaleDateString()}`);
        console.log(`       Payment ID: ${tx.square_payment_id}`);
        console.log(`       Customer ID: ${tx.customer_id || 'No customer linked'}`);
      });
      
      if (transactions.length > 5) {
        console.log(`       ... and ${transactions.length - 5} more transactions`);
      }

      // Transaction statistics
      const avgTransaction = totalRevenue / transactions.length;
      const transactionsWithCustomers = transactions.filter(tx => tx.customer_id).length;
      
      console.log(`\n  Statistics:`);
      console.log(`    - Average transaction: $${avgTransaction.toFixed(2)}`);
      console.log(`    - With linked customers: ${transactionsWithCustomers}/${transactions.length} (${Math.round(transactionsWithCustomers/transactions.length*100)}%)`);
    }

    console.log(`\n=== SYNC SUMMARY ===`);
    console.log(`✅ Account: ${accounts.length} record`);
    console.log(`✅ Customers: ${customers.length} records`);
    console.log(`✅ Transactions: ${transactions.length} records`);
    console.log(`\nData successfully synced from Square API to Supabase!`);

  } catch (error) {
    console.error('Error verifying sync:', error.message);
    process.exit(1);
  }
}

// Run the verification
if (require.main === module) {
  verifySync();
}

module.exports = { verifySync };