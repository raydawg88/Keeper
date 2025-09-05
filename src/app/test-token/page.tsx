'use client';

import { useState } from 'react';

export default function TestToken() {
  const [accessToken, setAccessToken] = useState('');
  const [testing, setTesting] = useState(false);
  const [results, setResults] = useState<any>(null);

  const testToken = async () => {
    if (!accessToken.trim()) {
      alert('Please enter an access token');
      return;
    }

    setTesting(true);
    setResults(null);

    try {
      const response = await fetch('/api/square/test-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          access_token: accessToken.trim()
        }),
      });

      const data = await response.json();
      setResults(data);
    } catch (error) {
      setResults({
        success: false,
        error: 'Network error: ' + error
      });
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Square Access Token Tester
          </h1>
          <p className="text-gray-600">
            Test if your access token can access real Square data
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="mb-6">
            <label htmlFor="token" className="block text-sm font-medium text-gray-700 mb-2">
              Access Token
            </label>
            <textarea
              id="token"
              value={accessToken}
              onChange={(e) => setAccessToken(e.target.value)}
              placeholder="Paste your Square access token here (starts with EAAA...)"
              className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              rows={3}
            />
          </div>

          <button
            onClick={testToken}
            disabled={testing || !accessToken.trim()}
            className={`w-full py-3 px-4 rounded-md font-medium ${
              testing || !accessToken.trim()
                ? 'bg-gray-400 cursor-not-allowed text-white'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            {testing ? 'Testing Token...' : 'Test Access Token'}
          </button>
        </div>

        {results && (
          <div className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-xl font-semibold mb-4">Test Results</h2>
            
            {results.success ? (
              <div className="space-y-6">
                <div className="text-sm text-gray-600 mb-4">
                  Token: {results.results.accessToken}
                </div>

                {/* Merchants Test */}
                <div className="border rounded-lg p-4">
                  <h3 className="font-medium mb-2 flex items-center">
                    Merchants API
                    {results.results.tests.merchants?.success ? (
                      <span className="ml-2 text-green-600">✅ Success</span>
                    ) : (
                      <span className="ml-2 text-red-600">❌ Failed</span>
                    )}
                  </h3>
                  <pre className="bg-gray-100 p-3 rounded text-xs overflow-auto">
                    {JSON.stringify(results.results.tests.merchants, null, 2)}
                  </pre>
                </div>

                {/* Locations Test */}
                <div className="border rounded-lg p-4">
                  <h3 className="font-medium mb-2 flex items-center">
                    Locations API
                    {results.results.tests.locations?.success ? (
                      <span className="ml-2 text-green-600">✅ Success</span>
                    ) : (
                      <span className="ml-2 text-red-600">❌ Failed</span>
                    )}
                  </h3>
                  <pre className="bg-gray-100 p-3 rounded text-xs overflow-auto">
                    {JSON.stringify(results.results.tests.locations, null, 2)}
                  </pre>
                </div>

                {/* Customers Test */}
                <div className="border rounded-lg p-4">
                  <h3 className="font-medium mb-2 flex items-center">
                    Customers API
                    {results.results.tests.customers?.success ? (
                      <span className="ml-2 text-green-600">✅ Success ({results.results.tests.customers.count} customers)</span>
                    ) : (
                      <span className="ml-2 text-red-600">❌ Failed</span>
                    )}
                  </h3>
                  <pre className="bg-gray-100 p-3 rounded text-xs overflow-auto">
                    {JSON.stringify(results.results.tests.customers, null, 2)}
                  </pre>
                </div>
              </div>
            ) : (
              <div className="text-red-600">
                <h3 className="font-medium mb-2">❌ Test Failed</h3>
                <pre className="bg-red-50 p-3 rounded text-sm">
                  {JSON.stringify(results, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}