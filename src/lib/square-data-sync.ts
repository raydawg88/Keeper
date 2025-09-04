/**
 * Square Data Synchronization Service for Keeper
 * Handles complete data sync from Square API to Supabase
 */

import { SquareApiClient } from './square-api-client';
import { createClient } from '@supabase/supabase-js';

interface SyncOptions {
  accountId: string;
  accessToken: string;
  environment: 'sandbox' | 'production';
  syncType: 'full' | 'incremental';
  entities?: string[]; // Optional: sync only specific entities
}

interface SyncResult {
  success: boolean;
  entity: string;
  recordsProcessed: number;
  recordsInserted: number;
  recordsUpdated: number;
  recordsSkipped: number;
  errors: string[];
  duration: number;
}

interface SyncStatus {
  accountId: string;
  overallStatus: 'pending' | 'running' | 'completed' | 'error';
  startTime: Date;
  endTime?: Date;
  results: SyncResult[];
  totalRecords: number;
  errorSummary?: string;
}

export class SquareDataSync {
  private supabase: any;
  private squareClient: SquareApiClient;
  private accountId: string;
  private syncStatus: SyncStatus;

  constructor(options: SyncOptions) {
    // Initialize Supabase client
    this.supabase = createClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!
    );

    // Initialize Square API client
    this.squareClient = new SquareApiClient({
      accessToken: options.accessToken,
      environment: options.environment
    });

    this.accountId = options.accountId;
    
