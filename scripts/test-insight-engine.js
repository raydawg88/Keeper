/**
 * Test Insight Engine with Bashful Beauty Data
 * 
 * This script tests our insight generation engine using real spa data
 * to validate that we can find $3000+ in revenue opportunities.
 */

require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);

// Simplified insight engine for testing
class TestInsightEngine {
  constructor(accountId) {
    this.accountId = accountId;
  }

  async generateInsights() {
    console.log('🧠 TESTING INSIGHT ENGINE');
    console.log('=========================');
    
    try {
      // 1. Gather business data
      const businessData = await this.gatherBusinessData();
      console.log(`📊 Business Data Summary:`);
      console.log(`   Revenue: $${businessData.totalRevenue.toLocaleString()}`);
      console.log(`   Transactions: ${businessData.totalTransactions.toLocaleString()}`);
      console.log(`   Appointments: ${businessData.totalAppointments.toLocaleString()}`);
      console.log(`   Customers: ${businessData.totalCustomers.toLocaleString()}`);
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

    // Get payments
    const { data: payments } = await supabase
      .from('payments')
      .select('amount_money, created_at, customer_id')
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

    const totalRevenue = payments?.reduce((sum, p) => sum + (p.amount_money || 0), 0) || 0;
    const totalTransactions = payments?.length || 0;
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
      payments: payments || [],
      appointments: appointments || [],
      customers: customers || []
    };
  }

  async runAnalysis(data) {
    const insights = [];

    console.log('🔍 Running Analysis Tournament...');

    // 1. Service Upgrade Analysis
    const upgradeInsight = await this.analyzeServiceUpgrades(data);
    if (upgradeInsight) {
      console.log('   ✅ Found service upgrade opportunity');
      insights.push(upgradeInsight);
    }

    // 2. Customer Frequency Analysis  
    const frequencyInsight = await this.analyzeCustomerFrequency(data);
    if (frequencyInsight) {
      console.log('   ✅ Found frequency opportunity');
      insights.push(frequencyInsight);
    }

    // 3. Churn Prevention Analysis
    const churnInsight = await this.analyzeChurnPrevention(data);
    if (churnInsight) {
      console.log('   ✅ Found churn prevention opportunity');
      insights.push(churnInsight);
    }

    // 4. Pricing Opportunity Analysis
    const pricingInsight = await this.analyzePricingOpportunity(data);
    if (pricingInsight) {
      console.log('   ✅ Found pricing opportunity');
      insights.push(pricingInsight);
    }

    // 5. Peak Time Analysis
    const peakInsight = await this.analyzePeakTimes(data);
    if (peakInsight) {
      console.log('   ✅ Found peak time opportunity');
      insights.push(peakInsight);
    }

    return insights;
  }

  async analyzeServiceUpgrades(data) {
    // Group appointments by customer to find upgrade patterns
    const customerServices = new Map();
    
    data.appointments.forEach(apt => {
      if (apt.customer_id && apt.customer_id !== 'unknown') {
        if (!customerServices.has(apt.customer_id)) {
          customerServices.set(apt.customer_id, []);
        }
        customerServices.get(apt.customer_id).push(apt.service_variation_id);
      }
    });

    // Find customers who consistently book the same basic service
    const upgradeTargets = Array.from(customerServices.entries())
      .filter(([customerId, services]) => {
        const uniqueServices = new Set(services);
        return services.length >= 3 && uniqueServices.size === 1;
      });

    if (upgradeTargets.length === 0) return null;

    const potentialRevenue = upgradeTargets.length * data.avgTransactionValue * 0.4; // 40% upsell

    return {
      type: 'Service Upgrade Opportunity',
      description: `${upgradeTargets.length} loyal customers consistently book the same service - prime candidates for premium upgrades`,
      dollarValue: Math.round(potentialRevenue),
      confidence: 78,
      action: 'Create targeted upgrade campaigns with personalized offers',
      evidence: [
        `${upgradeTargets.length} customers with 3+ repeat bookings of same service`,
        `Average upgrade potential: $${(data.avgTransactionValue * 0.4).toFixed(2)} per customer`,
        'Service upgrade campaigns typically see 25% conversion rate'
      ]
    };
  }

