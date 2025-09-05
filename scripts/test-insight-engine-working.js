/**
 * Working Insight Engine Test with Real Data
 * 
 * Tests insight generation using actual Bashful Beauty data from transactions table
 */

require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);

// Working insight engine using correct table structure
class WorkingInsightEngine {
  constructor(accountId) {
    this.accountId = accountId;
  }

  async generateInsights() {
    console.log('🧠 WORKING INSIGHT ENGINE TEST');
    console.log('===============================');
    
    try {
      // 1. Gather business data using correct tables
      const businessData = await this.gatherBusinessData();
      console.log(`📊 Business Data Summary:`);
      console.log(`   Revenue: $${businessData.totalRevenue.toLocaleString()}`);
      console.log(`   Transactions: ${businessData.totalTransactions.toLocaleString()}`);
      console.log(`   Appointments: ${businessData.totalAppointments.toLocaleString()}`);
      console.log(`   Avg Transaction: $${businessData.avgTransactionValue.toFixed(2)}`);
      console.log();

      // 2. Run analysis
      const insights = await this.runAnalysis(businessData);
      
      // 3. Display results
      this.displayInsights(insights);
      
      // 4. Validate $3000+ target
      const totalValue = insights.reduce((sum, insight) => sum + insight.dollarValue, 0);
      console.log();
      console.log('🎯 VALIDATION RESULTS');
      console.log('=====================');
      console.log(`Total Opportunity Found: $${totalValue.toLocaleString()}`);
      console.log(`Target: $3,000+`);
      console.log(`Status: ${totalValue >= 3000 ? '✅ PASSED' : '❌ FAILED'}`);
      
      return insights;
      
    } catch (error) {
      console.error('❌ Test failed:', error);
      return [];
    }
  }

  async gatherBusinessData() {
    // Get account
    const { data: account } = await supabase
      .from('accounts')
      .select('business_name')
      .eq('id', this.accountId)
      .single();

    // Get transactions (this is where the payment data is!)
    const { data: transactions } = await supabase
      .from('transactions')
      .select('amount_cents, timestamp, customer_id, tip_cents')
      .eq('account_id', this.accountId);

    // Get appointments
    const { data: appointments } = await supabase
      .from('appointments')
      .select('*')
      .eq('account_id', this.accountId);

    // Get customers
    const { data: customers } = await supabase
      .from('customers')
      .select('*')
      .eq('account_id', this.accountId);

    // Calculate metrics using correct field names
    const totalRevenue = transactions?.reduce((sum, t) => sum + ((t.amount_cents || 0) / 100), 0) || 0;
    const totalTransactions = transactions?.length || 0;
    const totalAppointments = appointments?.length || 0;
    const totalCustomers = customers?.length || 0;
    const avgTransactionValue = totalTransactions > 0 ? totalRevenue / totalTransactions : 0;

    return {
      businessName: account?.business_name || 'Unknown',
      totalRevenue,
      totalTransactions,
      totalAppointments,
      totalCustomers,
      avgTransactionValue,
      transactions: transactions || [],
      appointments: appointments || [],
      customers: customers || []
    };
  }

  async runAnalysis(data) {
    const insights = [];

    console.log('🔍 Running Real Data Analysis Tournament...');

    // 1. Revenue Per Customer Analysis
    const customerValueInsight = await this.analyzeCustomerValue(data);
    if (customerValueInsight) {
      console.log('   ✅ Found customer value opportunity');
      insights.push(customerValueInsight);
    }

    // 2. Appointment to Revenue Conversion
    const conversionInsight = await this.analyzeAppointmentRevenue(data);
    if (conversionInsight) {
      console.log('   ✅ Found appointment conversion opportunity');
      insights.push(conversionInsight);
    }

    // 3. Tip Optimization Analysis
    const tipInsight = await this.analyzeTipOptimization(data);
    if (tipInsight) {
      console.log('   ✅ Found tip optimization opportunity');
      insights.push(tipInsight);
    }

    // 4. High-Value Customer Growth
    const growthInsight = await this.analyzeCustomerGrowth(data);
    if (growthInsight) {
      console.log('   ✅ Found customer growth opportunity');
      insights.push(growthInsight);
    }

    // 5. Revenue Recovery Opportunity
    const recoveryInsight = await this.analyzeRevenueRecovery(data);
    if (recoveryInsight) {
      console.log('   ✅ Found revenue recovery opportunity');
      insights.push(recoveryInsight);
    }

    return insights;
  }

