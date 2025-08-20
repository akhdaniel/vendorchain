#!/bin/bash

# Blockchain Data Verification Script
# Verify contracts, vendors, and payments on Hyperledger Fabric

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to display menu
show_menu() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║          Blockchain Data Verification Tool                  ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Select verification method:${NC}"
    echo "1) Verify via CouchDB (Blockchain State Database)"
    echo "2) Verify via Fabric Peer (Direct Blockchain Query)"
    echo "3) Verify via API Gateway (Application Layer)"
    echo "4) Verify Transaction by ID"
    echo "5) View All Blockchain Transactions"
    echo "6) Compare Database vs Blockchain"
    echo "7) Exit"
    echo ""
    read -p "Enter choice [1-7]: " choice
}

# Function to verify via CouchDB
verify_couchdb() {
    echo -e "${YELLOW}Connecting to CouchDB (Blockchain State Database)...${NC}"
    echo ""
    
    # CouchDB credentials
    COUCH_URL="http://admin:adminpw@localhost:5984"
    
    echo -e "${BLUE}1. Checking Available Databases:${NC}"
    curl -s $COUCH_URL/_all_dbs | python3 -m json.tool | grep -E "vendorchain|contract|vendor" || echo "No blockchain databases found"
    
    echo ""
    echo -e "${BLUE}2. Enter Contract ID to verify (or press Enter to skip):${NC}"
    read -p "Contract ID: " contract_id
    
    if [ ! -z "$contract_id" ]; then
        echo -e "${YELLOW}Searching for contract $contract_id in CouchDB...${NC}"
        
        # Search in channel database (actual name may vary)
        DBS=$(curl -s $COUCH_URL/_all_dbs | python3 -c "import sys, json; dbs = json.load(sys.stdin); print(' '.join([db for db in dbs if 'channel' in db or 'contract' in db]))")
        
        for db in $DBS; do
            echo "Checking database: $db"
            # Query for contract
            RESULT=$(curl -s "$COUCH_URL/$db/_find" \
                -H "Content-Type: application/json" \
                -d "{\"selector\": {\"contract_id\": \"$contract_id\"}}" 2>/dev/null || echo "{}")
            
            if echo "$RESULT" | grep -q "$contract_id"; then
                echo -e "${GREEN}✓ Contract found in blockchain database: $db${NC}"
                echo "$RESULT" | python3 -m json.tool
                break
            fi
        done
    fi
    
    echo ""
    echo -e "${BLUE}3. View Recent Blockchain Entries:${NC}"
    # Get the most recent entries from CouchDB
    for db in $DBS; do
        if [ ! -z "$db" ]; then
            echo "Recent entries in $db:"
            curl -s "$COUCH_URL/$db/_all_docs?limit=5&include_docs=true" | \
                python3 -c "import sys, json; docs = json.load(sys.stdin); [print(f\"  - {doc['id']}: {doc.get('doc', {}).get('contract_id', 'N/A')}\") for doc in docs.get('rows', [])]" 2>/dev/null || echo "  No entries"
        fi
    done
}

# Function to verify via Fabric Peer
verify_fabric_peer() {
    echo -e "${YELLOW}Querying Fabric Peer Directly...${NC}"
    echo ""
    
    # Check if peer container is running
    if ! docker ps | grep -q "fabric-peer\|peer0"; then
        echo -e "${RED}Error: Fabric peer container is not running${NC}"
        return 1
    fi
    
    PEER_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "fabric-peer|peer0" | head -1)
    
    echo -e "${BLUE}1. Peer Status:${NC}"
    docker exec $PEER_CONTAINER peer node status 2>/dev/null || echo "Unable to get peer status"
    
    echo ""
    echo -e "${BLUE}2. Installed Chaincodes:${NC}"
    docker exec $PEER_CONTAINER peer lifecycle chaincode queryinstalled 2>/dev/null || echo "No chaincodes installed"
    
    echo ""
    echo -e "${BLUE}3. Channel Information:${NC}"
    docker exec $PEER_CONTAINER peer channel list 2>/dev/null || echo "No channels found"
    
    echo ""
    echo -e "${BLUE}4. Query Chaincode (if available):${NC}"
    read -p "Enter contract ID to query: " contract_id
    
    if [ ! -z "$contract_id" ]; then
        # Try to query chaincode
        docker exec $PEER_CONTAINER peer chaincode query \
            -C vendorchannel \
            -n vendorcontract \
            -c "{\"function\":\"queryContract\",\"Args\":[\"$contract_id\"]}" 2>/dev/null || \
            echo "Unable to query chaincode (chaincode may not be deployed)"
    fi
}

