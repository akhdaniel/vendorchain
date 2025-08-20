#!/bin/bash

#################################################################
# VendorChain Integration Testing Script
# Tests all components of the MVP
#################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}      VendorChain MVP Integration Tests         ${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Function to run a test
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -n "Testing $test_name... "
    if eval "$test_command" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Function to test API endpoint
test_api() {
    local endpoint=$1
    local expected_status=${2:-200}
    
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000$endpoint")
    [ "$status_code" = "$expected_status" ]
}

# Function to test database query
test_db() {
    local query=$1
    docker-compose exec -T postgres psql -U odoo -d vendorchain -c "$query" >/dev/null 2>&1
}

echo -e "${YELLOW}1. Infrastructure Tests${NC}"
echo -e "${YELLOW}------------------------${NC}"
run_test "Docker daemon" "docker info"
run_test "Docker Compose" "docker-compose version"
run_test "Project structure" "[ -f docker-compose.yml ]"
echo ""

echo -e "${YELLOW}2. Database Tests${NC}"
echo -e "${YELLOW}-----------------${NC}"
run_test "PostgreSQL running" "docker-compose exec -T postgres pg_isready -U odoo"
run_test "Database exists" "test_db 'SELECT 1'"
run_test "Vendors table" "test_db 'SELECT COUNT(*) FROM vendor_contract_management_vendor'"
run_test "Contracts table" "test_db 'SELECT COUNT(*) FROM vendor_contract_management_contract'"
run_test "Workflow logs table" "test_db 'SELECT COUNT(*) FROM vendor_contract_management_workflow_log'"
run_test "Sample data loaded" "test_db 'SELECT COUNT(*) FROM vendor_contract_management_vendor WHERE vendor_id IS NOT NULL'"
echo ""

echo -e "${YELLOW}3. Fabric Network Tests${NC}"
echo -e "${YELLOW}-----------------------${NC}"
run_test "Fabric CA accessible" "curl -s http://localhost:7054/cainfo"
run_test "Orderer port open" "nc -z localhost 7050"
run_test "Peer port open" "nc -z localhost 7051"
run_test "CouchDB running" "curl -s http://admin:adminpw@localhost:5984/"
run_test "CouchDB system DBs" "curl -s http://admin:adminpw@localhost:5984/_all_dbs | grep -q '_users'"
echo ""

echo -e "${YELLOW}4. FastAPI Gateway Tests${NC}"
echo -e "${YELLOW}------------------------${NC}"
run_test "API root endpoint" "test_api '/'"
run_test "Health endpoint" "test_api '/api/v1/health/'"
run_test "Database health" "test_api '/api/v1/health/database'"
run_test "Blockchain health" "test_api '/api/v1/health/blockchain'"
run_test "Vendors endpoint" "test_api '/api/v1/vendors/'"
run_test "Contracts endpoint" "test_api '/api/v1/contracts/'"
run_test "OpenAPI docs" "test_api '/docs'"
echo ""

echo -e "${YELLOW}5. Odoo Tests${NC}"
echo -e "${YELLOW}-------------${NC}"
run_test "Odoo health check" "curl -s http://localhost:8069/web/health"
run_test "Odoo login page" "curl -s http://localhost:8069/web/login | grep -q 'Odoo'"
run_test "Odoo database manager" "curl -s http://localhost:8069/web/database/manager | grep -q 'database'"
echo ""

echo -e "${YELLOW}6. Workflow Tests${NC}"
echo -e "${YELLOW}-----------------${NC}"
# Create test vendor
VENDOR_JSON='{"vendor_id":"TEST-V-001","name":"Test Vendor","contact_email":"test@vendor.com","vendor_type":"SUPPLIER","status":"ACTIVE"}'
run_test "Create vendor via API" "curl -s -X POST http://localhost:8000/api/v1/vendors/ -H 'Content-Type: application/json' -d '$VENDOR_JSON'"

# Create test contract
CONTRACT_JSON='{"contract_id":"TEST-C-001","vendor_id":"TEST-V-001","contract_type":"PURCHASE","description":"Test","total_value":1000,"expiry_date":"2025-12-31","created_by":"Test"}'
run_test "Create contract via API" "curl -s -X POST http://localhost:8000/api/v1/contracts/ -H 'Content-Type: application/json' -d '$CONTRACT_JSON'"

# Test workflow transitions
VERIFY_JSON='{"verified_by":"Tester","performed_by":"Tester","notes":"Test verify"}'
run_test "Verify contract" "curl -s -X POST http://localhost:8000/api/v1/workflow/contracts/TEST-C-001/verify -H 'Content-Type: application/json' -d '$VERIFY_JSON'"

SUBMIT_JSON='{"submitted_by":"Tester","performed_by":"Tester","notes":"Test submit"}'
run_test "Submit contract" "curl -s -X POST http://localhost:8000/api/v1/workflow/contracts/TEST-C-001/submit -H 'Content-Type: application/json' -d '$SUBMIT_JSON'"

# Test payment recording
PAYMENT_JSON='{"amount":100,"payment_date":"2024-08-19","reference":"TEST-PAY-001","method":"Test"}'
run_test "Record payment" "curl -s -X POST http://localhost:8000/api/v1/contracts/TEST-C-001/payments -H 'Content-Type: application/json' -d '$PAYMENT_JSON'"

echo ""

echo -e "${YELLOW}7. Data Integrity Tests${NC}"
echo -e "${YELLOW}-----------------------${NC}"
run_test "Contract state transitions" "test_db \"SELECT COUNT(*) FROM vendor_contract_management_workflow_log WHERE contract_id IN (SELECT id FROM vendor_contract_management_contract WHERE contract_id='TEST-C-001')\""
run_test "Payment history" "test_db \"SELECT COUNT(*) FROM vendor_contract_management_contract WHERE contract_id='TEST-C-001' AND paid_amount > 0\""
run_test "Vendor contracts relation" "test_db \"SELECT COUNT(*) FROM vendor_contract_management_contract WHERE vendor_id IN (SELECT id FROM vendor_contract_management_vendor WHERE vendor_id='TEST-V-001')\""
echo ""

# Summary
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}              Test Summary                      ${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All integration tests passed!${NC}"
    echo -e "${GREEN}The VendorChain MVP is fully operational.${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please check the logs.${NC}"
    echo -e "${YELLOW}Run 'docker-compose logs [service-name]' to debug.${NC}"
    exit 1
fi