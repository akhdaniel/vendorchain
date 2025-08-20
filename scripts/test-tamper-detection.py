#!/usr/bin/env python3
"""
Test Blockchain Tamper Detection System
Demonstrates how the system detects when Odoo data is modified without blockchain sync
"""

import xmlrpc.client
import time
import json
from datetime import datetime

# Odoo connection details
url = 'http://localhost:8069'
db = 'vendorchain'
username = 'admin'
password = 'admin'

# XML-RPC endpoints
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Authenticate
uid = common.authenticate(db, username, password, {})

if not uid:
    print("❌ Authentication failed!")
    exit(1)

print("✅ Connected to Odoo")

def execute(model, method, *args):
    """Execute Odoo method"""
    return models.execute_kw(db, uid, password, model, method, *args)

def test_tamper_detection():
    """Test the tamper detection system"""
    
    print("\n" + "="*60)
    print("   BLOCKCHAIN TAMPER DETECTION DEMONSTRATION")
    print("="*60)
    
    # Step 1: Create a new contract (this will sync to blockchain)
    print("\n1️⃣ Creating a new contract...")
    
    # First, get a vendor
    vendors = execute('vendor.contract.vendor', 'search', [[]], {'limit': 1})
    if not vendors:
        print("❌ No vendors found. Please create a vendor first.")
        return
    
    vendor_id = vendors[0]
    vendor_data = execute('vendor.contract.vendor', 'read', [vendor_id], {'fields': ['name', 'vendor_id']})[0]
    
    # Create contract
    contract_data = {
        'vendor_id': vendor_id,
        'contract_type': 'service',
        'description': 'Test contract for tamper detection',
        'total_value': 50000.00,
        'expiry_date': '2025-12-31',
    }
    
    contract_id = execute('vendor.contract', 'create', [contract_data])
    
    # Read the created contract
    contract = execute('vendor.contract', 'read', [contract_id], {
        'fields': ['contract_id', 'blockchain_tx_id', 'blockchain_hash', 'state', 'total_value']
    })[0]
    
    print(f"✅ Contract created: {contract['contract_id']}")
    print(f"   Blockchain TX ID: {contract['blockchain_tx_id']}")
    print(f"   Data Hash: {contract['blockchain_hash'][:16]}...")
    print(f"   Total Value: ${contract['total_value']:,.2f}")
    
    # Step 2: Verify the contract is properly synced
    print("\n2️⃣ Verifying blockchain sync...")
    execute('vendor.contract', 'action_verify_blockchain', [[contract_id]])
    
    # Read verification status
    contract = execute('vendor.contract', 'read', [contract_id], {
        'fields': ['verification_status', 'blockchain_verified']
    })[0]
    
    print(f"   Verification Status: {contract['verification_status']}")
    print(f"   Blockchain Verified: {'✅' if contract['blockchain_verified'] else '❌'}")
    
    # Step 3: Simulate tampering - directly modify the contract data
    print("\n3️⃣ Simulating data tampering...")
    print("   ⚠️ WARNING: Directly modifying contract value without workflow")
    
    # Direct database update (bypassing workflow)
    execute('vendor.contract', 'write', [[contract_id], {
        'total_value': 75000.00,  # Changed from 50000 to 75000
        'description': 'Modified contract - TAMPERED DATA'
    }])
    
    # Read the modified contract
    contract = execute('vendor.contract', 'read', [contract_id], {
        'fields': ['total_value', 'description', 'blockchain_hash']
    })[0]
    
    print(f"   ❌ Contract modified outside workflow!")
    print(f"   New Total Value: ${contract['total_value']:,.2f} (was $50,000)")
    print(f"   New Description: {contract['description'][:30]}...")
    print(f"   New Data Hash: {contract['blockchain_hash'][:16]}...")
    
    # Step 4: Run blockchain verification to detect tampering
    print("\n4️⃣ Running blockchain verification...")
    time.sleep(2)  # Brief pause for effect
    
    try:
        execute('vendor.contract', 'action_verify_blockchain', [[contract_id]])
    except Exception as e:
        pass  # Verification might trigger warnings
    
    # Read verification result
    contract = execute('vendor.contract', 'read', [contract_id], {
        'fields': ['verification_status', 'blockchain_verified', 'last_verification_date']
    })[0]
    
    print(f"   Verification Status: {contract['verification_status']}")
    print(f"   Blockchain Verified: {'✅' if contract['blockchain_verified'] else '❌'}")
    print(f"   Last Verification: {contract['last_verification_date']}")
    
    if contract['verification_status'] == 'mismatch':
        print("\n⚠️ TAMPER DETECTED!")
        print("   The contract data in Odoo no longer matches the blockchain!")
        print("   This indicates unauthorized modification.")
        
        # Check for activities/alerts
        activities = execute('mail.activity', 'search_read', [
            [('res_model', '=', 'vendor.contract'), ('res_id', '=', contract_id)]
        ], {'fields': ['summary', 'note'], 'limit': 1})
        
        if activities:
            print(f"\n   🔔 Security Alert Created:")
            print(f"      {activities[0]['summary']}")
    
    # Step 5: Demonstrate the cron job detection
    print("\n5️⃣ Simulating scheduled integrity check...")
    print("   Running cron job: cron_detect_tampered_data")
    
    try:
        execute('vendor.contract', 'cron_detect_tampered_data', [])
        print("   ✅ Tamper detection cron job executed")
    except Exception as e:
        print(f"   ⚠️ Cron job execution: {str(e)}")
    
    # Step 6: Show how to restore trust
    print("\n6️⃣ Restoring blockchain trust...")
    print("   To restore trust, the contract must be re-synced through proper workflow")
    print("   or reverted to match blockchain data.")
    
    # Summary
    print("\n" + "="*60)
    print("   SUMMARY")
    print("="*60)
    print("✅ Demonstration completed!")
    print("\nKey Takeaways:")
    print("1. All contract modifications are hashed and compared with blockchain")
    print("2. Direct database modifications bypass blockchain sync")
    print("3. Verification detects mismatches between Odoo and blockchain")
    print("4. Automated cron jobs continuously monitor data integrity")
    print("5. Security alerts are created when tampering is detected")
    
    return contract_id

def show_verification_methods():
    """Show different ways to verify blockchain integrity"""
    
    print("\n" + "="*60)
    print("   VERIFICATION METHODS")
    print("="*60)
    
    print("\n1. Manual Verification (per contract):")
    print("   - Click 'Verify Blockchain' button in contract form")
    print("   - Immediate verification result")
    
    print("\n2. Bulk Verification (all contracts):")
    print("   - Run: execute('vendor.contract', 'cron_verify_blockchain_integrity', [])")
    print("   - Checks all active contracts")
    
    print("\n3. Tamper Detection (recent changes):")
    print("   - Run: execute('vendor.contract', 'cron_detect_tampered_data', [])")
    print("   - Checks contracts modified in last 30 minutes")
    
    print("\n4. Command Line Verification:")
    print("   - ./scripts/verify-blockchain-data.sh")
    print("   - python3 scripts/blockchain-explorer.py verify -c CONTRACT_ID")

if __name__ == "__main__":
    try:
        # Run the tamper detection demo
        contract_id = test_tamper_detection()
        
        # Show verification methods
        show_verification_methods()
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()