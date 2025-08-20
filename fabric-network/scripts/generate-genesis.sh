#!/bin/bash

# Generate Genesis Block for VendorChain Network
# This script generates the genesis block for the orderer

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FABRIC_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "Generating Genesis Block"
echo "=========================================="

cd "$FABRIC_DIR"

# Add bin to PATH
export PATH=$FABRIC_DIR/bin:$PATH

# Ensure channel artifacts directory exists
mkdir -p channel-artifacts

# Generate genesis block
echo "Creating genesis block..."
configtxgen -profile VendorChainGenesis \
    -channelID system-channel \
    -outputBlock ./channel-artifacts/genesis.block \
    -configPath .

if [ -f "./channel-artifacts/genesis.block" ]; then
    echo "✓ Genesis block created successfully"
    ls -lh ./channel-artifacts/genesis.block
else
    echo "✗ Failed to create genesis block"
    exit 1
fi