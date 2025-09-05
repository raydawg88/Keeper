import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const { access_token } = await req.json();
    
    if (!access_token) {
      return NextResponse.json(
        { error: 'Access token required' },
        { status: 400 }
      );
    }

    console.log('🧪 Testing access token:', access_token.substring(0, 10) + '...');

    // Test the access token with Square's production API
    const headers = {
      'Authorization': `Bearer ${access_token}`,
      'Square-Version': '2025-08-20',
      'Content-Type': 'application/json'
    };

    // Try multiple endpoints to see what data we can access
    const testResults = {
      accessToken: access_token.substring(0, 10) + '...',
      tests: {}
    };

    // Test 1: Get merchant info
    try {
      const merchantResponse = await fetch('https://connect.squareup.com/v2/merchants', { 
        headers 
      });
      
      if (merchantResponse.ok) {
        const merchantData = await merchantResponse.json();
        testResults.tests.merchants = {
          success: true,
          data: merchantData
        };
        console.log('✅ Merchants API success:', JSON.stringify(merchantData, null, 2));
      } else {
        const errorText = await merchantResponse.text();
        testResults.tests.merchants = {
          success: false,
          status: merchantResponse.status,
          error: errorText
        };
        console.log('❌ Merchants API failed:', merchantResponse.status, errorText);
      }
    } catch (error) {
      testResults.tests.merchants = {
        success: false,
        error: error instanceof Error ? error.message : String(error)
      };
    }

    // Test 2: Get locations  
    try {
      const locationsResponse = await fetch('https://connect.squareup.com/v2/locations', { 
        headers 
      });
      
      if (locationsResponse.ok) {
        const locationsData = await locationsResponse.json();
        testResults.tests.locations = {
          success: true,
          data: locationsData
        };
        console.log('✅ Locations API success:', JSON.stringify(locationsData, null, 2));
      } else {
        const errorText = await locationsResponse.text();
        testResults.tests.locations = {
          success: false,
          status: locationsResponse.status,
          error: errorText
        };
        console.log('❌ Locations API failed:', locationsResponse.status, errorText);
      }
    } catch (error) {
      testResults.tests.locations = {
        success: false,
        error: error instanceof Error ? error.message : String(error)
      };
    }

    // Test 3: Get customers (first 3)
    try {
      const customersResponse = await fetch('https://connect.squareup.com/v2/customers?limit=3', { 
        headers 
      });
      
      if (customersResponse.ok) {
        const customersData = await customersResponse.json();
        testResults.tests.customers = {
          success: true,
          count: customersData.customers?.length || 0,
          data: customersData
        };
        console.log('✅ Customers API success:', customersData.customers?.length || 0, 'customers found');
      } else {
        const errorText = await customersResponse.text();
        testResults.tests.customers = {
          success: false,
          status: customersResponse.status,
          error: errorText
        };
        console.log('❌ Customers API failed:', customersResponse.status, errorText);
      }
    } catch (error) {
      testResults.tests.customers = {
        success: false,
        error: error instanceof Error ? error.message : String(error)
      };
    }

    return NextResponse.json({
      success: true,
      message: 'Access token test complete',
      results: testResults
    });

  } catch (error) {
    console.error('Token test error:', error);
    return NextResponse.json(
      { 
        error: 'Token test failed',
        details: error instanceof Error ? error.message : String(error)
      },
      { status: 500 }
    );
  }
}