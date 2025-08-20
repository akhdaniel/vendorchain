-- VendorChain MVP Sample Data
-- This script loads sample data for development and testing

-- Clear existing sample data (be careful in production!)
TRUNCATE TABLE vendor_contract_management_workflow_log CASCADE;
TRUNCATE TABLE vendor_contract_api_metadata CASCADE;
TRUNCATE TABLE vendor_contract_management_contract CASCADE;
TRUNCATE TABLE vendor_contract_management_vendor CASCADE;

-- =======================
-- SAMPLE VENDORS
-- =======================

INSERT INTO vendor_contract_management_vendor (vendor_id, name, registration_number, contact_email, contact_phone, address, vendor_type, status, blockchain_identity) VALUES
('VENDOR001', 'Acme Supplies Inc.', 'REG-2023-001', 'contact@acmesupplies.com', '+1-555-0100', '123 Industrial Way, Tech City, TC 12345', 'SUPPLIER', 'ACTIVE', '0x1234567890abcdef1234567890abcdef12345678'),
('VENDOR002', 'TechPro Services LLC', 'REG-2023-002', 'info@techproservices.com', '+1-555-0200', '456 Service Drive, Metro City, MC 67890', 'SERVICE_PROVIDER', 'ACTIVE', '0x2345678901bcdef2345678901bcdef234567890a'),
('VENDOR003', 'BuildRight Contractors', 'REG-2023-003', 'admin@buildright.com', '+1-555-0300', '789 Construction Blvd, Builder Town, BT 13579', 'CONTRACTOR', 'ACTIVE', '0x3456789012cdef3456789012cdef3456789012bc'),
('VENDOR004', 'Strategic Advisors Group', 'REG-2023-004', 'contact@strategicadvisors.com', '+1-555-0400', '321 Consulting Plaza, Business District, BD 24680', 'CONSULTANT', 'ACTIVE', '0x4567890123def4567890123def4567890123cdef'),
('VENDOR005', 'Global Logistics Co.', 'REG-2023-005', 'ops@globallogistics.com', '+1-555-0500', '555 Shipping Lane, Port City, PC 36912', 'SUPPLIER', 'ACTIVE', NULL),
('VENDOR006', 'CloudTech Solutions', 'REG-2023-006', 'support@cloudtech.com', '+1-555-0600', '999 Data Center Way, Silicon Valley, SV 95014', 'SERVICE_PROVIDER', 'SUSPENDED', NULL),
('VENDOR007', 'Eco Materials Ltd.', 'REG-2023-007', 'sales@ecomaterials.com', '+1-555-0700', '777 Green Street, Eco City, EC 14725', 'SUPPLIER', 'ACTIVE', '0x5678901234ef5678901234ef5678901234ef5678'),
('VENDOR008', 'Precision Tools Inc.', 'REG-2023-008', 'orders@precisiontools.com', '+1-555-0800', '888 Manufacturing Road, Tool Town, TT 25836', 'SUPPLIER', 'INACTIVE', NULL);

-- =======================
-- SAMPLE CONTRACTS
-- =======================

-- Active contracts in different stages
INSERT INTO vendor_contract_management_contract (
    contract_id, vendor_id, contract_type, status, description, 
    total_value, paid_amount, payment_history, expiry_date, 
    document_hash, blockchain_tx_id, created_by, verified_by, 
    verified_at, submitted_by, submitted_at, odoo_user_id
) VALUES
-- SUBMITTED contracts (fully processed)
('CONTRACT001', (SELECT id FROM vendor_contract_management_vendor WHERE vendor_id = 'VENDOR001'), 'PURCHASE', 'SUBMITTED', 'Office supplies for Q1 2025', 
 45000.00, 15000.00, 
 '[{"amount": 5000, "date": "2025-01-15", "reference": "PAY-001", "method": "bank_transfer"},
   {"amount": 10000, "date": "2025-02-15", "reference": "PAY-002", "method": "bank_transfer"}]'::jsonb,
 '2026-12-31', 
 'hash_abc123', 'tx_0x1234abcd', 'john.doe', 'jane.smith', 
 '2026-01-10 14:30:00', 'admin', '2026-01-11 09:00:00', 1),

