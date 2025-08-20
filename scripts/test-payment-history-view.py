#!/usr/bin/env python3
"""
Test Payment History List View Functionality
"""

import xmlrpc.client
import json
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

def create_test_contract(uid, models):
    """Create a test contract with vendor"""
    # Create vendor
    vendor_id_str = f"VENDOR-HISTORY-{int(datetime.now().timestamp())}"
    vendor_data = {
        'vendor_id': vendor_id_str,
        'name': 'Payment History Test Vendor',
        'contact_email': 'history@test.com',
        'contact_phone': '555-0300',
        'address': '789 History Lane',
        'registration_number': 'REG-HIST-456',
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
    contract_id_str = f"CONTRACT-HISTORY-{int(datetime.now().timestamp())}"
    contract_data = {
        'contract_id': contract_id_str,
        'vendor_id': vendor_id,
        'vendor_name': vendor_id_str,
        'contract_type': 'service',
        'description': 'Test contract for payment history view',
        'total_value': 250000.00,
        'expiry_date': '2025-12-31',
        'state': 'submitted'  # Set directly to submitted
    }
    
    contract_id = models.execute_kw(
        db, uid, password,
        'vendor.contract', 'create',
        [contract_data]
    )
    print(f"✅ Created contract: {contract_id_str}")
    
    return contract_id, contract_id_str

def create_payment_history_records(uid, models, contract_id):
    """Create multiple payment history records"""
    payments = [
        {
            'contract_id': contract_id,
            'payment_amount': 50000.00,
            'payment_date': '2025-01-15',
            'payment_reference': 'CHECK-001',
            'payment_method': 'check',
            'notes': 'Initial payment'
        },
        {
            'contract_id': contract_id,
            'payment_amount': 75000.00,
            'payment_date': '2025-02-15',
            'payment_reference': 'WIRE-002',
            'payment_method': 'wire',
            'notes': 'Second installment'
        },
        {
            'contract_id': contract_id,
            'payment_amount': 25000.00,
            'payment_date': '2025-03-15',
            'payment_reference': 'ACH-003',
            'payment_method': 'ach',
            'notes': 'Third payment'
        },
        {
            'contract_id': contract_id,
            'payment_amount': 100000.00,
            'payment_date': '2025-04-15',
            'payment_reference': 'CHECK-004',
            'payment_method': 'check',
            'notes': 'Final payment'
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
        print(f"✅ Created payment: {payment['payment_reference']} - ${payment['payment_amount']:,.2f}")
    
    return payment_ids

def check_contract_status(uid, models, contract_id):
    """Check contract payment status"""
    contract = models.execute_kw(
        db, uid, password,
        'vendor.contract', 'read',
        [[contract_id], ['contract_id', 'total_value', 'paid_amount', 'remaining_amount', 'payment_count', 'state']]
    )[0]
    
    print("\n📊 Contract Payment Status:")
    print(f"   Contract ID: {contract['contract_id']}")
    print(f"   Total Value: ${contract['total_value']:,.2f}")
    print(f"   Paid Amount: ${contract['paid_amount']:,.2f}")
    print(f"   Remaining: ${contract['remaining_amount']:,.2f}")
    print(f"   Payment Count: {contract['payment_count']} payments")
    
    return contract

def get_payment_history_view_action(uid, models, contract_id):
    """Get the action for viewing payment history"""
    # Execute the action_view_payments method
    action = models.execute_kw(
        db, uid, password,
        'vendor.contract', 'action_view_payments',
        [[contract_id]]
    )
    
    if action:
        print("\n✅ Payment History View Action:")
        print(f"   Action Type: {action.get('type')}")
        print(f"   Model: {action.get('res_model')}")
        print(f"   View Mode: {action.get('view_mode')}")
        print(f"   Domain: {action.get('domain')}")
        return True
    else:
        print("\n❌ Failed to get payment history view action")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("   Payment History List View Test")
    print("=" * 60)
    print()
    
    # Connect to Odoo
    uid, models = connect_odoo()
    
    # Create test contract
    contract_id, contract_id_str = create_test_contract(uid, models)
    
    # Create payment history records
    print("\n💰 Creating Payment History Records...")
    payment_ids = create_payment_history_records(uid, models, contract_id)
    
    # Check contract status
    contract = check_contract_status(uid, models, contract_id)
    
    # Test the view action
    get_payment_history_view_action(uid, models, contract_id)
    
    print("\n" + "=" * 60)
    print("✅ Payment History Test Complete!")
    print("=" * 60)
    print("\nTo verify the payment history list view:")
    print("1. Login to Odoo at http://localhost:8069")
    print("2. Navigate to Vendor Contracts → All Contracts")
    print(f"3. Open contract: {contract_id_str}")
    print("4. Click the 'Payments' button (shows count: 4)")
    print("5. You should see a list view with all 4 payments")
    print()
    print("Alternative:")
    print("1. Navigate to Vendor Contracts → Reports → Payment History")
    print("2. You should see all payment records across all contracts")
    print()

if __name__ == "__main__":
    main()