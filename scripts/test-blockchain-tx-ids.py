#!/usr/bin/env python3
"""
Test Blockchain Transaction ID Generation
"""

import xmlrpc.client
from datetime import datetime, date
import sys

# Odoo connection parameters
url = 'http://localhost:8069'
db = 'vendorchain'
username = 'admin'
password = 'admin'

def connect_odoo():
    """Connect to Odoo via XML-RPC"""
    try:
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})
        
        if not uid:
            print("❌ Failed to authenticate with Odoo")
            sys.exit(1)
            
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        print(f"✅ Connected to Odoo (uid: {uid})")
        return uid, models
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)

def create_test_contract_with_workflow(uid, models):
    """Create a test contract and process through workflow"""
    # Create vendor
    vendor_id_str = f"VENDOR-TX-{int(datetime.now().timestamp())}"
    vendor_data = {
        'vendor_id': vendor_id_str,
        'name': 'Blockchain TX Test Vendor',
        'contact_email': 'tx@test.com',
        'contact_phone': '555-0400',
        'address': '123 Blockchain Ave',
        'registration_number': 'REG-TX-789',
        'vendor_type': 'service_provider',
        'status': 'active'
    }
    
    vendor_id = models.execute_kw(
        db, uid, password,
        'vendor.contract.vendor', 'create',
        [vendor_data]
    )
    print(f"✅ Created vendor: {vendor_id_str}")
    
    # Create contract
    contract_id_str = f"CONTRACT-TX-{int(datetime.now().timestamp())}"
    contract_data = {
        'contract_id': contract_id_str,
        'vendor_id': vendor_id,
        'vendor_name': vendor_id_str,
        'contract_type': 'service',
        'description': 'Test contract for blockchain TX IDs',
        'total_value': 150000.00,
        'expiry_date': '2025-12-31',
        'state': 'created'
    }
    
    contract_id = models.execute_kw(
        db, uid, password,
        'vendor.contract', 'create',
        [contract_data]
    )
    print(f"✅ Created contract: {contract_id_str}")
    
    # Process through workflow to generate TX IDs
    print("\n🔄 Processing Contract Workflow...")
    
    # Verify the contract
    try:
        models.execute_kw(
            db, uid, password,
            'vendor.contract', 'write',
            [[contract_id], {'state': 'verified', 'verified_by': uid}]
        )
        
        # Trigger blockchain sync
        models.execute_kw(
            db, uid, password,
            'vendor.contract', 'action_sync_blockchain',
            [[contract_id]]
        )
        print("  ✅ Contract verified")
    except Exception as e:
        print(f"  ⚠️  Verification: {e}")
    
    # Submit the contract
    try:
        models.execute_kw(
            db, uid, password,
            'vendor.contract', 'write',
            [[contract_id], {'state': 'submitted', 'submitted_by': uid}]
        )
        
        # Trigger blockchain sync
        models.execute_kw(
            db, uid, password,
            'vendor.contract', 'action_sync_blockchain',
            [[contract_id]]
        )
        print("  ✅ Contract submitted")
    except Exception as e:
        print(f"  ⚠️  Submission: {e}")
    
    return contract_id, contract_id_str

def create_payments_with_tx_ids(uid, models, contract_id):
    """Create payments and check transaction IDs"""
    print("\n💰 Recording Payments with TX IDs...")
    
    payments = [
        {
            'contract_id': contract_id,
            'payment_amount': 30000.00,
            'payment_date': date.today().isoformat(),
            'payment_reference': 'TX-CHECK-001',
            'payment_method': 'check',
            'notes': 'Payment with blockchain TX'
        },
        {
            'contract_id': contract_id,
            'payment_amount': 45000.00,
            'payment_date': date.today().isoformat(),
            'payment_reference': 'TX-WIRE-002',
            'payment_method': 'wire',
            'notes': 'Wire transfer with TX ID'
        }
    ]
    
    payment_ids = []
    for payment in payments:
        payment_id = models.execute_kw(
            db, uid, password,
            'vendor.contract.payment.history', 'create',
            [payment]
        )
        payment_ids.append(payment_id)
        
        # Read back the payment to check TX ID
        payment_record = models.execute_kw(
            db, uid, password,
            'vendor.contract.payment.history', 'read',
            [[payment_id], ['payment_reference', 'payment_amount', 'blockchain_tx_id']]
        )[0]
        
        tx_id = payment_record.get('blockchain_tx_id')
        if tx_id:
            print(f"  ✅ Payment {payment['payment_reference']}: TX ID = {tx_id[:20]}...")
        else:
            print(f"  ❌ Payment {payment['payment_reference']}: No TX ID")
    
    return payment_ids

def check_workflow_logs_tx_ids(uid, models, contract_id):
    """Check workflow logs for transaction IDs"""
    print("\n📋 Checking Workflow Logs TX IDs...")
    
    # Get workflow logs for the contract
    logs = models.execute_kw(
        db, uid, password,
        'vendor.contract.workflow.log', 'search_read',
        [[['contract_id', '=', contract_id]]],
        {'fields': ['action', 'from_state', 'to_state', 'blockchain_tx_id']}
    )
    
    for log in logs:
        tx_id = log.get('blockchain_tx_id')
        action = log.get('action', 'Unknown')
        if tx_id:
            print(f"  ✅ {action}: TX ID = {tx_id[:20]}...")
        else:
            print(f"  ⚠️  {action}: No TX ID")

def check_contract_tx_id(uid, models, contract_id):
    """Check contract's main transaction ID"""
    print("\n📄 Checking Contract TX ID...")
    
    contract = models.execute_kw(
        db, uid, password,
        'vendor.contract', 'read',
        [[contract_id], ['contract_id', 'blockchain_tx_id', 'blockchain_synced']]
    )[0]
    
    tx_id = contract.get('blockchain_tx_id')
    synced = contract.get('blockchain_synced')
    
    if tx_id:
        print(f"  ✅ Contract TX ID: {tx_id[:30]}...")
        print(f"  ✅ Blockchain Synced: {synced}")
    else:
        print(f"  ❌ No blockchain TX ID found")
        print(f"  ❌ Blockchain Synced: {synced}")
    
    return tx_id

def main():
    """Main test function"""
    print("=" * 60)
    print("   Blockchain Transaction ID Test")
    print("=" * 60)
    print()
    
    # Connect to Odoo
    uid, models = connect_odoo()
    
    # Create and process contract
    contract_id, contract_id_str = create_test_contract_with_workflow(uid, models)
    
    # Check contract TX ID
    contract_tx_id = check_contract_tx_id(uid, models, contract_id)
    
    # Check workflow logs TX IDs
    check_workflow_logs_tx_ids(uid, models, contract_id)
    
    # Create payments with TX IDs
    payment_ids = create_payments_with_tx_ids(uid, models, contract_id)
    
    print("\n" + "=" * 60)
    print("✅ Blockchain TX ID Test Complete!")
    print("=" * 60)
    print("\nResults:")
    print(f"• Contract: {contract_id_str}")
    print(f"• Contract has TX ID: {'Yes ✅' if contract_tx_id else 'No ❌'}")
    print(f"• Payments created: {len(payment_ids)}")
    print()
    print("To verify in Odoo:")
    print("1. Login at http://localhost:8069")
    print("2. Go to Vendor Contracts → All Contracts")
    print(f"3. Open contract: {contract_id_str}")
    print("4. Check the Blockchain Transaction ID field")
    print("5. View Payment History tab for payment TX IDs")
    print("6. View Workflow Logs tab for workflow TX IDs")
    print()

if __name__ == "__main__":
    main()