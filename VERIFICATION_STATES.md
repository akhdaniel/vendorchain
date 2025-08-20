# Blockchain Verification States Explained

## Overview

The blockchain verification system has four possible states that indicate the synchronization status between Odoo data and the blockchain (Hyperledger Fabric/CouchDB).

## Verification States

### 1. ✅ **Verified**
- **Meaning**: Data in Odoo perfectly matches the blockchain record
- **How to achieve**: 
  - Record exists in blockchain (CouchDB)
  - All critical fields match exactly
  - No tampering detected

### 2. ⏳ **Verification Pending**
- **Meaning**: System cannot verify because blockchain record is missing or inaccessible
- **Common causes**:
  - No corresponding record in CouchDB
  - CouchDB is not running or accessible
  - Network connectivity issues
  - Record was created in Odoo but never synced to blockchain
- **How to fix**:
  ```bash
  # Quick fix - populate blockchain data
  python3 scripts/populate-blockchain-test-data.py
  
  # Or diagnose and fix specific issues
  python3 scripts/fix-verification-pending.py
  ```

### 3. ⚠️ **Data Mismatch**
- **Meaning**: Record exists in blockchain but data doesn't match
- **Common causes**:
  - Data was modified directly in database (bypassing Odoo workflow)
  - Manual edits that didn't trigger blockchain sync
  - Tampering or unauthorized modifications
- **How to fix**:
  - Investigate what changed and why
  - Either restore original data or re-sync through proper workflow
  - Review audit logs for unauthorized access

### 4. ❌ **Not on Blockchain**
- **Meaning**: Record has no blockchain transaction ID
- **Common causes**:
  - Record created before blockchain integration
  - Blockchain sync failed during creation
  - Manual record creation bypassing normal process
- **How to fix**:
  - Click "Sync to Blockchain" button to generate blockchain TX ID
  - Then run populate script to create blockchain record

## State Transition Flow

```mermaid
graph TD
    A[New Record Created] --> B[Generate Blockchain TX ID]
    B --> C[Sync to Blockchain]
    C --> D{Sync Successful?}
    D -->|Yes| E[Status: Verified ✅]
    D -->|No| F[Status: Pending ⏳]
    
    E --> G[User Modifies Data]
    G --> H{Through Workflow?}
    H -->|Yes| I[Re-sync to Blockchain]
    I --> E
    H -->|No| J[Status: Mismatch ⚠️]
    
    F --> K[Run Fix Script]
    K --> L[Create Blockchain Record]
    L --> E
    
    J --> M[Investigate Tampering]
    M --> N[Restore Original or Re-sync]
    N --> E
```

## Actions Required for Each State

### From "Verification Pending" → "Verified"

**Option 1: Run Populate Script (Recommended)**
```bash
python3 scripts/populate-blockchain-test-data.py
```
This creates blockchain records for all contracts and vendors.

**Option 2: Fix Specific Records**
```bash
python3 scripts/fix-verification-pending.py
```
This diagnoses issues and creates missing records only.

**Option 3: Manual Process**
1. Ensure CouchDB is running: `docker ps | grep couch`
2. Check if databases exist in CouchDB
3. Create missing blockchain records
4. Click "Verify Blockchain" again

### From "Data Mismatch" → "Verified"

**Option 1: Restore Original Data**
- Identify what fields changed
- Restore to match blockchain
- Verify again

**Option 2: Accept Changes and Re-sync**
- Use proper workflow to update
- Click "Sync to Blockchain"
- This creates new blockchain record

### From "Not on Blockchain" → "Verified"

1. Click "Sync to Blockchain" button
2. Run populate script
3. Verify blockchain sync

## Verification Process Details

### What Gets Verified

**For Contracts:**
- Contract ID
- Vendor ID
- Total Value
- Contract Type
- State
- Description

**For Vendors:**
- Vendor ID
- Name
- Status
- Contact Email
- Vendor Type
- Registration Number

### When Verification Happens

1. **Manual**: Click "Verify Blockchain" button
2. **Automatic**: Scheduled cron jobs (hourly)
3. **On-demand**: Via API or scripts

### How Verification Works

1. **Compute Hash**: System creates hash of current Odoo data
2. **Query Blockchain**: Search CouchDB for matching record
3. **Compare Data**: Check if critical fields match
4. **Update Status**: Set appropriate verification state
5. **Create Alerts**: If mismatch detected, create security alerts

## Troubleshooting

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| All records show "Pending" | CouchDB not accessible | Check Docker containers, ensure CouchDB is running |
| Specific record shows "Pending" | Missing blockchain record | Run populate script for that record |
| "Mismatch" after legitimate change | Change bypassed sync | Re-sync through proper workflow |
| Cannot connect to CouchDB | Network/Docker issue | Restart Docker containers |
| Verification takes long time | Large number of records | Be patient or verify in batches |

### Debug Commands

```bash
# Check if CouchDB is running
docker ps | grep couch

# View CouchDB databases
curl http://admin:adminpw@localhost:5984/_all_dbs

# Check specific contract in blockchain
curl http://admin:adminpw@localhost:5984/vendorchannel_contracts/_all_docs

# View Odoo logs for verification errors
docker logs vendorchain-odoo | grep verification

# Test verification for specific contract
python3 -c "
import xmlrpc.client
# ... (verification test code)
"
```

## Best Practices

1. **Always use workflow**: Make changes through Odoo UI, not direct database
2. **Regular verification**: Run verification periodically
3. **Monitor alerts**: Check for security alerts on mismatches
4. **Maintain sync**: Ensure blockchain sync after important changes
5. **Backup before fixes**: Always backup before running fix scripts

## Security Implications

- **"Verified"** = Data integrity confirmed, safe to trust
- **"Pending"** = Cannot confirm integrity, investigate why
- **"Mismatch"** = Potential tampering, immediate investigation required
- **"Not on Chain"** = No audit trail, sync required for compliance

## Automation

### Scheduled Jobs

The system runs automatic verification:
- **Hourly**: Full verification of all records
- **Every 30 min**: Check recently modified records
- **Daily**: Expire old contracts

### API Endpoints

```python
# Verify contract via API
POST /api/v1/contracts/{contract_id}/verify

# Verify vendor via API  
POST /api/v1/vendors/{vendor_id}/verify
```

## Summary

The verification system ensures data integrity by:
1. Creating immutable blockchain records
2. Detecting unauthorized modifications
3. Providing clear status indicators
4. Offering tools to fix issues

To maintain "Verified" status:
- Always use proper workflows
- Run populate script after bulk imports
- Monitor and investigate mismatches
- Keep CouchDB/blockchain infrastructure running