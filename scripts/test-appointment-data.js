#!/usr/bin/env node

const https = require('https');
require('dotenv').config({ path: '.env' });

// Configuration - will need new token with expanded scopes
const SQUARE_ACCESS_TOKEN = process.env.SQUARE_ACCESS_TOKEN || 'EAAAlnr4NgdhtBbcMt_Cz9zyufGUFuIlA19ibdvtoMRYmGnbLj90SdezKXj3Nnz6';
const SQUARE_ENVIRONMENT = process.env.SQUARE_ENVIRONMENT || 'production';
const SQUARE_BASE_URL = SQUARE_ENVIRONMENT === 'production' 
  ? 'https://connect.squareup.com'
  : 'https://connect.squareupsandbox.com';

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

// Test all appointment and employee related endpoints
async function testAppointmentData() {
  console.log('🔍 Testing Square Appointment and Employee Data Access...\n');
  
  const tests = [
    {
      name: 'Bookings/Appointments',
      endpoint: '/v2/bookings',
      description: 'Main appointments data'
    },
    {
      name: 'Booking Custom Attributes',
      endpoint: '/v2/bookings/custom-attribute-definitions',
      description: 'Custom attributes for bookings'
    },
    {
      name: 'Team Members',
      endpoint: '/v2/team-members',
      description: 'Employee/staff data'
    },
    {
      name: 'Labor Shifts',
      endpoint: '/v2/labor/shifts/search',
      description: 'Employee shift data',
      method: 'POST',
      data: {
        filter: {
          start: {
            start_at: '2024-01-01T00:00:00Z',
            end_at: '2025-12-31T23:59:59Z'
          }
        },
        limit: 10
      }
    },
    {
      name: 'Wage Settings',
      endpoint: '/v2/labor/team-member-wages',
      description: 'Employee wage settings'
    },
    {
      name: 'Workweek Configs',
      endpoint: '/v2/labor/workweek-configs',
      description: 'Payroll workweek configurations'
    }
  ];

  let successCount = 0;
  let totalRevenue = 0;
  let appointmentCount = 0;

  for (const test of tests) {
    try {
      console.log(`📊 Testing ${test.name}...`);
      
      const response = await makeSquareRequest(test.endpoint, test.method, test.data);
      
      if (response.errors && response.errors.length > 0) {
        console.log(`   ❌ ${test.name}: ${response.errors[0].detail || response.errors[0].code}`);
        continue;
      }
      
      // Analyze response based on endpoint
      if (test.endpoint === '/v2/bookings') {
        appointmentCount = response.bookings?.length || 0;
        console.log(`   ✅ ${test.name}: ${appointmentCount} appointments found`);
        if (appointmentCount > 0) {
          const sampleBooking = response.bookings[0];
          console.log(`      Sample: ${sampleBooking.appointment_segments?.[0]?.service_variation_id ? 'Service booking' : 'Basic booking'}`);
        }
      } else if (test.endpoint === '/v2/team-members') {
        const teamCount = response.team_members?.length || 0;
        console.log(`   ✅ ${test.name}: ${teamCount} team members found`);
        if (teamCount > 0) {
          const activeMembers = response.team_members.filter(m => m.status === 'ACTIVE').length;
          console.log(`      Active members: ${activeMembers}`);
        }
      } else if (test.endpoint.includes('labor')) {
        if (response.shifts) {
          console.log(`   ✅ ${test.name}: ${response.shifts.length} shifts found`);
        } else if (response.team_member_wages) {
          console.log(`   ✅ ${test.name}: ${response.team_member_wages.length} wage settings found`);
        } else if (response.workweek_configs) {
          console.log(`   ✅ ${test.name}: ${response.workweek_configs.length} workweek configs found`);
        } else {
          console.log(`   ✅ ${test.name}: Response received`);
        }
      } else {
        const dataKeys = Object.keys(response).filter(key => Array.isArray(response[key]));
        if (dataKeys.length > 0) {
          const totalItems = dataKeys.reduce((sum, key) => sum + response[key].length, 0);
          console.log(`   ✅ ${test.name}: ${totalItems} items found`);
        } else {
          console.log(`   ✅ ${test.name}: Data available`);
        }
      }
      
      successCount++;
      
    } catch (error) {
      if (error.message.includes('NOT_FOUND') || error.message.includes('404')) {
        console.log(`   ⚠️  ${test.name}: Endpoint not available or no data`);
      } else if (error.message.includes('UNAUTHORIZED') || error.message.includes('403')) {
        console.log(`   🔒 ${test.name}: Insufficient permissions - may need re-authentication with new scopes`);
      } else {
        console.log(`   ❌ ${test.name}: ${error.message}`);
      }
    }
    
    // Rate limiting
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  console.log('\n📋 SUMMARY:');
  console.log(`   Successful API calls: ${successCount}/${tests.length}`);
  console.log(`   Appointments found: ${appointmentCount}`);
  
  if (successCount === 0) {
    console.log('\n🔄 RECOMMENDATION: Re-authenticate through OAuth flow with new scopes');
    console.log('   1. Go to http://localhost:3000/dashboard');
    console.log('   2. Click "Connect to Square" to get new token with appointment permissions');
    console.log('   3. Update .env with the new access token');
    console.log('   4. Run this script again');
  }
}

if (require.main === module) {
  testAppointmentData().catch(console.error);
}

module.exports = { testAppointmentData };