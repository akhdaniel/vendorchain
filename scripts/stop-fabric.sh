#!/bin/bash

# Stop Hyperledger Fabric Network
# This script stops the Fabric network components

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "Stopping VendorChain Fabric Network"
echo "=========================================="

cd "$PROJECT_ROOT"

# Stop Fabric services
echo "Stopping Fabric services..."
docker-compose stop \
    ca.org1.vendorchain.com \
    orderer.vendorchain.com \
    peer0.org1.vendorchain.com \
    couchdb

echo ""
echo "Fabric network stopped."
echo "To remove containers and volumes, run: docker-compose down -v"