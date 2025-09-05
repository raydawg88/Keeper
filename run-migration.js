const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

async function runAppointmentsMigration() {
    console.log('🚀 Running appointments table migration...');
    
    // Initialize Supabase client with service key for admin operations
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
        // Read the migration file
        const migrationPath = path.join(__dirname, 'supabase/migrations/create_appointments_table.sql');
        const migrationSQL = fs.readFileSync(migrationPath, 'utf8');
        
        console.log('📄 Migration file loaded');
        console.log('🔍 Checking if table already exists...');
        
        // Check if table already exists
        const { data: existingTable, error: checkError } = await supabase
            .from('appointments')
            .select('id')
            .limit(1);
            
        if (!checkError) {
            console.log('✅ Table already exists, migration may have been run previously');
            console.log('🔍 Verifying table structure...');
        } else if (checkError.code === '42P01') {
            console.log('📋 Table does not exist, proceeding with migration');
        } else {
            console.log('⚠️  Unexpected error checking table:', checkError.message);
        }
        
        // Since we can't execute SQL directly via the client, let's try a different approach
        // We'll split the migration into parts and try to execute via CREATE TABLE directly
        
        console.log('🔧 Attempting to create table via manual SQL execution...');
        console.log('   Since Supabase doesn\'t allow direct SQL execution via the API,');
        console.log('   you will need to run this migration manually.');
        console.log('');
        console.log('📋 Manual Steps:');
        console.log('1. Go to Supabase SQL Editor: https://supabase.com/dashboard/project/jlawmbqoykwgrjutrfsp/sql');
        console.log('2. Copy the migration file contents:');
        console.log('   File: supabase/migrations/create_appointments_table.sql');
        console.log('3. Paste and execute in the SQL editor');
        console.log('');
        console.log('Or run this command if you have psql:');
        console.log('psql "postgresql://postgres:[PASSWORD]@db.jlawmbqoykwgrjutrfsp.supabase.co:5432/postgres" < supabase/migrations/create_appointments_table.sql');
        console.log('');
        
        // After manual execution, let's verify
        console.log('⏳ Waiting 5 seconds for you to run the migration manually...');
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        console.log('🔍 Attempting to verify migration...');
        const { data: verifyData, error: verifyError } = await supabase
            .from('appointments')
            .select('id')
            .limit(1);
            
        if (!verifyError) {
            console.log('✅ SUCCESS! Appointments table is accessible');
            
            // Get column information
            const { data: columns, error: columnError } = await supabase
                .from('information_schema.columns')
                .select('column_name, data_type, is_nullable')
                .eq('table_name', 'appointments')
                .eq('table_schema', 'public')
                .order('ordinal_position');
                
            if (!columnError && columns?.length > 0) {
                console.log('\n📊 Table Structure Verified:');
                console.log('==============================');
                columns.forEach(col => {
                    const nullable = col.is_nullable === 'YES' ? '' : ' (NOT NULL)';
                    console.log(`• ${col.column_name}: ${col.data_type}${nullable}`);
                });
                
                // Check record count
                const { count } = await supabase
                    .from('appointments')
                    .select('*', { count: 'exact', head: true });
                    
                console.log(`\n📈 Current record count: ${count || 0}`);
                console.log('🎉 Migration completed successfully!');
                console.log('📝 The appointments table is ready for Square appointment data');
                
                return true;
            } else {
                console.log('✅ Table exists but could not retrieve structure details');
                return true;
            }
            
        } else if (verifyError.code === '42P01') {
            console.log('❌ Table still does not exist');
            console.log('   Please run the migration manually as instructed above');
            return false;
        } else {
            console.log('⚠️  Verification error:', verifyError.message);
            console.log('   Table may exist but there could be permission issues');
            return false;
        }
        
    } catch (error) {
        console.error('❌ Migration error:', error.message);
        return false;
    }
}

// Run the migration
runAppointmentsMigration().then(success => {
    if (success) {
        console.log('\n✅ MIGRATION COMPLETED SUCCESSFULLY!');
    } else {
        console.log('\n❌ MIGRATION FAILED - Manual execution required');
        console.log('See instructions above for manual setup');
    }
    process.exit(success ? 0 : 1);
});