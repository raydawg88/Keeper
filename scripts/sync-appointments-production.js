/**
 * Production Appointment Sync Script for Keeper
 * 
 * Optimized script for syncing Square appointment data with 31-day chunking
 * Based on successful breakthrough approach that discovered historical data
 */

const https = require('https');
const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

const SQUARE_ACCESS_TOKEN = process.env.SQUARE_ACCESS_TOKEN;
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);

// Configuration
const CHUNK_SIZE_DAYS = 31;
const RATE_LIMIT_MS = 250;
const MAX_RETRIES = 3;
const BATCH_SIZE = 100;

function makeSquareRequest(endpoint, retries = 0) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'connect.squareup.com',
      port: 443,
      path: endpoint,
      method: 'GET',
      headers: {
        'Square-Version': '2025-08-20',
        'Authorization': `Bearer ${SQUARE_ACCESS_TOKEN}`,
        'Accept': 'application/json'
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const result = { status: res.statusCode, data: JSON.parse(data) };
          
          // Retry on rate limiting
          if (res.statusCode === 429 && retries < MAX_RETRIES) {
            const retryAfter = parseInt(res.headers['retry-after'] || '5') * 1000;
            console.log(`   ⏳ Rate limited, retrying in ${retryAfter}ms...`);
            setTimeout(() => {
              makeSquareRequest(endpoint, retries + 1)
                .then(resolve)
                .catch(reject);
            }, retryAfter);
            return;
          }
          
          resolve(result);
        } catch (e) {
          resolve({ status: res.statusCode, error: e.message, raw: data });
        }
      });
    });

    req.on('error', (err) => {
      if (retries < MAX_RETRIES) {
        console.log(`   🔄 Request error, retrying... (${retries + 1}/${MAX_RETRIES})`);
        setTimeout(() => {
          makeSquareRequest(endpoint, retries + 1)
            .then(resolve)
            .catch(reject);
        }, 1000 * (retries + 1));
      } else {
        reject(err);
      }
    });

    req.end();
  });
}

function generateDateRanges(startDate, endDate) {
  const ranges = [];
  let currentStart = new Date(startDate);
  const finalEnd = new Date(endDate);
  
  while (currentStart < finalEnd) {
    let currentEnd = new Date(currentStart);
    currentEnd.setDate(currentEnd.getDate() + CHUNK_SIZE_DAYS - 1);
    
    if (currentEnd > finalEnd) {
      currentEnd = new Date(finalEnd);
    }
    
    ranges.push({
      start: currentStart.toISOString(),
      end: currentEnd.toISOString(),
      label: `${currentStart.toISOString().substring(0, 10)} to ${currentEnd.toISOString().substring(0, 10)}`
    });
    
    currentStart.setDate(currentStart.getDate() + CHUNK_SIZE_DAYS);
  }
  
  return ranges;
}

async function getAccountId(businessName) {
  const { data: accounts, error } = await supabase
    .from('accounts')
    .select('id')
    .eq('business_name', businessName)
    .single();
    
  if (error) {
    throw new Error(`Failed to get account: ${error.message}`);
  }
  
  return accounts.id;
}

