-- VendorChain MVP Complete Database Schema
-- Version: 1.0.0
-- Date: 2025-08-19

-- Drop existing tables if they exist (for clean installation)
DROP TABLE IF EXISTS vendor_contract_management_workflow_log CASCADE;
DROP TABLE IF EXISTS vendor_contract_api_metadata CASCADE;
DROP TABLE IF EXISTS vendor_contract_management_contract CASCADE;
DROP TABLE IF EXISTS vendor_contract_management_vendor CASCADE;

-- Drop existing types if they exist
DROP TYPE IF EXISTS vendor_type_enum CASCADE;
DROP TYPE IF EXISTS vendor_status_enum CASCADE;
DROP TYPE IF EXISTS contract_type_enum CASCADE;
DROP TYPE IF EXISTS contract_status_enum CASCADE;

-- Create ENUM types for constrained fields
CREATE TYPE vendor_type_enum AS ENUM ('SUPPLIER', 'SERVICE_PROVIDER', 'CONTRACTOR', 'CONSULTANT');
CREATE TYPE vendor_status_enum AS ENUM ('ACTIVE', 'INACTIVE', 'SUSPENDED', 'BLACKLISTED');
CREATE TYPE contract_type_enum AS ENUM ('PURCHASE', 'SERVICE', 'LEASE', 'MAINTENANCE', 'CONSULTING');
CREATE TYPE contract_status_enum AS ENUM ('CREATED', 'VERIFIED', 'SUBMITTED', 'EXPIRED', 'TERMINATED');

