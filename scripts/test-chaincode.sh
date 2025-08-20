#!/bin/bash

# Test chaincode functions script for VendorChain MVP
# This script tests all chaincode functions through peer CLI

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
CHAINCODE_NAME="vendor-contract"
CHANNEL_NAME="vendorcontract"
ORDERER_ADDRESS="orderer.vendorchain.com:7050"
PEER_ADDRESS="peer0.org1.vendorchain.com:7051"
CORE_PEER_LOCALMSPID="Org1MSP"

# Set up environment
FABRIC_CFG_PATH="${PROJECT_ROOT}/fabric-network/config"
CORE_PEER_TLS_ENABLED=true
CORE_PEER_TLS_ROOTCERT_FILE="${PROJECT_ROOT}/fabric-network/organizations/peerOrganizations/org1.vendorchain.com/peers/peer0.org1.vendorchain.com/tls/ca.crt"
CORE_PEER_MSPCONFIGPATH="${PROJECT_ROOT}/fabric-network/organizations/peerOrganizations/org1.vendorchain.com/users/Admin@org1.vendorchain.com/msp"
CORE_PEER_ADDRESS="${PEER_ADDRESS}"
ORDERER_CA="${PROJECT_ROOT}/fabric-network/organizations/ordererOrganizations/vendorchain.com/orderers/orderer.vendorchain.com/msp/tlscacerts/tlsca.vendorchain.com-cert.pem"

export FABRIC_CFG_PATH CORE_PEER_TLS_ENABLED CORE_PEER_TLS_ROOTCERT_FILE CORE_PEER_MSPCONFIGPATH CORE_PEER_ADDRESS CORE_PEER_LOCALMSPID

echo -e "${GREEN}===== VendorChain Chaincode Function Tests =====${NC}"
echo ""

# Function to execute chaincode invoke
invoke_chaincode() {
    local function_call="$1"
    local description="$2"
    
    echo -e "${BLUE}Testing: ${description}${NC}"
    echo -e "${YELLOW}Function: ${function_call}${NC}"
    
    ./fabric-network/bin/peer chaincode invoke \
        -o "${ORDERER_ADDRESS}" \
        --ordererTLSHostnameOverride orderer.vendorchain.com \
        --tls \
        --cafile "${ORDERER_CA}" \
        -C "${CHANNEL_NAME}" \
        -n "${CHAINCODE_NAME}" \
        --peerAddresses "${PEER_ADDRESS}" \
        --tlsRootCertFiles "${CORE_PEER_TLS_ROOTCERT_FILE}" \
        -c "${function_call}"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ ${description} - SUCCESS${NC}"
    else
        echo -e "${RED}✗ ${description} - FAILED${NC}"
        return 1
    fi
    echo ""
}

# Function to execute chaincode query
query_chaincode() {
    local function_call="$1"
    local description="$2"
    
    echo -e "${BLUE}Testing: ${description}${NC}"
    echo -e "${YELLOW}Function: ${function_call}${NC}"
    
    local result
    result=$(./fabric-network/bin/peer chaincode query \
        -C "${CHANNEL_NAME}" \
        -n "${CHAINCODE_NAME}" \
        -c "${function_call}")
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ ${description} - SUCCESS${NC}"
        echo -e "${YELLOW}Result:${NC} ${result}"
    else
        echo -e "${RED}✗ ${description} - FAILED${NC}"
        return 1
    fi
    echo ""
}

# Test 1: Query all contracts (should show sample data from initLedger)
echo -e "${GREEN}=== Test 1: Query All Contracts ===${NC}"
query_chaincode '{"function":"queryAllContracts","Args":[]}' "Query all existing contracts"

# Test 2: Query specific contract
echo -e "${GREEN}=== Test 2: Query Specific Contract ===${NC}"
query_chaincode '{"function":"queryContract","Args":["CONTRACT0"]}' "Query specific contract (CONTRACT0)"

