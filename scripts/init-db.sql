-- VendorChain MVP Database Initialization Script
-- This script initializes the PostgreSQL database with required extensions

-- Create database if it doesn't exist (handled by POSTGRES_DB env var)
-- Ensure proper encoding and collation

-- Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create initial database schema placeholder
-- (Actual tables will be created by Odoo and migrations)

-- Set timezone
SET timezone = 'UTC';

-- Create audit log function for future use
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.write_date = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE vendorchain TO odoo;
GRANT ALL PRIVILEGES ON SCHEMA public TO odoo;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'VendorChain MVP database initialized successfully at %', NOW();
END $$;