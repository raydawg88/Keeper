/**
 * Square OAuth Manager for TypeScript/Next.js
 * Handles business account connection and token management
 */

interface OAuthResult {
  auth_url: string;
  state: string;
  session_id: string;
}

interface AccountResult {
  account_id: string;
  business_name: string;
  merchant_id: string;
  locations: any[];
  access_token?: string;
}

export class SquareOAuthManager {
  private clientId: string;
  private clientSecret: string;
  private environment: 'sandbox' | 'production';
  private oauthBaseUrl: string;
  private apiBaseUrl: string;

  constructor() {
    this.clientId = process.env.SQUARE_APPLICATION_ID || '';
    this.clientSecret = process.env.SQUARE_CLIENT_SECRET || '';
    this.environment = 'production'; // Now using production for real spa data
    
    if (this.environment === 'sandbox') {
      this.oauthBaseUrl = 'https://connect.squareupsandbox.com';
      this.apiBaseUrl = 'https://connect.squareupsandbox.com';
    } else {
      this.oauthBaseUrl = 'https://connect.squareup.com';
      this.apiBaseUrl = 'https://connect.squareup.com';
    }
  }

  generateOAuthUrl(redirectUri: string, businessName?: string): OAuthResult | null {
    try {
      // Generate secure state parameter
      const state = this.generateSecureState();
      
      // For now, we'll use a simple session ID
      // In production, this would be stored in database
      const sessionId = crypto.randomUUID();
      
      // Build authorization URL with READ-ONLY scopes for Keeper
      // Keeper only needs to analyze data, not modify Square account
      const keeperScopes = [
        'CUSTOMERS_READ',
        'PAYMENTS_READ', 
        'ORDERS_READ',
        'APPOINTMENTS_READ',
        'APPOINTMENTS_ALL_READ',           // Access to all appointment data
        'APPOINTMENTS_BUSINESS_SETTINGS_READ', // Business appointment settings
        'ITEMS_READ',
        'INVENTORY_READ',
        'EMPLOYEES_READ',
        'TIMECARDS_READ',
        'TIMECARDS_SETTINGS_READ',        // Timecard settings for payroll
        'MERCHANT_PROFILE_READ',
        'BANK_ACCOUNTS_READ'
      ];
      
      const params = new URLSearchParams({
        client_id: this.clientId,
        scope: keeperScopes.join(' ')
      });
      
      const authUrl = `${this.oauthBaseUrl}/oauth2/authorize?${params.toString()}`;
      
      console.log('=== OAUTH DEBUG ===');
      console.log('Generated OAuth URL:', authUrl);
      console.log('Client ID:', this.clientId);
      console.log('Redirect URI:', redirectUri);
      console.log('Scope:', 'CUSTOMERS_READ PAYMENTS_READ ITEMS_READ');
      console.log('State:', state);
      console.log('=================');
      
      return {
        auth_url: authUrl,
        state: state,
        session_id: sessionId
      };
      
    } catch (error) {
      console.error('OAuth URL generation failed:', error);
      return null;
    }
  }

  async handleOAuthCallback(authorizationCode: string, state: string): Promise<AccountResult | null> {
    try {
      // Exchange authorization code for access token
      const tokenUrl = `${this.apiBaseUrl}/oauth2/token`;
      const tokenData = {
        client_id: this.clientId,
        client_secret: this.clientSecret,
        code: authorizationCode,
        grant_type: 'authorization_code'
      };
      
      const tokenResponse = await fetch(tokenUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Square-Version': '2025-08-20'
        },
        body: JSON.stringify(tokenData)
      });
      
      if (!tokenResponse.ok) {
        const errorBody = await tokenResponse.text();
        console.error('Token exchange failed:', tokenResponse.status, tokenResponse.statusText);
        console.error('Error body:', errorBody);
        console.error('Token data sent:', JSON.stringify(tokenData, null, 2));
        throw new Error(`Token exchange failed: ${tokenResponse.statusText} - ${errorBody}`);
      }
      
      const tokenResult = await tokenResponse.json();
      const accessToken = tokenResult.access_token;
      
      console.log('OAuth callback successful! Access token received:', accessToken.substring(0, 10) + '...');
      
      // Get real merchant info from Square API
      const merchantInfo = await this.getMerchantInfo(accessToken);
      
      if (!merchantInfo) {
        throw new Error('Failed to get merchant information from Square API');
      }
      
      const accountId = crypto.randomUUID();
      
      return {
        account_id: accountId,
        business_name: merchantInfo.business_name,
        merchant_id: merchantInfo.merchant_id,
        locations: merchantInfo.locations,
        access_token: accessToken
      };
      
    } catch (error) {
      console.error('OAuth callback handling failed:', error);
      return null;
    }
  }

  private async getMerchantInfo(accessToken: string) {
    try {
      const headers = {
        'Authorization': `Bearer ${accessToken}`,
        'Square-Version': '2025-08-20',
        'Content-Type': 'application/json'
      };
      
      // Get merchant info
      const merchantResponse = await fetch(`${this.apiBaseUrl}/v2/merchants`, { headers });
      
      if (!merchantResponse.ok) {
        throw new Error(`Merchant API failed: ${merchantResponse.statusText}`);
      }
      
      const merchantData = await merchantResponse.json();
      
      // Handle both 'merchants' and 'merchant' response formats
      const merchants = merchantData.merchants || merchantData.merchant;
      if (!merchants || merchants.length === 0) {
        throw new Error('No merchant data found');
      }
      
      const merchant = merchants[0];
      
      // Get locations
      const locationsResponse = await fetch(`${this.apiBaseUrl}/v2/locations`, { headers });
      
      if (!locationsResponse.ok) {
        throw new Error(`Locations API failed: ${locationsResponse.statusText}`);
      }
      
      const locationsData = await locationsResponse.json();
      
      return {
        merchant_id: merchant.id,
        business_name: merchant.business_name || 'Unknown Business',
        locations: locationsData.locations || []
      };
      
    } catch (error) {
      console.error('Failed to get merchant info:', error);
      return null;
    }
  }

  private generateSecureState(): string {
    // Generate a secure random state parameter
    const array = new Uint8Array(16);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  }
}