('CONTRACT002', (SELECT id FROM vendor_contract_management_vendor WHERE vendor_id = 'VENDOR002'), 'SERVICE', 'SUBMITTED', 'Annual IT support and maintenance', 
 120000.00, 30000.00,
 '[{"amount": 10000, "date": "2025-01-01", "reference": "PAY-003", "method": "wire_transfer"},
   {"amount": 10000, "date": "2025-02-01", "reference": "PAY-004", "method": "wire_transfer"},
   {"amount": 10000, "date": "2025-03-01", "reference": "PAY-005", "method": "wire_transfer"}]'::jsonb,
 '2026-12-31', 
 'hash_def456', 'tx_0x5678efgh', 'alice.johnson', 'bob.wilson', 
 '2026-01-05 10:00:00', 'admin', '2026-01-06 11:00:00', 2),

-- VERIFIED contracts (ready for submission)
('CONTRACT003', (SELECT id FROM vendor_contract_management_vendor WHERE vendor_id = 'VENDOR003'), 'MAINTENANCE', 'VERIFIED', 'Building maintenance contract 2025', 
 75000.00, 0.00, '[]'::jsonb,
 '2026-06-30', 
 'hash_ghi789', 'tx_0x9012ijkl', 'mike.brown', 'sarah.davis', 
 CURRENT_TIMESTAMP - INTERVAL '5 days', NULL, NULL, 3),

('CONTRACT004', (SELECT id FROM vendor_contract_management_vendor WHERE vendor_id = 'VENDOR004'), 'CONSULTING', 'VERIFIED', 'Strategic planning consultation', 
 95000.00, 0.00, '[]'::jsonb,
 '2026-09-30', 
 'hash_jkl012', 'tx_0x3456mnop', 'emily.white', 'james.taylor', 
 '2026-02-10 09:30:00', NULL, NULL, 4),

-- CREATED contracts (pending verification)
('CONTRACT005', (SELECT id FROM vendor_contract_management_vendor WHERE vendor_id = 'VENDOR005'), 'LEASE', 'CREATED', 'Warehouse lease agreement', 
 180000.00, 0.00, '[]'::jsonb,
 '2026-01-31', 
 NULL, NULL, 'robert.jones', NULL, 
 NULL, NULL, NULL, 5),

('CONTRACT006', (SELECT id FROM vendor_contract_management_vendor WHERE vendor_id = 'VENDOR007'), 'PURCHASE', 'CREATED', 'Eco-friendly materials bulk order', 
 55000.00, 0.00, '[]'::jsonb,
 '2026-08-31', 
 NULL, NULL, 'lisa.martinez', NULL, 
 NULL, NULL, NULL, 6),

('CONTRACT007', (SELECT id FROM vendor_contract_management_vendor WHERE vendor_id = 'VENDOR001'), 'PURCHASE', 'CREATED', 'Emergency supplies order', 
 12500.00, 0.00, '[]'::jsonb,
 '2026-04-30', 
 NULL, NULL, 'david.garcia', NULL, 
 NULL, NULL, NULL, 7),

-- Expired contract example (will expire soon)
('CONTRACT008', (SELECT id FROM vendor_contract_management_vendor WHERE vendor_id = 'VENDOR008'), 'SERVICE', 'SUBMITTED', 'Tool maintenance service (expiring)', 
 25000.00, 25000.00,
 '[{"amount": 25000, "date": "2026-01-15", "reference": "PAY-006", "method": "check"}]'::jsonb,
 CURRENT_DATE + INTERVAL '5 days', 
 'hash_mno345', 'tx_0x7890qrst', 'admin', 'admin', 
 CURRENT_TIMESTAMP - INTERVAL '30 days', 'admin', CURRENT_TIMESTAMP - INTERVAL '29 days', 1);

-- =======================
-- SAMPLE WORKFLOW LOGS
-- =======================

