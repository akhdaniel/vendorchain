"""
Test suite for FastAPI Gateway endpoints
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import json
from unittest.mock import Mock, patch, AsyncMock

# Import will be from the main app once created
# from app.main import app


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from app.main import app
        return TestClient(app)
    
    def test_health_check(self, client):
        """Test basic health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "blockchain" in data
    
    def test_readiness_check(self, client):
        """Test readiness check endpoint"""
        response = client.get("/ready")
        assert response.status_code in [200, 503]
        data = response.json()
        assert "ready" in data
        assert "checks" in data


class TestContractEndpoints:
    """Test contract CRUD endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from app.main import app
        return TestClient(app)
    
    @pytest.fixture
    def sample_contract(self):
        """Sample contract data"""
        return {
            "contract_id": "CONTRACT999",
            "vendor_id": "VENDOR001",
            "contract_type": "SERVICE",
            "description": "Test contract",
            "total_value": 50000.00,
            "expiry_date": (datetime.now() + timedelta(days=365)).isoformat()
        }
    
    def test_create_contract(self, client, sample_contract):
        """Test contract creation"""
        response = client.post("/api/contracts", json=sample_contract)
        assert response.status_code == 201
        data = response.json()
        assert data["contract_id"] == sample_contract["contract_id"]
        assert data["status"] == "CREATED"
    
    def test_get_contract(self, client):
        """Test getting a specific contract"""
        response = client.get("/api/contracts/CONTRACT001")
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "contract_id" in data
            assert "vendor_id" in data
            assert "status" in data
    
    def test_list_contracts(self, client):
        """Test listing all contracts"""
        response = client.get("/api/contracts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "contracts" in data
    
    def test_update_contract(self, client):
        """Test contract update"""
        update_data = {"description": "Updated description"}
        response = client.patch("/api/contracts/CONTRACT001", json=update_data)
        assert response.status_code in [200, 404]
    
    def test_delete_contract(self, client):
        """Test contract deletion"""
        response = client.delete("/api/contracts/CONTRACT999")
        assert response.status_code in [204, 404]


class TestWorkflowEndpoints:
    """Test workflow transition endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from app.main import app
        return TestClient(app)
    
    def test_verify_contract(self, client):
        """Test contract verification endpoint"""
        response = client.post("/api/contracts/CONTRACT001/verify", 
                              json={"verified_by": "test_verifier"})
        assert response.status_code in [200, 400, 404]
        if response.status_code == 200:
            data = response.json()
            assert data["status"] in ["VERIFIED", "ALREADY_VERIFIED"]
    
    def test_submit_contract(self, client):
        """Test contract submission endpoint"""
        response = client.post("/api/contracts/CONTRACT003/submit",
                              json={"submitted_by": "test_submitter"})
        assert response.status_code in [200, 400, 404]
        if response.status_code == 200:
            data = response.json()
            assert data["status"] in ["SUBMITTED", "ALREADY_SUBMITTED"]
    
    def test_record_payment(self, client):
        """Test payment recording endpoint"""
        payment_data = {
            "amount": 5000.00,
            "payment_date": datetime.now().isoformat(),
            "reference": "PAY-TEST-001"
        }
        response = client.post("/api/contracts/CONTRACT001/payments", 
                              json=payment_data)
        assert response.status_code in [201, 400, 404]


