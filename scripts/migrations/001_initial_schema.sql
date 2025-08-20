-- Migration: 001_initial_schema.sql
-- Description: Initial VendorChain MVP database schema
-- Date: 2025-08-19
-- Version: 1

-- Check if migration has already been applied
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM schema_version WHERE version = 1) THEN
        RAISE NOTICE 'Migration 001 already applied, skipping...';
        RETURN;
    END IF;
    
    -- Execute the main schema script
    RAISE NOTICE 'Applying migration 001: Initial schema...';
END $$;