#!/bin/bash
# Health check validation script for VendorChain MVP Docker environment

set -e

echo "=== VendorChain MVP Docker Health Check Validation ==="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

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

# Check if Docker and Docker Compose are installed
check_docker_installation() {
    print_status "Checking Docker installation..." "INFO"
    
    if ! command -v docker &> /dev/null; then
        print_status "Docker not found. Please install Docker." "FAIL"
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_status "Docker Compose not found. Please install Docker Compose." "FAIL"
    fi
    
    print_status "Docker and Docker Compose are installed" "SUCCESS"
}

# Check if docker-compose.yml exists and is valid
check_compose_file() {
    print_status "Checking Docker Compose configuration..." "INFO"
    
    if [ ! -f "docker-compose.yml" ]; then
        print_status "docker-compose.yml not found" "FAIL"
    fi
    
    # Validate compose file
    if ! docker-compose config &> /dev/null; then
        print_status "docker-compose.yml is invalid" "FAIL"
    fi
    
    print_status "Docker Compose configuration is valid" "SUCCESS"
}

# Check if .env file exists
check_env_file() {
    print_status "Checking environment configuration..." "INFO"
    
    if [ ! -f ".env" ]; then
        print_status ".env file not found" "FAIL"
    fi
    
    # Check for required environment variables
    required_vars=("POSTGRES_DB" "POSTGRES_USER" "POSTGRES_PASSWORD" "ODOO_DB_PASSWORD")
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^$var=" .env; then
            print_status "Required environment variable $var not found in .env" "FAIL"
        fi
    done
    
    print_status "Environment configuration is complete" "SUCCESS"
}

# Test container startup
test_container_startup() {
    print_status "Testing container startup..." "INFO"
    
    # Start containers
    if ! docker-compose up -d --build; then
        print_status "Failed to start containers" "FAIL"
    fi
    
    print_status "Containers started successfully" "SUCCESS"
    
    # Wait for containers to initialize
    print_status "Waiting for containers to initialize (30 seconds)..." "INFO"
    sleep 30
}

# Test individual service health
test_service_health() {
    print_status "Testing service health checks..." "INFO"
    
    # Check PostgreSQL
    if docker-compose exec -T postgres pg_isready -U postgres &> /dev/null; then
        print_status "PostgreSQL is healthy" "SUCCESS"
    else
        print_status "PostgreSQL health check failed" "FAIL"
    fi
    
    # Check if Odoo is responding (basic port check)
    if nc -z localhost 8069 2>/dev/null; then
        print_status "Odoo is responding on port 8069" "SUCCESS"
    else
        print_status "Odoo is not responding on port 8069" "FAIL"
    fi
    
    # Check if FastAPI is responding
    if nc -z localhost 8000 2>/dev/null; then
        print_status "FastAPI Gateway is responding on port 8000" "SUCCESS"
    else
        print_status "FastAPI Gateway is not responding on port 8000" "FAIL"
    fi
    
    # Check Fabric containers are running
    fabric_services=("fabric-ca" "fabric-orderer" "fabric-peer")
    for service in "${fabric_services[@]}"; do
        if docker-compose ps "$service" | grep -q "Up"; then
            print_status "$service is running" "SUCCESS"
        else
            print_status "$service is not running" "FAIL"
        fi
    done
}

# Test container networking
test_networking() {
    print_status "Testing container networking..." "INFO"
    
    # Test if containers can communicate within Docker network
    if docker-compose exec -T fastapi-gateway ping -c 1 postgres &> /dev/null; then
        print_status "FastAPI can reach PostgreSQL" "SUCCESS"
    else
        print_status "FastAPI cannot reach PostgreSQL" "FAIL"
    fi
    
    if docker-compose exec -T odoo ping -c 1 postgres &> /dev/null; then
        print_status "Odoo can reach PostgreSQL" "SUCCESS"
    else
        print_status "Odoo cannot reach PostgreSQL" "FAIL"
    fi
}

# Cleanup function
cleanup() {
    print_status "Cleaning up test environment..." "INFO"
    docker-compose down -v &> /dev/null || true
    print_status "Cleanup completed" "SUCCESS"
}

# Trap cleanup on script exit
trap cleanup EXIT

# Main execution
main() {
    echo "Starting health check validation..."
    echo
    
    check_docker_installation
    check_compose_file
    check_env_file
    test_container_startup
    test_service_health
    test_networking
    
    echo
    print_status "All health checks passed!" "SUCCESS"
    echo "VendorChain MVP Docker environment is ready for development."
}

# Run main function
main "$@"