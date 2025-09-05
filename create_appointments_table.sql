-- Create appointments table for storing Square appointment/booking data
CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL,
    square_booking_id TEXT UNIQUE NOT NULL,
    customer_id TEXT NOT NULL,
    location_id TEXT NOT NULL,
    service_variation_id TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    start_at TIMESTAMP WITH TIME ZONE NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign key constraint to accounts table
    CONSTRAINT fk_appointments_account_id 
        FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

-- Create indexes for optimal performance
CREATE INDEX idx_appointments_account_id ON appointments(account_id);
CREATE INDEX idx_appointments_square_booking_id ON appointments(square_booking_id);
CREATE INDEX idx_appointments_customer_id ON appointments(customer_id);
CREATE INDEX idx_appointments_location_id ON appointments(location_id);
CREATE INDEX idx_appointments_start_at ON appointments(start_at);
CREATE INDEX idx_appointments_status ON appointments(status);
CREATE INDEX idx_appointments_created_at ON appointments(created_at);

-- Create a trigger function to automatically update the updated_at column
CREATE OR REPLACE FUNCTION update_appointments_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger
CREATE TRIGGER trigger_update_appointments_updated_at
    BEFORE UPDATE ON appointments
    FOR EACH ROW
    EXECUTE FUNCTION update_appointments_updated_at();

-- Add comments for documentation
COMMENT ON TABLE appointments IS 'Stores Square appointment/booking data';
COMMENT ON COLUMN appointments.id IS 'Primary key UUID';
COMMENT ON COLUMN appointments.account_id IS 'Foreign key to accounts table';
COMMENT ON COLUMN appointments.square_booking_id IS 'Unique Square booking identifier';
COMMENT ON COLUMN appointments.customer_id IS 'Square customer ID';
COMMENT ON COLUMN appointments.location_id IS 'Square location ID';
COMMENT ON COLUMN appointments.service_variation_id IS 'Square service variation ID';
COMMENT ON COLUMN appointments.duration_minutes IS 'Appointment duration in minutes';
COMMENT ON COLUMN appointments.start_at IS 'Appointment start time';
COMMENT ON COLUMN appointments.status IS 'Appointment status';
COMMENT ON COLUMN appointments.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN appointments.updated_at IS 'Record last update timestamp';