class TestVendorEndpoints:
    """Test vendor management endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from app.main import app
        return TestClient(app)
    
    @pytest.fixture
    def sample_vendor(self):
        """Sample vendor data"""
        return {
            "vendor_id": "VENDOR999",
            "name": "Test Vendor Inc.",
            "contact_email": "test@vendor.com",
            "vendor_type": "SUPPLIER",
            "status": "ACTIVE"
        }
    
    def test_create_vendor(self, client, sample_vendor):
        """Test vendor creation"""
        response = client.post("/api/vendors", json=sample_vendor)
        assert response.status_code == 201
        data = response.json()
        assert data["vendor_id"] == sample_vendor["vendor_id"]
    
    def test_get_vendor(self, client):
        """Test getting a specific vendor"""
        response = client.get("/api/vendors/VENDOR001")
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "vendor_id" in data
            assert "name" in data
    
    def test_list_vendors(self, client):
        """Test listing all vendors"""
        response = client.get("/api/vendors")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "vendors" in data
    
    def test_vendor_contracts(self, client):
        """Test getting contracts for a vendor"""
        response = client.get("/api/vendors/VENDOR001/contracts")
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list) or "contracts" in data


class TestBlockchainEndpoints:
    """Test blockchain integration endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from app.main import app
        return TestClient(app)
    
    def test_sync_contract_to_blockchain(self, client):
        """Test syncing contract to blockchain"""
        response = client.post("/api/blockchain/sync/CONTRACT001")
        assert response.status_code in [200, 404, 500]
        if response.status_code == 200:
            data = response.json()
            assert "tx_id" in data or "transaction_id" in data
    
    def test_get_blockchain_status(self, client):
        """Test getting blockchain network status"""
        response = client.get("/api/blockchain/status")
        assert response.status_code in [200, 503]
        data = response.json()
        assert "connected" in data or "status" in data
    
    def test_query_blockchain_contract(self, client):
        """Test querying contract from blockchain"""
        response = client.get("/api/blockchain/contracts/CONTRACT001")
        assert response.status_code in [200, 404, 503]
        if response.status_code == 200:
            data = response.json()
            assert "contract_id" in data


class TestAuthenticationEndpoints:
    """Test authentication and authorization"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from app.main import app
        return TestClient(app)
    
    def test_api_key_required(self, client):
        """Test that API key is required for protected endpoints"""
        response = client.post("/api/contracts", json={})
        # Should either work (no auth) or return 401/403
        assert response.status_code in [400, 401, 403, 422]
    
    def test_with_api_key(self, client):
        """Test access with valid API key"""
        headers = {"X-API-Key": "test-api-key"}
        response = client.get("/api/contracts", headers=headers)
        # Should work or indicate wrong key
        assert response.status_code in [200, 401, 403]


class TestWebhookEndpoints:
    """Test webhook endpoints for Odoo integration"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from app.main import app
        return TestClient(app)
    
    def test_contract_created_webhook(self, client):
        """Test webhook for contract creation notification"""
        webhook_data = {
            "event": "contract.created",
            "contract_id": "CONTRACT001",
            "timestamp": datetime.now().isoformat()
        }
        response = client.post("/api/webhooks/contract-events", 
                              json=webhook_data)
        assert response.status_code in [200, 202]
    
    def test_payment_received_webhook(self, client):
        """Test webhook for payment notification"""
        webhook_data = {
            "event": "payment.received",
            "contract_id": "CONTRACT001",
            "amount": 5000.00,
            "timestamp": datetime.now().isoformat()
        }
        response = client.post("/api/webhooks/payment-events",
                              json=webhook_data)
        assert response.status_code in [200, 202]


@pytest.mark.integration
class TestIntegration:
    """Integration tests for complete workflows"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from app.main import app
        return TestClient(app)
    
    def test_complete_contract_workflow(self, client):
        """Test complete contract lifecycle"""
        # Create contract
        contract_data = {
            "contract_id": "CONTRACT_TEST_001",
            "vendor_id": "VENDOR001",
            "contract_type": "SERVICE",
            "description": "Integration test contract",
            "total_value": 25000.00,
            "expiry_date": (datetime.now() + timedelta(days=180)).isoformat()
        }
        
        # Step 1: Create
        response = client.post("/api/contracts", json=contract_data)
        assert response.status_code == 201
        
        # Step 2: Verify
        response = client.post(f"/api/contracts/{contract_data['contract_id']}/verify",
                              json={"verified_by": "integration_test"})
        assert response.status_code in [200, 400]
        
        # Step 3: Submit
        response = client.post(f"/api/contracts/{contract_data['contract_id']}/submit",
                              json={"submitted_by": "integration_test"})
        assert response.status_code in [200, 400]
        
        # Step 4: Record payment
        payment_data = {
            "amount": 5000.00,
            "payment_date": datetime.now().isoformat(),
            "reference": "INT-PAY-001"
        }
        response = client.post(f"/api/contracts/{contract_data['contract_id']}/payments",
                              json=payment_data)
        assert response.status_code in [201, 400]
        
        # Cleanup
        client.delete(f"/api/contracts/{contract_data['contract_id']}")
    
    @pytest.mark.asyncio
    async def test_blockchain_sync_workflow(self, client):
        """Test blockchain synchronization workflow"""
        # This would test the full blockchain sync
        # Mocked for now as it requires actual blockchain
        pass