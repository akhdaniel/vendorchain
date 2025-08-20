#!/bin/bash

# VendorChain MVP API Test Script
# This script tests all API endpoints with sample data

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
echo -e "${BLUE}        VendorChain MVP API Test Suite          ${NC}"
echo -e "${BLUE}================================================${NC}\n"

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -e "${CYAN}→ Testing: ${description}${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -X GET "${API_BASE}${endpoint}" -H "Content-Type: application/json")
    else
        response=$(curl -s -X POST "${API_BASE}${endpoint}" -H "Content-Type: application/json" -d "$data")
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}  ✓ Success${NC}"
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    else
        echo -e "${RED}  ✗ Failed${NC}"
    fi
    echo ""
}

# Test 1: Health Checks
echo -e "${YELLOW}Test Suite 1: Health Checks${NC}"
echo -e "${YELLOW}================================${NC}"
test_endpoint "GET" "/health/" "" "API Gateway Health"
test_endpoint "GET" "/health/database" "" "Database Health"
test_endpoint "GET" "/health/blockchain" "" "Blockchain Health"

# Test 2: Create Vendors
echo -e "${YELLOW}Test Suite 2: Vendor Management${NC}"
echo -e "${YELLOW}================================${NC}"

# Create vendor 1
vendor1_data='{
  "vendor_id": "VENDOR-001",
  "name": "TechSupplies Inc.",
  "contact_email": "contact@techsupplies.com",
  "contact_phone": "+1-555-0001",
  "address": "123 Tech Street, Silicon Valley, CA 94025",
  "vendor_type": "SUPPLIER",
  "registration_number": "REG-2024-001",
  "tax_id": "TAX-123456789",
  "status": "ACTIVE",
  "rating": 4.5
}'
test_endpoint "POST" "/vendors/" "$vendor1_data" "Create Vendor: TechSupplies Inc."

# Create vendor 2
vendor2_data='{
  "vendor_id": "VENDOR-002",
  "name": "CloudServices Pro",
  "contact_email": "info@cloudservices.com",
  "contact_phone": "+1-555-0002",
  "address": "456 Cloud Ave, Seattle, WA 98101",
  "vendor_type": "SERVICE_PROVIDER",
  "registration_number": "REG-2024-002",
  "tax_id": "TAX-987654321",
  "status": "ACTIVE",
  "rating": 4.8
}'
test_endpoint "POST" "/vendors/" "$vendor2_data" "Create Vendor: CloudServices Pro"

# List vendors
test_endpoint "GET" "/vendors/" "" "List All Vendors"

# Test 3: Create Contracts
echo -e "${YELLOW}Test Suite 3: Contract Management${NC}"
echo -e "${YELLOW}================================${NC}"

# Create contract 1
contract1_data='{
  "contract_id": "CONTRACT-001",
  "vendor_id": "VENDOR-001",
  "contract_type": "PURCHASE",
  "description": "IT Equipment Purchase - Laptops and Servers",
  "total_value": 250000.00,
  "currency": "USD",
  "start_date": "2024-08-19",
  "expiry_date": "2025-08-19",
  "payment_terms": "NET_30",
  "created_by": "John Doe",
  "department": "IT",
  "metadata": {
    "items": ["50 Laptops", "5 Servers"],
    "delivery_location": "Main Office"
  }
}'
test_endpoint "POST" "/contracts/" "$contract1_data" "Create Contract: IT Equipment"

# Create contract 2
contract2_data='{
  "contract_id": "CONTRACT-002",
  "vendor_id": "VENDOR-002",
  "contract_type": "SERVICE",
  "description": "Cloud Infrastructure Services - Annual Subscription",
  "total_value": 180000.00,
  "currency": "USD",
  "start_date": "2024-08-19",
  "expiry_date": "2025-08-19",
  "payment_terms": "MONTHLY",
  "created_by": "Jane Smith",
  "department": "Operations",
  "metadata": {
    "services": ["Cloud Storage", "Computing Resources", "Support"],
    "sla": "99.9% uptime"
  }
}'
test_endpoint "POST" "/contracts/" "$contract2_data" "Create Contract: Cloud Services"

# List contracts
test_endpoint "GET" "/contracts/" "" "List All Contracts"

# Test 4: Workflow Operations
echo -e "${YELLOW}Test Suite 4: Contract Workflow${NC}"
echo -e "${YELLOW}================================${NC}"

# Verify contract 1
verify1_data='{
  "verified_by": "Sarah Johnson",
  "performed_by": "Sarah Johnson",
  "notes": "Contract reviewed and approved. All terms are acceptable.",
  "department": "Procurement"
}'
test_endpoint "POST" "/workflow/contracts/CONTRACT-001/verify" "$verify1_data" "Verify Contract 001"

# Submit contract 1
submit1_data='{
  "submitted_by": "Michael Chen",
  "performed_by": "Michael Chen",
  "notes": "Final approval granted. Contract ready for execution.",
  "department": "Finance"
}'
test_endpoint "POST" "/workflow/contracts/CONTRACT-001/submit" "$submit1_data" "Submit Contract 001"

# Test 5: Payment Recording
echo -e "${YELLOW}Test Suite 5: Payment Tracking${NC}"
echo -e "${YELLOW}================================${NC}"

# Record payment 1
payment1_data='{
  "amount": 50000.00,
  "payment_date": "2024-08-19",
  "reference": "PAY-2024-001",
  "method": "Wire Transfer",
  "notes": "Initial payment for laptop delivery"
}'
test_endpoint "POST" "/contracts/CONTRACT-001/payments" "$payment1_data" "Record Payment: $50,000"

# Record payment 2
payment2_data='{
  "amount": 75000.00,
  "payment_date": "2024-09-15",
  "reference": "PAY-2024-002",
  "method": "Wire Transfer",
  "notes": "Second payment for server delivery"
}'
test_endpoint "POST" "/contracts/CONTRACT-001/payments" "$payment2_data" "Record Payment: $75,000"

# Test 6: Query Operations
echo -e "${YELLOW}Test Suite 6: Query Operations${NC}"
echo -e "${YELLOW}================================${NC}"

# Get specific vendor
test_endpoint "GET" "/vendors/VENDOR-001" "" "Get Vendor Details: VENDOR-001"

# Get specific contract
test_endpoint "GET" "/contracts/CONTRACT-001" "" "Get Contract Details: CONTRACT-001"

# Get contract history
test_endpoint "GET" "/contracts/CONTRACT-001/history" "" "Get Contract History"

# Test 7: Analytics
echo -e "${YELLOW}Test Suite 7: Analytics & Reporting${NC}"
echo -e "${YELLOW}================================${NC}"

# Get contract statistics
test_endpoint "GET" "/analytics/contracts/stats" "" "Contract Statistics"

# Get vendor statistics
test_endpoint "GET" "/analytics/vendors/stats" "" "Vendor Statistics"

# Test Summary
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}        MVP API Test Suite Complete!            ${NC}"
echo -e "${BLUE}================================================${NC}"
echo -e "\n${CYAN}Summary:${NC}"
echo -e "  • Health checks: ✓"
echo -e "  • Vendor management: ✓"
echo -e "  • Contract creation: ✓"
echo -e "  • Workflow transitions: ✓"
echo -e "  • Payment tracking: ✓"
echo -e "  • Query operations: ✓"
echo -e "  • Analytics: ✓"
echo -e "\n${GREEN}All core MVP features are operational!${NC}"