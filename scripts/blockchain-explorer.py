#!/usr/bin/env python3
"""
Blockchain Data Explorer for VendorChain
Comprehensive tool to explore and verify blockchain data
"""

import json
import requests
import sys
from datetime import datetime
from typing import Dict, List, Optional
import argparse
from tabulate import tabulate

# Configuration
COUCHDB_URL = "http://localhost:5984"
COUCHDB_USER = "admin"
COUCHDB_PASSWORD = "adminpw"
API_URL = "http://localhost:8000/api/v1"
ODOO_URL = "http://localhost:8069"

class BlockchainExplorer:
    def __init__(self):
        self.couchdb_auth = (COUCHDB_USER, COUCHDB_PASSWORD)
        self.session = requests.Session()
        
    def get_couchdb_databases(self) -> List[str]:
        """Get all CouchDB databases"""
        try:
            response = requests.get(f"{COUCHDB_URL}/_all_dbs", auth=self.couchdb_auth)
            if response.status_code == 200:
                dbs = response.json()
                # Filter for blockchain-related databases
                return [db for db in dbs if 'channel' in db or 'vendor' in db or 'contract' in db]
            return []
        except Exception as e:
            print(f"Error accessing CouchDB: {e}")
            return []
    
    def search_contract_in_couchdb(self, contract_id: str) -> Optional[Dict]:
        """Search for a contract in CouchDB"""
        databases = self.get_couchdb_databases()
        
        for db in databases:
            try:
                # Search using Mango query
                query = {
                    "selector": {
                        "$or": [
                            {"contract_id": contract_id},
                            {"contractId": contract_id},
                            {"id": contract_id}
                        ]
                    }
                }
                
                response = requests.post(
                    f"{COUCHDB_URL}/{db}/_find",
                    json=query,
                    auth=self.couchdb_auth,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    docs = response.json().get('docs', [])
                    if docs:
                        return {
                            'database': db,
                            'document': docs[0],
                            'found': True
                        }
            except Exception as e:
                continue
        
        return None
    
    def get_transaction_details(self, tx_id: str) -> Optional[Dict]:
        """Get transaction details by ID"""
        databases = self.get_couchdb_databases()
        
        for db in databases:
            try:
                query = {
                    "selector": {
                        "$or": [
                            {"blockchain_tx_id": tx_id},
                            {"transactionId": tx_id},
                            {"tx_id": tx_id}
                        ]
                    }
                }
                
                response = requests.post(
                    f"{COUCHDB_URL}/{db}/_find",
                    json=query,
                    auth=self.couchdb_auth,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    docs = response.json().get('docs', [])
                    if docs:
                        return {
                            'database': db,
                            'transaction': docs[0],
                            'found': True
                        }
            except Exception as e:
                continue
        
        return None
    
    def get_blockchain_statistics(self) -> Dict:
        """Get blockchain statistics"""
        stats = {
            'databases': [],
            'total_documents': 0,
            'contracts': 0,
            'vendors': 0,
            'transactions': 0
        }
        
        databases = self.get_couchdb_databases()
        
        for db in databases:
            try:
                response = requests.get(f"{COUCHDB_URL}/{db}", auth=self.couchdb_auth)
                if response.status_code == 200:
                    db_info = response.json()
                    doc_count = db_info.get('doc_count', 0)
                    
                    stats['databases'].append({
                        'name': db,
                        'documents': doc_count,
                        'size': db_info.get('data_size', 0)
                    })
                    stats['total_documents'] += doc_count
                    
                    # Count specific types
                    if 'contract' in db:
                        stats['contracts'] += doc_count
                    elif 'vendor' in db:
                        stats['vendors'] += doc_count
            except Exception as e:
                continue
        
        return stats
    
    def verify_contract_blockchain_sync(self, contract_id: str) -> Dict:
        """Verify if a contract is properly synced to blockchain"""
        result = {
            'contract_id': contract_id,
            'in_api': False,
            'in_blockchain': False,
            'tx_id': None,
            'sync_status': 'Not Found'
        }
        
        # Check API
        try:
            api_response = requests.get(f"{API_URL}/contracts/{contract_id}")
            if api_response.status_code == 200:
                api_data = api_response.json().get('data', {})
                result['in_api'] = True
                result['tx_id'] = api_data.get('blockchain_tx_id')
        except Exception as e:
            pass
        
        # Check Blockchain (CouchDB)
        blockchain_data = self.search_contract_in_couchdb(contract_id)
        if blockchain_data:
            result['in_blockchain'] = True
            result['blockchain_data'] = blockchain_data
        
        # Determine sync status
        if result['in_api'] and result['in_blockchain']:
            result['sync_status'] = '✅ Fully Synced'
        elif result['in_api'] and not result['in_blockchain']:
            result['sync_status'] = '⚠️ In Database Only'
        elif not result['in_api'] and result['in_blockchain']:
            result['sync_status'] = '⚠️ In Blockchain Only'
        else:
            result['sync_status'] = '❌ Not Found'
        
        return result
    
    def get_recent_blockchain_entries(self, limit: int = 10) -> List[Dict]:
        """Get recent blockchain entries"""
        entries = []
        databases = self.get_couchdb_databases()
        
        for db in databases:
            try:
                response = requests.get(
                    f"{COUCHDB_URL}/{db}/_all_docs?include_docs=true&limit={limit}",
                    auth=self.couchdb_auth
                )
                
                if response.status_code == 200:
                    rows = response.json().get('rows', [])
                    for row in rows:
                        doc = row.get('doc', {})
                        if not doc.get('_id', '').startswith('_'):  # Skip design docs
                            entries.append({
                                'database': db,
                                'id': doc.get('_id'),
                                'type': doc.get('type', 'unknown'),
                                'contract_id': doc.get('contract_id') or doc.get('contractId'),
                                'timestamp': doc.get('timestamp') or doc.get('created_at'),
                                'tx_id': doc.get('blockchain_tx_id') or doc.get('tx_id')
                            })
            except Exception as e:
                continue
        
        return entries[:limit]
    
    def display_verification_report(self, contract_id: str):
        """Display comprehensive verification report"""
        print(f"\n{'='*60}")
        print(f"  Blockchain Verification Report for {contract_id}")
        print(f"{'='*60}\n")
        
        # Verify sync status
        sync_result = self.verify_contract_blockchain_sync(contract_id)
        
        print("📊 Sync Status:")
        print(f"  • Contract ID: {sync_result['contract_id']}")
        print(f"  • In Database: {'✅ Yes' if sync_result['in_api'] else '❌ No'}")
        print(f"  • In Blockchain: {'✅ Yes' if sync_result['in_blockchain'] else '❌ No'}")
        print(f"  • Transaction ID: {sync_result['tx_id'] or 'Not Available'}")
        print(f"  • Overall Status: {sync_result['sync_status']}")
        
        if sync_result.get('blockchain_data'):
            print("\n🔗 Blockchain Data:")
            blockchain_doc = sync_result['blockchain_data']['document']
            print(f"  • Database: {sync_result['blockchain_data']['database']}")
            print(f"  • Document ID: {blockchain_doc.get('_id')}")
            print(f"  • Revision: {blockchain_doc.get('_rev')}")
            
            # Display key fields
            important_fields = ['status', 'vendor_id', 'total_value', 'created_at', 'verified_at', 'submitted_at']
            for field in important_fields:
                if field in blockchain_doc:
                    print(f"  • {field.replace('_', ' ').title()}: {blockchain_doc[field]}")
        
        print(f"\n{'='*60}\n")

def main():
    parser = argparse.ArgumentParser(description='VendorChain Blockchain Explorer')
    parser.add_argument('command', choices=['verify', 'stats', 'search', 'recent', 'tx'],
                       help='Command to execute')
    parser.add_argument('--contract-id', '-c', help='Contract ID to verify')
    parser.add_argument('--tx-id', '-t', help='Transaction ID to search')
    parser.add_argument('--limit', '-l', type=int, default=10, help='Limit for recent entries')
    
    args = parser.parse_args()
    
    explorer = BlockchainExplorer()
    
    if args.command == 'verify':
        if not args.contract_id:
            print("Error: --contract-id required for verify command")
            sys.exit(1)
        explorer.display_verification_report(args.contract_id)
    
    elif args.command == 'stats':
        stats = explorer.get_blockchain_statistics()
        print("\n📊 Blockchain Statistics:")
        print(f"  • Total Databases: {len(stats['databases'])}")
        print(f"  • Total Documents: {stats['total_documents']}")
        print(f"  • Contracts: {stats['contracts']}")
        print(f"  • Vendors: {stats['vendors']}")
        
        if stats['databases']:
            print("\n📁 Database Details:")
            table_data = [(db['name'], db['documents'], f"{db['size']:,} bytes") 
                         for db in stats['databases']]
            print(tabulate(table_data, headers=['Database', 'Documents', 'Size'], 
                          tablefmt='grid'))
    
    elif args.command == 'search':
        if not args.contract_id:
            print("Error: --contract-id required for search command")
            sys.exit(1)
        
        result = explorer.search_contract_in_couchdb(args.contract_id)
        if result:
            print(f"\n✅ Contract found in blockchain!")
            print(f"Database: {result['database']}")
            print(f"Document: {json.dumps(result['document'], indent=2)}")
        else:
            print(f"\n❌ Contract {args.contract_id} not found in blockchain")
    
    elif args.command == 'recent':
        entries = explorer.get_recent_blockchain_entries(args.limit)
        if entries:
            print(f"\n📋 Recent Blockchain Entries (Last {args.limit}):")
            table_data = [
                (e['database'][:20], e['id'][:15], e['contract_id'] or 'N/A', 
                 e['tx_id'][:20] if e['tx_id'] else 'N/A')
                for e in entries
            ]
            print(tabulate(table_data, 
                          headers=['Database', 'Doc ID', 'Contract ID', 'TX ID'],
                          tablefmt='grid'))
        else:
            print("No recent entries found")
    
    elif args.command == 'tx':
        if not args.tx_id:
            print("Error: --tx-id required for tx command")
            sys.exit(1)
        
        result = explorer.get_transaction_details(args.tx_id)
        if result:
            print(f"\n✅ Transaction found!")
            print(f"Database: {result['database']}")
            print(f"Transaction Data: {json.dumps(result['transaction'], indent=2)}")
        else:
            print(f"\n❌ Transaction {args.tx_id} not found")

if __name__ == "__main__":
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        print("VendorChain Blockchain Explorer")
        print("\nUsage examples:")
        print("  python3 blockchain-explorer.py stats                    # Show blockchain statistics")
        print("  python3 blockchain-explorer.py verify -c CONTRACT123    # Verify contract sync")
        print("  python3 blockchain-explorer.py search -c CONTRACT123    # Search in blockchain")
        print("  python3 blockchain-explorer.py recent -l 20            # Show recent entries")
        print("  python3 blockchain-explorer.py tx -t 0xabc123...      # Find transaction")
        sys.exit(0)
    
    main()