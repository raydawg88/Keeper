import { NextRequest, NextResponse } from 'next/server'
import { SquareDataExplorer } from '@/lib/square-data-explorer'

export async function GET(req: NextRequest) {
  try {
    // For now, we'll use a hardcoded access token from our successful OAuth
    // In production, this would fetch from the database based on account_id
    const accessToken = process.env.SQUARE_ACCESS_TOKEN;
    
    if (!accessToken) {
      return NextResponse.json(
        { error: 'No Square access token available' },
        { status: 400 }
      )
    }

    console.log('🔍 Starting Square data exploration...');
    
    const explorer = new SquareDataExplorer(accessToken, 'production');
    const allData = await explorer.exploreAll();

    return NextResponse.json({
      success: true,
      message: 'Square data exploration complete',
      data: allData
    });

  } catch (error) {
    console.error('Square data exploration error:', error);
    return NextResponse.json(
      { error: 'Failed to explore Square data: ' + (error instanceof Error ? error.message : String(error)) },
      { status: 500 }
    )
  }
}

export async function POST(req: NextRequest) {
  try {
    const { access_token, entity_type } = await req.json();
    
    if (!access_token) {
      return NextResponse.json(
        { error: 'Access token required' },
        { status: 400 }
      )
    }

    const explorer = new SquareDataExplorer(access_token, 'production');
    
    let result;
    switch (entity_type) {
      case 'customers':
        result = await explorer.exploreCustomers();
        break;
      case 'payments':
        result = await explorer.explorePayments();
        break;
      case 'orders':
        result = await explorer.exploreOrders();
        break;
      case 'locations':
        result = await explorer.exploreLocations();
        break;
      case 'items':
        result = await explorer.exploreItems();
        break;
      case 'employees':
        result = await explorer.exploreEmployees();
        break;
      default:
        result = await explorer.exploreAll();
    }

    return NextResponse.json({
      success: true,
      entity_type,
      data: result
    });

  } catch (error) {
    console.error('Square data exploration error:', error);
    return NextResponse.json(
      { error: 'Failed to explore Square data: ' + (error instanceof Error ? error.message : String(error)) },
      { status: 500 }
    )
  }
}