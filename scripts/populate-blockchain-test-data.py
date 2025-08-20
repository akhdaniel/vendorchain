#!/usr/bin/env python3
"""
Populate CouchDB with test blockchain data for verification testing
This simulates what would normally be written by Hyperledger Fabric
"""

import requests
import json
import xmlrpc.client
from datetime import datetime

# CouchDB configuration
COUCH_URL = "http://localhost:5984"
COUCH_USER = "admin"
COUCH_PASSWORD = "adminpw"
DB_NAME = "vendorchannel_contracts"  # Simulated channel database

# Odoo configuration
ODOO_URL = 'http://localhost:8069'
ODOO_DB = 'vendorchain'
ODOO_USER = 'admin'
ODOO_PASSWORD = 'admin'

def setup_couchdb():
    """Create database if it doesn't exist"""
    auth = (COUCH_USER, COUCH_PASSWORD)
    
    # Check if database exists
    response = requests.get(f"{COUCH_URL}/{DB_NAME}", auth=auth)
    
    if response.status_code == 404:
        # Create database
        print(f"Creating database: {DB_NAME}")
        response = requests.put(f"{COUCH_URL}/{DB_NAME}", auth=auth)
        if response.status_code in [201, 202]:
            print(f"✅ Database {DB_NAME} created successfully")
        else:
            print(f"❌ Failed to create database: {response.text}")
            return False
    else:
        print(f"✅ Database {DB_NAME} already exists")
    
    return True

def get_contracts_from_odoo():
    """Get all contracts from Odoo that have blockchain TX IDs"""
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    
    if not uid:
        print("❌ Failed to authenticate with Odoo")
        return []
    
    # Search for contracts with blockchain TX IDs
    contract_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'vendor.contract', 'search',
        [[('blockchain_tx_id', '!=', False)]]
    )
    
    if not contract_ids:
        print("No contracts with blockchain TX IDs found")
        return []
    
    # Read contract details with vendor information
    contracts = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'vendor.contract', 'read',
        [contract_ids],
        {'fields': ['contract_id', 'blockchain_tx_id', 'vendor_id', 'contract_type', 
                   'description', 'total_value', 'expiry_date', 'state', 'vendor_name']}
    )
    
    # Get vendor details for proper vendor_id
    for contract in contracts:
        if contract['vendor_id']:
            vendor = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'vendor.contract.vendor', 'read',
                [contract['vendor_id'][0]],
                {'fields': ['vendor_id']}
            )[0]
            contract['vendor_vendor_id'] = vendor['vendor_id']  # Store the actual vendor_id field
    
    return contracts

def populate_blockchain_data(contracts):
    """Populate CouchDB with contract data to simulate blockchain"""
    auth = (COUCH_USER, COUCH_PASSWORD)
    
    for contract in contracts:
        # Prepare blockchain document (simulating chaincode data structure)
        blockchain_doc = {
            "_id": contract['blockchain_tx_id'],  # Use TX ID as document ID
            "docType": "contract",
            "contract_id": contract['contract_id'],
            "vendor_id": contract.get('vendor_vendor_id', ''),  # Use the actual vendor_id field
            "vendor_name": contract['vendor_name'],
            "contract_type": contract['contract_type'],
            "description": contract['description'],
            "total_value": float(contract['total_value']),
            "expiry_date": contract['expiry_date'],
            "state": contract['state'],
            "blockchain_tx_id": contract['blockchain_tx_id'],
            "timestamp": datetime.now().isoformat(),
            "chaincode_version": "1.0",
            "channel": "vendorchannel",
            "verified": True
        }
        
        # Check if document already exists
        check_response = requests.get(
            f"{COUCH_URL}/{DB_NAME}/{contract['blockchain_tx_id']}", 
            auth=auth
        )
        
        if check_response.status_code == 200:
            # Update existing document
            existing_doc = check_response.json()
            blockchain_doc['_rev'] = existing_doc['_rev']
            print(f"Updating existing blockchain record for {contract['contract_id']}")
        else:
            print(f"Creating new blockchain record for {contract['contract_id']}")
        
        # Save to CouchDB
        response = requests.put(
            f"{COUCH_URL}/{DB_NAME}/{contract['blockchain_tx_id']}",
            auth=auth,
            json=blockchain_doc,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [201, 202]:
            print(f"✅ Successfully saved {contract['contract_id']} to blockchain")
        else:
            print(f"❌ Failed to save {contract['contract_id']}: {response.text}")

def verify_populated_data():
    """Verify that data can be retrieved"""
    auth = (COUCH_USER, COUCH_PASSWORD)
    
    # Get all documents
    response = requests.get(
        f"{COUCH_URL}/{DB_NAME}/_all_docs?include_docs=true",
        auth=auth
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📊 Blockchain Database Summary:")
        print(f"   Total documents: {data['total_rows']}")
        
        if data['rows']:
            print("\n   Contracts in blockchain:")
            for row in data['rows']:
                doc = row['doc']
                print(f"   - {doc.get('contract_id', 'Unknown')} | TX: {doc.get('_id', '')[:20]}... | Value: ${doc.get('total_value', 0):,.2f}")
    
    return response.status_code == 200

def test_verification(contract_id):
    """Test that Odoo can now verify against blockchain"""
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    
    if not uid:
        return
    
    # Find contract by contract_id
    contract_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'vendor.contract', 'search',
        [[('contract_id', '=', contract_id)]]
    )
    
    if contract_ids:
        # Call verification
        result = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'vendor.contract', 'action_verify_blockchain',
            [contract_ids]
        )
        
        # Read verification status
        contract = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'vendor.contract', 'read',
            [contract_ids[0]],
            {'fields': ['verification_status', 'blockchain_verified']}
        )[0]
        
        print(f"\n🔍 Verification Test for {contract_id}:")
        print(f"   Status: {contract['verification_status']}")
        print(f"   Verified: {'✅' if contract['blockchain_verified'] else '❌'}")

def main():
    print("="*60)
    print("  POPULATE BLOCKCHAIN TEST DATA")
    print("="*60)
    
    # Step 1: Setup CouchDB
    print("\n1️⃣ Setting up CouchDB...")
    if not setup_couchdb():
        return
    
    # Step 2: Get contracts from Odoo
    print("\n2️⃣ Getting contracts from Odoo...")
    contracts = get_contracts_from_odoo()
    
    if not contracts:
        print("❌ No contracts found to populate")
        return
    
    print(f"✅ Found {len(contracts)} contracts with blockchain TX IDs")
    
    # Step 3: Populate blockchain data
    print(f"\n3️⃣ Populating blockchain data in CouchDB...")
    populate_blockchain_data(contracts)
    
    # Step 4: Verify data was saved
    print(f"\n4️⃣ Verifying blockchain data...")
    if verify_populated_data():
        print("✅ Blockchain data successfully populated!")
    
    # Step 5: Test verification
    if contracts:
        print(f"\n5️⃣ Testing verification...")
        test_verification(contracts[0]['contract_id'])
    
    print("\n" + "="*60)
    print("✅ Setup complete! Now you can:")
    print("1. Go to Odoo and click 'Verify Blockchain' on any contract")
    print("2. The verification should now show '✅ Verified' instead of 'Pending'")
    print("3. Try the tamper detection demo: python3 scripts/test-tamper-detection.py")
    print("="*60)

if __name__ == "__main__":
    main()