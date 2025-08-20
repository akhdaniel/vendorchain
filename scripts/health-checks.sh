#!/bin/bash
# Health check scripts for VendorChain MVP services

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
    elif [ "$2" = "INFO" ]; then
        echo -e "${YELLOW}ℹ $1${NC}"
    fi
}

# PostgreSQL Health Check
check_postgres() {
    print_status "Checking PostgreSQL..." "INFO"
    
    if docker-compose exec -T postgres pg_isready -U odoo -d vendorchain; then
        print_status "PostgreSQL is healthy" "SUCCESS"
        return 0
    else
        print_status "PostgreSQL is not responding" "FAIL"
        return 1
    fi
}

# Odoo Health Check
check_odoo() {
    print_status "Checking Odoo..." "INFO"
    
    # Check if Odoo port is accessible
    if nc -z localhost 8069 2>/dev/null; then
        print_status "Odoo is responding on port 8069" "SUCCESS"
        return 0
    else
        print_status "Odoo is not responding on port 8069" "FAIL"
        return 1
    fi
}

# FastAPI Health Check
check_fastapi() {
    print_status "Checking FastAPI Gateway..." "INFO"
    
    # Check health endpoint
    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        print_status "FastAPI Gateway is healthy" "SUCCESS"
        return 0
    else
        print_status "FastAPI Gateway is not responding" "FAIL"
        return 1
    fi
}

# Fabric CA Health Check
check_fabric_ca() {
    print_status "Checking Fabric CA..." "INFO"
    
    if docker-compose ps fabric-ca | grep -q "Up"; then
        print_status "Fabric CA is running" "SUCCESS"
        return 0
    else
        print_status "Fabric CA is not running" "FAIL"
        return 1
    fi
}

# Fabric Orderer Health Check
check_fabric_orderer() {
    print_status "Checking Fabric Orderer..." "INFO"
    
    if docker-compose ps fabric-orderer | grep -q "Up"; then
        print_status "Fabric Orderer is running" "SUCCESS"
        return 0
    else
        print_status "Fabric Orderer is not running" "FAIL"
        return 1
    fi
}

# Fabric Peer Health Check
check_fabric_peer() {
    print_status "Checking Fabric Peer..." "INFO"
    
    if docker-compose ps fabric-peer | grep -q "Up"; then
        print_status "Fabric Peer is running" "SUCCESS"
        return 0
    else
        print_status "Fabric Peer is not running" "FAIL"
        return 1
    fi
}

# CouchDB Health Check
check_couchdb() {
    print_status "Checking CouchDB..." "INFO"
    
    if curl -f -s http://admin:adminpw@localhost:5984/ > /dev/null 2>&1; then
        print_status "CouchDB is healthy" "SUCCESS"
        return 0
    else
        print_status "CouchDB is not responding" "FAIL"
        return 1
    fi
}

# Network Connectivity Check
check_network_connectivity() {
    print_status "Checking network connectivity..." "INFO"
    
    # Test FastAPI to PostgreSQL
    if docker-compose exec -T fastapi-gateway nc -z postgres 5432 2>/dev/null; then
        print_status "FastAPI can reach PostgreSQL" "SUCCESS"
    else
        print_status "FastAPI cannot reach PostgreSQL" "FAIL"
        return 1
    fi
    
    # Test Odoo to PostgreSQL
    if docker-compose exec -T odoo nc -z postgres 5432 2>/dev/null; then
        print_status "Odoo can reach PostgreSQL" "SUCCESS"
    else
        print_status "Odoo cannot reach PostgreSQL" "FAIL"
        return 1
    fi
    
    return 0
}

# Main health check function
main() {
    echo "=== VendorChain MVP Health Check ==="
    echo
    
    local all_healthy=true
    
    # Run all health checks
    check_postgres || all_healthy=false
    check_couchdb || all_healthy=false
    check_fabric_ca || all_healthy=false
    check_fabric_orderer || all_healthy=false
    check_fabric_peer || all_healthy=false
    check_fastapi || all_healthy=false
    check_odoo || all_healthy=false
    check_network_connectivity || all_healthy=false
    
    echo
    if $all_healthy; then
        print_status "All services are healthy!" "SUCCESS"
        exit 0
    else
        print_status "Some services are unhealthy!" "FAIL"
        exit 1
    fi
}

# Run health checks
main "$@"