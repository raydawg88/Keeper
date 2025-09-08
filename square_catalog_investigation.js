const { SquareClient, SquareEnvironment } = require('square');
require('dotenv').config();

const client = new SquareClient({
  accessToken: process.env.SQUARE_ACCESS_TOKEN,
  environment: SquareEnvironment.PRODUCTION
});

const ACCOUNT_ID = 'b491de6e-7d5b-4e0e-b1cd-625c6c4f7d81';
const SQUARE_MERCHANT_ID = '40GJBMWKZ4FZS';

async function investigateSquareCatalog() {
  console.log('🔍 SQUARE CATALOG INVESTIGATION');
  console.log('===============================');
  console.log(`Square Merchant ID: ${SQUARE_MERCHANT_ID}`);
  console.log('');

  try {
    const catalogApi = client.catalog;
    const locationsApi = client.locations;

    // 1. Get business locations
    console.log('1. GETTING BUSINESS LOCATIONS...');
    console.log('---------------------------------');
    
    try {
      const locationsResult = await locationsApi.list();
      
      if (locationsResult.locations && locationsResult.locations.length > 0) {
        console.log(`✅ Found ${locationsResult.locations.length} locations:`);
        locationsResult.locations.forEach((location, index) => {
          console.log(`${index + 1}. ${location.name} (${location.id})`);
          console.log(`   Address: ${location.address?.addressLine1 || 'N/A'}, ${location.address?.locality || 'N/A'}, ${location.address?.administrativeDistrictLevel1 || 'N/A'}`);
          console.log(`   Business Name: ${location.businessName || 'N/A'}`);
          console.log(`   Type: ${location.type || 'N/A'}`);
          console.log(`   Status: ${location.status || 'N/A'}`);
          console.log('');
        });
      }
    } catch (locError) {
      console.log('❌ Error getting locations:', locError.message);
    }

    // 2. Get catalog items (services)
    console.log('2. GETTING CATALOG ITEMS (SERVICES)...');
    console.log('---------------------------------------');
    
    try {
      const catalogResult = await catalogApi.list({ types: 'ITEM' });
      
      if (catalogResult.objects && catalogResult.objects.length > 0) {
        console.log(`✅ Found ${catalogResult.objects.length} catalog items:`);
        
        let serviceCount = 0;
        let suspiciousServices = [];
        let expectedServices = [];
        
        catalogResult.objects.forEach((item, index) => {
          if (item.type === 'ITEM' && item.itemData) {
            serviceCount++;
            const itemName = item.itemData.name || 'Unnamed Service';
            const category = item.itemData.categoryId || 'No Category';
            
            console.log(`\n${serviceCount}. ${itemName}`);
            console.log(`   ID: ${item.id}`);
            console.log(`   Category ID: ${category}`);
            
            if (item.itemData.variations && item.itemData.variations.length > 0) {
              console.log(`   Variations:`);
              item.itemData.variations.forEach((variation, vIndex) => {
                console.log(`     ${vIndex + 1}. ${variation.itemVariationData?.name || 'Default'}`);
                if (variation.itemVariationData?.priceMoney) {
                  const price = variation.itemVariationData.priceMoney.amount / 100;
                  console.log(`        Price: $${price}`);
                }
              });
            }
            
            // Check for suspicious services (not typical for Brazilian wax spa)
            const nameLower = itemName.toLowerCase();
            if (nameLower.includes('haircut') || 
                nameLower.includes('manicure') || 
                nameLower.includes('pedicure') || 
                (nameLower.includes('massage') && !nameLower.includes('brazilian')) ||
                (nameLower.includes('hair') && !nameLower.includes('removal')) ||
                nameLower.includes('nail')) {
              suspiciousServices.push(itemName);
            }
            
            // Check for expected services
            if (nameLower.includes('brazilian') || 
                nameLower.includes('wax') || 
                nameLower.includes('bikini') ||
                nameLower.includes('full body') ||
                nameLower.includes('eyebrow') ||
                nameLower.includes('brow') ||
                nameLower.includes('lash') ||
                nameLower.includes('facial')) {
              expectedServices.push(itemName);
            }
          }
        });
        
        console.log('\n📊 SERVICE ANALYSIS SUMMARY:');
        console.log('============================');
        console.log(`Total Services Found: ${serviceCount}`);
        
        if (suspiciousServices.length > 0) {
          console.log('\n🚨 SUSPICIOUS SERVICES (Not typical for Brazilian wax spa):');
          suspiciousServices.forEach(service => console.log(`❌ ${service}`));
        } else {
          console.log('\n✅ No suspicious services found - all appear appropriate for spa business');
        }
        
        if (expectedServices.length > 0) {
          console.log('\n✅ EXPECTED SERVICES (Typical for Brazilian wax/beauty spa):');
          expectedServices.forEach(service => console.log(`✅ ${service}`));
        }
        
      } else {
        console.log('❌ No catalog items found');
      }
      
    } catch (catalogError) {
      console.log('❌ Error getting catalog:', catalogError.message);
      console.log('Error details:', catalogError);
    }

    // 3. Get categories
    console.log('\n3. GETTING SERVICE CATEGORIES...');
    console.log('---------------------------------');
    
    try {
      const categoriesResult = await catalogApi.list({ types: 'CATEGORY' });
      
      if (categoriesResult.objects && categoriesResult.objects.length > 0) {
        console.log(`✅ Found ${categoriesResult.objects.length} categories:`);
        categoriesResult.objects.forEach((category, index) => {
          if (category.type === 'CATEGORY' && category.categoryData) {
            console.log(`${index + 1}. ${category.categoryData.name} (${category.id})`);
          }
        });
      }
    } catch (catError) {
      console.log('❌ Error getting categories:', catError.message);
    }

    console.log('\n🔍 SQUARE CATALOG INVESTIGATION COMPLETE');
    console.log('========================================');
    
  } catch (error) {
    console.error('💥 Critical error during Square investigation:', error);
  }
}

investigateSquareCatalog();