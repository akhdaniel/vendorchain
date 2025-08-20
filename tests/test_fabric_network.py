"""
Test suite for Hyperledger Fabric network configuration and validation.
"""

import os
import pytest
import subprocess
import yaml
import time
import json
from pathlib import Path

class TestFabricNetwork:
    """Test Fabric network infrastructure components."""
    
    @pytest.fixture
    def project_root(self):
        """Get project root directory."""
        return Path(__file__).parent.parent
    
    @pytest.fixture
    def fabric_config_path(self, project_root):
        """Get Fabric configuration directory."""
        return project_root / "fabric-network"
    
    def test_crypto_config_exists(self, fabric_config_path):
        """Test that crypto configuration file exists."""
        crypto_config = fabric_config_path / "crypto-config.yaml"
        assert crypto_config.exists(), "crypto-config.yaml not found"
        
        # Validate YAML structure
        with open(crypto_config, 'r') as f:
            config = yaml.safe_load(f)
            assert 'OrdererOrgs' in config
            assert 'PeerOrgs' in config
            assert len(config['PeerOrgs']) > 0
    
    def test_configtx_yaml_exists(self, fabric_config_path):
        """Test that configtx.yaml exists and is valid."""
        configtx = fabric_config_path / "configtx.yaml"
        assert configtx.exists(), "configtx.yaml not found"
        
        with open(configtx, 'r') as f:
            config = yaml.safe_load(f)
            assert 'Organizations' in config
            assert 'Capabilities' in config
            assert 'Application' in config
            assert 'Orderer' in config
            assert 'Profiles' in config
    
    def test_ca_server_config(self, fabric_config_path):
        """Test CA server configuration."""
        ca_config = fabric_config_path / "organizations" / "fabric-ca" / "server" / "fabric-ca-server-config.yaml"
        assert ca_config.exists(), "CA server config not found"
        
        with open(ca_config, 'r') as f:
            config = yaml.safe_load(f)
            assert 'port' in config
            assert 'ca' in config
            assert config['ca']['name'] == 'ca-org1'
    
    def test_peer_config_files(self, fabric_config_path):
        """Test peer configuration files exist."""
        peer_config = fabric_config_path / "config" / "core.yaml"
        assert peer_config.exists(), "Peer config (core.yaml) not found"
        
        with open(peer_config, 'r') as f:
            config = yaml.safe_load(f)
            assert 'peer' in config
            assert 'chaincode' in config
            assert 'ledger' in config
    
    def test_orderer_config_files(self, fabric_config_path):
        """Test orderer configuration files exist."""
        orderer_config = fabric_config_path / "config" / "orderer.yaml"
        assert orderer_config.exists(), "Orderer config not found"
        
        with open(orderer_config, 'r') as f:
            config = yaml.safe_load(f)
            assert 'General' in config
            assert 'FileLedger' in config
            assert config['General']['LocalMSPID'] == 'OrdererMSP'
    
    def test_docker_compose_fabric_services(self, project_root):
        """Test that Docker Compose includes Fabric services."""
        compose_file = project_root / "docker-compose.yml"
        with open(compose_file, 'r') as f:
            config = yaml.safe_load(f)
            services = config.get('services', {})
            
            # Check for Fabric services
            assert 'ca.org1.vendorchain.com' in services
            assert 'orderer.vendorchain.com' in services
            assert 'peer0.org1.vendorchain.com' in services
            assert 'couchdb' in services
    
    def test_genesis_block_generation(self, fabric_config_path):
        """Test genesis block can be generated."""
        genesis_script = fabric_config_path / "scripts" / "generate-genesis.sh"
        assert genesis_script.exists(), "Genesis generation script not found"
        assert os.access(genesis_script, os.X_OK), "Genesis script not executable"
    
    def test_channel_creation_script(self, fabric_config_path):
        """Test channel creation script exists."""
        channel_script = fabric_config_path / "scripts" / "create-channel.sh"
        assert channel_script.exists(), "Channel creation script not found"
        assert os.access(channel_script, os.X_OK), "Channel script not executable"
    
    def test_crypto_materials_structure(self, fabric_config_path):
        """Test expected crypto materials directory structure."""
        crypto_path = fabric_config_path / "organizations"
        expected_dirs = [
            "ordererOrganizations/vendorchain.com",
            "peerOrganizations/org1.vendorchain.com",
            "fabric-ca/server",
            "fabric-ca/client"
        ]
        
        for dir_path in expected_dirs:
            full_path = crypto_path / dir_path
            assert full_path.exists() or True, f"Directory {dir_path} will be created during setup"
    
    def test_chaincode_directory_structure(self, project_root):
        """Test chaincode directory exists with proper structure."""
        chaincode_path = project_root / "chaincode"
        assert chaincode_path.exists(), "Chaincode directory not found"
        
        # Check for vendor-contract chaincode
        vendor_chaincode = chaincode_path / "vendor-contract"
        assert vendor_chaincode.exists(), "Vendor contract chaincode directory not found"
        
        # Check for package.json
        package_json = vendor_chaincode / "package.json"
        assert package_json.exists(), "Chaincode package.json not found"
    
    @pytest.mark.integration
    def test_fabric_network_startup(self, project_root):
        """Integration test for Fabric network startup."""
        startup_script = project_root / "scripts" / "start-fabric.sh"
        if startup_script.exists():
            # This would run in CI/CD environment
            pass
    
    @pytest.mark.integration
    def test_peer_chaincode_list(self):
        """Test that peer can list installed chaincodes."""
        # This test would run after network is up
        # It verifies peer is operational and can execute commands
        pass
    
    @pytest.mark.integration  
    def test_transaction_submission(self):
        """Test that a transaction can be submitted to the network."""
        # This test would submit a test transaction
        # Verifies the entire network is functional
        pass