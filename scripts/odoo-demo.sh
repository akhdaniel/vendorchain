#!/bin/bash

# Odoo-Blockchain Integration Demo
# This script demonstrates the complete integration between Odoo and blockchain

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    ${YELLOW}VendorChain - Odoo Blockchain Integration Demo${BLUE}          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}\n"

# Step 1: Check Services
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 1: Checking All Services${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check PostgreSQL
echo -e "${CYAN}→ PostgreSQL Database${NC}"
if docker-compose exec -T postgres pg_isready -U odoo &>/dev/null; then
    echo -e "  ${GREEN}✓ Running${NC}"
else
    echo -e "  ${RED}✗ Not running${NC}"
fi

# Check FastAPI
echo -e "${CYAN}→ FastAPI Gateway${NC}"
if curl -s http://localhost:8000/api/v1/health/ | grep -q "healthy"; then
    echo -e "  ${GREEN}✓ Running (http://localhost:8000/docs)${NC}"
else
    echo -e "  ${RED}✗ Not running${NC}"
fi

# Check Fabric Network
echo -e "${CYAN}→ Hyperledger Fabric${NC}"
if curl -s http://localhost:8000/api/v1/health/blockchain | grep -q "connected"; then
    echo -e "  ${GREEN}✓ Connected${NC}"
else
    echo -e "  ${RED}✗ Not connected${NC}"
fi

# Check Odoo
echo -e "${CYAN}→ Odoo ERP${NC}"
if docker ps | grep -q vendorchain-odoo; then
    echo -e "  ${GREEN}✓ Running (http://localhost:8069)${NC}"
else
    echo -e "  ${RED}✗ Not running${NC}"
fi
echo ""

# Step 2: Odoo Setup Instructions
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 2: Odoo Setup Instructions${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${CYAN}To set up Odoo with blockchain integration:${NC}\n"

echo -e "${GREEN}1. Database Setup:${NC}"
echo -e "   • Open: http://localhost:8069"
echo -e "   • Click 'Create Database'"
echo -e "   • Database Name: vendorchain"
echo -e "   • Email: admin@vendorchain.com"
echo -e "   • Password: admin"
echo -e "   • Language: English"
echo -e "   • Country: United States"
echo -e "   • Click 'Create Database'\n"

echo -e "${GREEN}2. Install VendorChain Addon:${NC}"
echo -e "   • After login, go to Apps menu"
echo -e "   • Remove 'Apps' filter to see all modules"
echo -e "   • Search for 'Vendor Contract Management'"
echo -e "   • Click 'Install'"
echo -e "   • Wait for installation to complete\n"

echo -e "${GREEN}3. Configure User Roles:${NC}"
echo -e "   • Go to Settings → Users & Companies → Users"
echo -e "   • Edit Admin user"
echo -e "   • In 'Vendor Contract Management' section"
echo -e "   • Select 'Manager' role"
echo -e "   • Save changes\n"

# Step 3: Integration Features
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 3: Integration Features${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${CYAN}The Odoo addon provides:${NC}\n"

echo -e "${GREEN}📋 Vendor Management:${NC}"
echo -e "   • Create and manage vendors"
echo -e "   • Auto-generate vendor IDs (VENDOR-XXXXX)"
echo -e "   • Sync vendors to blockchain"
echo -e "   • Track blockchain identity\n"

echo -e "${GREEN}📄 Contract Management:${NC}"
echo -e "   • Create contracts with auto-ID (CONTRACTXXXXXXX)"
echo -e "   • Three-stage workflow:"
echo -e "     - CREATED (initial state)"
echo -e "     - VERIFIED (procurement approval)"
echo -e "     - SUBMITTED (finance approval)"
echo -e "   • Real-time blockchain sync"
echo -e "   • Transaction ID tracking\n"

echo -e "${GREEN}💰 Payment Tracking:${NC}"
echo -e "   • Record payments against contracts"
echo -e "   • Automatic balance calculation"
echo -e "   • Payment history in JSON format"
echo -e "   • Blockchain immutability\n"

echo -e "${GREEN}🔄 Blockchain Integration:${NC}"
echo -e "   • All actions recorded on Hyperledger Fabric"
echo -e "   • Immutable audit trail"
echo -e "   • Smart contract enforcement"
echo -e "   • Real-time synchronization\n"

# Step 4: Demo Workflow
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 4: Demo Workflow in Odoo${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${CYAN}Once the addon is installed, follow this workflow:${NC}\n"

echo -e "${GREEN}1. Test API Connection:${NC}"
echo -e "   • Go to Vendor Contracts → Configuration → Test API Connection"
echo -e "   • Click to verify blockchain connectivity\n"

echo -e "${GREEN}2. Create a Vendor:${NC}"
echo -e "   • Go to Vendor Contracts → Vendors → Create"
echo -e "   • Enter vendor details"
echo -e "   • Save (auto-generates VENDOR-XXXXX ID)"
echo -e "   • Check 'Blockchain' button for sync status\n"

echo -e "${GREEN}3. Create a Contract:${NC}"
echo -e "   • Go to Vendor Contracts → Contracts → Create"
echo -e "   • Select vendor"
echo -e "   • Enter contract details"
echo -e "   • Save (auto-generates CONTRACTXXXXXXX ID)"
echo -e "   • Status: CREATED\n"

echo -e "${GREEN}4. Verify Contract (as Procurement Manager):${NC}"
echo -e "   • Open the contract"
echo -e "   • Click 'Verify' button"
echo -e "   • Status changes to VERIFIED"
echo -e "   • Blockchain transaction recorded\n"

echo -e "${GREEN}5. Submit Contract (as Finance Director):${NC}"
echo -e "   • Click 'Submit' button"
echo -e "   • Status changes to SUBMITTED"
echo -e "   • Contract ready for execution\n"

echo -e "${GREEN}6. Record Payment:${NC}"
echo -e "   • Click 'Record Payment' button"
echo -e "   • Enter payment details"
echo -e "   • Save"
echo -e "   • Payment synced to blockchain\n"

# Step 5: Verification
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 5: Verify Blockchain Integration${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${CYAN}You can verify the blockchain integration by:${NC}\n"

echo -e "${GREEN}In Odoo:${NC}"
echo -e "   • Check 'Blockchain Info' tab in contracts"
echo -e "   • View Transaction ID (blockchain_tx_id)"
echo -e "   • See workflow history\n"

echo -e "${GREEN}Via API:${NC}"
echo -e "   • Open http://localhost:8000/docs"
echo -e "   • Use GET /api/v1/contracts/{contract_id}"
echo -e "   • Verify blockchain_tx_id matches\n"

echo -e "${GREEN}In CouchDB:${NC}"
echo -e "   • Open http://localhost:5984/_utils"
echo -e "   • Login: admin / adminpw"
echo -e "   • Browse contract documents\n"

# Summary
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                   ${GREEN}Integration Ready!${BLUE}                        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}\n"

echo -e "${GREEN}✅ System Components:${NC}"
echo -e "  • Odoo ERP: http://localhost:8069 (admin/admin)"
echo -e "  • API Gateway: http://localhost:8000/docs"
echo -e "  • Blockchain: Hyperledger Fabric 2.5.4"
echo -e "  • Database: PostgreSQL 15"
echo -e "  • State DB: CouchDB 3.3\n"

echo -e "${YELLOW}The VendorChain Odoo-Blockchain integration is ready for demonstration!${NC}"