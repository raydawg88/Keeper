/**
 * Square API Client for Keeper Data Sync
 * Includes rate limiting, retry logic, and data extraction
 */

interface RateLimitState {
  requests: number;
  resetTime: number;
}

interface SquareApiOptions {
  accessToken: string;
  environment: 'sandbox' | 'production';
  rateLimit?: {
    requestsPerMinute: number;
    burstLimit: number;
  };
}

interface PaginatedResponse<T> {
  data: T[];
  cursor?: string;
  hasMore: boolean;
}

export class SquareApiClient {
  private baseUrl: string;
  private accessToken: string;
  private version: string = '2025-08-20';
  private rateLimitState: RateLimitState;
  private rateLimit: { requestsPerMinute: number; burstLimit: number };

  constructor(options: SquareApiOptions) {
    this.accessToken = options.accessToken;
    this.baseUrl = options.environment === 'sandbox' 
      ? 'https://connect.squareupsandbox.com'
      : 'https://connect.squareup.com';
    
    // Default rate limits based on Square API docs
    this.rateLimit = options.rateLimit || {
      requestsPerMinute: 500,  // Conservative limit
      burstLimit: 10          // Max concurrent requests
    };

    this.rateLimitState = {
      requests: 0,
      resetTime: Date.now() + 60000 // Reset every minute
    };
  }

  /**
   * Rate limiting with exponential backoff
   */
  private async enforceRateLimit(): Promise<void> {
    const now = Date.now();
    
    // Reset counter if minute has passed
    if (now > this.rateLimitState.resetTime) {
      this.rateLimitState.requests = 0;
      this.rateLimitState.resetTime = now + 60000;
    }
    
    // If we're over the limit, wait
    if (this.rateLimitState.requests >= this.rateLimit.requestsPerMinute) {
      const waitTime = this.rateLimitState.resetTime - now;
      console.log(`Rate limit reached, waiting ${waitTime}ms...`);
      await new Promise(resolve => setTimeout(resolve, waitTime));
      
      // Reset after waiting
      this.rateLimitState.requests = 0;
      this.rateLimitState.resetTime = Date.now() + 60000;
    }
    
    this.rateLimitState.requests++;
  }

