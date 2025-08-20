#!/bin/bash
# Start VendorChain MVP Docker Environment

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

echo "=== Starting VendorChain MVP Environment ==="
echo

# Check if Docker is running
print_status "Checking Docker daemon..." "INFO"
if ! docker info > /dev/null 2>&1; then
    print_status "Docker daemon is not running. Please start Docker." "FAIL"
fi
print_status "Docker daemon is running" "SUCCESS"

# Check if .env file exists
print_status "Checking environment configuration..." "INFO"
if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..." "INFO"
    cp .env.example .env
fi
print_status "Environment configuration ready" "SUCCESS"

# Stop existing containers
print_status "Stopping existing containers..." "INFO"
docker-compose down -v > /dev/null 2>&1 || true

# Build and start services
print_status "Building and starting services..." "INFO"
if docker-compose up --build -d; then
    print_status "Services started successfully" "SUCCESS"
else
    print_status "Failed to start services" "FAIL"
fi

# Wait for services to initialize
print_status "Waiting for services to initialize..." "INFO"
echo "This may take up to 2 minutes for first-time setup..."

# Wait for PostgreSQL
print_status "Waiting for PostgreSQL..." "INFO"
for i in {1..60}; do
    if docker-compose exec -T postgres pg_isready -U odoo -d vendorchain > /dev/null 2>&1; then
        break
    fi
    if [ $i -eq 60 ]; then
        print_status "PostgreSQL failed to start within 60 seconds" "FAIL"
    fi
    sleep 1
done
print_status "PostgreSQL is ready" "SUCCESS"

# Wait for CouchDB
print_status "Waiting for CouchDB..." "INFO"
for i in {1..30}; do
    if curl -f -s http://admin:adminpw@localhost:5984/ > /dev/null 2>&1; then
        break
    fi
    if [ $i -eq 30 ]; then
        print_status "CouchDB failed to start within 30 seconds" "FAIL"
    fi
    sleep 1
done
print_status "CouchDB is ready" "SUCCESS"

# Wait for FastAPI
print_status "Waiting for FastAPI Gateway..." "INFO"
for i in {1..30}; do
    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        break
    fi
    if [ $i -eq 30 ]; then
        print_status "FastAPI Gateway failed to start within 30 seconds" "FAIL"
    fi
    sleep 1
done
print_status "FastAPI Gateway is ready" "SUCCESS"

# Wait for Odoo (takes longer to initialize)
print_status "Waiting for Odoo (this may take a while)..." "INFO"
for i in {1..120}; do
    if nc -z localhost 8069 > /dev/null 2>&1; then
        break
    fi
    if [ $i -eq 120 ]; then
        print_status "Odoo failed to start within 2 minutes" "FAIL"
    fi
    sleep 1
done
print_status "Odoo is ready" "SUCCESS"

echo
print_status "All services are running!" "SUCCESS"
echo
echo "Access points:"
echo "  • Odoo: http://localhost:8069"
echo "  • FastAPI Gateway: http://localhost:8000"
echo "  • FastAPI Docs: http://localhost:8000/docs"
echo "  • CouchDB: http://localhost:5984"
echo "  • PostgreSQL: localhost:5432"
echo
echo "Use 'docker-compose logs [service]' to view logs"
echo "Use './scripts/health-checks.sh' to verify all services"
echo "Use './scripts/stop-environment.sh' to stop all services"