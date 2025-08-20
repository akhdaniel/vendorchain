# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import requests
import json
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class VendorContractAPI(models.TransientModel):
    _name = 'vendor.contract.api'
    _description = 'API Integration with FastAPI Gateway'

    # API Configuration
    api_base_url = fields.Char(
        string='API Base URL',
        default='http://vendorchain-fastapi:8000/api/v1'
    )
    api_timeout = fields.Integer(
        string='API Timeout (seconds)',
        default=30
    )
    api_key = fields.Char(
        string='API Key'
    )
    
    @api.model
    def default_get(self, fields_list):
        """Set default values for API configuration"""
        res = super().default_get(fields_list)
        # Use the Docker service name for internal communication
        res['api_base_url'] = 'http://fastapi-gateway:8000/api/v1'
        res['api_timeout'] = 30
        return res

    def _get_headers(self):
        """Get API request headers"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        if self.api_key:
            headers['X-API-Key'] = self.api_key
        return headers

    def _make_request(self, method, endpoint, data=None):
        """Make API request"""
        # Ensure we have a valid base URL
        if not self.api_base_url:
            self.api_base_url = 'http://fastapi-gateway:8000/api/v1'
        url = f"{self.api_base_url}/{endpoint}"
        headers = self._get_headers()
        
        try:
            _logger.info(f"Making {method} request to {url}")
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=self.api_timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=self.api_timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=self.api_timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=self.api_timeout)
            else:
                return {'success': False, 'error': f'Unsupported method: {method}'}
            
            if response.status_code in [200, 201]:
                return {
                    'success': True,
                    'data': response.json() if response.text else {},
                    'status_code': response.status_code
                }
            else:
                return {
                    'success': False,
                    'error': f"API returned {response.status_code}: {response.text}",
                    'status_code': response.status_code
                }
                
        except requests.exceptions.Timeout:
            _logger.error(f"API request timeout: {url}")
            return {'success': False, 'error': 'Request timeout'}
        except requests.exceptions.ConnectionError:
            _logger.error(f"API connection error: {url}")
            return {'success': False, 'error': 'Connection error - API gateway may be down'}
        except Exception as e:
            _logger.error(f"API request error: {str(e)}")
            return {'success': False, 'error': str(e)}

    # Vendor Operations
    def create_or_update_vendor(self, vendor):
        """Create or update vendor via API"""
        # Convert False/empty values to None or empty string for API
        data = {
            'vendor_id': vendor.vendor_id,
            'name': vendor.name,
            'registration_number': vendor.registration_number or '',
            'contact_email': vendor.contact_email or '',
            'contact_phone': vendor.contact_phone or '',
            'address': vendor.address or '',
            'vendor_type': vendor.vendor_type.upper() if vendor.vendor_type else 'SUPPLIER',
            'status': vendor.status.upper() if vendor.status else 'ACTIVE',
            'blockchain_identity': vendor.blockchain_identity or '',
        }
        
        # Check if vendor exists
        result = self._make_request('GET', f'vendors/{vendor.vendor_id}')
        
        if result.get('success'):
            # Update existing vendor
            result = self._make_request('PUT', f'vendors/{vendor.vendor_id}', data)
        else:
            # Create new vendor
            result = self._make_request('POST', 'vendors', data)
        
        if result.get('success') and result.get('data'):
            return {
                'success': True,
                'blockchain_id': result['data'].get('blockchain_identity')
            }
        
        return result

    def get_vendor(self, vendor_id):
        """Get vendor from API"""
        return self._make_request('GET', f'vendors/{vendor_id}')

    # Contract Operations
    def create_contract(self, contract):
        """Create contract via API"""
        data = {
            'contract_id': contract.contract_id,
            'vendor_id': contract.vendor_id.vendor_id if contract.vendor_id else '',
            'contract_type': contract.contract_type.upper() if contract.contract_type else 'PURCHASE',
            'description': contract.description or '',
            'total_value': float(contract.total_value) if contract.total_value else 0.0,
            'expiry_date': contract.expiry_date.isoformat() if contract.expiry_date else None,
            'created_by': contract.created_by.name if contract.created_by else 'System',
            'document_hash': contract.document_hash or '',
        }
        
        result = self._make_request('POST', 'contracts', data)
        
        if result.get('success') and result.get('data'):
            return {
                'success': True,
                'tx_id': result['data'].get('blockchain_tx_id')
            }
        
        return result

    def verify_contract(self, contract):
        """Verify contract via API"""
        data = {
            'verified_by': contract.verified_by.name if contract.verified_by else 'System',
            'performed_by': self.env.user.name,
            'notes': f"Verified in Odoo at {datetime.now().isoformat()}"
        }
        
        result = self._make_request('POST', f'workflow/contracts/{contract.contract_id}/verify', data)
        
        if result.get('success') and result.get('data'):
            return {
                'success': True,
                'tx_id': result['data'].get('blockchain_tx_id')
            }
        
        return result

    def submit_contract(self, contract):
        """Submit contract via API"""
        data = {
            'submitted_by': contract.submitted_by.name if contract.submitted_by else 'System',
            'performed_by': self.env.user.name,
            'notes': f"Submitted in Odoo at {datetime.now().isoformat()}"
        }
        
        result = self._make_request('POST', f'workflow/contracts/{contract.contract_id}/submit', data)
        
        if result.get('success') and result.get('data'):
            return {
                'success': True,
                'tx_id': result['data'].get('blockchain_tx_id')
            }
        
        return result

    def record_payment(self, contract_id, payment_data):
        """Record payment for contract"""
        result = self._make_request('POST', f'contracts/{contract_id}/payments', payment_data)
        
        if result.get('success'):
            return {
                'success': True,
                'tx_id': result.get('data', {}).get('blockchain_tx_id')
            }
        
        return result

    def get_contract(self, contract_id):
        """Get contract from API"""
        return self._make_request('GET', f'contracts/{contract_id}')

    def get_workflow_logs(self, contract_id):
        """Get workflow logs for contract"""
        return self._make_request('GET', f'contracts/{contract_id}/workflow-logs')

    # Health Check
    def check_api_health(self):
        """Check API gateway health"""
        result = self._make_request('GET', 'health')
        
        if result.get('success'):
            return {
                'api': 'online',
                'status': result['data'].get('status', 'unknown')
            }
        
        return {
            'api': 'offline',
            'error': result.get('error', 'Unknown error')
        }

    def check_blockchain_health(self):
        """Check blockchain connectivity"""
        result = self._make_request('GET', 'health/blockchain')
        
        if result.get('success'):
            return {
                'blockchain': result['data'].get('blockchain', 'unknown'),
                'status': result['data'].get('status', 'unknown')
            }
        
        return {
            'blockchain': 'offline',
            'error': result.get('error', 'Unknown error')
        }

    @api.model
    def test_connection(self):
        """Test API connection"""
        api = self.create({})
        health = api.check_api_health()
        blockchain = api.check_blockchain_health()
        
        message = f"API: {health.get('api', 'offline')}\n"
        message += f"Blockchain: {blockchain.get('blockchain', 'offline')}"
        
        if health.get('api') == 'online':
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('API Connection Test'),
                    'message': message,
                    'type': 'success' if health.get('api') == 'online' else 'warning',
                    'sticky': False,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('API Connection Test Failed'),
                    'message': f"Error: {health.get('error', 'Unknown')}",
                    'type': 'danger',
                    'sticky': True,
                }
            }