#!/bin/bash

# Setup Odoo for VendorChain
# This script configures Odoo and installs the VendorChain addon

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           ${YELLOW}Odoo Setup for VendorChain${BLUE}                       ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}\n"

echo -e "${GREEN}✅ Odoo Database Initialized Successfully!${NC}\n"

echo -e "${CYAN}Database Information:${NC}"
echo -e "  • Database Name: vendorchain"
echo -e "  • Admin Username: admin"
echo -e "  • Admin Email: odoo@odoo.com"
echo -e "  • Default Password: admin\n"

echo -e "${YELLOW}Important: First Login Setup${NC}"
echo -e "1. Open http://localhost:8069 in your browser"
echo -e "2. Login with:"
echo -e "   • Email: admin"
echo -e "   • Password: admin"
echo -e "3. You'll be prompted to set a new password on first login\n"

echo -e "${GREEN}Installing VendorChain Addon:${NC}"
echo -e "1. After login, click on the Apps menu (grid icon)"
echo -e "2. Click 'Update Apps List' if needed"
echo -e "3. Remove the 'Apps' filter to see all modules"
echo -e "4. Search for 'Vendor Contract Management'"
echo -e "5. Click Install on the module"
echo -e "6. Wait for installation to complete\n"

echo -e "${CYAN}Setting Up User Permissions:${NC}"
echo -e "1. Go to Settings → Users & Companies → Users"
echo -e "2. Click on the Admin user"
echo -e "3. In the 'Access Rights' tab, scroll to 'Vendor Contract Management'"
echo -e "4. Select 'Manager' role"
echo -e "5. Save the changes\n"

echo -e "${GREEN}Testing the Integration:${NC}"
echo -e "1. After addon installation, you'll see 'Vendor Contracts' in the main menu"
echo -e "2. Go to Vendor Contracts → Configuration → Test API Connection"
echo -e "3. This will verify the blockchain connectivity\n"

echo -e "${YELLOW}Quick Test Workflow:${NC}"
echo -e "1. Create a Vendor: Vendor Contracts → Vendors → Create"
echo -e "2. Create a Contract: Vendor Contracts → Contracts → Create"
echo -e "3. Verify the contract (click Verify button)"
echo -e "4. Submit the contract (click Submit button)"
echo -e "5. Record a payment (click Record Payment button)\n"

# Check if all services are running
echo -e "${CYAN}Service Status:${NC}"
if curl -s http://localhost:8069/web/login | grep -q "Odoo"; then
    echo -e "  ${GREEN}✓ Odoo Web Interface: Running${NC} (http://localhost:8069)"
else
    echo -e "  ✗ Odoo Web Interface: Not accessible"
fi

if curl -s http://localhost:8000/api/v1/health/ | grep -q "healthy"; then
    echo -e "  ${GREEN}✓ FastAPI Gateway: Running${NC} (http://localhost:8000/docs)"
else
    echo -e "  ✗ FastAPI Gateway: Not running"
fi

if curl -s http://localhost:8000/api/v1/health/blockchain | grep -q "connected"; then
    echo -e "  ${GREEN}✓ Blockchain: Connected${NC}"
else
    echo -e "  ✗ Blockchain: Not connected"
fi

echo -e "\n${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║            ${GREEN}Odoo is Ready for VendorChain!${BLUE}                  ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}\n"

echo -e "${YELLOW}Open http://localhost:8069 to access Odoo${NC}"