-- =======================
-- VENDORS TABLE
-- =======================
CREATE TABLE vendor_contract_management_vendor (
    id SERIAL PRIMARY KEY,
    vendor_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    registration_number VARCHAR(100),
    contact_email VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(50),
    address TEXT,
    vendor_type vendor_type_enum NOT NULL DEFAULT 'SUPPLIER',
    status vendor_status_enum NOT NULL DEFAULT 'ACTIVE',
    blockchain_identity VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT vendor_email_check CHECK (contact_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT vendor_id_format CHECK (vendor_id ~ '^[A-Z0-9_-]+$')
);

-- Create indexes for vendors
CREATE INDEX idx_vendor_vendor_id ON vendor_contract_management_vendor(vendor_id);
CREATE INDEX idx_vendor_name ON vendor_contract_management_vendor(name);
CREATE INDEX idx_vendor_status ON vendor_contract_management_vendor(status);
CREATE INDEX idx_vendor_type ON vendor_contract_management_vendor(vendor_type);
CREATE INDEX idx_vendor_email ON vendor_contract_management_vendor(contact_email);

-- =======================
-- CONTRACTS TABLE
-- =======================
CREATE TABLE vendor_contract_management_contract (
    id SERIAL PRIMARY KEY,
    contract_id VARCHAR(50) UNIQUE NOT NULL,
    vendor_id INTEGER NOT NULL,
    contract_type contract_type_enum NOT NULL,
    status contract_status_enum NOT NULL DEFAULT 'CREATED',
    description TEXT,
    total_value DECIMAL(15,2) NOT NULL CHECK (total_value >= 0),
    paid_amount DECIMAL(15,2) DEFAULT 0 CHECK (paid_amount >= 0),
    remaining_amount DECIMAL(15,2) GENERATED ALWAYS AS (total_value - paid_amount) STORED,
    payment_history JSONB DEFAULT '[]'::jsonb,
    expiry_date DATE NOT NULL,
    document_hash VARCHAR(255),
    blockchain_tx_id VARCHAR(255),
    created_by VARCHAR(100) NOT NULL,
    verified_by VARCHAR(100),
    verified_at TIMESTAMP,
    submitted_by VARCHAR(100),
    submitted_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    odoo_user_id INTEGER,
    
    -- Foreign key constraint
    CONSTRAINT fk_contract_vendor FOREIGN KEY (vendor_id) 
        REFERENCES vendor_contract_management_vendor(id) ON DELETE RESTRICT,
    
    -- Business rule constraints
    CONSTRAINT contract_id_format CHECK (contract_id ~ '^CONTRACT[0-9]+$'),
    CONSTRAINT paid_not_exceed_total CHECK (paid_amount <= total_value),
    CONSTRAINT expiry_after_creation CHECK (expiry_date > created_at::date),
    CONSTRAINT verified_requires_verifier CHECK (
        (status != 'VERIFIED' AND status != 'SUBMITTED') OR 
        (verified_by IS NOT NULL AND verified_at IS NOT NULL)
    ),
    CONSTRAINT submitted_requires_verification CHECK (
        status != 'SUBMITTED' OR 
        (verified_by IS NOT NULL AND submitted_by IS NOT NULL)
    )
);

-- Create indexes for contracts
CREATE INDEX idx_contract_contract_id ON vendor_contract_management_contract(contract_id);
CREATE INDEX idx_contract_vendor_id ON vendor_contract_management_contract(vendor_id);
CREATE INDEX idx_contract_status ON vendor_contract_management_contract(status);
CREATE INDEX idx_contract_type ON vendor_contract_management_contract(contract_type);
CREATE INDEX idx_contract_expiry ON vendor_contract_management_contract(expiry_date);
CREATE INDEX idx_contract_blockchain_tx ON vendor_contract_management_contract(blockchain_tx_id);
CREATE INDEX idx_contract_payment_history ON vendor_contract_management_contract USING GIN(payment_history);
CREATE INDEX idx_contract_created_at ON vendor_contract_management_contract(created_at);

-- =======================
-- WORKFLOW LOGS TABLE
-- =======================
CREATE TABLE vendor_contract_management_workflow_log (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    from_status contract_status_enum,
    to_status contract_status_enum NOT NULL,
    performed_by VARCHAR(100) NOT NULL,
    performed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    blockchain_tx_id VARCHAR(255),
    odoo_user_id INTEGER,
    
    -- Foreign key constraint
    CONSTRAINT fk_workflow_contract FOREIGN KEY (contract_id) 
        REFERENCES vendor_contract_management_contract(id) ON DELETE CASCADE,
    
    -- Business rule constraints
    CONSTRAINT valid_action CHECK (action IN ('CREATE', 'VERIFY', 'SUBMIT', 'EXPIRE', 'TERMINATE', 'PAYMENT')),
    CONSTRAINT valid_transition CHECK (
        (action = 'CREATE' AND from_status IS NULL AND to_status = 'CREATED') OR
        (action = 'VERIFY' AND from_status = 'CREATED' AND to_status = 'VERIFIED') OR
        (action = 'SUBMIT' AND from_status = 'VERIFIED' AND to_status = 'SUBMITTED') OR
        (action = 'EXPIRE' AND to_status = 'EXPIRED') OR
        (action = 'TERMINATE' AND to_status = 'TERMINATED') OR
        (action = 'PAYMENT' AND from_status = to_status)
    )
);

-- Create indexes for workflow logs
CREATE INDEX idx_workflow_contract_id ON vendor_contract_management_workflow_log(contract_id);
CREATE INDEX idx_workflow_action ON vendor_contract_management_workflow_log(action);
CREATE INDEX idx_workflow_performed_at ON vendor_contract_management_workflow_log(performed_at);
CREATE INDEX idx_workflow_performed_by ON vendor_contract_management_workflow_log(performed_by);

-- =======================
-- API METADATA TABLE
-- =======================
CREATE TABLE vendor_contract_api_metadata (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER,
    api_endpoint VARCHAR(255) NOT NULL,
    http_method VARCHAR(10) NOT NULL,
    request_payload JSONB,
    response_payload JSONB,
    status_code INTEGER,
    blockchain_sync BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint (nullable for non-contract specific calls)
    CONSTRAINT fk_api_contract FOREIGN KEY (contract_id) 
        REFERENCES vendor_contract_management_contract(id) ON DELETE CASCADE,
    
    -- Constraints
    CONSTRAINT valid_http_method CHECK (http_method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH')),
    CONSTRAINT valid_status_code CHECK (status_code >= 100 AND status_code < 600)
);

-- Create indexes for API metadata
CREATE INDEX idx_api_contract_id ON vendor_contract_api_metadata(contract_id);
CREATE INDEX idx_api_endpoint ON vendor_contract_api_metadata(api_endpoint);
CREATE INDEX idx_api_created_at ON vendor_contract_api_metadata(created_at);
CREATE INDEX idx_api_blockchain_sync ON vendor_contract_api_metadata(blockchain_sync);

-- =======================
-- TRIGGERS
-- =======================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to vendors table
CREATE TRIGGER update_vendor_updated_at 
    BEFORE UPDATE ON vendor_contract_management_vendor
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Apply updated_at trigger to contracts table
CREATE TRIGGER update_contract_updated_at 
    BEFORE UPDATE ON vendor_contract_management_contract
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Function to log contract status changes
CREATE OR REPLACE FUNCTION log_contract_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO vendor_contract_management_workflow_log (
            contract_id, 
            action,
            from_status,
            to_status,
            performed_by,
            performed_at,
            notes
        ) VALUES (
            NEW.id,
            CASE 
                WHEN NEW.status = 'VERIFIED' THEN 'VERIFY'
                WHEN NEW.status = 'SUBMITTED' THEN 'SUBMIT'
                WHEN NEW.status = 'EXPIRED' THEN 'EXPIRE'
                WHEN NEW.status = 'TERMINATED' THEN 'TERMINATE'
                ELSE 'UPDATE'
            END,
            OLD.status,
            NEW.status,
            COALESCE(NEW.verified_by, NEW.submitted_by, NEW.created_by),
            CURRENT_TIMESTAMP,
            'Automatic log entry for status change'
        );
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply status change trigger to contracts table
CREATE TRIGGER log_contract_status_changes
    AFTER UPDATE ON vendor_contract_management_contract
    FOR EACH ROW
    WHEN (OLD.status IS DISTINCT FROM NEW.status)
    EXECUTE FUNCTION log_contract_status_change();

-- Function to validate payment updates
CREATE OR REPLACE FUNCTION validate_payment_update()
RETURNS TRIGGER AS $$
BEGIN
    -- Ensure payment history is properly formatted
    IF NEW.payment_history IS NOT NULL AND jsonb_typeof(NEW.payment_history) != 'array' THEN
        RAISE EXCEPTION 'payment_history must be a JSON array';
    END IF;
    
    -- Ensure paid amount matches sum of payment history
    IF NEW.payment_history IS NOT NULL AND jsonb_array_length(NEW.payment_history) > 0 THEN
        NEW.paid_amount = (
            SELECT COALESCE(SUM((payment->>'amount')::decimal), 0)
            FROM jsonb_array_elements(NEW.payment_history) AS payment
        );
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply payment validation trigger
CREATE TRIGGER validate_contract_payments
    BEFORE INSERT OR UPDATE ON vendor_contract_management_contract
    FOR EACH ROW
    WHEN (NEW.payment_history IS NOT NULL)
    EXECUTE FUNCTION validate_payment_update();

-- =======================
-- VIEWS
-- =======================

-- View for active contracts with vendor details
CREATE OR REPLACE VIEW active_contracts_view AS
SELECT 
    c.id,
    c.contract_id,
    c.status,
    c.contract_type,
    v.vendor_id,
    v.name as vendor_name,
    v.contact_email as vendor_email,
    c.total_value,
    c.paid_amount,
    c.remaining_amount,
    c.expiry_date,
    c.created_at,
    c.updated_at,
    CASE 
        WHEN c.expiry_date < CURRENT_DATE THEN 'EXPIRED'
        WHEN c.expiry_date < CURRENT_DATE + INTERVAL '30 days' THEN 'EXPIRING_SOON'
        ELSE 'ACTIVE'
    END as expiry_status
FROM vendor_contract_management_contract c
JOIN vendor_contract_management_vendor v ON c.vendor_id = v.id
WHERE c.status IN ('CREATED', 'VERIFIED', 'SUBMITTED')
AND v.status = 'ACTIVE';

-- View for payment summary
CREATE OR REPLACE VIEW payment_summary_view AS
SELECT 
    v.vendor_id,
    v.name as vendor_name,
    COUNT(c.id) as total_contracts,
    SUM(c.total_value) as total_contract_value,
    SUM(c.paid_amount) as total_paid,
    SUM(c.remaining_amount) as total_remaining,
    AVG(c.paid_amount / NULLIF(c.total_value, 0) * 100) as avg_payment_percentage
FROM vendor_contract_management_vendor v
LEFT JOIN vendor_contract_management_contract c ON v.id = c.vendor_id
GROUP BY v.vendor_id, v.name;

-- =======================
-- PERMISSIONS
-- =======================

-- Grant permissions on all tables to the odoo user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO odoo;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO odoo;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO odoo;

-- =======================
-- SCHEMA VERSION
-- =======================

-- Create schema version table for migrations
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    description VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Record initial schema version
INSERT INTO schema_version (version, description) 
VALUES (1, 'Initial VendorChain MVP schema')
ON CONFLICT (version) DO NOTHING;