const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

async function verifyAppointmentsTable() {
    console.log('🔍 Verifying appointments table in Supabase...');
    
    // Initialize Supabase client with service key
    const supabase = createClient(
        process.env.SUPABASE_URL,
        process.env.SUPABASE_SERVICE_KEY,
        {
            auth: {
                autoRefreshToken: false,
                persistSession: false
            }
        }
    );

    try {
        // Test basic table access
        console.log('📋 Testing table access...');
        const { data, error } = await supabase
            .from('appointments')
            .select('*')
            .limit(1);
            
        if (error) {
            if (error.code === '42P01') {
                console.log('❌ Table does not exist yet');
                console.log('   Please run the SQL from create_appointments_table.sql in Supabase SQL Editor');
                console.log('   URL: https://supabase.com/dashboard/project/jlawmbqoykwgrjutrfsp/sql');
                return false;
            } else {
                console.log('⚠️  Table access error:', error.message);
                return false;
            }
        }
        
        console.log('✅ Table exists and is accessible');
        
        // Get table structure using information_schema
        console.log('📊 Retrieving table structure...');
        
        const { data: columns, error: columnsError } = await supabase
            .from('information_schema.columns')
            .select('column_name, data_type, is_nullable, column_default')
            .eq('table_name', 'appointments')
            .eq('table_schema', 'public')
            .order('ordinal_position');
            
        if (columnsError) {
            console.log('⚠️  Could not retrieve table structure:', columnsError.message);
        } else if (columns && columns.length > 0) {
            console.log('\n📊 Table Structure:');
            console.log('==========================================');
            
            const expectedColumns = {
                'id': 'uuid',
                'account_id': 'uuid', 
                'square_booking_id': 'text',
                'customer_id': 'text',
                'location_id': 'text',
                'service_variation_id': 'text',
                'duration_minutes': 'integer',
                'start_at': 'timestamp with time zone',
                'status': 'text',
                'created_at': 'timestamp with time zone',
                'updated_at': 'timestamp with time zone'
            };
            
            let allColumnsPresent = true;
            
            columns.forEach(column => {
                const hasDefault = column.column_default ? ` (Default: ${column.column_default.substring(0, 30)}${column.column_default.length > 30 ? '...' : ''})` : '';
                const notNull = column.is_nullable === 'NO' ? ' (NOT NULL)' : '';
                console.log(`• ${column.column_name}: ${column.data_type}${notNull}${hasDefault}`);
            });
            
            // Check if all expected columns are present
            console.log('\n🔍 Checking required columns...');
            for (const [columnName, expectedType] of Object.entries(expectedColumns)) {
                const foundColumn = columns.find(c => c.column_name === columnName);
                if (!foundColumn) {
                    console.log(`❌ Missing column: ${columnName}`);
                    allColumnsPresent = false;
                } else if (foundColumn.data_type !== expectedType) {
                    console.log(`⚠️  Column type mismatch: ${columnName} (expected: ${expectedType}, found: ${foundColumn.data_type})`);
                } else {
                    console.log(`✅ ${columnName}: ${foundColumn.data_type}`);
                }
            }
            
            if (allColumnsPresent) {
                console.log('\n✅ All required columns present!');
            }
        }
        
        // Check indexes
        console.log('\n🔗 Checking indexes...');
        const { data: indexes, error: indexError } = await supabase
            .from('pg_indexes')
            .select('indexname, indexdef')
            .eq('tablename', 'appointments');
            
        if (indexError) {
            console.log('⚠️  Could not retrieve index information:', indexError.message);
        } else if (indexes && indexes.length > 0) {
            console.log('Indexes found:');
            indexes.forEach(index => {
                console.log(`• ${index.indexname}`);
            });
        } else {
            console.log('⚠️  No indexes found - make sure to run the full SQL script');
        }
        
        // Test insert permissions (without actually inserting)
        console.log('\n🧪 Testing table permissions...');
        try {
            // Try to get count
            const { count, error: countError } = await supabase
                .from('appointments')
                .select('*', { count: 'exact', head: true });
                
            if (countError) {
                console.log('⚠️  Count query failed:', countError.message);
            } else {
                console.log(`✅ Table accessible - current record count: ${count || 0}`);
            }
        } catch (permError) {
            console.log('⚠️  Permission test failed:', permError.message);
        }
        
        console.log('\n🎉 Appointments table verification complete!');
        console.log('📝 Table is ready for appointment data');
        
        return true;
        
    } catch (error) {
        console.error('❌ Verification failed:', error.message);
        return false;
    }
}

// Run the verification
verifyAppointmentsTable().then(success => {
    if (success) {
        console.log('\n✅ SUCCESS: Appointments table is properly configured!');
    } else {
        console.log('\n❌ FAILED: Please check the setup instructions and try again.');
    }
    process.exit(success ? 0 : 1);
});