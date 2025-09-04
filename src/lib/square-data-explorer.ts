/**
 * Square Data Structure Explorer
 * Use this to understand what data Square provides for Keeper
 */

interface SquareApiClient {
  baseUrl: string;
  accessToken: string;
  version: string;
}

export class SquareDataExplorer {
  private client: SquareApiClient;

  constructor(accessToken: string, environment: 'sandbox' | 'production' = 'sandbox') {
    this.client = {
      baseUrl: environment === 'sandbox' 
        ? 'https://connect.squareupsandbox.com'
        : 'https://connect.squareup.com',
      accessToken: accessToken,
      version: '2025-08-20'
    };
  }

  private async makeRequest(endpoint: string, method: 'GET' | 'POST' = 'GET', body?: any) {
    const headers = {
      'Authorization': `Bearer ${this.client.accessToken}`,
      'Square-Version': this.client.version,
      'Content-Type': 'application/json'
    };

    const response = await fetch(`${this.client.baseUrl}${endpoint}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined
    });

    if (!response.ok) {
      throw new Error(`Square API error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  }

  async exploreCustomers(limit: number = 5) {
    console.log('=== EXPLORING SQUARE CUSTOMERS ===');
    const result = await this.makeRequest(`/v2/customers?limit=${limit}`);
    console.log('Customers structure:', JSON.stringify(result, null, 2));
    return result;
  }

  async explorePayments(limit: number = 5) {
    console.log('=== EXPLORING SQUARE PAYMENTS ===');
    const result = await this.makeRequest(`/v2/payments?limit=${limit}`);
    console.log('Payments structure:', JSON.stringify(result, null, 2));
    return result;
  }

  async exploreOrders(limit: number = 5) {
    console.log('=== EXPLORING SQUARE ORDERS ===');
    try {
      const result = await this.makeRequest(`/v2/orders/search`, 'POST', {
        limit: limit
      });
      console.log('Orders structure:', JSON.stringify(result, null, 2));
      return result;
    } catch (error) {
      console.log('Orders API error (likely empty):', error);
      return { orders: [], message: 'No orders found or API error' };
    }
  }

  async exploreLocations() {
    console.log('=== EXPLORING SQUARE LOCATIONS ===');
    const result = await this.makeRequest('/v2/locations');
    console.log('Locations structure:', JSON.stringify(result, null, 2));
    return result;
  }

  async exploreItems(limit: number = 5) {
    console.log('=== EXPLORING SQUARE CATALOG ITEMS ===');
    const result = await this.makeRequest('/v2/catalog/list?types=ITEM', 'GET');
    console.log('Items structure:', JSON.stringify(result, null, 2));
    return result;
  }

  async exploreMerchant() {
    console.log('=== EXPLORING MERCHANT INFO ===');
    const result = await this.makeRequest('/v2/merchants');
    console.log('Merchant structure:', JSON.stringify(result, null, 2));
    return result;
  }

  async exploreEmployees() {
    console.log('=== EXPLORING SQUARE EMPLOYEES ===');
    try {
      const result = await this.makeRequest('/v2/team-members');
      console.log('Team Members structure:', JSON.stringify(result, null, 2));
      return result;
    } catch (error) {
      console.log('Team Members API error:', error);
      return null;
    }
  }

  async exploreInventory() {
    console.log('=== EXPLORING SQUARE INVENTORY ===');
    try {
      // First get catalog items to find item IDs
      const catalog = await this.makeRequest('/v2/catalog/list?types=ITEM_VARIATION');
      console.log('Inventory-related catalog:', JSON.stringify(catalog, null, 2));
      return catalog;
    } catch (error) {
      console.log('Inventory API error:', error);
      return null;
    }
  }

  async exploreAll() {
    console.log('🔍 EXPLORING ALL SQUARE DATA STRUCTURES FOR KEEPER');
    console.log('This will help us design the perfect data sync pipeline\n');

    const results = {
      merchant: await this.exploreMerchant(),
      locations: await this.exploreLocations(),
      customers: await this.exploreCustomers(),
      payments: await this.explorePayments(),
      orders: await this.exploreOrders(),
      items: await this.exploreItems(),
      employees: await this.exploreEmployees(),
      inventory: await this.exploreInventory()
    };

    console.log('\n🎯 EXPLORATION COMPLETE - Ready to design Keeper data models!');
    return results;
  }
}