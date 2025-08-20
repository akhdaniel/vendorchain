#!/bin/bash

# Apply database migrations for VendorChain MVP
# This script applies all pending migrations in order

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Database connection parameters
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-vendorchain}"
DB_USER="${POSTGRES_USER:-odoo}"
DB_PASSWORD="${POSTGRES_PASSWORD:-odoo}"

echo "=========================================="
echo "Applying Database Migrations"
echo "=========================================="
echo "Database: $DB_NAME@$DB_HOST:$DB_PORT"
echo ""

# Export password for psql
export PGPASSWORD="$DB_PASSWORD"

# Function to execute SQL file
execute_sql() {
    local sql_file=$1
    echo "Executing: $(basename $sql_file)"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$sql_file"
}

# Apply main schema if not exists
if [ -f "$SCRIPT_DIR/schema.sql" ]; then
    echo "Applying main schema..."
    execute_sql "$SCRIPT_DIR/schema.sql"
    echo "✓ Main schema applied"
else
    echo "⚠ Main schema file not found"
fi

# Apply migrations in order
if [ -d "$SCRIPT_DIR/migrations" ]; then
    for migration in "$SCRIPT_DIR/migrations"/*.sql; do
        if [ -f "$migration" ]; then
            execute_sql "$migration"
            echo "✓ $(basename $migration) applied"
        fi
    done
else
    echo "⚠ No migrations directory found"
fi

# Apply sample data if requested
if [ "$1" == "--with-sample-data" ]; then
    if [ -f "$SCRIPT_DIR/sample-data.sql" ]; then
        echo ""
        echo "Loading sample data..."
        execute_sql "$SCRIPT_DIR/sample-data.sql"
        echo "✓ Sample data loaded"
    else
        echo "⚠ Sample data file not found"
    fi
fi

echo ""
echo "=========================================="
echo "Migration Complete!"
echo "=========================================="

# Show current schema version
echo "Current schema version:"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT version, description, applied_at FROM schema_version ORDER BY version DESC LIMIT 1;"

unset PGPASSWORD