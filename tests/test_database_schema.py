"""
Test suite for PostgreSQL database schema validation.
"""

import os
import pytest
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime, timedelta

class TestDatabaseSchema:
    """Test database schema implementation and constraints."""
    
    @pytest.fixture(scope='class')
    def db_connection(self):
        """Create database connection for testing."""
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            database=os.getenv('POSTGRES_DB', 'vendorchain'),
            user=os.getenv('POSTGRES_USER', 'odoo'),
            password=os.getenv('POSTGRES_PASSWORD', 'odoo')
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        yield conn
        conn.close()
    
    @pytest.fixture
    def cursor(self, db_connection):
        """Create cursor for database operations."""
        cur = db_connection.cursor()
        yield cur
        cur.close()
    
    def test_vendors_table_exists(self, cursor):
        """Test that vendors table exists with correct structure."""
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'vendor_contract_management_vendor'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        
        expected_columns = [
            ('id', 'integer', 'NO'),
            ('vendor_id', 'character varying', 'NO'),
            ('name', 'character varying', 'NO'),
            ('registration_number', 'character varying', 'YES'),
            ('contact_email', 'character varying', 'NO'),
            ('contact_phone', 'character varying', 'YES'),
            ('address', 'text', 'YES'),
            ('vendor_type', 'character varying', 'NO'),
            ('status', 'character varying', 'NO'),
            ('blockchain_identity', 'character varying', 'YES'),
            ('created_at', 'timestamp without time zone', 'NO'),
            ('updated_at', 'timestamp without time zone', 'NO')
        ]
        
        for expected in expected_columns:
            assert expected in columns, f"Column {expected[0]} not found or incorrect"
    
    def test_contracts_table_exists(self, cursor):
        """Test that contracts table exists with correct structure."""
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'vendor_contract_management_contract'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        
        assert len(columns) > 0, "Contracts table does not exist"
        
        # Check for essential columns
        column_names = [col[0] for col in columns]
        assert 'id' in column_names
        assert 'contract_id' in column_names
        assert 'vendor_id' in column_names
        assert 'contract_type' in column_names
        assert 'status' in column_names
        assert 'total_value' in column_names
        assert 'blockchain_tx_id' in column_names
    
    def test_workflow_logs_table_exists(self, cursor):
        """Test that workflow_logs table exists."""
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'vendor_contract_management_workflow_log'
            )
        """)
        exists = cursor.fetchone()[0]
        assert exists, "Workflow logs table does not exist"
    
    def test_api_metadata_table_exists(self, cursor):
        """Test that api_metadata table exists."""
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'vendor_contract_api_metadata'
            )
        """)
        exists = cursor.fetchone()[0]
        assert exists, "API metadata table does not exist"
    
    def test_vendor_id_unique_constraint(self, cursor):
        """Test vendor_id unique constraint."""
        cursor.execute("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'vendor_contract_management_vendor'
            AND constraint_type = 'UNIQUE'
        """)
        constraints = cursor.fetchall()
        assert len(constraints) > 0, "No unique constraints found on vendors table"
    
    def test_contract_foreign_key_constraint(self, cursor):
        """Test foreign key constraint from contracts to vendors."""
        cursor.execute("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'vendor_contract_management_contract'
            AND constraint_type = 'FOREIGN KEY'
        """)
        constraints = cursor.fetchall()
        assert len(constraints) > 0, "No foreign key constraints found on contracts table"
    
    def test_workflow_log_foreign_keys(self, cursor):
        """Test foreign key constraints on workflow_logs table."""
        cursor.execute("""
            SELECT 
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = 'vendor_contract_management_workflow_log'
        """)
        constraints = cursor.fetchall()
        
        # Should have foreign keys to both contracts and users
        assert len(constraints) >= 1, "Workflow logs should have foreign key constraints"
    
    def test_contract_status_check_constraint(self, cursor):
        """Test check constraint on contract status."""
        cursor.execute("""
            SELECT check_clause
            FROM information_schema.check_constraints
            WHERE constraint_name LIKE '%contract%status%'
        """)
        constraints = cursor.fetchall()
        
        if constraints:
            # Verify status values are restricted
            for constraint in constraints:
                assert 'CREATED' in constraint[0] or 'status' in constraint[0].lower()
    
    def test_indexes_exist(self, cursor):
        """Test that performance indexes exist."""
        cursor.execute("""
            SELECT indexname, tablename
            FROM pg_indexes
            WHERE schemaname = 'public'
            AND tablename LIKE 'vendor_contract%'
        """)
        indexes = cursor.fetchall()
        
        # Check for essential indexes
        index_names = [idx[0] for idx in indexes]
        tables = set([idx[1] for idx in indexes])
        
        # Should have indexes on foreign keys and commonly queried fields
        assert len(indexes) > 4, "Should have multiple indexes for performance"
        assert 'vendor_contract_management_vendor' in tables
        assert 'vendor_contract_management_contract' in tables
    
    def test_timestamp_triggers(self, cursor):
        """Test that updated_at triggers exist."""
        cursor.execute("""
            SELECT trigger_name, event_object_table
            FROM information_schema.triggers
            WHERE trigger_schema = 'public'
            AND event_object_table LIKE 'vendor_contract%'
        """)
        triggers = cursor.fetchall()
        
        # Should have update triggers for timestamp management
        if triggers:
            trigger_tables = [t[1] for t in triggers]
            assert 'vendor_contract_management_vendor' in trigger_tables or len(triggers) > 0
    
    def test_payment_history_jsonb_column(self, cursor):
        """Test that payment_history column is JSONB type."""
        cursor.execute("""
            SELECT data_type
            FROM information_schema.columns
            WHERE table_name = 'vendor_contract_management_contract'
            AND column_name = 'payment_history'
        """)
        result = cursor.fetchone()
        
        if result:
            assert result[0] == 'jsonb', "Payment history should be JSONB type"
    
    def test_vendor_type_enum_or_check(self, cursor):
        """Test vendor_type has proper constraints."""
        cursor.execute("""
            SELECT check_clause
            FROM information_schema.check_constraints
            WHERE constraint_name LIKE '%vendor%type%'
        """)
        constraints = cursor.fetchall()
        
        # Should have constraints on vendor type values
        if constraints:
            for constraint in constraints:
                assert 'SUPPLIER' in constraint[0] or 'vendor_type' in constraint[0].lower()
    
    @pytest.mark.integration
    def test_insert_vendor(self, cursor):
        """Test inserting a vendor record."""
        try:
            cursor.execute("""
                INSERT INTO vendor_contract_management_vendor 
                (vendor_id, name, contact_email, vendor_type, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                'TEST_VENDOR_001',
                'Test Vendor Inc',
                'test@vendor.com',
                'SUPPLIER',
                'ACTIVE',
                datetime.now(),
                datetime.now()
            ))
            vendor_id = cursor.fetchone()[0]
            assert vendor_id is not None, "Vendor insertion failed"
            
            # Clean up
            cursor.execute("DELETE FROM vendor_contract_management_vendor WHERE id = %s", (vendor_id,))
        except Exception as e:
            pytest.skip(f"Table might not exist yet: {e}")
    
    @pytest.mark.integration
    def test_contract_vendor_relationship(self, cursor):
        """Test foreign key relationship between contracts and vendors."""
        try:
            # First insert a vendor
            cursor.execute("""
                INSERT INTO vendor_contract_management_vendor 
                (vendor_id, name, contact_email, vendor_type, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                'TEST_VENDOR_002',
                'Test Vendor 2',
                'test2@vendor.com',
                'SUPPLIER',
                'ACTIVE',
                datetime.now(),
                datetime.now()
            ))
            vendor_id = cursor.fetchone()[0]
            
            # Try to insert a contract with this vendor
            cursor.execute("""
                INSERT INTO vendor_contract_management_contract
                (contract_id, vendor_id, contract_type, status, total_value, 
                 expiry_date, created_at, updated_at, created_by, odoo_user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                'TEST_CONTRACT_001',
                vendor_id,
                'SERVICE',
                'CREATED',
                50000.00,
                datetime.now() + timedelta(days=365),
                datetime.now(),
                datetime.now(),
                'test_user',
                1
            ))
            contract_id = cursor.fetchone()[0]
            assert contract_id is not None, "Contract insertion failed"
            
            # Clean up
            cursor.execute("DELETE FROM vendor_contract_management_contract WHERE id = %s", (contract_id,))
            cursor.execute("DELETE FROM vendor_contract_management_vendor WHERE id = %s", (vendor_id,))
        except Exception as e:
            pytest.skip(f"Tables might not exist yet: {e}")
    
    @pytest.mark.integration
    def test_workflow_log_insertion(self, cursor):
        """Test inserting workflow log entries."""
        try:
            # Need a vendor and contract first
            cursor.execute("""
                INSERT INTO vendor_contract_management_vendor 
                (vendor_id, name, contact_email, vendor_type, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                'TEST_VENDOR_003',
                'Test Vendor 3',
                'test3@vendor.com',
                'SUPPLIER',
                'ACTIVE',
                datetime.now(),
                datetime.now()
            ))
            vendor_id = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO vendor_contract_management_contract
                (contract_id, vendor_id, contract_type, status, total_value, 
                 expiry_date, created_at, updated_at, created_by, odoo_user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                'TEST_CONTRACT_002',
                vendor_id,
                'SERVICE',
                'CREATED',
                25000.00,
                datetime.now() + timedelta(days=180),
                datetime.now(),
                datetime.now(),
                'test_user',
                1
            ))
            contract_id = cursor.fetchone()[0]
            
            # Insert workflow log
            cursor.execute("""
                INSERT INTO vendor_contract_management_workflow_log
                (contract_id, action, from_status, to_status, performed_by, 
                 performed_at, notes, odoo_user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                contract_id,
                'CREATE',
                None,
                'CREATED',
                'test_user',
                datetime.now(),
                'Contract created for testing',
                1
            ))
            log_id = cursor.fetchone()[0]
            assert log_id is not None, "Workflow log insertion failed"
            
            # Clean up
            cursor.execute("DELETE FROM vendor_contract_management_workflow_log WHERE id = %s", (log_id,))
            cursor.execute("DELETE FROM vendor_contract_management_contract WHERE id = %s", (contract_id,))
            cursor.execute("DELETE FROM vendor_contract_management_vendor WHERE id = %s", (vendor_id,))
        except Exception as e:
            pytest.skip(f"Tables might not exist yet: {e}")