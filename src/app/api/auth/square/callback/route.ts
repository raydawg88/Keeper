import { NextRequest, NextResponse } from 'next/server'
import { SquareOAuthManager } from '@/lib/square_oauth'

// Simple in-memory cache to prevent duplicate processing
const processedCodes = new Set<string>()

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url)
    const code = searchParams.get('code')
    const state = searchParams.get('state')
    
    console.log('=== CALLBACK DEBUG ===')
    console.log('Received code:', code ? code.substring(0, 20) + '...' : 'MISSING')
    console.log('Received state:', state || 'MISSING')
    
    if (!code) {
      return NextResponse.json(
        { error: 'Missing authorization code' },
        { status: 400 }
      )
    }
    
    // Prevent duplicate processing of the same code
    if (processedCodes.has(code)) {
      console.log('Duplicate code detected, ignoring:', code.substring(0, 20) + '...')
      return NextResponse.json(
        { error: 'Code already processed' },
        { status: 409 }
      )
    }
    
    // Mark code as being processed
    processedCodes.add(code)
    
    // Initialize OAuth manager
    const oauthManager = new SquareOAuthManager()
    
    // Handle the callback and create account
    const result = await oauthManager.handleOAuthCallback(code, state || 'no-state')
    
    if (!result) {
      return NextResponse.json(
        { error: 'OAuth callback processing failed' },
        { status: 500 }
      )
    }
    
    console.log('Callback success! Account created:', result.account_id)
    
    // Clean up processed code after successful processing
    setTimeout(() => {
      processedCodes.delete(code)
    }, 60000) // Remove after 1 minute
    
    return NextResponse.json({
      account_id: result.account_id,
      business_name: result.business_name,
      merchant_id: result.merchant_id,
      locations: result.locations,
      access_token: result.access_token  // Temporarily expose for testing
    })
    
  } catch (error) {
    console.error('OAuth callback API error:', error)
    return NextResponse.json(
      { error: 'Internal server error: ' + (error instanceof Error ? error.message : String(error)) },
      { status: 500 }
    )
  }
}