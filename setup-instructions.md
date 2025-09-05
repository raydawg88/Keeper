# Create Appointments Table in Supabase

## Automated Setup Failed
The automated setup scripts could not execute SQL directly due to Supabase's security restrictions. Please follow the manual setup instructions below.

## Manual Setup Instructions

### Option 1: Using Supabase SQL Editor (Recommended)

1. Go to your Supabase dashboard: https://supabase.com/dashboard/project/jlawmbqoykwgrjutrfsp/sql

2. Copy and paste the entire contents of `create_appointments_table.sql` into the SQL editor

3. Click the "Run" button to execute the SQL

### Option 2: Using PostgreSQL Client

If you have PostgreSQL client installed, you can connect directly:

```bash
psql "postgresql://postgres:[YOUR_DB_PASSWORD]@db.jlawmbqoykwgrjutrfsp.supabase.co:5432/postgres"
```

You can find your database password in: Dashboard → Settings → Database → Database password

Then copy and paste the contents of `create_appointments_table.sql`

## What the SQL Creates

The script will create:

1. **appointments table** with the following columns:
   - `id` (UUID, Primary Key)
   - `account_id` (UUID, Foreign Key to accounts table)
   - `square_booking_id` (TEXT, Unique Square booking ID)
   - `customer_id` (TEXT, Square customer ID)
   - `location_id` (TEXT, Square location ID) 
   - `service_variation_id` (TEXT, Square service variation ID)
   - `duration_minutes` (INTEGER, Appointment duration)
   - `start_at` (TIMESTAMP WITH TIME ZONE, Appointment start time)
   - `status` (TEXT, Appointment status)
   - `created_at` (TIMESTAMP WITH TIME ZONE, Record creation time)
   - `updated_at` (TIMESTAMP WITH TIME ZONE, Record update time)

2. **Indexes** for optimal performance:
   - account_id, square_booking_id, customer_id, location_id, start_at, status, created_at

3. **Trigger function** to automatically update `updated_at` timestamp

4. **Comments** for documentation

## Verification

After running the SQL, you can verify the table was created by running the verification script:

```bash
node verify-appointments-table.js
```

## Table Structure Expected

```
• id: uuid (NOT NULL)
• account_id: uuid (NOT NULL) 
• square_booking_id: text (NOT NULL)
• customer_id: text (NOT NULL)
• location_id: text (NOT NULL)
• service_variation_id: text (NOT NULL)
• duration_minutes: integer (NOT NULL)
• start_at: timestamp with time zone (NOT NULL)
• status: text (NOT NULL)
• created_at: timestamp with time zone
• updated_at: timestamp with time zone
```

The table will be ready to store Square appointment/booking data once created.