  async analyzeCustomerValue(data) {
    if (data.totalCustomers === 0 || data.totalRevenue === 0) return null;

    const avgCustomerValue = data.totalRevenue / data.totalCustomers;
    
    // Group transactions by customer to find distribution
    const customerRevenue = new Map();
    data.transactions.forEach(t => {
      if (t.customer_id && t.customer_id !== 'unknown') {
        const current = customerRevenue.get(t.customer_id) || 0;
        customerRevenue.set(t.customer_id, current + (t.amount_cents / 100));
      }
    });

    const customerValues = Array.from(customerRevenue.values());
    customerValues.sort((a, b) => b - a);
    
    // Find customers in bottom 50% who could be upgraded
    const median = customerValues[Math.floor(customerValues.length / 2)];
    const lowValueCustomers = customerValues.filter(v => v < median).length;
    
    // Potential to move bottom 20% up by 40%
    const targetCustomers = Math.floor(lowValueCustomers * 0.2);
    const currentBottomRevenue = customerValues.slice(-targetCustomers).reduce((sum, val) => sum + val, 0);
    const potentialIncrease = currentBottomRevenue * 0.4;

    if (potentialIncrease < 1000) return null; // Must be significant

    return {
      type: 'Customer Value Enhancement',
      description: `${targetCustomers} low-spending customers could generate significantly more revenue through targeted engagement`,
      dollarValue: Math.round(potentialIncrease),
      confidence: 82,
      action: 'Create personalized upselling campaign for bottom-tier customers',
      evidence: [
        `${targetCustomers} customers spending below $${median.toFixed(2)} median`,
        `Average customer value: $${avgCustomerValue.toFixed(2)}`,
        `Bottom 20% upgrade potential: 40% increase in spending`
      ]
    };
  }

  async analyzeAppointmentRevenue(data) {
    if (data.totalAppointments === 0 || data.totalTransactions === 0) return null;

    // Calculate appointments that didn't convert to revenue
    const appointmentsWithRevenue = data.transactions.filter(t => t.customer_id && t.customer_id !== 'unknown').length;
    const conversionRate = appointmentsWithRevenue / data.totalAppointments;
    
    if (conversionRate > 0.85) return null; // Already good conversion

    const missedAppointments = data.totalAppointments - appointmentsWithRevenue;
    const potentialRevenue = missedAppointments * data.avgTransactionValue * 0.6; // 60% recovery rate

    return {
      type: 'Appointment Revenue Conversion',
      description: `${missedAppointments.toLocaleString()} appointments didn't convert to tracked revenue - recovery opportunity`,
      dollarValue: Math.round(potentialRevenue),
      confidence: 75,
      action: 'Implement appointment follow-up system and payment tracking improvements',
      evidence: [
        `Current conversion rate: ${(conversionRate * 100).toFixed(1)}%`,
        `${missedAppointments.toLocaleString()} appointments without tracked revenue`,
        `Industry standard: 90%+ appointment-to-payment conversion`
      ]
    };
  }

  async analyzeTipOptimization(data) {
    // Calculate current tip performance
    const transactionsWithTips = data.transactions.filter(t => (t.tip_cents || 0) > 0);
    const totalTips = data.transactions.reduce((sum, t) => sum + ((t.tip_cents || 0) / 100), 0);
    const avgTipRate = totalTips / data.totalRevenue;
    
    if (avgTipRate > 0.18) return null; // Already good tip rate
    
    // Industry standard for spa services is 18-22%
    const targetTipRate = 0.20;
    const potentialTipIncrease = data.totalRevenue * (targetTipRate - avgTipRate);
    
    if (potentialTipIncrease < 2000) return null; // Must be significant

    return {
      type: 'Tip Rate Optimization',
      description: `Current tip rate is ${(avgTipRate * 100).toFixed(1)}% - below industry standard of 18-22%`,
      dollarValue: Math.round(potentialTipIncrease),
      confidence: 78,
      action: 'Implement tip optimization strategies: suggested amounts, staff training, service excellence',
      evidence: [
        `Current tip rate: ${(avgTipRate * 100).toFixed(1)}%`,
        `Industry standard: 18-22% for spa services`,
        `${transactionsWithTips.length} of ${data.totalTransactions} transactions included tips`
      ]
    };
  }

  async analyzeCustomerGrowth(data) {
    // Analyze customer acquisition trends
    const customerTransactionCounts = new Map();
    data.transactions.forEach(t => {
      if (t.customer_id && t.customer_id !== 'unknown') {
        const current = customerTransactionCounts.get(t.customer_id) || 0;
        customerTransactionCounts.set(t.customer_id, current + 1);
      }
    });

    const repeatCustomers = Array.from(customerTransactionCounts.values()).filter(count => count > 1).length;
    const oneTimeCustomers = Array.from(customerTransactionCounts.values()).filter(count => count === 1).length;
    
    const repeatRate = repeatCustomers / (repeatCustomers + oneTimeCustomers);
    
    if (repeatRate > 0.7) return null; // Already good repeat rate
    
    // Potential to convert 30% of one-time customers to repeat customers
    const conversionTargets = Math.floor(oneTimeCustomers * 0.3);
    const potentialRevenue = conversionTargets * data.avgTransactionValue * 2; // 2 additional visits

    return {
      type: 'Customer Retention Improvement',
      description: `${oneTimeCustomers} one-time customers could be converted to repeat customers`,
      dollarValue: Math.round(potentialRevenue),
      confidence: 71,
      action: 'Launch first-visit follow-up campaign with incentives for return visits',
      evidence: [
        `Current repeat customer rate: ${(repeatRate * 100).toFixed(1)}%`,
        `${oneTimeCustomers} customers made only one purchase`,
        `Target: Convert 30% to repeat customers (industry standard: 70%+)`
      ]
    };
  }

