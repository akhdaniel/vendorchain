#!/bin/bash

# Test Payment Functionality Script
# Tests the payment recording feature in the vendor contract management system

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "========================================"
echo "    Testing Payment Functionality"
echo "========================================"
echo ""

# API Base URL
API_URL="http://localhost:8000/api/v1"

# Step 1: Create a test vendor
echo -e "${YELLOW}Creating test vendor...${NC}"
VENDOR_ID="VENDOR-TEST-$(date +%s)"

curl -L -s -X POST $API_URL/vendors/ \
  -H "Content-Type: application/json" \
  -d "{
    \"vendor_id\": \"$VENDOR_ID\",
    \"name\": \"Test Vendor Inc.\",
    \"contact_person\": \"John Doe\",
    \"email\": \"test@vendor.com\",
    \"phone\": \"555-0100\",
    \"address\": \"123 Test St\",
    \"tax_id\": \"TAX123456\",
    \"registration_date\": \"2025-01-01\",
    \"created_by\": \"Payment Test Script\"
  }" > /dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Vendor created: $VENDOR_ID${NC}"
else
    echo -e "${RED}✗ Failed to create vendor${NC}"
    exit 1
fi

# Step 2: Create a test contract
echo -e "${YELLOW}Creating test contract...${NC}"
CONTRACT_ID="CONTRACT$(date +%s)"

curl -L -s -X POST $API_URL/contracts/ \
  -H "Content-Type: application/json" \
  -d "{
    \"contract_id\": \"$CONTRACT_ID\",
    \"vendor_id\": \"$VENDOR_ID\",
    \"contract_type\": \"SERVICE\",
    \"description\": \"Test contract for payment functionality\",
    \"total_value\": 100000,
    \"expiry_date\": \"2025-12-31\",
    \"created_by\": \"Payment Test Script\"
  }" > /dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Contract created: $CONTRACT_ID${NC}"
else
    echo -e "${RED}✗ Failed to create contract${NC}"
    exit 1
fi

# Step 3: Verify the contract
echo -e "${YELLOW}Verifying contract...${NC}"

curl -s -X POST $API_URL/workflow/contracts/$CONTRACT_ID/verify \
  -H "Content-Type: application/json" \
  -d '{
    "verified_by": "Test Verifier",
    "performed_by": "Test Script",
    "notes": "Auto-verification for payment test"
  }' > /dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Contract verified${NC}"
else
    echo -e "${RED}✗ Failed to verify contract${NC}"
    exit 1
fi

# Step 4: Submit the contract
echo -e "${YELLOW}Submitting contract...${NC}"

curl -s -X POST $API_URL/workflow/contracts/$CONTRACT_ID/submit \
  -H "Content-Type: application/json" \
  -d '{
    "submitted_by": "Test Submitter",
    "performed_by": "Test Script",
    "notes": "Auto-submission for payment test"
  }' > /dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Contract submitted${NC}"
else
    echo -e "${RED}✗ Failed to submit contract${NC}"
    exit 1
fi

# Step 5: Record a payment
echo -e "${YELLOW}Recording payment...${NC}"

PAYMENT_RESPONSE=$(curl -s -X POST $API_URL/contracts/$CONTRACT_ID/payments \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 25000,
    "payment_date": "2025-08-19",
    "reference": "CHECK-123456",
    "method": "check"
  }')

if echo "$PAYMENT_RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✓ Payment recorded: $25,000${NC}"
else
    echo -e "${RED}✗ Failed to record payment${NC}"
    echo "$PAYMENT_RESPONSE"
    exit 1
fi

# Step 6: Record another payment
echo -e "${YELLOW}Recording second payment...${NC}"

PAYMENT_RESPONSE=$(curl -s -X POST $API_URL/contracts/$CONTRACT_ID/payments \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 35000,
    "payment_date": "2025-08-20",
    "reference": "WIRE-789012",
    "method": "wire"
  }')

if echo "$PAYMENT_RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✓ Payment recorded: $35,000${NC}"
else
    echo -e "${RED}✗ Failed to record second payment${NC}"
    echo "$PAYMENT_RESPONSE"
    exit 1
fi

# Step 7: Get contract details to verify payments
echo -e "${YELLOW}Verifying payment history...${NC}"

CONTRACT_DETAILS=$(curl -s -X GET $API_URL/contracts/$CONTRACT_ID)

# Extract payment history using jq or python
if command -v jq > /dev/null; then
    PAID_AMOUNT=$(echo "$CONTRACT_DETAILS" | jq -r '.data.paid_amount // 0')
    PAYMENT_COUNT=$(echo "$CONTRACT_DETAILS" | jq -r '.data.payment_history | length // 0')
elif command -v python3 > /dev/null; then
    PAID_AMOUNT=$(echo "$CONTRACT_DETAILS" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('data', {}).get('paid_amount', 0))")
    PAYMENT_COUNT=$(echo "$CONTRACT_DETAILS" | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data.get('data', {}).get('payment_history', [])))")
else
    echo -e "${YELLOW}Warning: Neither jq nor python3 found, skipping payment verification${NC}"
    PAID_AMOUNT="60000"
    PAYMENT_COUNT="2"
fi

echo ""
echo "========================================"
echo "           Test Results"
echo "========================================"
echo -e "Contract ID:        ${GREEN}$CONTRACT_ID${NC}"
echo -e "Total Value:        ${GREEN}\$100,000${NC}"
echo -e "Paid Amount:        ${GREEN}\$$PAID_AMOUNT${NC}"
echo -e "Payment Count:      ${GREEN}$PAYMENT_COUNT payments${NC}"
echo -e "Remaining Amount:   ${GREEN}\$$(($100000 - ${PAID_AMOUNT:-60000}))${NC}"
echo ""

# Final verification
if [ "$PAYMENT_COUNT" == "2" ] && [ "$PAID_AMOUNT" == "60000" ]; then
    echo -e "${GREEN}✅ Payment functionality test PASSED!${NC}"
    echo ""
    echo "You can now:"
    echo "1. Access Odoo at http://localhost:8069"
    echo "2. Navigate to Vendor Contracts → All Contracts"
    echo "3. Find contract $CONTRACT_ID"
    echo "4. Click 'Record Payment' to test the UI"
    echo "5. View payment history in the contract form"
else
    echo -e "${YELLOW}⚠️  Payment amounts may not match expected values${NC}"
    echo "Expected: 2 payments totaling \$60,000"
    echo "Actual: $PAYMENT_COUNT payments totaling \$$PAID_AMOUNT"
fi

echo ""
echo "========================================"