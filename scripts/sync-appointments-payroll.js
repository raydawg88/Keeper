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

// Sync all appointments with pagination
async function syncAllAppointments(accountId) {
  console.log('📅 Starting appointments sync...');
  let allAppointments = [];
  let cursor = null;
  let page = 1;
  let totalSynced = 0;
  
  do {
    try {
      console.log(`📄 Fetching appointments page ${page}...`);
      
      let endpoint = '/v2/bookings?limit=100';
      if (cursor) {
        endpoint += `&cursor=${encodeURIComponent(cursor)}`;
      }
      
      const response = await makeSquareRequest(endpoint);
      
      if (response.bookings && response.bookings.length > 0) {
        console.log(`   Found ${response.bookings.length} appointments on page ${page}`);
        
        // Transform appointment data for Supabase
        const appointmentData = response.bookings.map(booking => {
          const segment = booking.appointment_segments?.[0] || {};
          return {
            account_id: accountId,
            square_booking_id: booking.id,
            customer_id: booking.customer_id,
            location_id: booking.location_id,
            service_variation_id: segment.service_variation_id || null,
            duration_minutes: segment.duration_minutes || null,
            start_at: segment.start_at || null,
            status: booking.status,
            created_at: booking.created_at || new Date().toISOString(),
            updated_at: booking.updated_at || new Date().toISOString()
          };
        });

        // Table should be created manually using create_appointments_table.sql
        // But we'll try creating it here if it doesn't exist
        try {
          await supabase.rpc('create_appointments_table_if_not_exists');
        } catch (error) {
          // Table might already exist, that's ok
          console.log('   (Table creation skipped - may already exist)');
        }

        // Insert appointments (simple insert for now)
        const { error } = await supabase
          .from('appointments')
          .insert(appointmentData);

        if (error) {
          console.error(`❌ Error inserting appointments:`, error);
        } else {
          totalSynced += appointmentData.length;
          console.log(`   ✅ Synced ${appointmentData.length} appointments (total: ${totalSynced})`);
        }
        
        allAppointments.push(...response.bookings);
      }
      
      cursor = response.cursor;
      page++;
      
      await sleep(500);
      
    } catch (error) {
      console.error(`❌ Error fetching appointments page ${page}:`, error.message);
      break;
    }
  } while (cursor);
  
  console.log(`🎉 Appointments sync complete! Total synced: ${totalSynced}`);
  return allAppointments;
}

// Sync labor shifts
async function syncLaborShifts(accountId) {
  console.log('⏰ Starting labor shifts sync...');
  
  try {
    const response = await makeSquareRequest('/v2/labor/shifts/search', 'POST', {
      filter: {
        start: {
          start_at: '2024-01-01T00:00:00Z',
          end_at: '2025-12-31T23:59:59Z'
        }
      },
      limit: 200
    });
    
    if (response.shifts && response.shifts.length > 0) {
      console.log(`   Found ${response.shifts.length} labor shifts`);
      
      // Transform shift data
      const shiftData = response.shifts.map(shift => ({
        account_id: accountId,
        square_shift_id: shift.id,
        team_member_id: shift.team_member_id,
        location_id: shift.location_id,
        start_at: shift.start_at,
        end_at: shift.end_at,
        wage: shift.wage ? parseFloat(shift.wage.hourly_rate || 0) / 100 : null, // Convert from cents
        status: shift.status,
        created_at: shift.created_at || new Date().toISOString(),
        updated_at: shift.updated_at || new Date().toISOString()
      }));

      // Log to console for now (would need to create shifts table)
      console.log(`   Sample shift: ${shiftData[0].start_at} - ${shiftData[0].end_at} ($${shiftData[0].wage || 0}/hr)`);
      console.log(`   ✅ Processed ${shiftData.length} shifts`);
      
      return shiftData;
    }
  } catch (error) {
    console.error('❌ Error syncing labor shifts:', error.message);
  }
  
  return [];
}

// Main sync function
async function syncAppointmentsAndPayroll() {
  try {
    console.log('🎯 Starting complete appointments and payroll sync for Bashful Beauty...\n');
    
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
    
    // Sync appointments
    const appointments = await syncAllAppointments(accountId);
    console.log(`📈 Total appointments retrieved: ${appointments.length}\n`);
    
    // Sync labor shifts
    const shifts = await syncLaborShifts(accountId);
    console.log(`📈 Total shifts processed: ${shifts.length}\n`);
    
    // Final summary
    console.log('🏁 SYNC SUMMARY:');
    console.log(`   Appointments: ${appointments.length} retrieved and synced`);
    console.log(`   Labor Shifts: ${shifts.length} processed`);
    console.log('   Status: Complete ✅');
    
  } catch (error) {
    console.error('💥 Sync failed:', error);
  }
}

// Run the sync
if (require.main === module) {
  syncAppointmentsAndPayroll();
}

module.exports = { syncAppointmentsAndPayroll };