#!/bin/bash

# Package and deploy chaincode script for VendorChain MVP
# This script packages the vendor-contract chaincode and deploys it to the Fabric network

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
CHAINCODE_NAME="vendor-contract"
CHAINCODE_VERSION="1.0"
CHAINCODE_PATH="${PROJECT_ROOT}/chaincode/vendor-contract"
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

echo -e "${GREEN}Starting chaincode packaging and deployment process...${NC}"

# Function to check if containers are running
check_fabric_network() {
    echo -e "${YELLOW}Checking Fabric network status...${NC}"
    
    if ! docker ps | grep -q "peer0.org1.vendorchain.com"; then
        echo -e "${RED}Error: Fabric network is not running. Please start the network first.${NC}"
        echo "Run: ./scripts/start-fabric.sh"
        exit 1
    fi
    
    echo -e "${GREEN}Fabric network is running.${NC}"
}

# Function to package chaincode
package_chaincode() {
    echo -e "${YELLOW}Packaging chaincode...${NC}"
    
    cd "${PROJECT_ROOT}"
    
    # Remove existing package if it exists
    rm -f "${CHAINCODE_NAME}.tar.gz"
    
    # Package the chaincode
    ./fabric-network/bin/peer lifecycle chaincode package "${CHAINCODE_NAME}.tar.gz" \
        --path "${CHAINCODE_PATH}" \
        --lang node \
        --label "${CHAINCODE_NAME}_${CHAINCODE_VERSION}"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Chaincode packaged successfully: ${CHAINCODE_NAME}.tar.gz${NC}"
    else
        echo -e "${RED}Error: Failed to package chaincode.${NC}"
        exit 1
    fi
}

# Function to install chaincode
install_chaincode() {
    echo -e "${YELLOW}Installing chaincode on peer...${NC}"
    
    ./fabric-network/bin/peer lifecycle chaincode install "${CHAINCODE_NAME}.tar.gz"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Chaincode installed successfully.${NC}"
    else
        echo -e "${RED}Error: Failed to install chaincode.${NC}"
        exit 1
    fi
}

# Function to query installed chaincode
query_installed() {
    echo -e "${YELLOW}Querying installed chaincode...${NC}"
    
    ./fabric-network/bin/peer lifecycle chaincode queryinstalled
    
    # Get package ID
    PACKAGE_ID=$(./fabric-network/bin/peer lifecycle chaincode queryinstalled | grep "${CHAINCODE_NAME}_${CHAINCODE_VERSION}" | sed -n 's/.*Package ID: //; s/, Label:.*//p')
    
    if [ -z "$PACKAGE_ID" ]; then
        echo -e "${RED}Error: Could not find package ID for installed chaincode.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Package ID: ${PACKAGE_ID}${NC}"
}

# Function to approve chaincode definition
approve_chaincode() {
    echo -e "${YELLOW}Approving chaincode definition...${NC}"
    
    ./fabric-network/bin/peer lifecycle chaincode approveformyorg \
        -o "${ORDERER_ADDRESS}" \
        --ordererTLSHostnameOverride orderer.vendorchain.com \
        --tls \
        --cafile "${ORDERER_CA}" \
        --channelID "${CHANNEL_NAME}" \
        --name "${CHAINCODE_NAME}" \
        --version "${CHAINCODE_VERSION}" \
        --package-id "${PACKAGE_ID}" \
        --sequence 1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Chaincode definition approved successfully.${NC}"
    else
        echo -e "${RED}Error: Failed to approve chaincode definition.${NC}"
        exit 1
    fi
}

# Function to check commit readiness
check_commit_readiness() {
    echo -e "${YELLOW}Checking commit readiness...${NC}"
    
    ./fabric-network/bin/peer lifecycle chaincode checkcommitreadiness \
        --channelID "${CHANNEL_NAME}" \
        --name "${CHAINCODE_NAME}" \
        --version "${CHAINCODE_VERSION}" \
        --sequence 1 \
        --tls \
        --cafile "${ORDERER_CA}" \
        --output json
}

# Function to commit chaincode
commit_chaincode() {
    echo -e "${YELLOW}Committing chaincode...${NC}"
    
    ./fabric-network/bin/peer lifecycle chaincode commit \
        -o "${ORDERER_ADDRESS}" \
        --ordererTLSHostnameOverride orderer.vendorchain.com \
        --tls \
        --cafile "${ORDERER_CA}" \
        --channelID "${CHANNEL_NAME}" \
        --name "${CHAINCODE_NAME}" \
        --version "${CHAINCODE_VERSION}" \
        --sequence 1 \
        --peerAddresses "${PEER_ADDRESS}" \
        --tlsRootCertFiles "${CORE_PEER_TLS_ROOTCERT_FILE}"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Chaincode committed successfully.${NC}"
    else
        echo -e "${RED}Error: Failed to commit chaincode.${NC}"
        exit 1
    fi
}

# Function to query committed chaincode
query_committed() {
    echo -e "${YELLOW}Querying committed chaincode...${NC}"
    
    ./fabric-network/bin/peer lifecycle chaincode querycommitted \
        --channelID "${CHANNEL_NAME}" \
        --name "${CHAINCODE_NAME}" \
        --cafile "${ORDERER_CA}"
}

# Function to initialize ledger
initialize_ledger() {
    echo -e "${YELLOW}Initializing chaincode ledger...${NC}"
    
    sleep 5  # Wait for chaincode to be ready
    
    ./fabric-network/bin/peer chaincode invoke \
        -o "${ORDERER_ADDRESS}" \
        --ordererTLSHostnameOverride orderer.vendorchain.com \
        --tls \
        --cafile "${ORDERER_CA}" \
        -C "${CHANNEL_NAME}" \
        -n "${CHAINCODE_NAME}" \
        --peerAddresses "${PEER_ADDRESS}" \
        --tlsRootCertFiles "${CORE_PEER_TLS_ROOTCERT_FILE}" \
        -c '{"function":"initLedger","Args":[]}'
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Chaincode ledger initialized successfully.${NC}"
    else
        echo -e "${RED}Error: Failed to initialize chaincode ledger.${NC}"
        exit 1
    fi
}

# Main execution flow
echo -e "${GREEN}===== VendorChain Chaincode Deployment =====${NC}"
echo "Chaincode: ${CHAINCODE_NAME}"
echo "Version: ${CHAINCODE_VERSION}"
echo "Channel: ${CHANNEL_NAME}"
echo ""

check_fabric_network
package_chaincode
install_chaincode
query_installed
approve_chaincode
check_commit_readiness
commit_chaincode
query_committed
initialize_ledger

echo ""
echo -e "${GREEN}===== Chaincode deployment completed successfully! =====${NC}"
echo -e "${GREEN}You can now test the chaincode using the test script.${NC}"