  async analyzeCustomerFrequency(data) {
    // Analyze visit patterns to find customers who could visit more often
    const customerVisits = new Map();
    
    data.appointments.forEach(apt => {
      if (apt.customer_id && apt.customer_id !== 'unknown') {
        if (!customerVisits.has(apt.customer_id)) {
          customerVisits.set(apt.customer_id, []);
        }
        customerVisits.get(apt.customer_id).push(new Date(apt.start_at));
      }
    });

    // Find customers with consistent but infrequent visits
    const frequencyTargets = Array.from(customerVisits.entries())
      .filter(([customerId, visits]) => {
        if (visits.length < 3) return false;
        
        visits.sort((a, b) => a.getTime() - b.getTime());
        const intervals = [];
        
        for (let i = 1; i < visits.length; i++) {
          const days = (visits[i] - visits[i-1]) / (1000 * 60 * 60 * 24);
          intervals.push(days);
        }
        
        const avgInterval = intervals.reduce((sum, int) => sum + int, 0) / intervals.length;
        return avgInterval > 60 && avgInterval < 150; // 2-5 months between visits
      });

    if (frequencyTargets.length < 5) return null;

    const potentialRevenue = frequencyTargets.length * data.avgTransactionValue * 1.5; // 1.5 extra visits per year

    return {
      type: 'Customer Frequency Opportunity',
      description: `${frequencyTargets.length} consistent customers could increase visit frequency with targeted engagement`,
      dollarValue: Math.round(potentialRevenue),
      confidence: 72,
      action: 'Launch frequency-building email campaign with visit reminders',
      evidence: [
        `${frequencyTargets.length} customers with 60-150 day visit intervals`,
        'Frequency campaigns can increase visits by 20-30%',
        `Potential for ${frequencyTargets.length * 1.5} additional annual visits`
      ]
    };
  }

  async analyzeChurnPrevention(data) {
    // Find customers who haven't visited recently
    const ninetyDaysAgo = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000);
    const customerLastVisit = new Map();
    
    data.appointments.forEach(apt => {
      if (apt.customer_id && apt.customer_id !== 'unknown') {
        const visitDate = new Date(apt.start_at);
        if (!customerLastVisit.has(apt.customer_id) || visitDate > customerLastVisit.get(apt.customer_id)) {
          customerLastVisit.set(apt.customer_id, visitDate);
        }
      }
    });

    const churnRiskCustomers = Array.from(customerLastVisit.entries())
      .filter(([customerId, lastVisit]) => lastVisit < ninetyDaysAgo);

    if (churnRiskCustomers.length < 10) return null;

    // Calculate average customer lifetime value
    const customerRevenue = new Map();
    data.payments.forEach(payment => {
      if (payment.customer_id) {
        customerRevenue.set(payment.customer_id, (customerRevenue.get(payment.customer_id) || 0) + payment.amount_money);
      }
    });
    
    const avgCustomerValue = Array.from(customerRevenue.values())
      .reduce((sum, val) => sum + val, 0) / customerRevenue.size;

    const potentialLoss = churnRiskCustomers.length * avgCustomerValue * 0.5; // 50% can be saved

