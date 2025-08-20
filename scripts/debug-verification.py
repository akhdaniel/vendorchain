#!/usr/bin/env python3
"""
Debug why verification is not working
"""

import requests
import json

# Test direct CouchDB query
contract_id = 'CONTRACT-TX-1755658088'
tx_id = '0xe61dc23b8c31bf2a21905745ee485f807eac5ab4ec2b04f24f8309654931f223'
couch_url = "http://admin:adminpw@localhost:5984"

print("1. Checking what databases exist:")
dbs_response = requests.get(f"{couch_url}/_all_dbs")
if dbs_response.status_code == 200:
    all_dbs = dbs_response.json()
    print(f"   All databases: {all_dbs}")
    
    # Filter like Odoo does
    databases = [db for db in all_dbs if 'vendorchannel' in db or 'channel' in db or 'contract' in db]
    print(f"   Filtered databases: {databases}")

print("\n2. Searching for contract in each database:")
for db in databases:
    print(f"\n   Checking database: {db}")
    
    # Query exactly like Odoo does
    query = {
        "selector": {
            "$or": [
                {"contract_id": contract_id},
                {"blockchain_tx_id": tx_id}
            ]
        }
    }
    
    find_response = requests.post(
        f"{couch_url}/{db}/_find",
        json=query,
        headers={"Content-Type": "application/json"}
    )
    
    if find_response.status_code == 200:
        docs = find_response.json().get('docs', [])
        if docs:
            print(f"   ✅ FOUND! Document: {json.dumps(docs[0], indent=2)}")
            
            # Check what Odoo is comparing
            blockchain_data = docs[0]
            print(f"\n3. Comparing fields:")
            print(f"   contract_id match: {blockchain_data.get('contract_id')} == {contract_id}")
            print(f"   vendor_id in doc: {blockchain_data.get('vendor_id')}")
            print(f"   total_value in doc: {blockchain_data.get('total_value')}")
        else:
            print(f"   ❌ No documents found")
    else:
        print(f"   ❌ Query failed: {find_response.status_code}")

print("\n4. Testing API endpoint:")
api_response = requests.get(f"http://localhost:8000/api/v1/contracts/{contract_id}")
print(f"   API Status: {api_response.status_code}")
if api_response.status_code == 200:
    api_data = api_response.json().get('data', {})
    print(f"   API TX ID: {api_data.get('blockchain_tx_id')}")