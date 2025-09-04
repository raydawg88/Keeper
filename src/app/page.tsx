'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ArrowRight, BarChart3, DollarSign, TrendingUp, Users, Zap } from 'lucide-react'

export default function HomePage() {
  const [isConnecting, setIsConnecting] = useState(false)

  const handleConnectSquare = async () => {
    setIsConnecting(true)
    
    try {
      // Generate OAuth URL from our backend
      const response = await fetch('/api/auth/square/authorize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          business_name: 'New Business', // We'll make this dynamic later
          redirect_uri: `${window.location.origin}/auth/callback`
        })
      })
      
      if (!response.ok) {
        throw new Error('Failed to initialize Square connection')
      }
      
      const { auth_url } = await response.json()
      
      // Redirect to Square OAuth
      window.location.href = auth_url
      
    } catch (error) {
      console.error('OAuth initialization failed:', error)
      setIsConnecting(false)
      alert('Connection failed. Please try again.')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-sm font-medium mb-6">
            <Zap className="w-4 h-4" />
            Find Hidden Revenue in Under 90 Seconds
          </div>
          
          <h1 className="text-5xl font-bold text-gray-900 mb-6 leading-tight">
            Turn Your Square Data Into
            <span className="text-blue-600 block">$3,000+ Revenue Opportunities</span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
            Keeper's AI analyzes your Square POS data to find actionable insights with specific dollar values. 
            No generic advice—just precise opportunities to grow your business.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button 
              onClick={handleConnectSquare}
              disabled={isConnecting}
              size="lg"
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-6 text-lg font-medium"
            >
              {isConnecting ? (
                <>
                  <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full mr-2" />
                  Connecting to Square...
                </>
              ) : (
                <>
                  Connect Your Square Account
                  <ArrowRight className="ml-2 w-5 h-5" />
                </>
              )}
            </Button>
            
            <div className="text-sm text-gray-500">
              <span className="inline-flex items-center gap-1">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Secure OAuth Connection
              </span>
              <span className="mx-2">•</span>
              <span className="inline-flex items-center gap-1">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Read-Only Access
              </span>
            </div>
          </div>
        </div>

        {/* Value Proposition Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
            <CardHeader className="text-center pb-4">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <DollarSign className="w-6 h-6 text-green-600" />
              </div>
              <CardTitle className="text-xl">Revenue Discovery</CardTitle>
              <CardDescription>Find $3,000+ in hidden opportunities</CardDescription>
            </CardHeader>
            <CardContent className="text-center">
              <ul className="text-sm text-gray-600 space-y-2">
                <li>• High-value customer churn prevention</li>
                <li>• Tip optimization strategies</li>
                <li>• Service upselling opportunities</li>
                <li>• Staff performance insights</li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
            <CardHeader className="text-center pb-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="w-6 h-6 text-blue-600" />
              </div>
              <CardTitle className="text-xl">AI-Powered Analysis</CardTitle>
              <CardDescription>97%+ accuracy customer matching</CardDescription>
            </CardHeader>
            <CardContent className="text-center">
              <ul className="text-sm text-gray-600 space-y-2">
                <li>• Advanced pattern recognition</li>
                <li>• Multi-model validation</li>
                <li>• Real-time insights generation</li>
                <li>• Confidence-scored recommendations</li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
            <CardHeader className="text-center pb-4">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="w-6 h-6 text-purple-600" />
              </div>
              <CardTitle className="text-xl">Actionable Results</CardTitle>
              <CardDescription>Specific steps with dollar values</CardDescription>
            </CardHeader>
            <CardContent className="text-center">
              <ul className="text-sm text-gray-600 space-y-2">
                <li>• No obvious or generic advice</li>
                <li>• 75%+ confidence threshold</li>
                <li>• Detailed action scripts</li>
                <li>• ROI tracking and measurement</li>
              </ul>
            </CardContent>
          </Card>
        </div>

        {/* How It Works */}
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-12">How Keeper Works</h2>
          
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                1
              </div>
              <h3 className="text-lg font-semibold mb-2">Connect Square</h3>
              <p className="text-gray-600 text-sm">Secure OAuth connection to your Square POS data</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                2
              </div>
              <h3 className="text-lg font-semibold mb-2">AI Analysis</h3>
              <p className="text-gray-600 text-sm">8 specialized agents analyze your business patterns</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                3
              </div>
              <h3 className="text-lg font-semibold mb-2">Find Opportunities</h3>
              <p className="text-gray-600 text-sm">Discover $3,000+ in actionable revenue opportunities</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                4
              </div>
              <h3 className="text-lg font-semibold mb-2">Take Action</h3>
              <p className="text-gray-600 text-sm">Implement specific strategies with detailed scripts</p>
            </div>
          </div>
        </div>

        {/* Trust Indicators */}
        <div className="text-center">
          <div className="inline-flex items-center gap-6 text-sm text-gray-500">
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
              </svg>
              Bank-Level Security
            </div>
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 text-blue-500" />
              Trusted by 100+ Businesses
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="text-xs">
                97%+ Accuracy
              </Badge>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t bg-white">
        <div className="container mx-auto px-4 py-8 text-center text-gray-600">
          <p>&copy; 2024 Keeper.tools - Turn your data into revenue</p>
        </div>
      </footer>
    </div>
  )
}