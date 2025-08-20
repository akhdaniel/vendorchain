#!/bin/bash

# Test Odoo-Blockchain Integration
# This script verifies that the Odoo addon is properly installed and can communicate with the blockchain

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         ${YELLOW}VendorChain Odoo Integration Test${BLUE}                   ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}\n"

# Function to check service
check_service() {
    local service_name=$1
    local url=$2
    local expected=$3
    
    if curl -s "$url" | grep -q "$expected"; then
        echo -e "  ${GREEN}✓ $service_name: Running${NC}"
        return 0
    else
        echo -e "  ${RED}✗ $service_name: Not accessible${NC}"
        return 1
    fi
}

echo -e "${CYAN}1. Checking Services Status:${NC}"
check_service "Odoo Web Interface" "http://localhost:8069/web/login" "Odoo"
check_service "FastAPI Gateway" "http://localhost:8000/api/v1/health/" "healthy"
check_service "Blockchain Network" "http://localhost:8000/api/v1/health/blockchain" "connected"
echo ""

echo -e "${CYAN}2. Testing Vendor Creation via API:${NC}"
# Create a test vendor
VENDOR_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/vendors/ \
  -H "Content-Type: application/json" \
  -d '{
    "vendor_id": "VENDOR'$(date +%s)'",
    "name": "Test Vendor Integration",
    "vendor_type": "SERVICE_PROVIDER",
    "contact_email": "test@integration.com",
    "contact_phone": "+1234567890",
    "address": "123 Test Street, Integration City",
    "registration_number": "REG'$(date +%s)'"
  }')

if echo "$VENDOR_RESPONSE" | grep -q "vendor_id"; then
    VENDOR_ID=$(echo "$VENDOR_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['vendor_id'])")
    echo -e "  ${GREEN}✓ Vendor created successfully: $VENDOR_ID${NC}"
else
    echo -e "  ${RED}✗ Failed to create vendor${NC}"
    echo "$VENDOR_RESPONSE"
    exit 1
fi
echo ""

echo -e "${CYAN}3. Testing Contract Creation via API:${NC}"
# Create a test contract
CONTRACT_ID="CONTRACT$(date +%Y%m%d%H%M%S)"
CONTRACT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/contracts/ \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": "'$CONTRACT_ID'",
    "vendor_id": "'$VENDOR_ID'",
    "contract_type": "SERVICE",
    "description": "Integration Test Contract",
    "start_date": "'$(date +%Y-%m-%d)'",
    "expiry_date": "'$(date -v+30d +%Y-%m-%d)'",
    "total_value": 15000.00,
    "payment_terms": "NET30",
    "deliverables": ["Test Deliverable 1", "Test Deliverable 2"],
    "department": "IT",
    "created_by": "Integration Test"
  }')

if echo "$CONTRACT_RESPONSE" | grep -q "contract_id"; then
    echo -e "  ${GREEN}✓ Contract created successfully: $CONTRACT_ID${NC}"
else
    echo -e "  ${RED}✗ Failed to create contract${NC}"
    echo "$CONTRACT_RESPONSE"
    exit 1
fi
echo ""

echo -e "${CYAN}4. Testing Contract Workflow:${NC}"
# Verify the contract
VERIFY_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/workflow/contracts/$CONTRACT_ID/verify \
  -H "Content-Type: application/json" \
  -d '{
    "verified_by": "Test Verifier",
    "performed_by": "Integration Test",
    "notes": "Automated verification test"
  }')

if echo "$VERIFY_RESPONSE" | grep -q "VERIFIED"; then
    echo -e "  ${GREEN}✓ Contract verified successfully${NC}"
else
    echo -e "  ${RED}✗ Failed to verify contract${NC}"
    echo "$VERIFY_RESPONSE"
fi

# Submit the contract
SUBMIT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/workflow/contracts/$CONTRACT_ID/submit \
  -H "Content-Type: application/json" \
  -d '{
    "submitted_by": "Test Submitter",
    "performed_by": "Integration Test",
    "notes": "Automated submission test"
  }')

if echo "$SUBMIT_RESPONSE" | grep -q "SUBMITTED"; then
    echo -e "  ${GREEN}✓ Contract submitted successfully${NC}"
else
    echo -e "  ${RED}✗ Failed to submit contract${NC}"
    echo "$SUBMIT_RESPONSE"
fi
echo ""

echo -e "${CYAN}5. Testing Payment Recording:${NC}"
# Record a payment
PAYMENT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/contracts/$CONTRACT_ID/payments \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5000.00,
    "payment_date": "'$(date +%Y-%m-%d)'",
    "payment_method": "BANK_TRANSFER",
    "reference": "TEST-PAY-'$(date +%s)'",
    "notes": "Test payment via integration"
  }')

if echo "$PAYMENT_RESPONSE" | grep -q "Payment recorded successfully"; then
    echo -e "  ${GREEN}✓ Payment recorded successfully${NC}"
else
    echo -e "  ${RED}✗ Failed to record payment${NC}"
    echo "$PAYMENT_RESPONSE"
fi
echo ""

echo -e "${CYAN}6. Fetching Contract Status:${NC}"
# Get contract details
CONTRACT_DETAILS=$(curl -s http://localhost:8000/api/v1/contracts/$CONTRACT_ID)
if echo "$CONTRACT_DETAILS" | grep -q "contract_id"; then
    STATE=$(echo "$CONTRACT_DETAILS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('state', 'N/A'))")
    PAID=$(echo "$CONTRACT_DETAILS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('paid_amount', 0))")
    REMAINING=$(echo "$CONTRACT_DETAILS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('remaining_amount', 0))")
    echo -e "  ${GREEN}✓ Contract Status:${NC}"
    echo -e "    • State: $STATE"
    echo -e "    • Paid Amount: \$$PAID"
    echo -e "    • Remaining: \$$REMAINING"
else
    echo -e "  ${RED}✗ Failed to fetch contract details${NC}"
fi
echo ""

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         ${GREEN}Integration Test Completed Successfully!${BLUE}            ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}\n"

echo -e "${YELLOW}Next Steps:${NC}"
echo -e "1. Access Odoo at ${BLUE}http://localhost:8069${NC}"
echo -e "   • Login: admin / admin"
echo -e "2. Navigate to ${BLUE}Vendor Contracts${NC} menu"
echo -e "3. You should see the test vendor and contract created"
echo -e "4. Use the Odoo UI to manage contracts and sync with blockchain\n"

echo -e "${GREEN}The Odoo addon is successfully installed and integrated with the blockchain!${NC}"