# Function to verify via API
verify_api() {
    echo -e "${YELLOW}Verifying via API Gateway...${NC}"
    echo ""
    
    API_URL="http://localhost:8000/api/v1"
    
    echo -e "${BLUE}1. API Health Check:${NC}"
    curl -s $API_URL/health | python3 -m json.tool || echo "API not responding"
    
    echo ""
    echo -e "${BLUE}2. Blockchain Health:${NC}"
    curl -s $API_URL/health/blockchain | python3 -m json.tool || echo "Blockchain health endpoint not available"
    
    echo ""
    echo -e "${BLUE}3. Query Contract:${NC}"
    read -p "Enter contract ID: " contract_id
    
    if [ ! -z "$contract_id" ]; then
        echo -e "${YELLOW}Fetching contract $contract_id...${NC}"
        RESPONSE=$(curl -s $API_URL/contracts/$contract_id)
        
        if echo "$RESPONSE" | grep -q "blockchain_tx_id"; then
            echo -e "${GREEN}✓ Contract found with blockchain reference${NC}"
            echo "$RESPONSE" | python3 -m json.tool
            
            # Extract blockchain TX ID
            TX_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('data', {}).get('blockchain_tx_id', 'Not found'))")
            echo ""
            echo -e "${CYAN}Blockchain Transaction ID: $TX_ID${NC}"
        else
            echo -e "${RED}Contract not found or no blockchain reference${NC}"
        fi
    fi
}

# Function to verify transaction by ID
verify_transaction() {
    echo -e "${YELLOW}Verify Transaction by ID${NC}"
    echo ""
    
    read -p "Enter Transaction ID (e.g., 0x...): " tx_id
    
    if [ -z "$tx_id" ]; then
        echo -e "${RED}Transaction ID required${NC}"
        return 1
    fi
    
    echo -e "${BLUE}Searching for transaction $tx_id...${NC}"
    echo ""
    
    # Method 1: Check in peer logs
    echo "1. Checking peer logs..."
    PEER_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "fabric-peer|peer0" | head -1)
    if [ ! -z "$PEER_CONTAINER" ]; then
        docker logs $PEER_CONTAINER 2>&1 | grep -i "$tx_id" | tail -5 || echo "  Not found in peer logs"
    fi
    
    # Method 2: Check in orderer logs
    echo ""
    echo "2. Checking orderer logs..."
    ORDERER_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "orderer" | head -1)
    if [ ! -z "$ORDERER_CONTAINER" ]; then
        docker logs $ORDERER_CONTAINER 2>&1 | grep -i "$tx_id" | tail -5 || echo "  Not found in orderer logs"
    fi
    
    # Method 3: Check in CouchDB
    echo ""
    echo "3. Checking CouchDB..."
    COUCH_URL="http://admin:adminpw@localhost:5984"
    DBS=$(curl -s $COUCH_URL/_all_dbs | python3 -c "import sys, json; dbs = json.load(sys.stdin); print(' '.join([db for db in dbs if 'channel' in db or 'contract' in db]))" 2>/dev/null)
    
    for db in $DBS; do
        if [ ! -z "$db" ]; then
            RESULT=$(curl -s "$COUCH_URL/$db/_find" \
                -H "Content-Type: application/json" \
                -d "{\"selector\": {\"blockchain_tx_id\": \"$tx_id\"}}" 2>/dev/null)
            
            if echo "$RESULT" | grep -q "$tx_id"; then
                echo -e "${GREEN}✓ Transaction found in $db${NC}"
                echo "$RESULT" | python3 -m json.tool
                break
            fi
        fi
    done
}