INSERT INTO vendor_contract_management_workflow_log (
    contract_id, action, from_status, to_status, performed_by, 
    performed_at, notes, blockchain_tx_id, odoo_user_id
) VALUES
-- CONTRACT001 workflow
((SELECT id FROM vendor_contract_management_contract WHERE contract_id = 'CONTRACT001'), 'CREATE', NULL, 'CREATED', 'john.doe', '2026-01-08 10:00:00', 'Initial contract creation', NULL, 1),
((SELECT id FROM vendor_contract_management_contract WHERE contract_id = 'CONTRACT001'), 'VERIFY', 'CREATED', 'VERIFIED', 'jane.smith', '2026-01-10 14:30:00', 'Verified and approved', 'tx_verify_001', 2),
((SELECT id FROM vendor_contract_management_contract WHERE contract_id = 'CONTRACT001'), 'SUBMIT', 'VERIFIED', 'SUBMITTED', 'admin', '2026-01-11 09:00:00', 'Submitted to blockchain', 'tx_submit_001', 1),
((SELECT id FROM vendor_contract_management_contract WHERE contract_id = 'CONTRACT001'), 'PAYMENT', 'SUBMITTED', 'SUBMITTED', 'finance', '2026-01-15 16:00:00', 'First payment processed', 'tx_pay_001', 3),
((SELECT id FROM vendor_contract_management_contract WHERE contract_id = 'CONTRACT001'), 'PAYMENT', 'SUBMITTED', 'SUBMITTED', 'finance', '2026-02-15 16:00:00', 'Second payment processed', 'tx_pay_002', 3),

-- CONTRACT002 workflow
((SELECT id FROM vendor_contract_management_contract WHERE contract_id = 'CONTRACT002'), 'CREATE', NULL, 'CREATED', 'alice.johnson', '2026-01-03 09:00:00', 'IT support contract initiated', NULL, 4),
((SELECT id FROM vendor_contract_management_contract WHERE contract_id = 'CONTRACT002'), 'VERIFY', 'CREATED', 'VERIFIED', 'bob.wilson', '2026-01-05 10:00:00', 'Technical requirements verified', 'tx_verify_002', 5),
((SELECT id FROM vendor_contract_management_contract WHERE contract_id = 'CONTRACT002'), 'SUBMIT', 'VERIFIED', 'SUBMITTED', 'admin', '2026-01-06 11:00:00', 'Contract activated', 'tx_submit_002', 1),
((SELECT id FROM vendor_contract_management_contract WHERE contract_id = 'CONTRACT002'), 'PAYMENT', 'SUBMITTED', 'SUBMITTED', 'finance', '2026-01-01 12:00:00', 'Q1 payment', 'tx_pay_003', 3),

-- CONTRACT003 workflow
((SELECT id FROM vendor_contract_management_contract WHERE contract_id = 'CONTRACT003'), 'CREATE', NULL, 'CREATED', 'mike.brown', '2026-01-25 11:00:00', 'Maintenance contract drafted', NULL, 6),
((SELECT id FROM vendor_contract_management_contract WHERE contract_id = 'CONTRACT003'), 'VERIFY', 'CREATED', 'VERIFIED', 'sarah.davis', CURRENT_TIMESTAMP - INTERVAL '5 days', 'Terms and conditions verified', 'tx_verify_003', 7),

-- CONTRACT004 workflow
((SELECT id FROM vendor_contract_management_contract WHERE contract_id = 'CONTRACT004'), 'CREATE', NULL, 'CREATED', 'emily.white', '2026-02-08 08:30:00', 'Consulting agreement created', NULL, 8),
((SELECT id FROM vendor_contract_management_contract WHERE contract_id = 'CONTRACT004'), 'VERIFY', 'CREATED', 'VERIFIED', 'james.taylor', '2026-02-10 09:30:00', 'Scope and deliverables approved', 'tx_verify_004', 9),

-- CONTRACT005 workflow
((SELECT id FROM vendor_contract_management_contract WHERE contract_id = 'CONTRACT005'), 'CREATE', NULL, 'CREATED', 'robert.jones', CURRENT_TIMESTAMP - INTERVAL '2 days', 'Lease agreement initiated', NULL, 10),