    // Initialize sync status
    this.syncStatus = {
      accountId: options.accountId,
      overallStatus: 'pending',
      startTime: new Date(),
      results: [],
      totalRecords: 0
    };
  }

  /**
   * Start comprehensive data synchronization
   */
  async startSync(entities: string[] = ['merchants', 'locations', 'customers', 'payments', 'orders']): Promise<SyncStatus> {
    console.log(`🔄 Starting Square data sync for account ${this.accountId}`);
    console.log(`📊 Entities to sync: ${entities.join(', ')}`);
    
    this.syncStatus.overallStatus = 'running';
    await this.updateSyncStatus('running');

    try {
      // Process each entity in sequence to avoid overwhelming the API
      for (const entity of entities) {
        const result = await this.syncEntity(entity);
        this.syncStatus.results.push(result);
        this.syncStatus.totalRecords += result.recordsProcessed;
        
        // Log progress
        console.log(`✅ ${entity} sync completed: ${result.recordsInserted} inserted, ${result.recordsUpdated} updated`);
        
        // Small delay between entities to be respectful to Square API
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

      this.syncStatus.overallStatus = 'completed';
      this.syncStatus.endTime = new Date();
      
      console.log(`🎉 Sync completed successfully! Total records: ${this.syncStatus.totalRecords}`);
      
    } catch (error) {
      this.syncStatus.overallStatus = 'error';
      this.syncStatus.errorSummary = error instanceof Error ? error.message : String(error);
      this.syncStatus.endTime = new Date();
      
      console.error('❌ Sync failed:', error);
    }

    await this.updateSyncStatus(this.syncStatus.overallStatus);
    return this.syncStatus;
  }

  /**
   * Sync individual entity type
   */
  private async syncEntity(entity: string): Promise<SyncResult> {
    const startTime = Date.now();
    const result: SyncResult = {
      success: false,
      entity,
      recordsProcessed: 0,
      recordsInserted: 0,
      recordsUpdated: 0,
      recordsSkipped: 0,
      errors: [],
      duration: 0
    };

    try {
      console.log(`📥 Syncing ${entity}...`);

      switch (entity) {
        case 'merchants':
          await this.syncMerchants(result);
          break;
        case 'locations':
          await this.syncLocations(result);
          break;
        case 'customers':
          await this.syncCustomers(result);
          break;
        case 'payments':
          await this.syncPayments(result);
          break;
        case 'orders':
          await this.syncOrders(result);
          break;
        default:
          throw new Error(`Unknown entity type: ${entity}`);
      }

      result.success = true;
      
    } catch (error) {
      result.errors.push(error instanceof Error ? error.message : String(error));
      console.error(`❌ Error syncing ${entity}:`, error);
    }

    result.duration = Date.now() - startTime;
    return result;
  }

  /**
   * Sync merchant data
   */
  private async syncMerchants(result: SyncResult): Promise<void> {
    const merchantData = await this.squareClient.getMerchants();
    const merchants = merchantData.merchant || [];
    
    for (const merchant of merchants) {
      try {
        const transformedData = this.transformMerchant(merchant);
        await this.upsertRecord('square_merchants', transformedData, result);
      } catch (error) {
        result.errors.push(`Merchant ${merchant.id}: ${error}`);
      }
    }
  }

  /**
   * Sync location data
   */
  private async syncLocations(result: SyncResult): Promise<void> {
    const locationData = await this.squareClient.getLocations();
    const locations = locationData.locations || [];
    
    for (const location of locations) {
      try {
        const transformedData = this.transformLocation(location);
        await this.upsertRecord('square_locations', transformedData, result);
      } catch (error) {
        result.errors.push(`Location ${location.id}: ${error}`);
      }
    }
  }

  /**
   * Sync customer data with batching
   */
  private async syncCustomers(result: SyncResult): Promise<void> {
    const customers = await this.squareClient.getAllCustomers();
    
    // Process in batches of 50 to avoid overwhelming the database
    const batchSize = 50;
    for (let i = 0; i < customers.length; i += batchSize) {
      const batch = customers.slice(i, i + batchSize);
      
      for (const customer of batch) {
        try {
          const transformedData = this.transformCustomer(customer);
          await this.upsertRecord('square_customers', transformedData, result);
        } catch (error) {
          result.errors.push(`Customer ${customer.id}: ${error}`);
        }
      }
      
      // Small delay between batches
      if (i + batchSize < customers.length) {
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    }
  }

  /**
   * Sync payment data
   */
  private async syncPayments(result: SyncResult): Promise<void> {
    // Get payments from last 30 days for incremental sync
    const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString();
    const payments = await this.squareClient.getAllPayments(thirtyDaysAgo);
    
    const batchSize = 100;
    for (let i = 0; i < payments.length; i += batchSize) {
      const batch = payments.slice(i, i + batchSize);
      
      for (const payment of batch) {
        try {
          const transformedData = this.transformPayment(payment);
          await this.upsertRecord('square_payments', transformedData, result);
        } catch (error) {
          result.errors.push(`Payment ${payment.id}: ${error}`);
        }
      }
      
      if (i + batchSize < payments.length) {
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    }
  }

  /**
   * Sync order data
   */
  private async syncOrders(result: SyncResult): Promise<void> {
    const orders = await this.squareClient.getAllOrders();
    
    const batchSize = 100;
    for (let i = 0; i < orders.length; i += batchSize) {
      const batch = orders.slice(i, i + batchSize);
      
      for (const order of batch) {
        try {
          const transformedData = this.transformOrder(order);
          await this.upsertRecord('square_orders', transformedData, result);
        } catch (error) {
          result.errors.push(`Order ${order.id}: ${error}`);
        }
      }
      
      if (i + batchSize < orders.length) {
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    }
  }

  /**
   * Transform Square merchant data to our schema
   */
  private transformMerchant(merchant: any): any {
    return {
      id: merchant.id,
      account_id: this.accountId,
      business_name: merchant.business_name || 'Unknown Business',
      country: merchant.country || 'US',
      language_code: merchant.language_code || 'en-US',
      currency: merchant.currency || 'USD',
      status: merchant.status || 'ACTIVE',
      main_location_id: merchant.main_location_id,
      owner_email: merchant.owner_email,
      created_at: merchant.created_at ? new Date(merchant.created_at) : new Date(),
      updated_at: new Date(),
      synced_at: new Date()
    };
  }

  /**
   * Transform Square location data to our schema
   */
  private transformLocation(location: any): any {
    return {
      id: location.id,
      merchant_id: location.merchant_id,
      account_id: this.accountId,
      name: location.name || 'Unnamed Location',
      address_line_1: location.address?.address_line_1,
      address_line_2: location.address?.address_line_2,
      locality: location.address?.locality,
      administrative_district_level_1: location.address?.administrative_district_level_1,
      postal_code: location.address?.postal_code,
      country: location.address?.country,
      timezone: location.timezone,
      capabilities: location.capabilities || [],
      status: location.status || 'ACTIVE',
      location_type: location.type,
      business_name: location.business_name,
      mcc: location.mcc,
      business_hours: location.business_hours || {},
      created_at: location.created_at ? new Date(location.created_at) : new Date(),
      updated_at: new Date(),
      synced_at: new Date()
    };
  }

  /**
   * Transform Square customer data to our schema
   */
  private transformCustomer(customer: any): any {
    return {
      id: customer.id,
      account_id: this.accountId,
      location_id: null, // Will be populated if available
      given_name: customer.given_name,
      family_name: customer.family_name,
      nickname: customer.nickname,
      company_name: customer.company_name,
      email_address: customer.email_address,
      phone_number: customer.phone_number,
      birthday: customer.birthday,
      note: customer.note,
      reference_id: customer.reference_id,
      creation_source: customer.creation_source,
      email_unsubscribed: customer.preferences?.email_unsubscribed || false,
      version: customer.version || 0,
      
      // Address fields
      address_line_1: customer.address?.address_line_1,
      address_line_2: customer.address?.address_line_2,
      locality: customer.address?.locality,
      administrative_district_level_1: customer.address?.administrative_district_level_1,
      postal_code: customer.address?.postal_code,
      country: customer.address?.country,
      
      // Keeper-specific fields (initially empty, will be computed later)
      customer_profile: {},
      lifetime_value: 0,
      visit_frequency: 'unknown',
      churn_risk_score: 0,
      last_visit_date: null,
      
      created_at: customer.created_at ? new Date(customer.created_at) : new Date(),
      updated_at: customer.updated_at ? new Date(customer.updated_at) : new Date(),
      synced_at: new Date()
    };
  }

  /**
   * Transform Square payment data to our schema
   */
  private transformPayment(payment: any): any {
    const createdAt = new Date(payment.created_at);
    
    return {
      id: payment.id,
      account_id: this.accountId,
      location_id: payment.location_id,
      order_id: payment.order_id,
      customer_id: payment.buyer_email_address ? null : payment.customer_id, // Will match by email if no customer_id
      
      amount_money: parseFloat(payment.amount_money?.amount || '0') / 100, // Convert cents to dollars
      currency: payment.amount_money?.currency || 'USD',
      status: payment.status || 'UNKNOWN',
      source_type: payment.source_type,
      receipt_number: payment.receipt_number,
      receipt_url: payment.receipt_url,
      
      created_at: createdAt,
      updated_at: payment.updated_at ? new Date(payment.updated_at) : createdAt,
      processed_at: payment.processed_at ? new Date(payment.processed_at) : null,
      
      payment_source: payment.payment_source || {},
      risk_evaluation: payment.risk_evaluation || {},
      processing_fee: payment.processing_fee ? parseFloat(payment.processing_fee.amount || '0') / 100 : 0,
      
      // Keeper analytics
      time_of_day: createdAt.getHours(),
      day_of_week: createdAt.getDay(),
      is_weekend: createdAt.getDay() === 0 || createdAt.getDay() === 6,
      season: this.getSeason(createdAt),
      
      synced_at: new Date()
    };
  }

  /**
   * Transform Square order data to our schema
   */
  private transformOrder(order: any): any {
    const totalMoney = parseFloat(order.total_money?.amount || '0') / 100;
    const lineItems = order.line_items || [];
    
    return {
      id: order.id,
      account_id: this.accountId,
      location_id: order.location_id,
      customer_id: order.customer_id,
      
      state: order.state || 'UNKNOWN',
      version: order.version || 0,
      
      total_money: totalMoney,
      total_tax_money: parseFloat(order.total_tax_money?.amount || '0') / 100,
      total_discount_money: parseFloat(order.total_discount_money?.amount || '0') / 100,
      total_tip_money: parseFloat(order.total_tip_money?.amount || '0') / 100,
      total_service_charge_money: parseFloat(order.total_service_charge_money?.amount || '0') / 100,
      
      line_items: lineItems,
      fulfillments: order.fulfillments || [],
      
      // Keeper analytics
      item_count: lineItems.length,
      modifier_count: lineItems.reduce((sum: number, item: any) => sum + (item.modifiers?.length || 0), 0),
      total_modifiers_value: lineItems.reduce((sum: number, item: any) => {
        return sum + (item.modifiers?.reduce((modSum: number, mod: any) => 
          modSum + (parseFloat(mod.base_price_money?.amount || '0') / 100), 0) || 0);
      }, 0),
      avg_item_price: lineItems.length > 0 ? totalMoney / lineItems.length : 0,
      
      created_at: order.created_at ? new Date(order.created_at) : new Date(),
      updated_at: order.updated_at ? new Date(order.updated_at) : new Date(),
      closed_at: order.closed_at ? new Date(order.closed_at) : null,
      synced_at: new Date()
    };
  }

  /**
   * Upsert record with conflict resolution
   */
  private async upsertRecord(table: string, data: any, result: SyncResult): Promise<void> {
    result.recordsProcessed++;
    
    try {
      // First try to check if record exists
      const { data: existing } = await this.supabase
        .from(table)
        .select('id, updated_at')
        .eq('account_id', this.accountId)
        .eq('id', data.id)
        .single();

      if (existing) {
        // Update existing record
        const { error } = await this.supabase
          .from(table)
          .update(data)
          .eq('account_id', this.accountId)
          .eq('id', data.id);
          
        if (error) throw error;
        result.recordsUpdated++;
      } else {
        // Insert new record
        const { error } = await this.supabase
          .from(table)
          .insert(data);
          
        if (error) throw error;
        result.recordsInserted++;
      }
    } catch (error) {
      // If it's a unique constraint violation, skip
      if (error && typeof error === 'object' && 'code' in error && error.code === '23505') {
        result.recordsSkipped++;
      } else {
        throw error;
      }
    }
  }

  /**
   * Update sync status in database
   */
  private async updateSyncStatus(status: string): Promise<void> {
    try {
      const { error } = await this.supabase
        .from('square_sync_status')
        .upsert({
          account_id: this.accountId,
          entity_type: 'all',
          last_sync_at: new Date(),
          sync_status: status,
          error_message: this.syncStatus.errorSummary || null,
          records_synced: this.syncStatus.totalRecords,
          updated_at: new Date()
        });
        
      if (error) {
        console.error('Failed to update sync status:', error);
      }
    } catch (error) {
      console.error('Error updating sync status:', error);
    }
  }

  /**
   * Get season for date analytics
   */
  private getSeason(date: Date): string {
    const month = date.getMonth() + 1; // 0-based to 1-based
    
    if (month >= 3 && month <= 5) return 'spring';
    if (month >= 6 && month <= 8) return 'summer';
    if (month >= 9 && month <= 11) return 'fall';
    return 'winter';
  }
}