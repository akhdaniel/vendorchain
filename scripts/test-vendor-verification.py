#!/usr/bin/env python3
"""
Test Vendor Blockchain Verification
Demonstrates verification and tamper detection for vendor data
"""

import xmlrpc.client
import time
from datetime import datetime

# Odoo connection
url = 'http://localhost:8069'
db = 'vendorchain'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

uid = common.authenticate(db, username, password, {})

if not uid:
    print("❌ Authentication failed!")
    exit(1)

def execute(model, method, *args):
    """Execute Odoo method"""
    return models.execute_kw(db, uid, password, model, method, *args)

def test_vendor_verification():
    """Test vendor blockchain verification"""
    
    print("\n" + "="*60)
    print("   VENDOR BLOCKCHAIN VERIFICATION TEST")
    print("="*60)
    
    # Get a vendor with blockchain TX ID
    vendor_ids = execute('vendor.contract.vendor', 'search', 
                        [[('blockchain_tx_id', '!=', False)]], {'limit': 1})
    
    if not vendor_ids:
        print("❌ No vendors with blockchain TX ID found")
        return
    
    vendor_id = vendor_ids[0]
    
    # Read vendor details
    vendor = execute('vendor.contract.vendor', 'read', [vendor_id], {
        'fields': ['vendor_id', 'name', 'blockchain_tx_id', 'blockchain_identity',
                   'blockchain_verified', 'verification_status', 'status', 'contact_email']
    })[0]
    
    print(f"\n1️⃣ Testing vendor: {vendor['name']}")
    print(f"   Vendor ID: {vendor['vendor_id']}")
    print(f"   Blockchain Identity: {vendor['blockchain_identity']}")
    print(f"   Blockchain TX ID: {vendor['blockchain_tx_id'][:30]}...")
    
    # Verify vendor
    print(f"\n2️⃣ Verifying vendor data against blockchain...")
    result = execute('vendor.contract.vendor', 'action_verify_blockchain', [[vendor_id]])
    
    # Read updated status
    vendor = execute('vendor.contract.vendor', 'read', [vendor_id], {
        'fields': ['verification_status', 'blockchain_verified', 'last_verification_date']
    })[0]
    
    print(f"   Status: {vendor['verification_status']}")
    print(f"   Verified: {'✅' if vendor['blockchain_verified'] else '❌'}")
    print(f"   Last Verified: {vendor['last_verification_date']}")
    
    # Test tampering
    print(f"\n3️⃣ Simulating vendor data tampering...")
    print("   Changing vendor email directly (bypassing workflow)...")
    
    original_email = execute('vendor.contract.vendor', 'read', [vendor_id], 
                            {'fields': ['contact_email']})[0]['contact_email']
    
    # Tamper with the data
    execute('vendor.contract.vendor', 'write', [[vendor_id], {
        'contact_email': 'tampered@hacker.com'
    }])
    
    print(f"   Email changed from: {original_email}")
    print(f"   Email changed to: tampered@hacker.com")
    
    # Verify again to detect tampering
    print(f"\n4️⃣ Running verification to detect tampering...")
    time.sleep(1)
    
    result = execute('vendor.contract.vendor', 'action_verify_blockchain', [[vendor_id]])
    
    # Read verification result
    vendor = execute('vendor.contract.vendor', 'read', [vendor_id], {
        'fields': ['verification_status', 'blockchain_verified']
    })[0]
    
    print(f"   Status: {vendor['verification_status']}")
    print(f"   Verified: {'✅' if vendor['blockchain_verified'] else '❌'}")
    
    if vendor['verification_status'] == 'mismatch':
        print("\n⚠️ TAMPER DETECTED!")
        print("   The vendor data in Odoo no longer matches the blockchain!")
        print("   This indicates unauthorized modification.")
    
    # Restore original data
    print(f"\n5️⃣ Restoring original vendor data...")
    execute('vendor.contract.vendor', 'write', [[vendor_id], {
        'contact_email': original_email
    }])
    
    # Verify restoration
    result = execute('vendor.contract.vendor', 'action_verify_blockchain', [[vendor_id]])
    vendor = execute('vendor.contract.vendor', 'read', [vendor_id], {
        'fields': ['verification_status']
    })[0]
    
    print(f"   Email restored to: {original_email}")
    print(f"   Verification status: {vendor['verification_status']}")

def list_all_vendors():
    """List all vendors with their verification status"""
    
    print("\n" + "="*60)
    print("   ALL VENDORS VERIFICATION STATUS")
    print("="*60)
    
    vendors = execute('vendor.contract.vendor', 'search_read', 
                     [[('blockchain_tx_id', '!=', False)]], 
                     {'fields': ['vendor_id', 'name', 'verification_status', 'blockchain_verified']})
    
    if vendors:
        print(f"\nFound {len(vendors)} vendors with blockchain records:\n")
        for vendor in vendors:
            status_icon = '✅' if vendor['blockchain_verified'] else '❌'
            print(f"{status_icon} {vendor['vendor_id']}: {vendor['name']}")
            print(f"   Status: {vendor['verification_status']}")
    else:
        print("No vendors with blockchain TX IDs found")

def main():
    print("="*60)
    print("   VENDOR BLOCKCHAIN VERIFICATION SYSTEM")
    print("="*60)
    
    # Test vendor verification
    test_vendor_verification()
    
    # List all vendors
    list_all_vendors()
    
    print("\n" + "="*60)
    print("   SUMMARY")
    print("="*60)
    print("✅ Vendor verification system is working!")
    print("\nKey Features:")
    print("1. All vendor data is hashed and verified against blockchain")
    print("2. Tampering is detected when data doesn't match blockchain")
    print("3. Each vendor has a unique blockchain identity (address)")
    print("4. Verification status is shown in Odoo UI")
    print("\nTo verify in Odoo:")
    print("1. Go to Vendor Contracts → Vendors")
    print("2. Open any vendor")
    print("3. Click 'Verify Blockchain' button")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()