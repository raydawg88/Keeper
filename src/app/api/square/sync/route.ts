import { NextRequest, NextResponse } from 'next/server';
import { SquareDataSync } from '@/lib/square-data-sync';

export async function POST(req: NextRequest) {
  try {
    const { account_id, access_token, environment = 'production', sync_type = 'full', entities } = await req.json();
    
    if (!account_id || !access_token) {
      return NextResponse.json(
        { error: 'Account ID and access token are required' },
        { status: 400 }
      );
    }

    console.log(`🚀 Starting Square data sync for account ${account_id}`);
    console.log(`🌍 Environment: ${environment}`);
    
    // Initialize data sync service
    const syncService = new SquareDataSync({
      accountId: account_id,
      accessToken: access_token,
      environment: environment as 'sandbox' | 'production',
      syncType: sync_type,
      entities: entities
    });

    // Start the sync process
    const syncResult = await syncService.startSync(entities);

    return NextResponse.json({
      success: syncResult.overallStatus === 'completed',
      syncStatus: syncResult.overallStatus,
      totalRecords: syncResult.totalRecords,
      results: syncResult.results,
      duration: syncResult.endTime ? 
        syncResult.endTime.getTime() - syncResult.startTime.getTime() : 0,
      message: syncResult.overallStatus === 'completed' ? 
        `Successfully synced ${syncResult.totalRecords} records` : 
        'Sync completed with errors'
    });

  } catch (error) {
    console.error('Square sync API error:', error);
    return NextResponse.json(
      { 
        error: 'Failed to sync Square data',
        details: error instanceof Error ? error.message : String(error)
      },
      { status: 500 }
    );
  }
}

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const accountId = searchParams.get('account_id');
    
    if (!accountId) {
      return NextResponse.json(
        { error: 'Account ID is required' },
        { status: 400 }
      );
    }

    // Get sync status for the account
    // This would query the square_sync_status table
    // For now, return a placeholder response
    
    return NextResponse.json({
      success: true,
      message: 'Sync status endpoint ready',
      accountId
    });

  } catch (error) {
    console.error('Sync status API error:', error);
    return NextResponse.json(
      { error: 'Failed to get sync status' },
      { status: 500 }
    );
  }
}