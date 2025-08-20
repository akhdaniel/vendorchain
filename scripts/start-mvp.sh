#!/bin/bash

#################################################################
# VendorChain MVP Startup Script
# This script starts all components for the MVP demo
#################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}     VendorChain MVP - Starting All Services    ${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for service
wait_for_service() {
    local service_name=$1
    local check_command=$2
    local max_attempts=30
    local attempt=0
    
    echo -n "Waiting for $service_name to be ready..."
    while [ $attempt -lt $max_attempts ]; do
        if eval "$check_command" >/dev/null 2>&1; then
            echo -e " ${GREEN}✓${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    echo -e " ${RED}✗${NC}"
    return 1
}

# Step 1: Check prerequisites
echo -e "${YELLOW}Step 1: Checking prerequisites...${NC}"
if ! command_exists docker; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

if ! command_exists docker-compose; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}Error: Docker daemon is not running${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites met${NC}"
echo ""

# Step 2: Clean up any existing containers
echo -e "${YELLOW}Step 2: Cleaning up existing containers...${NC}"
docker-compose down -v 2>/dev/null || true
echo -e "${GREEN}✓ Cleanup complete${NC}"
echo ""

# Step 3: Create necessary directories
echo -e "${YELLOW}Step 3: Creating necessary directories...${NC}"
mkdir -p fabric-network/organizations
mkdir -p fabric-network/channel-artifacts
mkdir -p scripts
mkdir -p odoo-addon
mkdir -p fastapi-gateway
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Step 4: Start PostgreSQL first
echo -e "${YELLOW}Step 4: Starting PostgreSQL database...${NC}"
docker-compose up -d postgres
wait_for_service "PostgreSQL" "docker-compose exec -T postgres pg_isready -U odoo"
echo ""

# Step 5: Apply database schema
echo -e "${YELLOW}Step 5: Applying database schema...${NC}"
if [ -f "scripts/schema.sql" ]; then
    docker-compose exec -T postgres psql -U odoo -d vendorchain < scripts/schema.sql 2>/dev/null || {
        echo -e "${YELLOW}Schema already exists or partially applied${NC}"
    }
    echo -e "${GREEN}✓ Database schema applied${NC}"
else
    echo -e "${YELLOW}Warning: schema.sql not found, skipping${NC}"
fi

# Apply sample data if exists
if [ -f "scripts/sample-data.sql" ]; then
    docker-compose exec -T postgres psql -U odoo -d vendorchain < scripts/sample-data.sql 2>/dev/null || {
        echo -e "${YELLOW}Sample data already exists or partially applied${NC}"
    }
    echo -e "${GREEN}✓ Sample data loaded${NC}"
fi
echo ""

# Step 6: Start Fabric network components
echo -e "${YELLOW}Step 6: Starting Hyperledger Fabric network...${NC}"
docker-compose up -d ca.org1.vendorchain.com
wait_for_service "Fabric CA" "curl -s http://localhost:7054/cainfo"

docker-compose up -d orderer.vendorchain.com
wait_for_service "Orderer" "nc -z localhost 7050"

docker-compose up -d couchdb
wait_for_service "CouchDB" "curl -s http://admin:adminpw@localhost:5984/"

docker-compose up -d peer0.org1.vendorchain.com
wait_for_service "Peer" "nc -z localhost 7051"
echo ""

# Step 7: Start FastAPI Gateway
echo -e "${YELLOW}Step 7: Starting FastAPI Gateway...${NC}"
docker-compose up -d fastapi-gateway
wait_for_service "FastAPI Gateway" "curl -s http://localhost:8000/health"
echo ""

# Step 8: Start Odoo
echo -e "${YELLOW}Step 8: Starting Odoo ERP...${NC}"
docker-compose up -d odoo
echo -e "${YELLOW}Note: Odoo may take 1-2 minutes to fully initialize${NC}"
wait_for_service "Odoo" "curl -s http://localhost:8069/web/health"
echo ""

# Step 9: Verify all services
echo -e "${YELLOW}Step 9: Verifying all services...${NC}"
echo ""

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U odoo >/dev/null 2>&1; then
    echo -e "  PostgreSQL:        ${GREEN}✓ Running${NC} (port 5432)"
else
    echo -e "  PostgreSQL:        ${RED}✗ Not responding${NC}"
fi

# Check Fabric CA
if curl -s http://localhost:7054/cainfo >/dev/null 2>&1; then
    echo -e "  Fabric CA:         ${GREEN}✓ Running${NC} (port 7054)"
else
    echo -e "  Fabric CA:         ${RED}✗ Not responding${NC}"
fi

# Check Orderer
if nc -z localhost 7050 2>/dev/null; then
    echo -e "  Fabric Orderer:    ${GREEN}✓ Running${NC} (port 7050)"
else
    echo -e "  Fabric Orderer:    ${RED}✗ Not responding${NC}"
fi

# Check Peer
if nc -z localhost 7051 2>/dev/null; then
    echo -e "  Fabric Peer:       ${GREEN}✓ Running${NC} (port 7051)"
else
    echo -e "  Fabric Peer:       ${RED}✗ Not responding${NC}"
fi

# Check CouchDB
if curl -s http://admin:adminpw@localhost:5984/ >/dev/null 2>&1; then
    echo -e "  CouchDB:           ${GREEN}✓ Running${NC} (port 5984)"
else
    echo -e "  CouchDB:           ${RED}✗ Not responding${NC}"
fi

# Check FastAPI
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo -e "  FastAPI Gateway:   ${GREEN}✓ Running${NC} (port 8000)"
else
    echo -e "  FastAPI Gateway:   ${RED}✗ Not responding${NC}"
fi

# Check Odoo
if curl -s http://localhost:8069/web/health >/dev/null 2>&1; then
    echo -e "  Odoo ERP:          ${GREEN}✓ Running${NC} (port 8069)"
else
    echo -e "  Odoo ERP:          ${YELLOW}⏳ Still starting${NC} (port 8069)"
fi

echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}       VendorChain MVP Started Successfully!    ${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "${GREEN}Access Points:${NC}"
echo -e "  • Odoo UI:           http://localhost:8069"
echo -e "  • FastAPI Docs:      http://localhost:8000/docs"
echo -e "  • CouchDB Admin:     http://localhost:5984/_utils"
echo -e "  • PostgreSQL:        localhost:5432"
echo ""
echo -e "${GREEN}Default Credentials:${NC}"
echo -e "  • Odoo:      admin / admin"
echo -e "  • PostgreSQL: odoo / odoo"
echo -e "  • CouchDB:    admin / adminpw"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "  1. Access Odoo at http://localhost:8069"
echo -e "  2. Install the 'Vendor Contract Management' module"
echo -e "  3. Configure user permissions and test the workflow"
echo -e "  4. Run demo scenario: ./scripts/run-demo.sh"
echo ""
echo -e "${BLUE}To stop all services, run:${NC} docker-compose down"
echo -e "${BLUE}To view logs, run:${NC} docker-compose logs -f [service-name]"
echo ""