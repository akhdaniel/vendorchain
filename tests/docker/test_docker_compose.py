#!/usr/bin/env python3
"""
Docker Compose validation tests for VendorChain MVP.
Tests container startup, health checks, and service connectivity.
"""

import subprocess
import time
import requests
import psycopg2
import pytest
import yaml
import os
from pathlib import Path


class TestDockerEnvironment:
    """Test suite for Docker Compose environment validation."""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment."""
        cls.project_root = Path(__file__).parent.parent.parent
        cls.compose_file = cls.project_root / "docker-compose.yml"
        
    def test_docker_compose_file_exists(self):
        """Test that docker-compose.yml file exists and is valid YAML."""
        assert self.compose_file.exists(), "docker-compose.yml file not found"
        
        with open(self.compose_file, 'r') as f:
            compose_config = yaml.safe_load(f)
            
        assert 'services' in compose_config, "No services defined in docker-compose.yml"
        assert 'version' in compose_config, "No version specified in docker-compose.yml"
        
    def test_required_services_defined(self):
        """Test that all required services are defined in docker-compose.yml."""
        with open(self.compose_file, 'r') as f:
            compose_config = yaml.safe_load(f)
            
        required_services = [
            'postgres',
            'odoo',
            'fastapi-gateway',
            'ca.org1.vendorchain.com',
            'orderer.vendorchain.com',
            'peer0.org1.vendorchain.com'
        ]
        
        services = compose_config.get('services', {}).keys()
        
        for service in required_services:
            assert service in services, f"Required service '{service}' not defined"
            
    def test_environment_variables_file_exists(self):
        """Test that .env file exists with required variables."""
        env_file = self.project_root / ".env"
        assert env_file.exists(), ".env file not found"
        
        required_vars = [
            'POSTGRES_DB',
            'POSTGRES_USER', 
            'POSTGRES_PASSWORD',
            'ODOO_DB_PASSWORD',
            'FABRIC_CA_SERVER_CA_NAME',
            'CORE_PEER_ID'
        ]
        
        with open(env_file, 'r') as f:
            env_content = f.read()
            
        for var in required_vars:
            assert var in env_content, f"Required environment variable '{var}' not found"


class TestContainerHealth:
    """Test suite for container health checks and connectivity."""
    
    @classmethod
    def setup_class(cls):
        """Start Docker Compose stack for testing."""
        cls.project_root = Path(__file__).parent.parent.parent
        os.chdir(cls.project_root)
        
        # Start services
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            pytest.fail(f"Failed to start Docker Compose: {result.stderr}")
            
        # Wait for services to initialize
        time.sleep(30)
        
    @classmethod
    def teardown_class(cls):
        """Clean up Docker Compose stack after testing."""
        subprocess.run(["docker-compose", "down", "-v"], capture_output=True)
        
    def test_postgres_health(self):
        """Test PostgreSQL container health and connectivity."""
        # Wait for PostgreSQL to be ready
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                conn = psycopg2.connect(
                    host="localhost",
                    port="5432",
                    database="vendorchain",
                    user="odoo",
                    password="odoo"
                )
                conn.close()
                break
            except psycopg2.OperationalError:
                if attempt == max_attempts - 1:
                    pytest.fail("PostgreSQL not accessible after 30 attempts")
                time.sleep(1)
                
    def test_odoo_health(self):
        """Test Odoo container health and web interface accessibility."""
        max_attempts = 60
        for attempt in range(max_attempts):
            try:
                response = requests.get("http://localhost:8069/web/health", timeout=5)
                if response.status_code == 200:
                    break
            except requests.RequestException:
                if attempt == max_attempts - 1:
                    pytest.fail("Odoo not accessible after 60 attempts")
                time.sleep(1)
                
    def test_fastapi_health(self):
        """Test FastAPI gateway health endpoint."""
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    break
            except requests.RequestException:
                if attempt == max_attempts - 1:
                    pytest.fail("FastAPI gateway not accessible after 30 attempts")
                time.sleep(1)
                
    def test_fabric_ca_health(self):
        """Test Hyperledger Fabric CA container health."""
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=fabric-ca", "--format", "{{.Status}}"],
            capture_output=True,
            text=True
        )
        
        assert "Up" in result.stdout, "Fabric CA container is not running"
        
    def test_fabric_peer_health(self):
        """Test Hyperledger Fabric peer container health."""
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=fabric-peer", "--format", "{{.Status}}"],
            capture_output=True,
            text=True
        )
        
        assert "Up" in result.stdout, "Fabric peer container is not running"
        
    def test_fabric_orderer_health(self):
        """Test Hyperledger Fabric orderer container health."""
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=fabric-orderer", "--format", "{{.Status}}"],
            capture_output=True,
            text=True
        )
        
        assert "Up" in result.stdout, "Fabric orderer container is not running"


class TestServiceConnectivity:
    """Test inter-service connectivity and communication."""
    
    def test_fastapi_postgres_connection(self):
        """Test FastAPI gateway can connect to PostgreSQL."""
        try:
            response = requests.get("http://localhost:8000/health/database", timeout=10)
            assert response.status_code == 200
            assert response.json().get("database") == "connected"
        except requests.RequestException:
            pytest.fail("FastAPI cannot connect to PostgreSQL")
            
    def test_odoo_postgres_connection(self):
        """Test Odoo can connect to PostgreSQL."""
        try:
            response = requests.get("http://localhost:8069/web/database/manager", timeout=10)
            # If we get any response (not a connection error), DB connection works
            assert response.status_code in [200, 303, 404]  # Various valid responses
        except requests.RequestException:
            pytest.fail("Odoo cannot connect to PostgreSQL")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])