# Test 3: Create new contract
echo -e "${GREEN}=== Test 3: Create New Contract ===${NC}"
invoke_chaincode '{"function":"createContract","Args":["CONTRACT_TEST_001","VENDOR_TEST_001","Test Vendor Corporation","Service Agreement","2025-12-31","100000"]}' "Create new contract"

# Test 4: Query the newly created contract
echo -e "${GREEN}=== Test 4: Query Newly Created Contract ===${NC}"
query_chaincode '{"function":"queryContract","Args":["CONTRACT_TEST_001"]}' "Query newly created contract"

# Test 5: Verify the contract (simulate verificator role)
echo -e "${GREEN}=== Test 5: Verify Contract ===${NC}"
invoke_chaincode '{"function":"verifyContract","Args":["CONTRACT_TEST_001"]}' "Verify contract"

# Test 6: Query contract after verification
echo -e "${GREEN}=== Test 6: Query Contract After Verification ===${NC}"
query_chaincode '{"function":"queryContract","Args":["CONTRACT_TEST_001"]}' "Query contract after verification"

# Test 7: Submit the contract (simulate admin role)
echo -e "${GREEN}=== Test 7: Submit Contract ===${NC}"
invoke_chaincode '{"function":"submitContract","Args":["CONTRACT_TEST_001"]}' "Submit contract"

# Test 8: Query contract after submission
echo -e "${GREEN}=== Test 8: Query Contract After Submission ===${NC}"
query_chaincode '{"function":"queryContract","Args":["CONTRACT_TEST_001"]}' "Query contract after submission"

# Test 9: Record payment
echo -e "${GREEN}=== Test 9: Record Payment ===${NC}"
invoke_chaincode '{"function":"recordPayment","Args":["CONTRACT_TEST_001","25000","2025-08-19","PAY_001"]}' "Record payment"

# Test 10: Query contract after payment
echo -e "${GREEN}=== Test 10: Query Contract After Payment ===${NC}"
query_chaincode '{"function":"queryContract","Args":["CONTRACT_TEST_001"]}' "Query contract after payment"

# Test 11: Get contracts by vendor
echo -e "${GREEN}=== Test 11: Get Contracts by Vendor ===${NC}"
query_chaincode '{"function":"getContractsByVendor","Args":["VENDOR_TEST_001"]}' "Get contracts by vendor"

# Test 12: Get contract history
echo -e "${GREEN}=== Test 12: Get Contract History ===${NC}"
query_chaincode '{"function":"getContractHistory","Args":["CONTRACT_TEST_001"]}' "Get contract transaction history"

# Test 13: Get expiring contracts
echo -e "${GREEN}=== Test 13: Get Expiring Contracts ===${NC}"
query_chaincode '{"function":"getExpiringContracts","Args":["365"]}' "Get contracts expiring in 365 days"

# Test 14: Create second contract for additional testing
echo -e "${GREEN}=== Test 14: Create Second Contract ===${NC}"
invoke_chaincode '{"function":"createContract","Args":["CONTRACT_TEST_002","VENDOR_TEST_002","Another Test Vendor","Supply Contract","2025-06-30","75000"]}' "Create second contract"

# Test 15: Query all contracts again (should show all contracts)
echo -e "${GREEN}=== Test 15: Query All Contracts (Final) ===${NC}"
query_chaincode '{"function":"queryAllContracts","Args":[]}' "Query all contracts after testing"

echo ""
echo -e "${GREEN}===== All Chaincode Function Tests Completed =====${NC}"
echo -e "${GREEN}The three-stage workflow (CREATED → VERIFIED → SUBMITTED) has been successfully tested!${NC}"
echo ""
echo -e "${YELLOW}Test Summary:${NC}"
echo "• Contract creation ✓"
echo "• Contract verification ✓" 
echo "• Contract submission ✓"
echo "• Payment recording ✓"
echo "• Query operations ✓"
echo "• History tracking ✓"
echo "• Vendor filtering ✓"
echo "• Expiry checking ✓"