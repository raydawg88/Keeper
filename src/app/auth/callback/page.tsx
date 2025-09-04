'use client'

import { useEffect, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { CheckCircle, AlertCircle, Loader2 } from 'lucide-react'

export default function AuthCallbackPage() {
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing')
  const [accountInfo, setAccountInfo] = useState<any>(null)
  const [errorMessage, setErrorMessage] = useState<string>('')
  
  const searchParams = useSearchParams()
  const router = useRouter()
  
  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code')
      const state = searchParams.get('state')
      const error = searchParams.get('error')
      
      if (error) {
        setStatus('error')
        setErrorMessage(`Square authorization failed: ${error}`)
        return
      }
      
      if (!code) {
        setStatus('error')
        setErrorMessage('Missing authorization code')
        return
      }
      
      try {
        // Handle OAuth callback
        const response = await fetch('/api/auth/square/callback', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ code, state: state || 'no-state' })
        })
        
        if (!response.ok) {
          throw new Error(`Callback failed: ${response.statusText}`)
        }
        
        const result = await response.json()
        
        setAccountInfo(result)
        setStatus('success')
        
        // Redirect to homepage after success (dashboard will be built later)
        setTimeout(() => {
          router.push('/')
        }, 3000)
        
      } catch (error) {
        console.error('Callback processing error:', error)
        setStatus('error')
        setErrorMessage(error instanceof Error ? error.message : 'Unknown error occurred')
      }
    }
    
    handleCallback()
  }, [searchParams, router])
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4">
            {status === 'processing' && (
              <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
            )}
            {status === 'success' && (
              <CheckCircle className="w-12 h-12 text-green-600" />
            )}
            {status === 'error' && (
              <AlertCircle className="w-12 h-12 text-red-600" />
            )}
          </div>
          
          <CardTitle>
            {status === 'processing' && 'Connecting Your Business...'}
            {status === 'success' && 'Connection Successful!'}
            {status === 'error' && 'Connection Failed'}
          </CardTitle>
          
          <CardDescription>
            {status === 'processing' && 'Securely connecting to your Square account'}
            {status === 'success' && 'Your business data is now being analyzed'}
            {status === 'error' && 'There was an issue connecting your account'}
          </CardDescription>
        </CardHeader>
        
        <CardContent className="text-center">
          {status === 'processing' && (
            <div className="space-y-2">
              <p className="text-sm text-gray-600">Please wait while we:</p>
              <ul className="text-sm text-gray-500 space-y-1">
                <li>✓ Verify your Square credentials</li>
                <li>⏳ Create your Keeper account</li>
                <li>⏳ Begin data analysis</li>
              </ul>
            </div>
          )}
          
          {status === 'success' && accountInfo && (
            <div className="space-y-4">
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="font-medium text-green-800">{accountInfo.business_name}</p>
                <p className="text-sm text-green-600">
                  {accountInfo.locations?.length || 0} location(s) connected
                </p>
              </div>
              
              <p className="text-sm text-gray-600">
                Redirecting to your dashboard in a few seconds...
              </p>
              
              <Button 
                onClick={() => router.push('/')}
                className="w-full"
              >
                Return to Home
              </Button>
            </div>
          )}
          
          {status === 'error' && (
            <div className="space-y-4">
              <div className="bg-red-50 p-4 rounded-lg">
                <p className="text-sm text-red-600">{errorMessage}</p>
              </div>
              
              <div className="space-y-2">
                <Button 
                  onClick={() => router.push('/')}
                  className="w-full"
                >
                  Try Again
                </Button>
                
                <Button 
                  variant="outline"
                  onClick={() => window.open('mailto:support@keeper.tools', '_blank')}
                  className="w-full"
                >
                  Contact Support
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}