import { NextRequest, NextResponse } from 'next/server'
import { SquareOAuthManager } from '@/lib/square_oauth'

export async function POST(req: NextRequest) {
  try {
    const { business_name, redirect_uri } = await req.json()
    
    if (!redirect_uri) {
      return NextResponse.json(
        { error: 'redirect_uri is required' },
        { status: 400 }
      )
    }
    
    // Initialize OAuth manager
    const oauthManager = new SquareOAuthManager()
    
    // Generate OAuth URL
    const oauthResult = oauthManager.generateOAuthUrl(redirect_uri, business_name)
    
    if (!oauthResult) {
      return NextResponse.json(
        { error: 'Failed to generate OAuth URL' },
        { status: 500 }
      )
    }
    
    return NextResponse.json({
      auth_url: oauthResult.auth_url,
      state: oauthResult.state,
      session_id: oauthResult.session_id
    })
    
  } catch (error) {
    console.error('OAuth authorization error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}