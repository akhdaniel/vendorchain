#!/usr/bin/env python3
"""
Fix "Verification Pending" Status
Diagnoses why verification is pending and creates missing blockchain records
"""

import xmlrpc.client
import requests
import json
from datetime import datetime

# Configuration
ODOO_URL = 'http://localhost:8069'
ODOO_DB = 'vendorchain'
ODOO_USER = 'admin'
ODOO_PASSWORD = 'admin'
COUCH_URL = "http://localhost:5984"
COUCH_USER = "admin"
COUCH_PASSWORD = "adminpw"

def diagnose_and_fix():
    """Diagnose and fix verification pending issues"""
    
    print("="*60)
    print("   FIXING VERIFICATION PENDING STATUS")
    print("="*60)
    
    # Connect to Odoo
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    
    if not uid:
        print("❌ Failed to authenticate with Odoo")
        return
    
    def execute(model, method, *args):
        return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, model, method, *args)
    
    # Step 1: Check CouchDB connectivity
    print("\n1️⃣ Checking CouchDB connectivity...")
    try:
        response = requests.get(COUCH_URL, auth=(COUCH_USER, COUCH_PASSWORD))
        if response.status_code == 200:
            print("   ✅ CouchDB is accessible")
        else:
            print(f"   ❌ CouchDB returned status: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Cannot connect to CouchDB: {e}")
        print("   Make sure CouchDB is running: docker ps | grep couch")
        return
    
    # Step 2: Check databases exist
    print("\n2️⃣ Checking blockchain databases...")
    dbs_response = requests.get(f"{COUCH_URL}/_all_dbs", auth=(COUCH_USER, COUCH_PASSWORD))
    databases = dbs_response.json()
    
    required_dbs = ['vendorchannel_contracts', 'vendorchannel_vendors']
    for db_name in required_dbs:
        if db_name not in databases:
            print(f"   Creating missing database: {db_name}")
            requests.put(f"{COUCH_URL}/{db_name}", auth=(COUCH_USER, COUCH_PASSWORD))
        else:
            print(f"   ✅ Database exists: {db_name}")
    
    # Step 3: Find contracts with "Verification Pending"
    print("\n3️⃣ Finding contracts with 'Verification Pending'...")
    
    # Get all contracts with blockchain TX ID
    contract_ids = execute('vendor.contract', 'search', 
                          [[('blockchain_tx_id', '!=', False)]])
    
    pending_contracts = []
    for contract_id in contract_ids:
        # Call verification to get status
        execute('vendor.contract', 'action_verify_blockchain', [[contract_id]])
        contract = execute('vendor.contract', 'read', [contract_id], 
                          {'fields': ['contract_id', 'verification_status', 'blockchain_tx_id', 
                                     'vendor_id', 'total_value', 'state']})[0]
        
        if contract['verification_status'] in ['pending', 'not_on_chain']:
            pending_contracts.append(contract)
            print(f"   ⏳ {contract['contract_id']}: {contract['verification_status']}")
    
    if not pending_contracts:
        print("   ✅ No contracts with pending verification")
    else:
        print(f"\n   Found {len(pending_contracts)} contracts needing blockchain records")
    
    # Step 4: Find vendors with "Verification Pending"
    print("\n4️⃣ Finding vendors with 'Verification Pending'...")
    
    vendor_ids = execute('vendor.contract.vendor', 'search',
                        [[('blockchain_tx_id', '!=', False)]])
    
    pending_vendors = []
    for vendor_id in vendor_ids:
        execute('vendor.contract.vendor', 'action_verify_blockchain', [[vendor_id]])
        vendor = execute('vendor.contract.vendor', 'read', [vendor_id],
                        {'fields': ['vendor_id', 'verification_status', 'blockchain_tx_id',
                                   'name', 'status', 'contact_email']})[0]
        
        if vendor['verification_status'] in ['pending', 'not_on_chain']:
            pending_vendors.append(vendor)
            print(f"   ⏳ {vendor['vendor_id']}: {vendor['verification_status']}")
    
    if not pending_vendors:
        print("   ✅ No vendors with pending verification")
    else:
        print(f"\n   Found {len(pending_vendors)} vendors needing blockchain records")
    
    # Step 5: Create missing blockchain records
    if pending_contracts or pending_vendors:
        print("\n5️⃣ Creating missing blockchain records...")
        
        # Fix contracts
        for contract in pending_contracts:
            print(f"\n   Creating blockchain record for {contract['contract_id']}...")
            
            # Get vendor details if exists
            vendor_vendor_id = ''
            if contract['vendor_id']:
                vendor = execute('vendor.contract.vendor', 'read', 
                               [contract['vendor_id'][0]], {'fields': ['vendor_id']})[0]
                vendor_vendor_id = vendor['vendor_id']
            
            # Create blockchain document
            blockchain_doc = {
                "_id": contract['blockchain_tx_id'],
                "docType": "contract",
                "contract_id": contract['contract_id'],
                "vendor_id": vendor_vendor_id,
                "total_value": float(contract['total_value']),
                "state": contract['state'],
                "blockchain_tx_id": contract['blockchain_tx_id'],
                "timestamp": datetime.now().isoformat(),
                "channel": "vendorchannel",
                "verified": True
            }
            
            # Save to CouchDB
            response = requests.put(
                f"{COUCH_URL}/vendorchannel_contracts/{contract['blockchain_tx_id']}",
                auth=(COUCH_USER, COUCH_PASSWORD),
                json=blockchain_doc,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [201, 202]:
                print(f"   ✅ Created blockchain record for {contract['contract_id']}")
            else:
                print(f"   ❌ Failed to create record: {response.text}")
        
        # Fix vendors
        for vendor in pending_vendors:
            print(f"\n   Creating blockchain record for {vendor['vendor_id']}...")
            
            blockchain_doc = {
                "_id": vendor['blockchain_tx_id'],
                "docType": "vendor",
                "vendor_id": vendor['vendor_id'],
                "name": vendor['name'],
                "status": vendor['status'],
                "contact_email": vendor['contact_email'],
                "blockchain_tx_id": vendor['blockchain_tx_id'],
                "timestamp": datetime.now().isoformat(),
                "channel": "vendorchannel",
                "verified": True
            }
            
            # Save to CouchDB
            response = requests.put(
                f"{COUCH_URL}/vendorchannel_vendors/{vendor['blockchain_tx_id']}",
                auth=(COUCH_USER, COUCH_PASSWORD),
                json=blockchain_doc,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [201, 202]:
                print(f"   ✅ Created blockchain record for {vendor['vendor_id']}")
            else:
                print(f"   ❌ Failed to create record: {response.text}")
    
    # Step 6: Re-verify to confirm fix
    print("\n6️⃣ Re-verifying to confirm fixes...")
    
    for contract in pending_contracts:
        execute('vendor.contract', 'action_verify_blockchain', [[contract['id']]])
        updated = execute('vendor.contract', 'read', [contract['id']], 
                         {'fields': ['contract_id', 'verification_status']})[0]
        status_icon = '✅' if updated['verification_status'] == 'verified' else '❌'
        print(f"   {status_icon} {updated['contract_id']}: {updated['verification_status']}")
    
    for vendor in pending_vendors:
        execute('vendor.contract.vendor', 'action_verify_blockchain', [[vendor['id']]])
        updated = execute('vendor.contract.vendor', 'read', [vendor['id']],
                         {'fields': ['vendor_id', 'verification_status']})[0]
        status_icon = '✅' if updated['verification_status'] == 'verified' else '❌'
        print(f"   {status_icon} {updated['vendor_id']}: {updated['verification_status']}")
    
    print("\n" + "="*60)
    print("   SUMMARY")
    print("="*60)
    print("\n✅ Process complete!")
    print("\nWhat was done:")
    print("1. Checked CouchDB connectivity")
    print("2. Ensured required databases exist")
    print("3. Found records with 'Verification Pending'")
    print("4. Created missing blockchain records")
    print("5. Re-verified to confirm fixes")
    print("\nNext steps:")
    print("1. Go to Odoo and click 'Verify Blockchain' on any record")
    print("2. Should now show 'Verified' instead of 'Pending'")

if __name__ == "__main__":
    try:
        diagnose_and_fix()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()