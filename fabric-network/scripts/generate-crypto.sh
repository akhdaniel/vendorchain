#!/bin/bash

# Generate Crypto Materials for VendorChain Network
# This script generates certificates and keys for the Fabric network

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FABRIC_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$FABRIC_DIR")"

echo "=========================================="
echo "Generating Crypto Materials for VendorChain"
echo "=========================================="

cd "$FABRIC_DIR"

# Download Fabric binaries if not present
if [ ! -d "bin" ]; then
    echo "Downloading Hyperledger Fabric binaries..."
    curl -sSL https://bit.ly/2ysbOFE | bash -s -- 2.5.4 1.5.7 -d -s
fi

# Add bin to PATH
export PATH=$FABRIC_DIR/bin:$PATH

# Clean up existing crypto materials
echo "Cleaning up existing crypto materials..."
rm -rf organizations/ordererOrganizations
rm -rf organizations/peerOrganizations
rm -rf channel-artifacts/*

# Generate crypto materials using cryptogen
echo "Generating certificates using cryptogen..."
cryptogen generate --config=crypto-config.yaml --output="organizations"

# Create channel artifacts directory
mkdir -p channel-artifacts

# Generate genesis block for orderer
echo "Generating Genesis block..."
configtxgen -profile VendorChainGenesis -channelID system-channel -outputBlock ./channel-artifacts/genesis.block

# Generate channel configuration transaction
echo "Generating channel configuration transaction..."
configtxgen -profile VendorContractChannel -outputCreateChannelTx ./channel-artifacts/vendorcontract.tx -channelID vendorcontract

# Generate anchor peer update for Org1
echo "Generating anchor peer update for Org1..."
configtxgen -profile VendorContractChannel -outputAnchorPeersUpdate ./channel-artifacts/Org1MSPanchors.tx -channelID vendorcontract -asOrg Org1MSP

echo "=========================================="
echo "Crypto materials generated successfully!"
echo "=========================================="

# Set proper permissions
chmod -R 755 organizations/
chmod -R 755 channel-artifacts/

echo "Files generated:"
echo "  - Genesis Block: channel-artifacts/genesis.block"
echo "  - Channel TX: channel-artifacts/vendorcontract.tx"
echo "  - Anchor Peer Update: channel-artifacts/Org1MSPanchors.tx"
echo ""
echo "Crypto materials are in: organizations/"