async function syncAppointmentChunk(accountId, range, chunkIndex, totalChunks) {
  console.log(`📅 Chunk ${chunkIndex + 1}/${totalChunks}: ${range.label}`);
  
  let chunkAppointments = [];
  let cursor = null;
  let page = 1;
  let totalApiCalls = 0;
  
  do {
    const endpoint = cursor 
      ? `/v2/bookings?start_at_min=${encodeURIComponent(range.start)}&start_at_max=${encodeURIComponent(range.end)}&cursor=${encodeURIComponent(cursor)}&limit=${BATCH_SIZE}`
      : `/v2/bookings?start_at_min=${encodeURIComponent(range.start)}&start_at_max=${encodeURIComponent(range.end)}&limit=${BATCH_SIZE}`;
    
    totalApiCalls++;
    const response = await makeSquareRequest(endpoint);
    
    if (response.status === 200 && response.data.bookings) {
      const pageCount = response.data.bookings.length;
      chunkAppointments = chunkAppointments.concat(response.data.bookings);
      
      if (pageCount > 0) {
        console.log(`   📄 Page ${page}: ${pageCount} appointments (Total: ${chunkAppointments.length})`);
      }
      
      cursor = response.data.cursor;
      page++;
    } else if (response.status === 400) {
      console.log(`   ⚠️  API error: ${response.data?.errors?.[0]?.detail || 'Unknown'}`);
      break;
    } else {
      console.log(`   ❌ HTTP ${response.status}: ${response.data?.errors?.[0]?.detail || 'Unknown error'}`);
      break;
    }
    
    // Rate limiting
    await new Promise(resolve => setTimeout(resolve, RATE_LIMIT_MS));
    
  } while (cursor);
  
  // Insert appointments if found
  if (chunkAppointments.length > 0) {
    console.log(`   ✅ Found ${chunkAppointments.length} appointments`);
    
    const appointmentData = chunkAppointments.map(booking => ({
      account_id: accountId,
      square_booking_id: booking.id,
      customer_id: booking.customer_id || 'unknown',
      location_id: booking.location_id || 'unknown',
      service_variation_id: booking.appointment_segments?.[0]?.service_variation_id || 'unknown',
      duration_minutes: booking.appointment_segments?.[0]?.duration_minutes || 60,
      start_at: booking.start_at || new Date().toISOString(),
      status: booking.status || 'unknown',
      created_at: booking.created_at || new Date().toISOString(),
      updated_at: booking.updated_at || new Date().toISOString()
    }));
    
    const { error } = await supabase
      .from('appointments')
      .upsert(appointmentData, { 
        onConflict: 'square_booking_id',
        ignoreDuplicates: false 
      });
      
    if (error) {
      console.error(`   ❌ Insert error: ${error.message}`);
      return { success: false, count: 0, apiCalls: totalApiCalls };
    } else {
      console.log(`   💾 Inserted/updated ${appointmentData.length} appointments`);
    }
  } else {
    console.log(`   📭 No appointments in this range`);
  }
  
  return { 
    success: true, 
    count: chunkAppointments.length, 
    apiCalls: totalApiCalls 
  };
}

