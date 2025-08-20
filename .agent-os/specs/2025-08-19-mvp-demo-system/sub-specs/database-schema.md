# Database Schema

This is the database schema implementation for the spec detailed in @.agent-os/specs/2025-08-19-mvp-demo-system/spec.md

> Created: 2025-08-19
> Version: 1.0.0

## Schema Changes

### New Tables

#### vendor_contract_management_contract
- **Purpose:** Primary contract entity storing core contract information
- **Migration:** Create new table with proper foreign key relationships
- **Indexes:** Primary key, unique constraint on contract_number, foreign key indexes

#### vendor_contract_management_vendor
- **Purpose:** Vendor profile information and contact details
- **Migration:** Create new table with unique constraints on vendor codes
- **Indexes:** Primary key, unique constraint on vendor_code, email index

#### vendor_contract_management_workflow_log
- **Purpose:** Audit trail for all workflow state changes
- **Migration:** Create new table with proper timestamp and user tracking
- **Indexes:** Primary key, composite index on (contract_id, created_date)

### Table Specifications

```sql
-- Vendor Profile Table
CREATE TABLE vendor_contract_management_vendor (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    vendor_code VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    contact_person VARCHAR(255),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_uid INTEGER REFERENCES res_users(id),
    write_uid INTEGER REFERENCES res_users(id)
);

-- Contract Table
CREATE TABLE vendor_contract_management_contract (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contract_number VARCHAR(100) UNIQUE NOT NULL,
    vendor_id INTEGER NOT NULL REFERENCES vendor_contract_management_vendor(id),
    contract_value DECIMAL(15,2) NOT NULL,
    contract_date DATE NOT NULL,
    expiration_date DATE,
    description TEXT,
    workflow_stage VARCHAR(20) DEFAULT 'creator' CHECK (workflow_stage IN ('creator', 'verificator', 'submitted')),
    blockchain_tx_id VARCHAR(255),
    blockchain_contract_id VARCHAR(255),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_uid INTEGER REFERENCES res_users(id),
    write_uid INTEGER REFERENCES res_users(id),
    verificator_uid INTEGER REFERENCES res_users(id),
    verification_date TIMESTAMP,
    submission_date TIMESTAMP,
    active BOOLEAN DEFAULT true
);

-- Workflow Audit Log Table
CREATE TABLE vendor_contract_management_workflow_log (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL REFERENCES vendor_contract_management_contract(id),
    from_stage VARCHAR(20),
    to_stage VARCHAR(20) NOT NULL,
    user_id INTEGER NOT NULL REFERENCES res_users(id),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    blockchain_tx_id VARCHAR(255)
);

-- API Gateway Metadata Table (for FastAPI)
CREATE TABLE vendor_contract_api_metadata (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL REFERENCES vendor_contract_management_contract(id),
    last_blockchain_sync TIMESTAMP,
    sync_status VARCHAR(20) DEFAULT 'pending' CHECK (sync_status IN ('pending', 'synced', 'failed')),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes and Constraints

```sql
-- Performance Indexes
CREATE INDEX idx_contract_workflow_stage ON vendor_contract_management_contract(workflow_stage);
CREATE INDEX idx_contract_vendor ON vendor_contract_management_contract(vendor_id);
CREATE INDEX idx_contract_dates ON vendor_contract_management_contract(contract_date, expiration_date);
CREATE INDEX idx_workflow_log_contract_date ON vendor_contract_management_workflow_log(contract_id, created_date);
CREATE INDEX idx_api_metadata_sync ON vendor_contract_api_metadata(last_blockchain_sync, sync_status);

-- Unique Constraints
CREATE UNIQUE INDEX idx_contract_blockchain_id ON vendor_contract_management_contract(blockchain_contract_id) WHERE blockchain_contract_id IS NOT NULL;

-- Composite Indexes for Common Queries
CREATE INDEX idx_contract_active_stage ON vendor_contract_management_contract(active, workflow_stage) WHERE active = true;
CREATE INDEX idx_vendor_active ON vendor_contract_management_vendor(active) WHERE active = true;
```

### Odoo Security Groups and Access Rules

```python
# Security groups (in security/groups.xml)
<record id="group_contract_creator" model="res.groups">
    <field name="name">Contract Creator</field>
    <field name="category_id" ref="base.module_category_operations"/>
</record>

<record id="group_contract_verificator" model="res.groups">
    <field name="name">Contract Verificator</field>
    <field name="category_id" ref="base.module_category_operations"/>
</record>

<record id="group_contract_viewer" model="res.groups">
    <field name="name">Contract Viewer</field>
    <field name="category_id" ref="base.module_category_operations"/>
</record>

# Access rules (in security/ir.model.access.csv)
contract_creator_access,vendor.contract.creator,model_vendor_contract_management_contract,group_contract_creator,1,1,1,0
contract_verificator_access,vendor.contract.verificator,model_vendor_contract_management_contract,group_contract_verificator,1,0,1,0
contract_viewer_access,vendor.contract.viewer,model_vendor_contract_management_contract,group_contract_viewer,1,0,0,0
```

### Record Rules for Row-Level Security

```xml
<!-- Record rule for creators to see their own contracts -->
<record id="rule_contract_creator_own" model="ir.rule">
    <field name="name">Contract: Creator can see own contracts</field>
    <field name="model_id" ref="model_vendor_contract_management_contract"/>
    <field name="domain_force">[('create_uid', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('group_contract_creator'))]"/>
</record>

<!-- Record rule for verificators to see contracts in verificator stage -->
<record id="rule_contract_verificator_stage" model="ir.rule">
    <field name="name">Contract: Verificator can see pending verification</field>
    <field name="model_id" ref="model_vendor_contract_management_contract"/>
    <field name="domain_force">[('workflow_stage', '=', 'verificator')]</field>
    <field name="groups" eval="[(4, ref('group_contract_verificator'))]"/>
</record>
```

## Migration Scripts

### Initial Data Setup

```sql
-- Create default vendor for testing
INSERT INTO vendor_contract_management_vendor (name, vendor_code, email, contact_person) 
VALUES ('Demo Vendor Inc.', 'DEMO001', 'contact@demovendor.com', 'John Demo');

-- Create demo users and assign to groups (handled by Odoo data files)
```

### Triggers for Automatic Timestamp Updates

```sql
-- Function to update write_date automatically
CREATE OR REPLACE FUNCTION update_write_date()
RETURNS TRIGGER AS $$
BEGIN
    NEW.write_date = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for automatic timestamp updates
CREATE TRIGGER tr_contract_write_date
    BEFORE UPDATE ON vendor_contract_management_contract
    FOR EACH ROW EXECUTE FUNCTION update_write_date();

CREATE TRIGGER tr_vendor_write_date
    BEFORE UPDATE ON vendor_contract_management_vendor
    FOR EACH ROW EXECUTE FUNCTION update_write_date();
```

## Data Integrity Rules

### Business Logic Constraints
- Contract numbers must follow format: VCM-YYYY-NNNN (enforced in Odoo model)
- Workflow stages can only transition in specific order: creator → verificator → submitted
- Expiration dates must be after contract dates
- Contract values must be positive numbers
- Verificator user cannot be the same as creator user

### Referential Integrity
- All contracts must have valid vendor references
- Workflow logs must reference valid contracts and users
- API metadata must reference valid contracts
- User references must exist in res_users table

### Performance Considerations
- Partition workflow_log table by month for large datasets
- Use partial indexes for active records only
- Implement database connection pooling
- Regular VACUUM and ANALYZE operations for PostgreSQL optimization