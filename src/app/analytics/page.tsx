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
  totalAppointments: number;
  averageTransaction: number;
  appointmentConversionRate: number;
  yearlyRevenue: Array<{ year: number; revenue: number; transactions: number; appointments: number }>;
  monthlyRevenue: Array<{ month: string; revenue: number; transactions: number; appointments: number }>;
  appointmentsByStatus: Array<{ status: string; count: number; percentage: number }>;
  averageAppointmentDuration: number;
  recentTransactions: Array<{ amount: number; created_at: string }>;
  recentAppointments: Array<{ start_at: string; status: string; duration_minutes: number }>;
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

      // Get aggregated data using PostgreSQL functions (server-side calculation)
      // This avoids the 1000 row limit and is much faster
      const { data: aggregated, error: aggregatedError } = await supabase
        .rpc('get_transaction_analytics');

      let totalRevenue = 0;
      let totalTransactions = 0;
      let totalAppointments = 0;
      let avgTransaction = 0;
      let appointmentConversionRate = 0;

      if (aggregatedError) {
        console.log('RPC not available, using fallback calculation...');
        
        // Get exact count first
        const { count: transactionCount, error: countError } = await supabase
          .from('transactions')
          .select('*', { count: 'exact', head: true });

        if (countError) {
          throw countError;
        }

        totalTransactions = transactionCount || 0;

        // For revenue, we need to fetch all data in chunks to avoid limits
        let currentRevenue = 0;
        let offset = 0;
        const chunkSize = 1000;
        let hasMore = true;

        while (hasMore) {
          const { data: chunk, error: chunkError } = await supabase
            .from('transactions')
            .select('amount')
            .range(offset, offset + chunkSize - 1);

          if (chunkError) {
            throw chunkError;
          }

          if (chunk && chunk.length > 0) {
            currentRevenue += chunk.reduce((sum, t) => sum + (parseFloat(t.amount) || 0), 0);
            offset += chunkSize;
            hasMore = chunk.length === chunkSize;
          } else {
            hasMore = false;
          }
        }

        totalRevenue = currentRevenue;
        avgTransaction = totalTransactions > 0 ? totalRevenue / totalTransactions : 0;
        
      } else {
        // Use RPC results
        totalRevenue = aggregated?.total_revenue || 0;
        totalTransactions = aggregated?.total_transactions || 0;
        avgTransaction = aggregated?.avg_transaction || 0;
      }

      // Get customer count
      const { count: customerCount, error: customersError } = await supabase
        .from('customers')
        .select('*', { count: 'exact', head: true });

      if (customersError) {
        throw customersError;
      }

      // Get appointment analytics
      const { count: appointmentCount, error: appointmentError } = await supabase
        .from('appointments')
        .select('*', { count: 'exact', head: true });

      if (appointmentError) {
        console.log('Appointments table not available yet:', appointmentError.message);
        totalAppointments = 0;
      } else {
        totalAppointments = appointmentCount || 0;
        appointmentConversionRate = totalTransactions > 0 && totalAppointments > 0
          ? (totalTransactions / totalAppointments) * 100
          : 0;
      }

      // Get appointment status breakdown
      const { data: appointmentStatusData, error: statusError } = await supabase
        .from('appointments')
        .select('status')
        .limit(10000); // Sample for status analysis

      let appointmentsByStatus: Array<{ status: string; count: number; percentage: number }> = [];
      let averageAppointmentDuration = 0;

      if (!statusError && appointmentStatusData) {
        const statusCounts: { [key: string]: number } = {};
        appointmentStatusData.forEach(apt => {
          const status = apt.status || 'unknown';
          statusCounts[status] = (statusCounts[status] || 0) + 1;
        });

        const totalSample = appointmentStatusData.length;
        appointmentsByStatus = Object.entries(statusCounts).map(([status, count]) => ({
          status,
          count,
          percentage: totalSample > 0 ? (count / totalSample) * 100 : 0
        })).sort((a, b) => b.count - a.count);
      }

      // Get average appointment duration
      const { data: durationData, error: durationError } = await supabase
        .from('appointments')
        .select('duration_minutes')
        .limit(1000); // Sample for duration analysis

      if (!durationError && durationData) {
        const validDurations = durationData
          .map(apt => apt.duration_minutes)
          .filter(duration => duration && duration > 0);
        
        if (validDurations.length > 0) {
          averageAppointmentDuration = validDurations.reduce((sum, duration) => sum + duration, 0) / validDurations.length;
        }
      }

      // Get transactions for trending (limit to recent data for performance)
      const { data: transactions, error: transactionsError } = await supabase
        .from('transactions')
        .select('amount, created_at')
        .order('created_at', { ascending: false })
        .limit(10000); // Get recent 10k for trending analysis

      if (transactionsError) {
        throw transactionsError;
      }

      // Get appointments for trending
      const { data: appointments, error: appointmentsError } = await supabase
        .from('appointments')
        .select('start_at, status, duration_minutes')
        .order('start_at', { ascending: false })
        .limit(10000); // Get recent 10k for trending analysis

      if (appointmentsError) {
        console.log('Could not fetch appointments for trending:', appointmentsError.message);
      }

      if (totalTransactions === 0) {
        setData({
          totalRevenue: 0,
          totalTransactions: 0,
          totalCustomers: customerCount || 0,
          totalAppointments: totalAppointments,
          averageTransaction: 0,
          appointmentConversionRate: 0,
          yearlyRevenue: [],
          monthlyRevenue: [],
          appointmentsByStatus: [],
          averageAppointmentDuration: 0,
          recentTransactions: [],
          recentAppointments: []
        });
        return;
      }

      // Group by year
      const yearlyData: { [key: number]: { revenue: number; transactions: number; appointments: number } } = {};
      const monthlyData: { [key: string]: { revenue: number; transactions: number; appointments: number } } = {};

      transactions.forEach(transaction => {
        const date = new Date(transaction.created_at);
        const year = date.getFullYear();
        const monthKey = `${year}-${(date.getMonth() + 1).toString().padStart(2, '0')}`;

        // Yearly aggregation
        if (!yearlyData[year]) {
          yearlyData[year] = { revenue: 0, transactions: 0, appointments: 0 };
        }
        yearlyData[year].revenue += transaction.amount || 0;
        yearlyData[year].transactions += 1;

        // Monthly aggregation (last 12 months)
        if (!monthlyData[monthKey]) {
          monthlyData[monthKey] = { revenue: 0, transactions: 0, appointments: 0 };
        }
        monthlyData[monthKey].revenue += transaction.amount || 0;
        monthlyData[monthKey].transactions += 1;
      });

      // Add appointment data to yearly/monthly aggregation
      if (appointments) {
        appointments.forEach(appointment => {
          const date = new Date(appointment.start_at);
          const year = date.getFullYear();
          const monthKey = `${year}-${(date.getMonth() + 1).toString().padStart(2, '0')}`;

          // Yearly aggregation
          if (!yearlyData[year]) {
            yearlyData[year] = { revenue: 0, transactions: 0, appointments: 0 };
          }
          yearlyData[year].appointments += 1;

          // Monthly aggregation
          if (!monthlyData[monthKey]) {
            monthlyData[monthKey] = { revenue: 0, transactions: 0, appointments: 0 };
          }
          monthlyData[monthKey].appointments += 1;
        });
      }

      // Convert to arrays and sort
      const yearlyRevenue = Object.entries(yearlyData)
        .map(([year, data]) => ({
          year: parseInt(year),
          revenue: data.revenue,
          transactions: data.transactions,
          appointments: data.appointments
        }))
        .sort((a, b) => a.year - b.year);

      const monthlyRevenue = Object.entries(monthlyData)
        .map(([month, data]) => ({
          month,
          revenue: data.revenue,
          transactions: data.transactions,
          appointments: data.appointments
        }))
        .sort((a, b) => a.month.localeCompare(b.month))
        .slice(-12); // Last 12 months

      // Recent transactions
      const recentTransactions = transactions.slice(0, 10).map(t => ({
        amount: t.amount || 0,
        created_at: t.created_at
      }));

      // Recent appointments
      const recentAppointments = appointments ? appointments.slice(0, 10).map(apt => ({
        start_at: apt.start_at,
        status: apt.status || 'unknown',
        duration_minutes: apt.duration_minutes || 60
      })) : [];

      setData({
        totalRevenue,
        totalTransactions,
        totalCustomers: customerCount || 0,
        totalAppointments,
        averageTransaction: avgTransaction,
        appointmentConversionRate,
        yearlyRevenue,
        monthlyRevenue,
        appointmentsByStatus,
        averageAppointmentDuration,
        recentTransactions,
        recentAppointments
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
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
            <div className="text-3xl font-bold text-pink-600 mb-2">
              {data.totalAppointments.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Total Appointments</div>
            <div className="text-xs text-gray-500 mt-1">
              {data.appointmentConversionRate.toFixed(1)}% conversion rate
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
        </div>

        {/* Service Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-3xl font-bold text-orange-600 mb-2">
              {formatCurrency(data.averageTransaction)}
            </div>
            <div className="text-sm text-gray-600">Average Transaction</div>
            <div className="text-xs text-gray-500 mt-1">
              Per service visit
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-3xl font-bold text-teal-600 mb-2">
              {Math.round(data.averageAppointmentDuration)}m
            </div>
            <div className="text-sm text-gray-600">Average Session</div>
            <div className="text-xs text-gray-500 mt-1">
              Service duration
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-3xl font-bold text-indigo-600 mb-2">
              {Math.round(data.totalAppointments / (data.yearlyRevenue.length * 365))}
            </div>
            <div className="text-sm text-gray-600">Appointments/Day</div>
            <div className="text-xs text-gray-500 mt-1">
              8-year average
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
                  {year.appointments > 0 && (
                    <div className="text-xs text-pink-600 mt-1">
                      📅 {year.appointments.toLocaleString()} appointments
                    </div>
                  )}
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
                  {month.appointments > 0 && (
                    <span className="text-pink-600"> • {month.appointments} appointments</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Appointment Analytics */}
        {data.appointmentsByStatus.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* Appointment Status Breakdown */}
            <div className="bg-white rounded-lg shadow-md p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">📊 Appointment Status</h2>
              <div className="space-y-3">
                {data.appointmentsByStatus.slice(0, 6).map((status, index) => (
                  <div key={index} className="flex justify-between items-center py-2">
                    <div className="flex items-center">
                      <div className="w-3 h-3 rounded-full mr-3" 
                           style={{ 
                             backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'][index % 6] 
                           }}>
                      </div>
                      <span className="text-sm font-medium text-gray-700 capitalize">
                        {status.status.replace(/_/g, ' ').toLowerCase()}
                      </span>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-semibold text-gray-900">
                        {status.count.toLocaleString()}
                      </div>
                      <div className="text-xs text-gray-500">
                        {status.percentage.toFixed(1)}%
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Appointments */}
            <div className="bg-white rounded-lg shadow-md p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">📅 Recent Appointments</h2>
              <div className="space-y-3">
                {data.recentAppointments.slice(0, 8).map((appointment, index) => (
                  <div key={index} className="flex justify-between items-center py-2 border-b border-gray-100 last:border-b-0">
                    <div>
                      <div className="text-sm font-medium text-gray-900 capitalize">
                        {appointment.status.replace(/_/g, ' ').toLowerCase()}
                      </div>
                      <div className="text-xs text-gray-500">
                        {appointment.duration_minutes} minutes
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-700">
                        {formatDate(appointment.start_at)}
                      </div>
                      <div className="text-xs text-gray-500">
                        {new Date(appointment.start_at).toLocaleTimeString('en-US', { 
                          hour: 'numeric', 
                          minute: '2-digit',
                          hour12: true 
                        })}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Recent Transactions */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
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
                <li>• {data.totalAppointments.toLocaleString()} total appointments scheduled</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-gray-800 mb-2">Operational Metrics</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• {Math.round(data.totalTransactions / (data.yearlyRevenue.length * 365))} transactions per day average</li>
                <li>• {Math.round(data.totalAppointments / (data.yearlyRevenue.length * 365))} appointments per day average</li>
                <li>• {data.appointmentConversionRate.toFixed(1)}% appointment-to-transaction conversion rate</li>
                <li>• Average {Math.round(data.averageAppointmentDuration)} minute service sessions</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}