  /**
   * Make HTTP request with retry logic
   */
  private async makeRequest<T>(
    endpoint: string, 
    method: 'GET' | 'POST' = 'GET', 
    body?: any,
    retries: number = 3
  ): Promise<T> {
    await this.enforceRateLimit();
    
    const headers = {
      'Authorization': `Bearer ${this.accessToken}`,
      'Square-Version': this.version,
      'Content-Type': 'application/json'
    };

    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
          method,
          headers,
          body: body ? JSON.stringify(body) : undefined
        });

        if (response.status === 429) {
          // Rate limited - wait and retry
          const retryAfter = response.headers.get('retry-after');
          const waitTime = retryAfter ? parseInt(retryAfter) * 1000 : Math.pow(2, attempt) * 1000;
          console.log(`Rate limited (429), waiting ${waitTime}ms before retry ${attempt}/${retries}`);
          await new Promise(resolve => setTimeout(resolve, waitTime));
          continue;
        }

        if (!response.ok) {
          throw new Error(`Square API error: ${response.status} ${response.statusText}`);
        }

        return await response.json();
      } catch (error) {
        if (attempt === retries) throw error;
        
        // Exponential backoff for retries
        const waitTime = Math.pow(2, attempt) * 1000;
        console.log(`Request failed, retrying in ${waitTime}ms... (${attempt}/${retries})`);
        await new Promise(resolve => setTimeout(resolve, waitTime));
      }
    }

    throw new Error('Max retries exceeded');
  }

  /**
   * Get merchant information
   */
  async getMerchants(): Promise<any> {
    return await this.makeRequest('/v2/merchants');
  }

  /**
   * Get locations with pagination
   */
  async getLocations(): Promise<any> {
    return await this.makeRequest('/v2/locations');
  }

  /**
   * Get customers with pagination and cursor
   */
  async getCustomers(cursor?: string, limit: number = 100): Promise<PaginatedResponse<any>> {
    let endpoint = `/v2/customers?limit=${limit}`;
    if (cursor) {
      endpoint += `&cursor=${cursor}`;
    }
    
    const response = await this.makeRequest(endpoint);
    
    return {
      data: response.customers || [],
      cursor: response.cursor,
      hasMore: !!response.cursor
    };
  }

  /**
   * Get all customers with automatic pagination
   */
  async getAllCustomers(): Promise<any[]> {
    const allCustomers: any[] = [];
    let cursor: string | undefined = undefined;
    let pageCount = 0;
    const maxPages = 100; // Safety limit
    
    console.log('📥 Starting customer data sync...');
    
    do {
      try {
        const response = await this.getCustomers(cursor, 100);
        allCustomers.push(...response.data);
        cursor = response.cursor;
        pageCount++;
        
        console.log(`   📄 Page ${pageCount}: ${response.data.length} customers (total: ${allCustomers.length})`);
        
        if (pageCount >= maxPages) {
          console.log('⚠️  Maximum page limit reached');
          break;
        }
      } catch (error) {
        console.error(`Error fetching customers page ${pageCount}:`, error);
        break;
      }
    } while (cursor);
    
    console.log(`✅ Customer sync complete: ${allCustomers.length} total customers`);
    return allCustomers;
  }

  /**
   * Get payments with date range and pagination
   */
  async getPayments(
    beginTime?: string, 
    endTime?: string, 
    cursor?: string, 
    limit: number = 100
  ): Promise<PaginatedResponse<any>> {
    let endpoint = `/v2/payments?limit=${limit}`;
    
    if (beginTime) endpoint += `&begin_time=${beginTime}`;
    if (endTime) endpoint += `&end_time=${endTime}`;
    if (cursor) endpoint += `&cursor=${cursor}`;
    
    const response = await this.makeRequest(endpoint);
    
    return {
      data: response.payments || [],
      cursor: response.cursor,
      hasMore: !!response.cursor
    };
  }

  /**
   * Get all payments for date range
   */
  async getAllPayments(beginTime?: string, endTime?: string): Promise<any[]> {
    const allPayments: any[] = [];
    let cursor: string | undefined = undefined;
    let pageCount = 0;
    const maxPages = 200; // Higher limit for payments
    
    console.log('💳 Starting payment data sync...');
    if (beginTime) console.log(`   📅 Date range: ${beginTime} to ${endTime || 'now'}`);
    
    do {
      try {
        const response = await this.getPayments(beginTime, endTime, cursor, 100);
        allPayments.push(...response.data);
        cursor = response.cursor;
        pageCount++;
        
        console.log(`   📄 Page ${pageCount}: ${response.data.length} payments (total: ${allPayments.length})`);
        
        if (pageCount >= maxPages) {
          console.log('⚠️  Maximum page limit reached');
          break;
        }
      } catch (error) {
        console.error(`Error fetching payments page ${pageCount}:`, error);
        break;
      }
    } while (cursor);
    
    console.log(`✅ Payment sync complete: ${allPayments.length} total payments`);
    return allPayments;
  }

  /**
   * Search orders with pagination
   */
  async searchOrders(
    locationIds?: string[], 
    cursor?: string, 
    limit: number = 100
  ): Promise<PaginatedResponse<any>> {
    const body: any = {
      limit: limit
    };
    
    if (locationIds && locationIds.length > 0) {
      body.location_ids = locationIds;
    }
    
    if (cursor) {
      body.cursor = cursor;
    }
    
    const response = await this.makeRequest('/v2/orders/search', 'POST', body);
    
    return {
      data: response.orders || [],
      cursor: response.cursor,
      hasMore: !!response.cursor
    };
  }

  /**
   * Get all orders
   */
  async getAllOrders(locationIds?: string[]): Promise<any[]> {
    const allOrders: any[] = [];
    let cursor: string | undefined = undefined;
    let pageCount = 0;
    const maxPages = 100;
    
    console.log('🛒 Starting order data sync...');
    if (locationIds) console.log(`   📍 Locations: ${locationIds.join(', ')}`);
    
    do {
      try {
        const response = await this.searchOrders(locationIds, cursor, 100);
        allOrders.push(...response.data);
        cursor = response.cursor;
        pageCount++;
        
        console.log(`   📄 Page ${pageCount}: ${response.data.length} orders (total: ${allOrders.length})`);
        
        if (pageCount >= maxPages) {
          console.log('⚠️  Maximum page limit reached');
          break;
        }
      } catch (error) {
        console.error(`Error fetching orders page ${pageCount}:`, error);
        break;
      }
    } while (cursor);
    
    console.log(`✅ Order sync complete: ${allOrders.length} total orders`);
    return allOrders;
  }

  /**
   * Get catalog items (products/services)
   */
  async getCatalogItems(cursor?: string): Promise<PaginatedResponse<any>> {
    let endpoint = '/v2/catalog/list?types=ITEM';
    if (cursor) {
      endpoint += `&cursor=${cursor}`;
    }
    
    const response = await this.makeRequest(endpoint);
    
    return {
      data: response.objects || [],
      cursor: response.cursor,
      hasMore: !!response.cursor
    };
  }

  /**
   * Get team members (employees)
   */
  async getTeamMembers(): Promise<any> {
    try {
      return await this.makeRequest('/v2/team-members');
    } catch (error) {
      console.log('Team members not available (may require different permissions)');
      return { team_members: [] };
    }
  }

  /**
   * Comprehensive data sync for an account
   */
  async syncAllData(): Promise<{
    merchants: any;
    locations: any;
    customers: any[];
    payments: any[];
    orders: any[];
    catalogItems: any[];
    teamMembers: any;
  }> {
    console.log('🔄 Starting comprehensive Square data sync...');
    console.log('⏱️  This may take several minutes depending on data volume');
    
    try {
      // Get basic account info first
      const merchants = await this.getMerchants();
      const locations = await this.getLocations();
      
      // Extract location IDs for order filtering
      const locationIds = locations.locations?.map((loc: any) => loc.id) || [];
      
      // Get all transactional data with pagination
      const [customers, payments, orders, catalogItems, teamMembers] = await Promise.all([
        this.getAllCustomers(),
        this.getAllPayments(), // Get all payments
        this.getAllOrders(locationIds),
        this.getCatalogItems().then(response => response.data),
        this.getTeamMembers()
      ]);
      
      console.log('\n✅ Comprehensive data sync complete!');
      console.log('📊 Summary:');
      console.log(`   👥 Customers: ${customers.length}`);
      console.log(`   💳 Payments: ${payments.length}`);
      console.log(`   🛒 Orders: ${orders.length}`);
      console.log(`   📦 Catalog Items: ${catalogItems.length}`);
      console.log(`   👨‍💼 Team Members: ${teamMembers.team_members?.length || 0}`);
      
      return {
        merchants,
        locations,
        customers,
        payments,
        orders,
        catalogItems,
        teamMembers
      };
      
    } catch (error) {
      console.error('❌ Data sync failed:', error);
      throw error;
    }
  }
}