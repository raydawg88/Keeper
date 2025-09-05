'use client';

import { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client (using public URL and anon key for client-side)
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://jlawmbqoykwgrjutrfsp.supabase.co',
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'sb_publishable_AIOxrVwsfPTo-XotyIp5hw_mMQuN76Z'
);

interface AnalyticsData {
  totalRevenue: number;
  totalTransactions: number;
  totalCustomers: number;
  averageTransaction: number;
  yearlyRevenue: Array<{ year: number; revenue: number; transactions: number }>;
  monthlyRevenue: Array<{ month: string; revenue: number; transactions: number }>;
  recentTransactions: Array<{ amount: number; created_at: string }>;
}

export default function Analytics() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get total revenue and transaction count
      const { data: transactions, error: transactionsError } = await supabase
        .from('transactions')
        .select('amount, created_at')
        .order('created_at', { ascending: false });

      if (transactionsError) {
        throw transactionsError;
      }

      // Get customer count
      const { count: customerCount, error: customersError } = await supabase
        .from('customers')
        .select('*', { count: 'exact', head: true });

      if (customersError) {
        throw customersError;
      }

      if (!transactions || transactions.length === 0) {
        setData({
          totalRevenue: 0,
          totalTransactions: 0,
          totalCustomers: customerCount || 0,
          averageTransaction: 0,
          yearlyRevenue: [],
          monthlyRevenue: [],
          recentTransactions: []
        });
        return;
      }

      // Calculate totals
      const totalRevenue = transactions.reduce((sum, t) => sum + (t.amount || 0), 0);
      const totalTransactions = transactions.length;
      const averageTransaction = totalRevenue / totalTransactions;

      // Group by year
      const yearlyData: { [key: number]: { revenue: number; transactions: number } } = {};
      const monthlyData: { [key: string]: { revenue: number; transactions: number } } = {};

      transactions.forEach(transaction => {
        const date = new Date(transaction.created_at);
        const year = date.getFullYear();
        const monthKey = `${year}-${(date.getMonth() + 1).toString().padStart(2, '0')}`;

        // Yearly aggregation
        if (!yearlyData[year]) {
          yearlyData[year] = { revenue: 0, transactions: 0 };
        }
        yearlyData[year].revenue += transaction.amount || 0;
        yearlyData[year].transactions += 1;

        // Monthly aggregation (last 12 months)
        if (!monthlyData[monthKey]) {
          monthlyData[monthKey] = { revenue: 0, transactions: 0 };
        }
        monthlyData[monthKey].revenue += transaction.amount || 0;
        monthlyData[monthKey].transactions += 1;
      });

      // Convert to arrays and sort
      const yearlyRevenue = Object.entries(yearlyData)
        .map(([year, data]) => ({
          year: parseInt(year),
          revenue: data.revenue,
          transactions: data.transactions
        }))
        .sort((a, b) => a.year - b.year);

      const monthlyRevenue = Object.entries(monthlyData)
        .map(([month, data]) => ({
          month,
          revenue: data.revenue,
          transactions: data.transactions
        }))
        .sort((a, b) => a.month.localeCompare(b.month))
        .slice(-12); // Last 12 months

      // Recent transactions
      const recentTransactions = transactions.slice(0, 10).map(t => ({
        amount: t.amount || 0,
        created_at: t.created_at
      }));

      setData({
        totalRevenue,
        totalTransactions,
        totalCustomers: customerCount || 0,
        averageTransaction,
        yearlyRevenue,
        monthlyRevenue,
        recentTransactions
      });

    } catch (error) {
      console.error('Error fetching analytics:', error);
      setError(error instanceof Error ? error.message : 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading business intelligence data...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <h3 className="text-lg font-medium text-red-800">Error Loading Analytics</h3>
            <p className="mt-2 text-sm text-red-600">{error}</p>
            <button 
              onClick={fetchAnalyticsData}
              className="mt-3 bg-red-100 hover:bg-red-200 text-red-800 px-4 py-2 rounded text-sm"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const growthRate = data.yearlyRevenue.length >= 2 
    ? ((data.yearlyRevenue[data.yearlyRevenue.length - 1]?.revenue || 0) - (data.yearlyRevenue[0]?.revenue || 0)) / (data.yearlyRevenue[0]?.revenue || 1) * 100
    : 0;

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            📊 Bashful Beauty Business Intelligence
          </h1>
          <p className="text-xl text-gray-600">
            Complete 8-year analysis • {data.yearlyRevenue[0]?.year} - {data.yearlyRevenue[data.yearlyRevenue.length - 1]?.year}
          </p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">
              {formatCurrency(data.totalRevenue)}
            </div>
            <div className="text-sm text-gray-600">Total Revenue (8 Years)</div>
            {growthRate > 0 && (
              <div className="text-xs text-green-500 mt-1">
                ↗ {growthRate.toFixed(0)}% growth
              </div>
            )}
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">
              {data.totalTransactions.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Total Transactions</div>
            <div className="text-xs text-gray-500 mt-1">
              Avg {Math.round(data.totalTransactions / data.yearlyRevenue.length).toLocaleString()}/year
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-3xl font-bold text-purple-600 mb-2">
              {data.totalCustomers.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Total Customers</div>
            <div className="text-xs text-gray-500 mt-1">
              Active customer base
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-3xl font-bold text-orange-600 mb-2">
              {formatCurrency(data.averageTransaction)}
            </div>
            <div className="text-sm text-gray-600">Average Transaction</div>
            <div className="text-xs text-gray-500 mt-1">
              Per service visit
            </div>
          </div>
        </div>

        {/* Yearly Revenue Trend */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">📈 8-Year Revenue Growth</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {data.yearlyRevenue.map((year, index) => {
              const previousYear = index > 0 ? data.yearlyRevenue[index - 1] : null;
              const yearGrowth = previousYear 
                ? ((year.revenue - previousYear.revenue) / previousYear.revenue) * 100 
                : 0;

              return (
                <div key={year.year} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="text-lg font-bold text-gray-900">{year.year}</div>
                  <div className="text-xl font-semibold text-green-600">
                    {formatCurrency(year.revenue)}
                  </div>
                  <div className="text-sm text-gray-600">
                    {year.transactions.toLocaleString()} transactions
                  </div>
                  {previousYear && (
                    <div className={`text-xs mt-1 ${yearGrowth >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {yearGrowth >= 0 ? '↗' : '↘'} {Math.abs(yearGrowth).toFixed(0)}% vs prev year
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Monthly Trend (Last 12 Months) */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">📅 Monthly Revenue (Last 12 Months)</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {data.monthlyRevenue.map((month) => (
              <div key={month.month} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="text-sm font-medium text-gray-700">{month.month}</div>
                <div className="text-lg font-semibold text-blue-600">
                  {formatCurrency(month.revenue)}
                </div>
                <div className="text-xs text-gray-500">
                  {month.transactions} transactions
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">💳 Recent Transactions</h2>
          <div className="space-y-3">
            {data.recentTransactions.map((transaction, index) => (
              <div key={index} className="flex justify-between items-center py-2 border-b border-gray-100 last:border-b-0">
                <span className="text-lg font-medium text-green-600">
                  {formatCurrency(transaction.amount)}
                </span>
                <span className="text-sm text-gray-500">
                  {formatDate(transaction.created_at)}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Summary Insights */}
        <div className="mt-12 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">✨ Business Insights</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-gray-800 mb-2">Growth Analysis</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• {growthRate.toFixed(0)}% total revenue growth over 8 years</li>
                <li>• Average {formatCurrency(data.totalRevenue / data.yearlyRevenue.length)} annual revenue</li>
                <li>• Strong customer base of {data.totalCustomers.toLocaleString()} clients</li>
                <li>• Consistent {formatCurrency(data.averageTransaction)} average transaction value</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-gray-800 mb-2">Operational Metrics</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• {Math.round(data.totalTransactions / (data.yearlyRevenue.length * 365))} transactions per day</li>
                <li>• Peak performance in recent years</li>
                <li>• Stable service pricing and customer retention</li>
                <li>• Ready for advanced customer segmentation analysis</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}