async function syncAppointments(businessName, startDate = '2017-01-01', endDate = null) {
  console.log('🔄 KEEPER APPOINTMENT SYNC');
  console.log('==========================');
  
  try {
    const accountId = await getAccountId(businessName);
    console.log(`📊 Account ID: ${accountId}`);
    console.log(`🏢 Business: ${businessName}`);
    
    const finalEndDate = endDate || new Date().toISOString();
    console.log(`📅 Sync period: ${startDate} to ${finalEndDate.substring(0, 10)}`);
    
    // Check current progress
    const { count: currentCount } = await supabase
      .from('appointments')
      .select('*', { count: 'exact', head: true })
      .eq('account_id', accountId);
    
    console.log(`📊 Current appointments in DB: ${currentCount?.toLocaleString() || 0}`);
    
    const dateRanges = generateDateRanges(startDate, finalEndDate);
    console.log(`📅 Processing ${dateRanges.length} date ranges (${CHUNK_SIZE_DAYS}-day chunks)`);
    console.log();
    
    let totalNewAppointments = 0;
    let totalApiCalls = 0;
    const appointmentsByYear = {};
    const startTime = Date.now();
    
    for (let i = 0; i < dateRanges.length; i++) {
      const range = dateRanges[i];
      const year = range.start.substring(0, 4);
      
      try {
        const result = await syncAppointmentChunk(accountId, range, i, dateRanges.length);
        
        if (result.success) {
          // Track by year
          if (!appointmentsByYear[year]) appointmentsByYear[year] = 0;
          appointmentsByYear[year] += result.count;
          totalNewAppointments += result.count;
          totalApiCalls += result.apiCalls;
        }
        
      } catch (chunkError) {
        console.error(`❌ Chunk ${i + 1} failed: ${chunkError.message}`);
      }
      
      // Progress report every 10 chunks
      if ((i + 1) % 10 === 0 || i === dateRanges.length - 1) {
        const elapsed = (Date.now() - startTime) / 1000;
        const remaining = dateRanges.length - (i + 1);
        const avgTimePerChunk = elapsed / (i + 1);
        const eta = remaining * avgTimePerChunk;
        
        console.log(`\n📊 PROGRESS: ${i + 1}/${dateRanges.length} chunks complete`);
        console.log(`   ⏱️  Elapsed: ${Math.round(elapsed)}s | ETA: ${Math.round(eta)}s`);
        console.log(`   📊 New appointments: ${totalNewAppointments.toLocaleString()}`);
        console.log(`   🌐 API calls: ${totalApiCalls.toLocaleString()}`);
        
        if (Object.keys(appointmentsByYear).length > 0) {
          console.log(`   📈 By year: ${Object.entries(appointmentsByYear)
            .map(([y, count]) => `${y}: ${count.toLocaleString()}`)
            .join(', ')}`);
        }
        console.log();
      }
    }
    
    // Final summary
    const { count: finalCount } = await supabase
      .from('appointments')
      .select('*', { count: 'exact', head: true })
      .eq('account_id', accountId);
    
    const { data: dateRange } = await supabase
      .from('appointments')
      .select('start_at')
      .eq('account_id', accountId)
      .order('start_at', { ascending: true })
      .limit(1);
      
    const { data: latestDate } = await supabase
      .from('appointments')
      .select('start_at')
      .eq('account_id', accountId)
      .order('start_at', { ascending: false })
      .limit(1);
    
    const totalTime = (Date.now() - startTime) / 1000;
    
    console.log(`🎉 APPOINTMENT SYNC COMPLETE!`);
    console.log('=====================================');
    console.log(`📊 Total appointments: ${finalCount?.toLocaleString()}`);
    console.log(`📊 New appointments added: ${totalNewAppointments.toLocaleString()}`);
    console.log(`📅 Date range: ${dateRange?.[0]?.start_at?.substring(0, 10)} to ${latestDate?.[0]?.start_at?.substring(0, 10)}`);
    console.log(`⏱️  Total time: ${Math.round(totalTime)}s`);
    console.log(`🌐 Total API calls: ${totalApiCalls.toLocaleString()}`);
    console.log(`📈 By year: ${Object.entries(appointmentsByYear)
      .map(([y, count]) => `${y}: ${count.toLocaleString()}`)
      .join(', ')}`);
    console.log('=====================================');
    
    return {
      success: true,
      totalAppointments: finalCount,
      newAppointments: totalNewAppointments,
      apiCalls: totalApiCalls,
      timeSeconds: totalTime
    };
    
  } catch (error) {
    console.error('❌ Sync failed:', error.message);
    return { success: false, error: error.message };
  }
}

// CLI execution
if (require.main === module) {
  const args = process.argv.slice(2);
  const businessName = args[0] || 'Bashful Beauty';
  const startDate = args[1] || '2017-01-01';
  const endDate = args[2] || null;
  
  console.log(`Starting appointment sync for: ${businessName}`);
  
  syncAppointments(businessName, startDate, endDate)
    .then(result => {
      if (result.success) {
        console.log(`✅ Sync completed successfully!`);
        process.exit(0);
      } else {
        console.error(`❌ Sync failed: ${result.error}`);
        process.exit(1);
      }
    })
    .catch(error => {
      console.error(`❌ Unexpected error: ${error.message}`);
      process.exit(1);
    });
}

module.exports = { syncAppointments };