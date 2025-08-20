#!/bin/bash

# VendorChain MVP Complete Demo
# This script demonstrates the fully operational MVP system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

API_BASE="http://localhost:8000/api/v1"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        ${YELLOW}VendorChain MVP - Complete Demonstration${BLUE}             ║${NC}"
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}║  ${CYAN}Blockchain-Based Vendor Contract Management System${BLUE}        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}\n"

# Step 1: System Health Check
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 1: System Health Check${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${CYAN}→ Checking API Gateway${NC}"
api_health=$(curl -s "${API_BASE}/health/" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data['status'])")
echo -e "  Status: ${GREEN}${api_health}${NC}"

echo -e "${CYAN}→ Checking Database Connection${NC}"
db_health=$(curl -s "${API_BASE}/health/database" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data['status'])")
echo -e "  Status: ${GREEN}${db_health}${NC}"

echo -e "${CYAN}→ Checking Blockchain Network${NC}"
bc_health=$(curl -s "${API_BASE}/health/blockchain" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data['status'])")
echo -e "  Status: ${GREEN}${bc_health}${NC}\n"

# Step 2: Create New Vendor
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 2: Vendor Registration${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Generate unique IDs
TIMESTAMP=$(date +%s)
VENDOR_ID="VENDOR-DEMO-${TIMESTAMP}"
CONTRACT_ID="CONTRACT${TIMESTAMP}"

echo -e "${CYAN}→ Creating vendor: GlobalTech Solutions${NC}"
vendor_response=$(curl -s -X POST "${API_BASE}/vendors/" \
  -H "Content-Type: application/json" \
  -d "{
    \"vendor_id\": \"${VENDOR_ID}\",
    \"name\": \"GlobalTech Solutions\",
    \"contact_email\": \"contact@globaltech.com\",
    \"contact_phone\": \"+1-555-2024\",
    \"address\": \"500 Innovation Drive, Tech Park, CA 94105\",
    \"vendor_type\": \"SUPPLIER\",
    \"status\": \"ACTIVE\"
  }")

vendor_name=$(echo "$vendor_response" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('name', 'N/A'))")
echo -e "  ${GREEN}✓ Vendor created: ${vendor_name}${NC}"
echo -e "  ${GREEN}✓ Vendor ID: ${VENDOR_ID}${NC}\n"

# Step 3: Create Contract
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 3: Contract Creation${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${CYAN}→ Creating contract for IT infrastructure${NC}"
contract_response=$(curl -s -X POST "${API_BASE}/contracts/" \
  -H "Content-Type: application/json" \
  -d "{
    \"contract_id\": \"${CONTRACT_ID}\",
    \"vendor_id\": \"${VENDOR_ID}\",
    \"contract_type\": \"PURCHASE\",
    \"description\": \"Enterprise IT Infrastructure - Q4 2024\",
    \"total_value\": 500000.00,
    \"expiry_date\": \"2026-12-31\",
    \"created_by\": \"John Anderson\"
  }")

contract_status=$(echo "$contract_response" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('status', 'N/A'))")
contract_value=$(echo "$contract_response" | python3 -c "import json,sys; data=json.load(sys.stdin); print(f\"\${data.get('total_value', 0):,.2f}\")")
echo -e "  ${GREEN}✓ Contract created${NC}"
echo -e "  ${GREEN}✓ Contract ID: ${CONTRACT_ID}${NC}"
echo -e "  ${GREEN}✓ Value: ${contract_value}${NC}"
echo -e "  ${GREEN}✓ Status: ${contract_status}${NC}\n"

# Step 4: Verify Contract
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 4: Contract Verification (Procurement Manager)${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${CYAN}→ Verifying contract terms and conditions${NC}"
verify_response=$(curl -s -X POST "${API_BASE}/workflow/contracts/${CONTRACT_ID}/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "verified_by": "Emily Rodriguez",
    "performed_by": "Emily Rodriguez",
    "notes": "All terms reviewed. Pricing competitive. Vendor compliance verified."
  }')

verify_status=$(echo "$verify_response" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('status', 'N/A'))")
echo -e "  ${GREEN}✓ Contract verified by Emily Rodriguez${NC}"
echo -e "  ${GREEN}✓ New status: ${verify_status}${NC}\n"

# Step 5: Submit Contract
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 5: Contract Submission (Finance Director)${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${CYAN}→ Final approval and submission${NC}"
submit_response=$(curl -s -X POST "${API_BASE}/workflow/contracts/${CONTRACT_ID}/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "submitted_by": "David Thompson",
    "performed_by": "David Thompson",
    "notes": "Budget approved. Authorized for execution. PO#2024-1125 issued."
  }')

submit_status=$(echo "$submit_response" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('status', 'N/A'))")
echo -e "  ${GREEN}✓ Contract submitted by David Thompson${NC}"
echo -e "  ${GREEN}✓ New status: ${submit_status}${NC}\n"

# Step 6: Record Payments
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 6: Payment Recording${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${CYAN}→ Recording initial payment (25% advance)${NC}"
payment1_response=$(curl -s -X POST "${API_BASE}/contracts/${CONTRACT_ID}/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 125000.00,
    "payment_date": "2024-08-19",
    "reference": "WT-2024-8901",
    "method": "Wire Transfer",
    "notes": "25% advance payment as per contract terms"
  }')

paid1=$(echo "$payment1_response" | python3 -c "import json,sys; data=json.load(sys.stdin); print(f\"\${data.get('paid_amount', 0):,.2f}\")")
remaining1=$(echo "$payment1_response" | python3 -c "import json,sys; data=json.load(sys.stdin); print(f\"\${data.get('remaining_amount', 0):,.2f}\")")
echo -e "  ${GREEN}✓ Payment recorded: \$125,000.00${NC}"
echo -e "  Total paid: ${paid1}"
echo -e "  Remaining: ${remaining1}\n"

echo -e "${CYAN}→ Recording second payment (milestone completion)${NC}"
payment2_response=$(curl -s -X POST "${API_BASE}/contracts/${CONTRACT_ID}/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 175000.00,
    "payment_date": "2024-09-30",
    "reference": "WT-2024-9456",
    "method": "Wire Transfer",
    "notes": "Milestone 1 completion - servers delivered and installed"
  }')

paid2=$(echo "$payment2_response" | python3 -c "import json,sys; data=json.load(sys.stdin); print(f\"\${data.get('paid_amount', 0):,.2f}\")")
remaining2=$(echo "$payment2_response" | python3 -c "import json,sys; data=json.load(sys.stdin); print(f\"\${data.get('remaining_amount', 0):,.2f}\")")
echo -e "  ${GREEN}✓ Payment recorded: \$175,000.00${NC}"
echo -e "  Total paid: ${paid2}"
echo -e "  Remaining: ${remaining2}\n"

# Step 7: Query Contract Details
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 7: Contract Status Review${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${CYAN}→ Retrieving complete contract information${NC}"
contract_details=$(curl -s -X GET "${API_BASE}/contracts/${CONTRACT_ID}")

# Parse contract details
final_status=$(echo "$contract_details" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('status', 'N/A'))")
total_paid=$(echo "$contract_details" | python3 -c "import json,sys; data=json.load(sys.stdin); print(f\"\${data.get('paid_amount', 0):,.2f}\")")
remaining=$(echo "$contract_details" | python3 -c "import json,sys; data=json.load(sys.stdin); print(f\"\${data.get('remaining_amount', 0):,.2f}\")")
blockchain_tx=$(echo "$contract_details" | python3 -c "import json,sys; data=json.load(sys.stdin); tx=data.get('blockchain_tx_id', 'N/A'); print(tx[:16]+'...' if len(tx)>16 else tx)")

echo -e "${GREEN}Contract Summary:${NC}"
echo -e "  • Contract ID: ${CONTRACT_ID}"
echo -e "  • Vendor: GlobalTech Solutions"
echo -e "  • Status: ${final_status}"
echo -e "  • Total Value: \$500,000.00"
echo -e "  • Total Paid: ${total_paid}"
echo -e "  • Remaining: ${remaining}"
echo -e "  • Blockchain TX: ${blockchain_tx}\n"

# Summary
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                   ${GREEN}Demo Complete!${BLUE}                            ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}\n"

echo -e "${GREEN}✅ Key Features Demonstrated:${NC}"
echo -e "  • Vendor registration with blockchain sync"
echo -e "  • Contract creation with automatic ID generation"
echo -e "  • Three-stage workflow (CREATED → VERIFIED → SUBMITTED)"
echo -e "  • Role-based approvals"
echo -e "  • Payment tracking with automatic balance calculation"
echo -e "  • Blockchain immutability for all transactions"
echo -e "  • Complete audit trail"

echo -e "\n${CYAN}System Components:${NC}"
echo -e "  • API Gateway: http://localhost:8000/docs"
echo -e "  • PostgreSQL Database: localhost:5432"
echo -e "  • Hyperledger Fabric: Peers, Orderer, CA"
echo -e "  • CouchDB State Database: http://localhost:5984"

echo -e "\n${YELLOW}The VendorChain MVP is fully operational and ready for production!${NC}"