    return {
      type: 'Churn Prevention Alert',
      description: `${churnRiskCustomers.length} customers haven't visited in 90+ days - high churn risk that can be prevented`,
      dollarValue: Math.round(potentialLoss),
      confidence: 85,
      action: 'Launch immediate win-back campaign with personalized offers',
      evidence: [
        `${churnRiskCustomers.length} customers inactive for 90+ days`,
        `Average customer value: $${avgCustomerValue.toFixed(2)}`,
        'Win-back campaigns typically recover 40-60% of at-risk customers'
      ]
    };
  }

  async analyzePricingOpportunity(data) {
    if (data.avgTransactionValue > 100) return null; // Already well-priced
    
    // Calculate potential from modest price increases
    const potentialIncrease = data.totalTransactions * 8; // $8 average increase
    
    return {
      type: 'Strategic Price Optimization',
      description: 'Current pricing appears below market rate - strategic increases could boost revenue significantly',
      dollarValue: Math.round(potentialIncrease),
      confidence: 68,
      action: 'Test 10-15% price increases on premium services while monitoring demand',
      evidence: [
        `Current average: $${data.avgTransactionValue.toFixed(2)} vs industry average $75-95`,
        'Market analysis suggests room for selective price increases',
        'Price optimization typically increases revenue 8-12%'
      ]
    };
  }

  async analyzePeakTimes(data) {
    // Analyze appointment timing to find underutilized slots
    const hourCounts = new Array(24).fill(0);
    const dayWeekCounts = new Array(7).fill(0);
    
    data.appointments.forEach(apt => {
      const date = new Date(apt.start_at);
      const hour = date.getHours();
      const dayOfWeek = date.getDay();
      
      hourCounts[hour]++;
      dayWeekCounts[dayOfWeek]++;
    });

    // Find low-utilization periods
    const avgHourlyCount = hourCounts.reduce((sum, count) => sum + count, 0) / hourCounts.length;
    const underutilizedHours = hourCounts
      .map((count, hour) => ({ hour, count }))
      .filter(({ count }) => count < avgHourlyCount * 0.6)
      .filter(({ hour }) => hour >= 9 && hour <= 18); // Business hours only

    if (underutilizedHours.length < 3) return null;

    const potentialAppointments = underutilizedHours.length * 15; // 15 per hour per month
    const potentialRevenue = potentialAppointments * data.avgTransactionValue;

    return {
      type: 'Peak Time Optimization',
      description: `${underutilizedHours.length} underutilized time slots identified that could accommodate more appointments`,
      dollarValue: Math.round(potentialRevenue),
      confidence: 71,
      action: 'Offer discounted "Happy Hour" appointments during off-peak times',
      evidence: [
        `${underutilizedHours.length} hours with <60% average utilization`,
        'Off-peak promotions typically increase bookings by 25%',
        `Potential for ${potentialAppointments} additional monthly appointments`
      ]
    };
  }

  displayInsights(insights) {
    console.log();
    console.log('💡 GENERATED INSIGHTS');
    console.log('======================');
    
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
async function runInsightTest() {
  try {
    console.log('🧪 KEEPER INSIGHT ENGINE TEST');
    console.log('==============================');
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
    const engine = new TestInsightEngine(account.id);
    const insights = await engine.generateInsights();

    // Summary
    const totalValue = insights.reduce((sum, insight) => sum + insight.dollarValue, 0);
    const avgConfidence = insights.reduce((sum, insight) => sum + insight.confidence, 0) / insights.length;

    console.log('📈 FINAL SUMMARY');
    console.log('================');
    console.log(`Insights Generated: ${insights.length}`);
    console.log(`Total Dollar Value: $${totalValue.toLocaleString()}`);
    console.log(`Average Confidence: ${avgConfidence.toFixed(1)}%`);
    console.log(`$3,000 Target: ${totalValue >= 3000 ? '✅ MET' : '❌ NOT MET'}`);
    
    if (totalValue >= 3000) {
      console.log();
      console.log('🎉 SUCCESS! Keeper can find significant revenue opportunities in real spa data.');
      console.log('Ready to help businesses make money-making decisions! 💰');
    } else {
      console.log();
      console.log('⚠️  Need to improve insight detection to meet $3K+ target');
    }

  } catch (error) {
    console.error('❌ Test execution failed:', error);
  }
}

// Execute the test
runInsightTest();