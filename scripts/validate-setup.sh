#!/bin/bash
# Validate VendorChain MVP setup without starting containers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ "$2" = "SUCCESS" ]; then
        echo -e "${GREEN}✓ $1${NC}"
    elif [ "$2" = "FAIL" ]; then
        echo -e "${RED}✗ $1${NC}"
        exit 1
    elif [ "$2" = "INFO" ]; then
        echo -e "${YELLOW}ℹ $1${NC}"
    fi
}

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=== VendorChain MVP Setup Validation ==="
echo

# Check project structure
print_status "Checking project structure..." "INFO"
required_dirs=(
    "odoo-addon/vendor_contract_management"
    "fastapi-gateway/app"
    "fabric-network/organizations"
    "tests/docker"
    "scripts"
    "config"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        print_status "Directory $dir exists" "SUCCESS"
    else
        print_status "Directory $dir missing" "FAIL"
    fi
done

# Check required files
print_status "Checking required files..." "INFO"
required_files=(
    "docker-compose.yml"
    ".env"
    "config/odoo.conf"
    "scripts/init-db.sql"
    "fastapi-gateway/Dockerfile"
    "fastapi-gateway/requirements.txt"
    "fastapi-gateway/app/main.py"
    "odoo-addon/vendor_contract_management/__manifest__.py"
    "tests/docker/test_docker_compose.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_status "File $file exists" "SUCCESS"
    else
        print_status "File $file missing" "FAIL"
    fi
done

# Validate Docker Compose file
print_status "Validating Docker Compose configuration..." "INFO"
if docker-compose config > /dev/null 2>&1; then
    print_status "Docker Compose configuration is valid" "SUCCESS"
else
    print_status "Docker Compose configuration is invalid" "FAIL"
fi

# Check environment variables
print_status "Validating environment variables..." "INFO"
required_env_vars=("POSTGRES_DB" "POSTGRES_USER" "POSTGRES_PASSWORD" "FABRIC_CA_SERVER_CA_NAME")

for var in "${required_env_vars[@]}"; do
    if grep -q "^$var=" .env; then
        print_status "Environment variable $var is set" "SUCCESS"
    else
        print_status "Environment variable $var is missing" "FAIL"
    fi
done

# Check script permissions
print_status "Checking script permissions..." "INFO"
executable_scripts=(
    "scripts/start-environment.sh"
    "scripts/stop-environment.sh"
    "scripts/health-checks.sh"
    "tests/docker/test_health_checks.sh"
)

for script in "${executable_scripts[@]}"; do
    if [ -x "$script" ]; then
        print_status "Script $script is executable" "SUCCESS"
    else
        print_status "Script $script is not executable" "FAIL"
    fi
done

echo
print_status "All validation checks passed!" "SUCCESS"
echo
echo "Next steps:"
echo "1. Run: ./scripts/start-environment.sh"
echo "2. Wait for all services to start (may take 2-3 minutes)"
echo "3. Run: ./scripts/health-checks.sh"
echo "4. Access Odoo at: http://localhost:8069"
echo "5. Access FastAPI docs at: http://localhost:8000/docs"