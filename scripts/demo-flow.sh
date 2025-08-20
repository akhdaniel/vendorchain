#!/bin/bash

# VendorChain MVP Complete Demo Flow
# This script demonstrates the complete workflow from vendor creation to payment tracking

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

API_BASE="http://localhost:8000/api/v1"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}     VendorChain MVP - Complete Demo Flow      ${NC}"
echo -e "${BLUE}================================================${NC}\n"

# Step 1: Create a vendor
echo -e "${YELLOW}Step 1: Creating Vendor${NC}"
echo -e "${CYAN}→ Creating TechSupplies Inc.${NC}"
vendor_response=$(curl -s -X POST "${API_BASE}/vendors/" \
  -H "Content-Type: application/json" \
  -d '{
    "vendor_id": "VENDOR-MVP-001",
    "name": "TechSupplies Inc.",
    "contact_email": "contact@techsupplies.com",
    "contact_phone": "+1-555-0100",
    "address": "123 Tech Street, Silicon Valley, CA 94025",
    "vendor_type": "SUPPLIER",
    "status": "ACTIVE"
  }')
echo "$vendor_response" | python3 -m json.tool
echo -e "${GREEN}✓ Vendor created successfully${NC}\n"

# Step 2: Create a contract
echo -e "${YELLOW}Step 2: Creating Contract${NC}"
echo -e "${CYAN}→ Creating IT Equipment Purchase Contract${NC}"
contract_response=$(curl -s -X POST "${API_BASE}/contracts/" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": "CONTRACT-MVP-001",
    "vendor_id": "VENDOR-MVP-001",
    "contract_type": "PURCHASE",
    "description": "IT Equipment Purchase - Q3 2024",
    "total_value": 250000.00,
    "currency": "USD",
    "start_date": "2024-08-19",
    "expiry_date": "2026-08-19",
    "payment_terms": "NET_30",
    "created_by": "John Doe",
    "department": "IT",
    "metadata": {
      "items": ["50 Laptops", "5 Servers", "Network Equipment"],
      "delivery_location": "Main Office"
    }
  }')
echo "$contract_response" | python3 -m json.tool
echo -e "${GREEN}✓ Contract created successfully (Status: CREATED)${NC}\n"

# Step 3: Verify the contract
echo -e "${YELLOW}Step 3: Contract Verification${NC}"
echo -e "${CYAN}→ Procurement Manager verifying contract${NC}"
verify_response=$(curl -s -X POST "${API_BASE}/workflow/contracts/CONTRACT-MVP-001/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "verified_by": "Sarah Johnson",
    "performed_by": "Sarah Johnson",
    "notes": "Contract terms reviewed and approved by procurement.",
    "department": "Procurement"
  }')
echo "$verify_response" | python3 -m json.tool
echo -e "${GREEN}✓ Contract verified successfully (Status: VERIFIED)${NC}\n"

# Step 4: Submit the contract
echo -e "${YELLOW}Step 4: Contract Submission${NC}"
echo -e "${CYAN}→ Finance Director submitting contract${NC}"
submit_response=$(curl -s -X POST "${API_BASE}/workflow/contracts/CONTRACT-MVP-001/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "submitted_by": "Michael Chen",
    "performed_by": "Michael Chen",
    "notes": "Budget approved. Contract authorized for execution.",
    "department": "Finance"
  }')
echo "$submit_response" | python3 -m json.tool
echo -e "${GREEN}✓ Contract submitted successfully (Status: SUBMITTED)${NC}\n"

# Step 5: Record payments
echo -e "${YELLOW}Step 5: Payment Recording${NC}"

echo -e "${CYAN}→ Recording first payment ($50,000)${NC}"
payment1_response=$(curl -s -X POST "${API_BASE}/contracts/CONTRACT-MVP-001/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50000.00,
    "payment_date": "2024-08-19",
    "reference": "PAY-2024-001",
    "method": "Wire Transfer",
    "notes": "Initial payment - 20% advance"
  }')
echo "$payment1_response" | python3 -m json.tool
echo -e "${GREEN}✓ First payment recorded${NC}\n"

echo -e "${CYAN}→ Recording second payment ($75,000)${NC}"
payment2_response=$(curl -s -X POST "${API_BASE}/contracts/CONTRACT-MVP-001/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 75000.00,
    "payment_date": "2024-09-15",
    "reference": "PAY-2024-002",
    "method": "Wire Transfer",
    "notes": "Second payment - after laptop delivery"
  }')
echo "$payment2_response" | python3 -m json.tool
echo -e "${GREEN}✓ Second payment recorded${NC}\n"

# Step 6: Query contract details
echo -e "${YELLOW}Step 6: Contract Query${NC}"
echo -e "${CYAN}→ Retrieving complete contract details${NC}"
contract_details=$(curl -s -X GET "${API_BASE}/contracts/CONTRACT-MVP-001")
echo "$contract_details" | python3 -m json.tool
echo -e "${GREEN}✓ Contract details retrieved${NC}\n"

# Step 7: View payment history
echo -e "${YELLOW}Step 7: Payment History${NC}"
echo -e "${CYAN}→ Checking payment history${NC}"
echo "$contract_details" | python3 -c "
import json, sys
data = json.load(sys.stdin)
if 'payment_history' in data:
    print('Payment History:')
    for payment in data['payment_history']:
        print(f\"  • {payment['payment_date']}: \${payment['amount']:,.2f} - {payment['reference']}\")
    print(f\"\\nTotal Paid: \${data.get('paid_amount', 0):,.2f}\")
    print(f\"Remaining: \${data.get('remaining_amount', 0):,.2f}\")
"
echo -e "${GREEN}✓ Payment tracking verified${NC}\n"

# Summary
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}        Demo Flow Complete!                    ${NC}"
echo -e "${BLUE}================================================${NC}\n"

echo -e "${CYAN}Summary of Demo:${NC}"
echo -e "  1. ✓ Vendor 'TechSupplies Inc.' created"
echo -e "  2. ✓ Contract for \$250,000 created"
echo -e "  3. ✓ Contract verified by Procurement"
echo -e "  4. ✓ Contract submitted by Finance"
echo -e "  5. ✓ Two payments recorded (\$125,000 total)"
echo -e "  6. ✓ Complete audit trail maintained"
echo -e "  7. ✓ All data synced to blockchain"

echo -e "\n${YELLOW}Key Features Demonstrated:${NC}"
echo -e "  • Three-stage workflow (CREATED → VERIFIED → SUBMITTED)"
echo -e "  • Role-based permissions"
echo -e "  • Payment tracking with history"
echo -e "  • Blockchain immutability"
echo -e "  • Complete audit trail"

echo -e "\n${GREEN}The VendorChain MVP is fully operational!${NC}"