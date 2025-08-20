#!/bin/bash

# Health Check for Hyperledger Fabric Network
# This script verifies all Fabric components are healthy

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "Fabric Network Health Check"
echo "=========================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check function
check_service() {
    local service_name=$1
    local check_command=$2
    
    echo -n "Checking $service_name... "
    
    if eval "$check_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
        return 0
    else
        echo -e "${RED}✗ Unhealthy${NC}"
        return 1
    fi
}

# Initialize health status
all_healthy=true

# Check CouchDB
check_service "CouchDB" "docker exec couchdb curl -f http://admin:adminpw@localhost:5984/" || all_healthy=false

# Check CA
check_service "Certificate Authority" "docker exec ca.org1.vendorchain.com curl -f http://localhost:17054/healthz" || all_healthy=false

# Check Orderer
check_service "Orderer" "docker exec orderer.vendorchain.com nc -z localhost 7050" || all_healthy=false

# Check Peer
check_service "Peer0 Org1" "docker exec peer0.org1.vendorchain.com peer node status" || all_healthy=false

# Check channel
echo -n "Checking channel 'vendorcontract'... "
if docker exec peer0.org1.vendorchain.com peer channel list 2>/dev/null | grep -q "vendorcontract"; then
    echo -e "${GREEN}✓ Joined${NC}"
else
    echo -e "${YELLOW}⚠ Not joined or doesn't exist${NC}"
    all_healthy=false
fi

echo ""
echo "=========================================="
if [ "$all_healthy" = true ]; then
    echo -e "${GREEN}All Fabric components are healthy!${NC}"
    exit 0
else
    echo -e "${RED}Some Fabric components are unhealthy${NC}"
    echo "Run './scripts/start-fabric.sh' to start the network"
    exit 1
fi