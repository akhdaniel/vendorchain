#!/usr/bin/env python3
"""
Test Vendor Blockchain Identity and Transaction ID
"""

import xmlrpc.client
from datetime import datetime
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

def create_vendor_with_blockchain(uid, models):
    """Create a vendor and check blockchain fields"""
    vendor_id_str = f"VENDOR-BC-{int(datetime.now().timestamp())}"
    
    print(f"\n📝 Creating vendor: {vendor_id_str}")
    
    vendor_data = {
        'vendor_id': vendor_id_str,
        'name': 'Blockchain Test Vendor Corp.',
        'contact_email': 'blockchain@vendor.com',
        'contact_phone': '555-0500',
        'address': '999 Blockchain Plaza, Crypto City',
        'registration_number': 'REG-BC-2025',
        'vendor_type': 'service_provider',
        'status': 'active'
    }
    
    vendor_id = models.execute_kw(
        db, uid, password,
        'vendor.contract.vendor', 'create',
        [vendor_data]
    )
    
    print(f"✅ Vendor created with ID: {vendor_id}")
    
    # Read back the vendor to check blockchain fields
    vendor = models.execute_kw(
        db, uid, password,
        'vendor.contract.vendor', 'read',
        [[vendor_id], ['vendor_id', 'name', 'blockchain_identity', 'blockchain_tx_id', 'blockchain_synced']]
    )[0]
    
    return vendor

def display_vendor_blockchain_info(vendor):
    """Display vendor blockchain information"""
    print("\n🔗 Blockchain Information:")
    print("=" * 60)
    
    # Vendor basic info
    print(f"Vendor ID:          {vendor['vendor_id']}")
    print(f"Vendor Name:        {vendor['name']}")
    print()
    
    # Blockchain fields
    blockchain_identity = vendor.get('blockchain_identity')
    blockchain_tx_id = vendor.get('blockchain_tx_id')
    blockchain_synced = vendor.get('blockchain_synced')
    
    print("📊 Blockchain Fields:")
    print("-" * 40)
    
    # Blockchain Identity (Address)
    if blockchain_identity:
        print(f"✅ Blockchain Identity: {blockchain_identity}")
        print(f"   (Vendor's unique address on the blockchain)")
    else:
        print("❌ Blockchain Identity: Not generated")
    
    # Transaction ID
    if blockchain_tx_id:
        print(f"✅ Transaction ID:      {blockchain_tx_id[:30]}...")
        print(f"   (Registration transaction on blockchain)")
    else:
        print("❌ Transaction ID:      Not generated")
    
    # Sync Status
    print(f"✅ Synced to Blockchain: {blockchain_synced}")
    
    return blockchain_identity, blockchain_tx_id

def test_manual_sync(uid, models, vendor_id):
    """Test manual blockchain sync"""
    print("\n🔄 Testing Manual Blockchain Sync...")
    
    try:
        # Trigger manual sync
        models.execute_kw(
            db, uid, password,
            'vendor.contract.vendor', 'action_sync_blockchain',
            [[vendor_id]]
        )
        print("✅ Manual sync triggered")
        
        # Read vendor again to check updated fields
        vendor = models.execute_kw(
            db, uid, password,
            'vendor.contract.vendor', 'read',
            [[vendor_id], ['blockchain_identity', 'blockchain_tx_id', 'blockchain_synced']]
        )[0]
        
        print("\n📊 After Manual Sync:")
        print(f"   Blockchain Identity: {vendor.get('blockchain_identity', 'None')}")
        print(f"   Transaction ID:      {vendor.get('blockchain_tx_id', 'None')[:30] if vendor.get('blockchain_tx_id') else 'None'}...")
        print(f"   Synced:             {vendor.get('blockchain_synced', False)}")
        
        return vendor
        
    except Exception as e:
        print(f"⚠️  Manual sync error: {e}")
        return None

def explain_blockchain_fields():
    """Explain the difference between blockchain fields"""
    print("\n" + "=" * 60)
    print("📚 Understanding Blockchain Fields")
    print("=" * 60)
    print()
    print("1️⃣  **Blockchain Identity** (Address)")
    print("   • What: Vendor's unique address/identifier on blockchain")
    print("   • Format: 0x + 40 hex characters (like Ethereum address)")
    print("   • Purpose: Permanent identity for all transactions")
    print("   • Example: 0xa5b4c3d2e1f0...")
    print()
    print("2️⃣  **Blockchain Transaction ID**")
    print("   • What: Specific transaction hash for registration")
    print("   • Format: 0x + 64 hex characters")
    print("   • Purpose: Proof of vendor registration on blockchain")
    print("   • Example: 0x7f8e9d6c5b4a3...")
    print()
    print("📌 Key Difference:")
    print("   • Identity = WHO (vendor's address)")
    print("   • TX ID = WHAT (registration transaction)")
    print()

def main():
    """Main test function"""
    print("=" * 60)
    print("   Vendor Blockchain Fields Test")
    print("=" * 60)
    
    # Connect to Odoo
    uid, models = connect_odoo()
    
    # Create vendor
    vendor = create_vendor_with_blockchain(uid, models)
    vendor_id = vendor['id']
    
    # Display initial blockchain info
    blockchain_identity, blockchain_tx_id = display_vendor_blockchain_info(vendor)
    
    # If fields are empty, try manual sync
    if not blockchain_identity or not blockchain_tx_id:
        print("\n⚠️  Some blockchain fields are empty, triggering sync...")
        updated_vendor = test_manual_sync(uid, models, vendor_id)
        if updated_vendor:
            display_vendor_blockchain_info(updated_vendor)
    
    # Explain the fields
    explain_blockchain_fields()
    
    print("=" * 60)
    print("✅ Vendor Blockchain Test Complete!")
    print("=" * 60)
    print()
    print("To verify in Odoo UI:")
    print("1. Login at http://localhost:8069")
    print("2. Go to Vendor Contracts → Vendors → All Vendors")
    print(f"3. Open vendor: {vendor['vendor_id']}")
    print("4. Check the 'Blockchain Information' section")
    print("   • Blockchain Identity (vendor address)")
    print("   • Blockchain Transaction ID (registration TX)")
    print("   • Synced to Blockchain checkbox")
    print()

if __name__ == "__main__":
    main()