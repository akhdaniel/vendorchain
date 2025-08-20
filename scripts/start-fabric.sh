#!/bin/bash

# Start Hyperledger Fabric Network
# This script initializes and starts the Fabric network components

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FABRIC_DIR="$PROJECT_ROOT/fabric-network"

echo "=========================================="
echo "Starting VendorChain Fabric Network"
echo "=========================================="

# Check if crypto materials exist
if [ ! -d "$FABRIC_DIR/organizations/ordererOrganizations" ] || [ ! -d "$FABRIC_DIR/organizations/peerOrganizations" ]; then
    echo "Crypto materials not found. Generating..."
    cd "$FABRIC_DIR"
    ./scripts/generate-crypto.sh
    cd "$PROJECT_ROOT"
fi

# Start only Fabric-related services
echo "Starting Fabric services..."
docker-compose up -d ca.org1.vendorchain.com couchdb

# Wait for CA to be healthy
echo "Waiting for CA to be ready..."
timeout=60
while [ $timeout -gt 0 ]; do
    if docker exec ca.org1.vendorchain.com curl -f http://localhost:17054/healthz 2>/dev/null; then
        echo "CA is ready"
        break
    fi
    sleep 2
    timeout=$((timeout - 2))
done

# Start orderer
echo "Starting orderer..."
docker-compose up -d orderer.vendorchain.com

# Wait for orderer
echo "Waiting for orderer to be ready..."
sleep 10

# Start peer
echo "Starting peer..."
docker-compose up -d peer0.org1.vendorchain.com

# Wait for peer to be ready
echo "Waiting for peer to be ready..."
timeout=60
while [ $timeout -gt 0 ]; do
    if docker exec peer0.org1.vendorchain.com peer node status 2>/dev/null | grep -q "STARTED"; then
        echo "Peer is ready"
        break
    fi
    sleep 2
    timeout=$((timeout - 2))
done

# Create channel if it doesn't exist
if [ ! -f "$FABRIC_DIR/channel-artifacts/vendorcontract.block" ]; then
    echo "Creating channel..."
    cd "$FABRIC_DIR"
    ./scripts/create-channel.sh
    cd "$PROJECT_ROOT"
else
    echo "Channel already exists"
fi

echo "=========================================="
echo "Fabric Network Started Successfully!"
echo "=========================================="
echo ""
echo "Network Status:"
docker ps --filter "name=vendorchain" --filter "name=org1" --format "table {{.Names}}\t{{.Status}}"
echo ""
echo "CA Admin Portal: http://localhost:17054"
echo "Peer Operations: http://localhost:17051"
echo "Orderer Operations: http://localhost:17050"
echo "CouchDB Admin: http://localhost:5984/_utils (admin/adminpw)"