# Function to view all transactions
view_all_transactions() {
    echo -e "${YELLOW}Viewing All Blockchain Transactions${NC}"
    echo ""
    
    # Get transaction count from peer
    PEER_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "fabric-peer|peer0" | head -1)
    
    if [ ! -z "$PEER_CONTAINER" ]; then
        echo -e "${BLUE}Block Height Information:${NC}"
        docker exec $PEER_CONTAINER peer channel getinfo -c vendorchannel 2>/dev/null || echo "Channel info not available"
        
        echo ""
        echo -e "${BLUE}Recent Blocks:${NC}"
        # Try to fetch recent blocks
        for i in {0..4}; do
            echo "Block $i:"
            docker exec $PEER_CONTAINER peer channel fetch $i -c vendorchannel 2>/dev/null || break
        done
    fi
    
    echo ""
    echo -e "${BLUE}Recent Transactions from Logs:${NC}"
    docker logs $PEER_CONTAINER 2>&1 | grep -E "Invoke|commit|Transaction" | tail -10
}

# Function to compare database vs blockchain
compare_data() {
    echo -e "${YELLOW}Comparing Database vs Blockchain${NC}"
    echo ""
    
    # Get contract count from PostgreSQL
    echo -e "${BLUE}1. PostgreSQL Database:${NC}"
    POSTGRES_COUNT=$(docker exec vendorchain-postgres psql -U odoo -d vendorchain -t -c "SELECT COUNT(*) FROM vendor_contract;" 2>/dev/null | tr -d ' ' || echo "0")
    echo "  Total contracts in database: $POSTGRES_COUNT"
    
    # Get recent contracts
    echo "  Recent contracts:"
    docker exec vendorchain-postgres psql -U odoo -d vendorchain -c "SELECT contract_id, blockchain_tx_id, state FROM vendor_contract ORDER BY id DESC LIMIT 5;" 2>/dev/null || echo "Unable to query"
    
    echo ""
    echo -e "${BLUE}2. CouchDB (Blockchain State):${NC}"
    COUCH_URL="http://admin:adminpw@localhost:5984"
    DBS=$(curl -s $COUCH_URL/_all_dbs | python3 -c "import sys, json; dbs = json.load(sys.stdin); print(' '.join([db for db in dbs if 'channel' in db]))" 2>/dev/null)
    
    for db in $DBS; do
        if [ ! -z "$db" ]; then
            DOC_COUNT=$(curl -s "$COUCH_URL/$db" | python3 -c "import sys, json; info = json.load(sys.stdin); print(info.get('doc_count', 0))" 2>/dev/null || echo "0")
            echo "  Documents in $db: $DOC_COUNT"
        fi
    done
    
    echo ""
    echo -e "${BLUE}3. Verification Summary:${NC}"
    echo "  • Database contracts: $POSTGRES_COUNT"
    echo "  • Blockchain entries: Check CouchDB documents above"
    echo "  • Sync status: Check if numbers match"
}

# Main loop
while true; do
    show_menu
    case $choice in
        1)
            verify_couchdb
            ;;
        2)
            verify_fabric_peer
            ;;
        3)
            verify_api
            ;;
        4)
            verify_transaction
            ;;
        5)
            view_all_transactions
            ;;
        6)
            compare_data
            ;;
        7)
            echo -e "${GREEN}Exiting...${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option. Please try again.${NC}"
            ;;
    esac
    echo ""
    read -p "Press Enter to continue..."
    clear
done