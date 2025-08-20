#!/bin/bash
# Stop VendorChain MVP Docker Environment

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

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=== Stopping VendorChain MVP Environment ==="
echo

# Stop and remove containers
print_status "Stopping containers..." "INFO"
if docker-compose down; then
    print_status "Containers stopped successfully" "SUCCESS"
else
    print_status "Failed to stop some containers" "FAIL"
fi

# Option to remove volumes
if [ "$1" = "--volumes" ] || [ "$1" = "-v" ]; then
    print_status "Removing volumes..." "INFO"
    if docker-compose down -v; then
        print_status "Volumes removed successfully" "SUCCESS"
    else
        print_status "Failed to remove some volumes" "FAIL"
    fi
fi

# Clean up unused networks
print_status "Cleaning up networks..." "INFO"
docker network prune -f > /dev/null 2>&1 || true

echo
print_status "Environment stopped successfully" "SUCCESS"
echo
if [ "$1" != "--volumes" ] && [ "$1" != "-v" ]; then
    echo "Data volumes preserved. Use '$0 --volumes' to remove all data."
fi