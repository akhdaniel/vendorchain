#!/bin/bash

#################################################################
# VendorChain MVP Demo Script
# This script demonstrates the complete workflow
#################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# API Base URL
API_BASE="http://localhost:8000/api/v1"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}        VendorChain MVP Demo Scenario           ${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Function to make API call and pretty print
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -e "${CYAN}→ $description${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -X GET "$API_BASE/$endpoint" -H "Content-Type: application/json")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -X POST "$API_BASE/$endpoint" -H "Content-Type: application/json" -d "$data")
    elif [ "$method" = "PUT" ]; then
        response=$(curl -s -X PUT "$API_BASE/$endpoint" -H "Content-Type: application/json" -d "$data")
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}  ✓ Success${NC}"
        if command -v python3 >/dev/null 2>&1; then
            echo "$response" | python3 -m json.tool 2>/dev/null | head -20 || echo "$response"
        else
            echo "$response"
        fi
    else
        echo -e "${RED}  ✗ Failed${NC}"
        return 1
    fi
    echo ""
}

# Function to pause between steps
pause_demo() {
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read -r
    echo ""
}

# Step 1: Check system health
echo -e "${YELLOW}Step 1: System Health Check${NC}"
echo -e "${YELLOW}================================${NC}"
api_call "GET" "health" "" "Checking API Gateway health"
api_call "GET" "health/database" "" "Checking database connectivity"
api_call "GET" "health/blockchain" "" "Checking blockchain connectivity"
pause_demo

# Step 2: Create a vendor
echo -e "${YELLOW}Step 2: Vendor Registration${NC}"
echo -e "${YELLOW}================================${NC}"
VENDOR_DATA='{
  "vendor_id": "VENDOR-DEMO-001",
  "name": "TechSupplies Inc.",
  "registration_number": "REG-2024-001",
  "contact_email": "contact@techsupplies.com",
  "contact_phone": "+1-555-0123",
  "address": "123 Tech Street, Silicon Valley, CA 94025",
  "vendor_type": "SUPPLIER",
  "status": "ACTIVE"
}'
api_call "POST" "vendors" "$VENDOR_DATA" "Creating new vendor: TechSupplies Inc."
pause_demo

# Step 3: Create a contract
echo -e "${YELLOW}Step 3: Contract Creation${NC}"
echo -e "${YELLOW}================================${NC}"
CONTRACT_DATA='{
  "contract_id": "CONTRACT-DEMO-001",
  "vendor_id": "VENDOR-DEMO-001",
  "contract_type": "PURCHASE",
  "description": "Annual IT equipment supply contract for laptops, monitors, and accessories",
  "total_value": 250000.00,
  "expiry_date": "2025-12-31",
  "created_by": "John Doe (Procurement Manager)",
  "document_hash": "sha256:abcdef1234567890"
}'
api_call "POST" "contracts" "$CONTRACT_DATA" "Creating new contract for TechSupplies Inc."
pause_demo

# Step 4: View contract details
echo -e "${YELLOW}Step 4: Contract Details${NC}"
echo -e "${YELLOW}================================${NC}"
api_call "GET" "contracts/CONTRACT-DEMO-001" "" "Retrieving contract details"
pause_demo

# Step 5: Verify the contract
echo -e "${YELLOW}Step 5: Contract Verification (Procurement Manager)${NC}"
echo -e "${YELLOW}================================${NC}"
VERIFY_DATA='{
  "verified_by": "Jane Smith (Procurement Manager)",
  "performed_by": "Jane Smith",
  "notes": "Contract terms reviewed and approved. Vendor credentials verified."
}'
api_call "POST" "workflow/contracts/CONTRACT-DEMO-001/verify" "$VERIFY_DATA" "Verifying contract"
pause_demo

# Step 6: Submit the contract
echo -e "${YELLOW}Step 6: Contract Submission (Finance Team)${NC}"
echo -e "${YELLOW}================================${NC}"
SUBMIT_DATA='{
  "submitted_by": "Mike Johnson (Finance Director)",
  "performed_by": "Mike Johnson",
  "notes": "Budget approved. Contract submitted for execution."
}'
api_call "POST" "workflow/contracts/CONTRACT-DEMO-001/submit" "$SUBMIT_DATA" "Submitting contract"
pause_demo

# Step 7: Record a payment
echo -e "${YELLOW}Step 7: Payment Recording${NC}"
echo -e "${YELLOW}================================${NC}"
PAYMENT_DATA='{
  "amount": 50000.00,
  "payment_date": "2024-08-19",
  "reference": "PAY-2024-001",
  "method": "Wire Transfer"
}'
api_call "POST" "contracts/CONTRACT-DEMO-001/payments" "$PAYMENT_DATA" "Recording first payment of $50,000"
pause_demo

# Step 8: View workflow history
echo -e "${YELLOW}Step 8: Workflow History${NC}"
echo -e "${YELLOW}================================${NC}"
api_call "GET" "contracts/CONTRACT-DEMO-001/workflow-logs" "" "Viewing contract workflow history"
pause_demo

# Step 9: List all contracts
echo -e "${YELLOW}Step 9: Contract Dashboard View${NC}"
echo -e "${YELLOW}================================${NC}"
api_call "GET" "contracts?limit=5" "" "Listing all contracts"
pause_demo

# Step 10: Summary
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}         Demo Scenario Complete!                ${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "${GREEN}What we demonstrated:${NC}"
echo -e "  ✓ Vendor registration with blockchain sync"
echo -e "  ✓ Contract creation with initial CREATED state"
echo -e "  ✓ Contract verification by Procurement Manager"
echo -e "  ✓ Contract submission by Finance Team"
echo -e "  ✓ Payment recording and tracking"
echo -e "  ✓ Complete audit trail via workflow logs"
echo -e "  ✓ Real-time blockchain synchronization"
echo ""
echo -e "${CYAN}Contract Workflow States:${NC}"
echo -e "  CREATED → VERIFIED → SUBMITTED ✓"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "  1. Access Odoo UI to see the visual representation"
echo -e "  2. Check blockchain explorer for transaction details"
echo -e "  3. View CouchDB for state database"
echo -e "  4. Explore API documentation at http://localhost:8000/docs"
echo ""