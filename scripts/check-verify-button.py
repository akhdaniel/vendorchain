#!/usr/bin/env python3
"""
Check if Verify Blockchain button is available in contracts
"""

import xmlrpc.client

# Odoo connection
url = 'http://localhost:8069'
db = 'vendorchain'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

uid = common.authenticate(db, username, password, {})

def execute(model, method, *args):
    return models.execute_kw(db, uid, password, model, method, *args)

print("Checking for Verify Blockchain functionality...\n")

# Get a contract
contracts = execute('vendor.contract', 'search', [[('blockchain_tx_id', '!=', False)]], {'limit': 1})

if contracts:
    contract_id = contracts[0]
    
    # Read contract with verification fields
    contract = execute('vendor.contract', 'read', [contract_id], {
        'fields': ['contract_id', 'blockchain_tx_id', 'blockchain_verified', 
                   'verification_status', 'last_verification_date', 'blockchain_hash']
    })[0]
    
    print(f"Contract: {contract['contract_id']}")
    print(f"Blockchain TX ID: {contract['blockchain_tx_id']}")
    print(f"Blockchain Verified: {contract.get('blockchain_verified', 'Field not found')}")
    print(f"Verification Status: {contract.get('verification_status', 'Field not found')}")
    print(f"Last Verification: {contract.get('last_verification_date', 'Field not found')}")
    print(f"Blockchain Hash: {contract.get('blockchain_hash', 'Field not found')[:20] if contract.get('blockchain_hash') else 'Field not found'}...")
    
    print("\nTrying to call action_verify_blockchain...")
    try:
        result = execute('vendor.contract', 'action_verify_blockchain', [[contract_id]])
        print("✅ action_verify_blockchain method exists and was called successfully!")
        print(f"Result: {result}")
    except Exception as e:
        print(f"❌ Error calling action_verify_blockchain: {e}")
    
    print("\nTo see the button in Odoo UI:")
    print(f"1. Go to: http://localhost:8069")
    print(f"2. Navigate to: Vendor Contracts → Contracts")
    print(f"3. Open contract: {contract['contract_id']}")
    print(f"4. Look in the header for 'Verify Blockchain' button (yellow button with shield icon)")
    print(f"   - It should appear next to 'Sync to Blockchain' button")
    print(f"   - Only visible if contract has blockchain_tx_id")
    
else:
    print("No contracts with blockchain TX ID found. Create a contract first.")
    
    # Create one
    vendors = execute('vendor.contract.vendor', 'search', [[]], {'limit': 1})
    if vendors:
        contract_data = {
            'vendor_id': vendors[0],
            'contract_type': 'service',
            'description': 'Test contract for verify button',
            'total_value': 10000,
            'expiry_date': '2025-12-31'
        }
        new_id = execute('vendor.contract', 'create', [contract_data])
        print(f"\nCreated new contract. Check it at:")
        print(f"http://localhost:8069/web#id={new_id}&model=vendor.contract&view_type=form")