-- CONTRACT006 workflow
((SELECT id FROM vendor_contract_management_contract WHERE contract_id = 'CONTRACT006'), 'CREATE', NULL, 'CREATED', 'lisa.martinez', CURRENT_TIMESTAMP - INTERVAL '1 day', 'Eco materials order placed', NULL, 11),

-- CONTRACT007 workflow
((SELECT id FROM vendor_contract_management_contract WHERE contract_id = 'CONTRACT007'), 'CREATE', NULL, 'CREATED', 'david.garcia', CURRENT_TIMESTAMP - INTERVAL '3 hours', 'Emergency order created', NULL, 12);

-- =======================
-- SAMPLE API METADATA
-- =======================

INSERT INTO vendor_contract_api_metadata (
    contract_id, api_endpoint, http_method, request_payload, 
    response_payload, status_code, blockchain_sync, error_message
) VALUES
((SELECT id FROM vendor_contract_management_contract WHERE contract_id = 'CONTRACT001'), '/api/contracts/create', 'POST', 
 '{"contract_id": "CONTRACT001", "vendor_id": "VENDOR001", "total_value": 45000}'::jsonb,
 '{"success": true, "contract_id": "CONTRACT001", "status": "CREATED"}'::jsonb,
 201, true, NULL),

((SELECT id FROM vendor_contract_management_contract WHERE contract_id = 'CONTRACT001'), '/api/contracts/verify', 'PUT',
 '{"contract_id": "CONTRACT001", "action": "verify"}'::jsonb,
 '{"success": true, "status": "VERIFIED", "tx_id": "tx_verify_001"}'::jsonb,
 200, true, NULL),

((SELECT id FROM vendor_contract_management_contract WHERE contract_id = 'CONTRACT001'), '/api/contracts/submit', 'PUT',
 '{"contract_id": "CONTRACT001", "action": "submit"}'::jsonb,
 '{"success": true, "status": "SUBMITTED", "tx_id": "tx_submit_001"}'::jsonb,
 200, true, NULL),

((SELECT id FROM vendor_contract_management_contract WHERE contract_id = 'CONTRACT002'), '/api/contracts/create', 'POST',
 '{"contract_id": "CONTRACT002", "vendor_id": "VENDOR002", "total_value": 120000}'::jsonb,
 '{"success": true, "contract_id": "CONTRACT002", "status": "CREATED"}'::jsonb,
 201, true, NULL),

(NULL, '/api/vendors/list', 'GET',
 NULL,
 '{"count": 8, "vendors": ["VENDOR001", "VENDOR002", "VENDOR003"]}'::jsonb,
 200, false, NULL),

((SELECT id FROM vendor_contract_management_contract WHERE contract_id = 'CONTRACT003'), '/api/blockchain/sync', 'POST',
 '{"contract_id": "CONTRACT003", "action": "sync"}'::jsonb,
 '{"error": "Connection timeout"}'::jsonb,
 500, false, 'Failed to connect to blockchain network'),

(NULL, '/api/health', 'GET',
 NULL,
 '{"status": "healthy", "database": "connected", "blockchain": "connected"}'::jsonb,
 200, false, NULL);

-- =======================
-- SUMMARY
-- =======================

DO $$
DECLARE
    vendor_count INTEGER;
    contract_count INTEGER;
    submitted_count INTEGER;
    verified_count INTEGER;
    created_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO vendor_count FROM vendor_contract_management_vendor;
    SELECT COUNT(*) INTO contract_count FROM vendor_contract_management_contract;
    SELECT COUNT(*) INTO submitted_count FROM vendor_contract_management_contract WHERE status = 'SUBMITTED';
    SELECT COUNT(*) INTO verified_count FROM vendor_contract_management_contract WHERE status = 'VERIFIED';
    SELECT COUNT(*) INTO created_count FROM vendor_contract_management_contract WHERE status = 'CREATED';
    
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Sample Data Loaded Successfully!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Vendors: %', vendor_count;
    RAISE NOTICE 'Contracts: % total', contract_count;
    RAISE NOTICE '  - Submitted: %', submitted_count;
    RAISE NOTICE '  - Verified: %', verified_count;
    RAISE NOTICE '  - Created: %', created_count;
    RAISE NOTICE '========================================';
END $$;