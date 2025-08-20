#!/bin/bash

# Create and Join Channel for VendorChain Network
# This script creates the vendorcontract channel and joins peers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FABRIC_DIR="$(dirname "$SCRIPT_DIR")"
CHANNEL_NAME="vendorcontract"

echo "=========================================="
echo "Creating Channel: $CHANNEL_NAME"
echo "=========================================="

cd "$FABRIC_DIR"

# Add bin to PATH
export PATH=$FABRIC_DIR/bin:$PATH

# Set environment variables for peer CLI
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=$FABRIC_DIR/organizations/peerOrganizations/org1.vendorchain.com/peers/peer0.org1.vendorchain.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=$FABRIC_DIR/organizations/peerOrganizations/org1.vendorchain.com/users/Admin@org1.vendorchain.com/msp
export CORE_PEER_ADDRESS=localhost:7051

# Wait for orderer to be ready
echo "Waiting for orderer to be ready..."
sleep 5

# Create the channel
echo "Creating channel '$CHANNEL_NAME'..."
peer channel create \
    -o localhost:7050 \
    -c $CHANNEL_NAME \
    -f ./channel-artifacts/vendorcontract.tx \
    --outputBlock ./channel-artifacts/vendorcontract.block \
    --tls \
    --cafile $FABRIC_DIR/organizations/ordererOrganizations/vendorchain.com/orderers/orderer.vendorchain.com/msp/tlscacerts/tlsca.vendorchain.com-cert.pem

echo "Channel created successfully"

# Join peer to the channel
echo "Joining peer0.org1 to channel '$CHANNEL_NAME'..."
peer channel join -b ./channel-artifacts/vendorcontract.block

echo "Peer joined channel successfully"

# Update anchor peers
echo "Updating anchor peers for Org1..."
peer channel update \
    -o localhost:7050 \
    -c $CHANNEL_NAME \
    -f ./channel-artifacts/Org1MSPanchors.tx \
    --tls \
    --cafile $FABRIC_DIR/organizations/ordererOrganizations/vendorchain.com/orderers/orderer.vendorchain.com/msp/tlscacerts/tlsca.vendorchain.com-cert.pem

echo "=========================================="
echo "Channel '$CHANNEL_NAME' setup complete!"
echo "=========================================="