  async analyzeRevenueRecovery(data) {
    // Analyze transaction timing to find lapsed customers
    const customerLastTransaction = new Map();
    
    data.transactions.forEach(t => {
      if (t.customer_id && t.customer_id !== 'unknown' && t.timestamp) {
        const date = new Date(t.timestamp);
        const current = customerLastTransaction.get(t.customer_id);
        if (!current || date > current) {
          customerLastTransaction.set(t.customer_id, date);
        }
      }
    });

    // Find customers who haven't transacted in 6+ months
    const sixMonthsAgo = new Date();
    sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
    
    const lapsedCustomers = Array.from(customerLastTransaction.entries())
      .filter(([customerId, lastDate]) => lastDate < sixMonthsAgo);

    if (lapsedCustomers.length < 50) return null; // Need meaningful number

    // Calculate their historical value
    const lapsedCustomerRevenue = new Map();
    data.transactions.forEach(t => {
      if (t.customer_id && lapsedCustomers.some(([id]) => id === t.customer_id)) {
        const current = lapsedCustomerRevenue.get(t.customer_id) || 0;
        lapsedCustomerRevenue.set(t.customer_id, current + (t.amount_cents / 100));
      }
    });

    const avgLapsedValue = Array.from(lapsedCustomerRevenue.values())
      .reduce((sum, val) => sum + val, 0) / lapsedCustomers.length;
    
    // Assume 25% can be reactivated
    const reactivationPotential = Math.floor(lapsedCustomers.length * 0.25);
    const potentialRevenue = reactivationPotential * avgLapsedValue * 0.5; // 50% of their historical value

    return {
      type: 'Lapsed Customer Reactivation',
      description: `${lapsedCustomers.length} customers haven't visited in 6+ months - high-value reactivation opportunity`,
      dollarValue: Math.round(potentialRevenue),
      confidence: 80,
      action: 'Launch "We miss you" win-back campaign with exclusive offers',
      evidence: [
        `${lapsedCustomers.length} customers inactive for 6+ months`,
        `Average historical value: $${avgLapsedValue.toFixed(2)}`,
        `Reactivation campaigns typically recover 20-30% of lapsed customers`
      ]
    };
  }

  displayInsights(insights) {
    console.log();
    console.log('💡 GENERATED BUSINESS INSIGHTS');
    console.log('===============================');
    
    insights.forEach((insight, index) => {
      console.log(`${index + 1}. ${insight.type}`);
      console.log(`   💰 Value: $${insight.dollarValue.toLocaleString()}`);
      console.log(`   🎯 Confidence: ${insight.confidence}%`);
      console.log(`   📝 ${insight.description}`);
      console.log(`   🚀 Action: ${insight.action}`);
      console.log(`   📊 Evidence:`);
      insight.evidence.forEach(evidence => {
        console.log(`      • ${evidence}`);
      });
      console.log();
    });
  }
}

// Main execution
async function runWorkingInsightTest() {
  try {
    console.log('🧪 KEEPER WORKING INSIGHT ENGINE TEST');
    console.log('=====================================');
    console.log();

    // Get Bashful Beauty account ID
    const { data: account } = await supabase
      .from('accounts')
      .select('id, business_name')
      .eq('business_name', 'Bashful Beauty')
      .single();

    if (!account) {
      console.error('❌ Bashful Beauty account not found');
      return;
    }

    console.log(`🏢 Testing with: ${account.business_name}`);
    console.log(`📋 Account ID: ${account.id}`);
    console.log();

    // Run insight generation
    const engine = new WorkingInsightEngine(account.id);
    const insights = await engine.generateInsights();

    // Summary
    const totalValue = insights.reduce((sum, insight) => sum + insight.dollarValue, 0);
    const avgConfidence = insights.length > 0 ? 
      insights.reduce((sum, insight) => sum + insight.confidence, 0) / insights.length : 0;

    console.log('📈 FINAL SUMMARY');
    console.log('================');
    console.log(`Insights Generated: ${insights.length}`);
    console.log(`Total Dollar Value: $${totalValue.toLocaleString()}`);
    console.log(`Average Confidence: ${avgConfidence.toFixed(1)}%`);
    console.log(`$3,000 Target: ${totalValue >= 3000 ? '✅ MET' : '❌ NOT MET'}`);
    
    if (totalValue >= 3000) {
      console.log();
      console.log('🎉 SUCCESS! Keeper can find significant revenue opportunities in real spa data.');
      console.log(`💰 Found $${totalValue.toLocaleString()} in potential revenue opportunities!`);
      console.log('✅ Ready to help businesses make money-making decisions!');
    } else {
      console.log();
      console.log(`⚠️  Generated $${totalValue.toLocaleString()} but need $3K+ target`);
    }

  } catch (error) {
    console.error('❌ Test execution failed:', error);
  }
}

// Execute the test
runWorkingInsightTest();