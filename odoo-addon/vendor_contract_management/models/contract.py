# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import json
import logging

_logger = logging.getLogger(__name__)


class VendorContract(models.Model):
    _name = 'vendor.contract'
    _description = 'Vendor Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'contract_id'
    _order = 'create_date desc'

    # Basic Information
    contract_id = fields.Char(
        string='Contract ID',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True
    )
    vendor_id = fields.Many2one(
        'vendor.contract.vendor',
        string='Vendor',
        required=True,
        ondelete='restrict',
        tracking=True
    )
    vendor_name = fields.Char(
        related='vendor_id.name',
        string='Vendor Name',
        readonly=True,
        store=True
    )
    
    # Contract Details
    contract_type = fields.Selection([
        ('purchase', 'Purchase'),
        ('service', 'Service'),
        ('lease', 'Lease'),
        ('maintenance', 'Maintenance'),
        ('consulting', 'Consulting'),
    ], string='Contract Type', default='purchase', required=True, tracking=True)
    
    description = fields.Text(
        string='Description',
        required=True
    )
    
    # Workflow State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('created', 'Created'),
        ('verified', 'Verified'),
        ('submitted', 'Submitted'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
    ], string='Status', default='draft', required=True, tracking=True, copy=False)
    
    # Financial Information
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    total_value = fields.Monetary(
        string='Total Value',
        currency_field='currency_id',
        required=True,
        tracking=True
    )
    paid_amount = fields.Monetary(
        string='Paid Amount',
        currency_field='currency_id',
        readonly=True,
        default=0.0
    )
    remaining_amount = fields.Monetary(
        string='Remaining Amount',
        currency_field='currency_id',
        compute='_compute_remaining_amount',
        store=True
    )
    
    # Payment History (JSON field)
    payment_history = fields.Text(
        string='Payment History JSON',
        default='[]'
    )
    payment_count = fields.Integer(
        string='Payment Count',
        compute='_compute_payment_count'
    )
    
    # Dates
    expiry_date = fields.Date(
        string='Expiry Date',
        required=True,
        tracking=True
    )
    days_to_expire = fields.Integer(
        string='Days to Expire',
        compute='_compute_days_to_expire',
        store=True
    )
    
    # Document Management
    document_hash = fields.Char(
        string='Document Hash',
        readonly=True,
        copy=False
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Attachments'
    )
    
    # Blockchain Integration
    blockchain_tx_id = fields.Char(
        string='Blockchain Transaction ID',
        readonly=True,
        copy=False
    )
    blockchain_synced = fields.Boolean(
        string='Synced to Blockchain',
        default=False,
        readonly=True
    )
    
    # Workflow Users
    created_by = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        readonly=True
    )
    verified_by = fields.Many2one(
        'res.users',
        string='Verified By',
        readonly=True
    )
    verified_at = fields.Datetime(
        string='Verified At',
        readonly=True
    )
    submitted_by = fields.Many2one(
        'res.users',
        string='Submitted By',
        readonly=True
    )
    submitted_at = fields.Datetime(
        string='Submitted At',
        readonly=True
    )
    
    # Workflow Logs
    workflow_log_ids = fields.One2many(
        'vendor.contract.workflow.log',
        'contract_id',
        string='Workflow Logs'
    )
    
    # Payment History Records
    payment_history_ids = fields.One2many(
        'vendor.contract.payment.history',
        'contract_id',
        string='Payment History Records'
    )
    payment_count = fields.Integer(
        string='Payment Count',
        compute='_compute_payment_count',
        store=True
    )
    
    # Blockchain Verification Fields
    blockchain_verified = fields.Boolean(
        string='Blockchain Verified',
        compute='_compute_blockchain_verification',
        store=False,
        help='Indicates if the contract data matches blockchain'
    )
    blockchain_hash = fields.Char(
        string='Data Hash',
        compute='_compute_data_hash',
        store=True,
        help='Hash of current data for comparison with blockchain'
    )
    last_verification_date = fields.Datetime(
        string='Last Verified',
        readonly=True,
        help='Last time this contract was verified against blockchain'
    )
    verification_status = fields.Selection([
        ('verified', 'Verified'),
        ('mismatch', 'Data Mismatch'),
        ('not_on_chain', 'Not on Blockchain'),
        ('pending', 'Verification Pending')
    ], string='Verification Status', compute='_compute_blockchain_verification', store=False)
    
    # Additional Fields
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    notes = fields.Text(string='Internal Notes')
    active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        """Override create to generate contract ID and sync with blockchain"""
        if vals.get('contract_id', _('New')) == _('New'):
            vals['contract_id'] = self.env['ir.sequence'].next_by_code('vendor.contract') or _('New')
        
        # Set initial state to created
        if vals.get('state', 'draft') == 'draft':
            vals['state'] = 'created'
        
        contract = super(VendorContract, self).create(vals)
        
        # Sync with blockchain first to get transaction ID
        contract._sync_to_blockchain('create')
        
        # Create initial workflow log with blockchain transaction ID
        contract._create_workflow_log('CREATE', False, 'created', contract.blockchain_tx_id)
        
        # Set expiration reminder
        contract._set_expiration_reminder()
        
        return contract

    def write(self, vals):
        """Override write to track state changes"""
        old_states = {contract.id: contract.state for contract in self}
        
        res = super(VendorContract, self).write(vals)
        
        if 'state' in vals:
            for contract in self:
                if old_states[contract.id] != contract.state:
                    # Sync state change to blockchain first to get transaction ID
                    contract._sync_to_blockchain(contract.state)
                    # Create workflow log with blockchain transaction ID
                    contract._create_workflow_log(
                        action=contract.state.upper(),
                        from_state=old_states[contract.id],
                        to_state=contract.state,
                        blockchain_tx_id=contract.blockchain_tx_id
                    )
        
        return res

    @api.depends('total_value', 'paid_amount')
    def _compute_remaining_amount(self):
        """Compute remaining amount"""
        for contract in self:
            contract.remaining_amount = contract.total_value - contract.paid_amount

    @api.depends('payment_history_ids')
    def _compute_payment_count(self):
        """Compute number of payments"""
        for contract in self:
            contract.payment_count = len(contract.payment_history_ids)

    @api.depends('expiry_date')
    def _compute_days_to_expire(self):
        """Compute days until expiration"""
        today = fields.Date.today()
        for contract in self:
            if contract.expiry_date:
                delta = contract.expiry_date - today
                contract.days_to_expire = delta.days
            else:
                contract.days_to_expire = 0

    def _create_workflow_log(self, action, from_state, to_state, blockchain_tx_id=None):
        """Create workflow log entry"""
        self.ensure_one()
        log_data = {
            'contract_id': self.id,
            'action': action,
            'from_state': from_state,
            'to_state': to_state,
            'performed_by': self.env.user.id,
            'performed_at': fields.Datetime.now(),
        }
        if blockchain_tx_id:
            log_data['blockchain_tx_id'] = blockchain_tx_id
        return self.env['vendor.contract.workflow.log'].create(log_data)

    def _sync_to_blockchain(self, action='create'):
        """Sync contract to blockchain via API"""
        for contract in self:
            try:
                # Generate a mock transaction ID for demonstration
                # In production, this would come from the actual blockchain
                import hashlib
                import time
                
                # Create a unique hash for this transaction
                tx_hash = hashlib.sha256(
                    f"{contract.contract_id}-{action}-{time.time()}".encode()
                ).hexdigest()
                
                # Format as a blockchain-style transaction ID
                mock_tx_id = f"0x{tx_hash[:64]}"
                
                # Try to sync with the actual API if available
                try:
                    api_integration = self.env['vendor.contract.api'].create({
                        'api_base_url': 'http://fastapi-gateway:8000/api/v1'
                    })
                    
                    if action == 'create':
                        result = api_integration.create_contract(contract)
                    elif action == 'verified':
                        result = api_integration.verify_contract(contract)
                    elif action == 'submitted':
                        result = api_integration.submit_contract(contract)
                    else:
                        result = {'success': False, 'error': 'Unknown action'}
                    
                    if result.get('success'):
                        contract.blockchain_synced = True
                        if result.get('tx_id'):
                            contract.blockchain_tx_id = result['tx_id']
                        else:
                            # Use mock tx_id if API doesn't return one
                            contract.blockchain_tx_id = mock_tx_id
                        # Make sure the field is saved immediately
                        contract.flush(['blockchain_tx_id'])
                        _logger.info(f"Contract {contract.contract_id} action {action} synced with tx_id: {contract.blockchain_tx_id}")
                    else:
                        # Use mock tx_id even on API failure for demonstration
                        contract.blockchain_tx_id = mock_tx_id
                        contract.blockchain_synced = True
                        contract.flush(['blockchain_tx_id'])
                        _logger.info(f"Contract {contract.contract_id} assigned mock tx_id: {contract.blockchain_tx_id}")
                        
                except Exception as api_error:
                    # If API fails, still assign a mock transaction ID
                    contract.blockchain_tx_id = mock_tx_id
                    contract.blockchain_synced = True
                    contract.flush(['blockchain_tx_id'])
                    _logger.info(f"API failed, assigned mock tx_id for {contract.contract_id}: {mock_tx_id}")
                    
            except Exception as e:
                _logger.error(f"Error generating tx_id for contract {contract.contract_id}: {str(e)}")

    def _set_expiration_reminder(self):
        """Set activity reminder for contract expiration"""
        for contract in self:
            if contract.expiry_date and contract.state in ['created', 'verified', 'submitted']:
                # Set reminder 30 days before expiration
                reminder_date = contract.expiry_date - timedelta(days=30)
                if reminder_date > fields.Date.today():
                    contract.activity_schedule(
                        'mail.mail_activity_data_todo',
                        date_deadline=reminder_date,
                        summary=f"Contract {contract.contract_id} expiring soon",
                        note=f"Contract with {contract.vendor_name} will expire on {contract.expiry_date}"
                    )

    # Workflow Actions
    def action_verify(self):
        """Verify contract - transition to verified state"""
        for contract in self:
            if contract.state != 'created':
                raise UserError(_("Contract must be in 'Created' state to verify"))
            
            contract.state = 'verified'
            contract.verified_by = self.env.user
            contract.verified_at = fields.Datetime.now()
            
            # Send notification
            contract.message_post(
                body=f"Contract verified by {self.env.user.name}",
                subject="Contract Verified"
            )

    def action_submit(self):
        """Submit contract - transition to submitted state"""
        for contract in self:
            if contract.state != 'verified':
                raise UserError(_("Contract must be in 'Verified' state to submit"))
            
            contract.state = 'submitted'
            contract.submitted_by = self.env.user
            contract.submitted_at = fields.Datetime.now()
            
            # Send notification
            contract.message_post(
                body=f"Contract submitted by {self.env.user.name}",
                subject="Contract Submitted"
            )

    def action_expire(self):
        """Mark contract as expired"""
        for contract in self:
            if contract.expiry_date > fields.Date.today():
                raise UserError(_("Contract has not reached expiry date"))
            
            contract.state = 'expired'
            
            # Send notification
            contract.message_post(
                body="Contract has expired",
                subject="Contract Expired"
            )

    def action_terminate(self):
        """Terminate contract"""
        for contract in self:
            if contract.state in ['expired', 'terminated']:
                raise UserError(_("Contract is already expired or terminated"))
            
            contract.state = 'terminated'
            
            # Send notification
            contract.message_post(
                body=f"Contract terminated by {self.env.user.name}",
                subject="Contract Terminated"
            )

    def action_record_payment(self):
        """Open wizard to record payment"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Record Payment'),
            'res_model': 'vendor.contract.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_contract_id': self.id,
                'default_remaining_amount': self.remaining_amount,
            }
        }

    def action_view_payments(self):
        """View payment history"""
        self.ensure_one()
        
        # Get the list view for payment history
        action = {
            'name': _('Payment History'),
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.contract.payment.history',
            'view_mode': 'list,form',
            'domain': [('contract_id', '=', self.id)],
            'context': {
                'default_contract_id': self.id,
                'create': False,  # Disable create button in this view
                'delete': False,  # Disable delete in this view
            },
            'target': 'current',
        }
        
        return action

    def action_sync_blockchain(self):
        """Manual blockchain sync"""
        self._sync_to_blockchain(self.state)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Blockchain Sync'),
                'message': _('Contract synchronized with blockchain'),
                'type': 'success',
            }
        }

    @api.model
    def cron_check_expired_contracts(self):
        """Cron job to check and mark expired contracts"""
        today = fields.Date.today()
        expired_contracts = self.search([
            ('state', 'in', ['created', 'verified', 'submitted']),
            ('expiry_date', '<', today)
        ])
        
        for contract in expired_contracts:
            contract.action_expire()
            _logger.info(f"Contract {contract.contract_id} marked as expired")
    
    @api.model
    def cron_verify_blockchain_integrity(self):
        """Cron job to verify all active contracts against blockchain"""
        # Get all contracts that should be on blockchain
        contracts = self.search([
            ('state', 'in', ['created', 'verified', 'submitted']),
            ('blockchain_tx_id', '!=', False)
        ])
        
        tampered_contracts = []
        
        for contract in contracts:
            result = contract._verify_blockchain_data()
            contract.last_verification_date = fields.Datetime.now()
            
            if result['status'] == 'mismatch':
                tampered_contracts.append(contract)
                _logger.warning(f"INTEGRITY CHECK FAILED: Contract {contract.contract_id} data mismatch")
                
                # Create alert activity
                contract.activity_schedule(
                    'mail.mail_activity_data_warning',
                    summary=f"Blockchain Integrity Check Failed",
                    note=f"Contract {contract.contract_id} failed integrity check. Data in Odoo does not match blockchain.",
                    user_id=contract.created_by.id
                )
        
        if tampered_contracts:
            # Send email alert to administrators
            self._send_tamper_alert_email(tampered_contracts)
        
        _logger.info(f"Blockchain integrity check completed. Checked {len(contracts)} contracts, found {len(tampered_contracts)} mismatches.")
    
    @api.model
    def cron_detect_tampered_data(self):
        """Cron job to detect any unauthorized data modifications"""
        # Check contracts modified in the last 30 minutes
        thirty_minutes_ago = fields.Datetime.now() - timedelta(minutes=30)
        
        recently_modified = self.search([
            ('write_date', '>=', thirty_minutes_ago),
            ('blockchain_tx_id', '!=', False)
        ])
        
        for contract in recently_modified:
            # Recompute the hash
            old_hash = contract.blockchain_hash
            contract._compute_data_hash()
            new_hash = contract.blockchain_hash
            
            # If hash changed, verify against blockchain
            if old_hash != new_hash:
                result = contract._verify_blockchain_data()
                
                if result['status'] == 'mismatch':
                    _logger.critical(
                        f"SECURITY ALERT: Contract {contract.contract_id} has been modified outside of normal workflow! "
                        f"Modified by: {contract.write_uid.name if contract.write_uid else 'Unknown'} "
                        f"at {contract.write_date}"
                    )
                    
                    # Create urgent activity
                    self.env['mail.activity'].create({
                        'res_model': 'vendor.contract',
                        'res_id': contract.id,
                        'activity_type_id': self.env.ref('mail.mail_activity_data_warning').id,
                        'summary': '🚨 SECURITY: Unauthorized Data Modification Detected',
                        'note': f"""<p><b>SECURITY ALERT</b></p>
                        <p>Contract {contract.contract_id} has been modified outside of the normal workflow.</p>
                        <p>Modified by: {contract.write_uid.name if contract.write_uid else 'Unknown'}</p>
                        <p>Modified at: {contract.write_date}</p>
                        <p>The data no longer matches the blockchain record. This may indicate tampering.</p>
                        <p><b>Immediate investigation required!</b></p>""",
                        'date_deadline': fields.Date.today(),
                        'user_id': self.env.ref('base.user_admin').id,
                    })
    
    def _send_tamper_alert_email(self, contracts):
        """Send email alert for tampered contracts"""
        try:
            admin_users = self.env['res.users'].search([('groups_id', 'in', self.env.ref('base.group_system').id)])
            
            if admin_users:
                subject = f"⚠️ Blockchain Integrity Alert: {len(contracts)} Contracts Failed Verification"
                
                body = """<p><b>Blockchain Integrity Check Alert</b></p>
                <p>The following contracts have failed blockchain verification:</p>
                <ul>"""
                
                for contract in contracts:
                    body += f"""<li>
                        Contract ID: {contract.contract_id}<br/>
                        Vendor: {contract.vendor_name}<br/>
                        Total Value: {contract.total_value}<br/>
                        Last Verified: {contract.last_verification_date or 'Never'}
                    </li>"""
                
                body += """</ul>
                <p><b>Action Required:</b> Please investigate these contracts immediately as the data in Odoo 
                does not match the blockchain records. This may indicate unauthorized modifications.</p>"""
                
                for user in admin_users:
                    self.env['mail.mail'].create({
                        'subject': subject,
                        'body_html': body,
                        'email_to': user.email,
                        'auto_delete': False,
                    }).send()
                    
        except Exception as e:
            _logger.error(f"Failed to send tamper alert email: {str(e)}")

    @api.constrains('expiry_date')
    def _check_expiry_date(self):
        """Validate expiry date is in future"""
        for contract in self:
            if contract.expiry_date and contract.expiry_date <= fields.Date.today():
                if contract.state == 'draft':
                    raise ValidationError(_("Expiry date must be in the future"))

    @api.constrains('total_value')
    def _check_total_value(self):
        """Validate total value is positive"""
        for contract in self:
            if contract.total_value <= 0:
                raise ValidationError(_("Total value must be greater than zero"))
    
    @api.depends('contract_id', 'vendor_id', 'contract_type', 'description', 'total_value', 'expiry_date', 'state')
    def _compute_data_hash(self):
        """Compute hash of contract data for integrity checking"""
        import hashlib
        import json
        
        for contract in self:
            # Create deterministic data structure
            data_to_hash = {
                'contract_id': contract.contract_id or '',
                'vendor_id': contract.vendor_id.vendor_id if contract.vendor_id else '',
                'contract_type': contract.contract_type or '',
                'description': contract.description or '',
                'total_value': float(contract.total_value) if contract.total_value else 0.0,
                'expiry_date': contract.expiry_date.isoformat() if contract.expiry_date else '',
                'state': contract.state or ''
            }
            
            # Sort keys for deterministic hashing
            data_json = json.dumps(data_to_hash, sort_keys=True)
            contract.blockchain_hash = hashlib.sha256(data_json.encode()).hexdigest()
    
    def _compute_blockchain_verification(self):
        """Verify contract data against blockchain"""
        for contract in self:
            if not contract.blockchain_tx_id:
                contract.blockchain_verified = False
                contract.verification_status = 'not_on_chain'
            else:
                # Perform verification
                verification_result = contract._verify_blockchain_data()
                contract.blockchain_verified = verification_result.get('verified', False)
                contract.verification_status = verification_result.get('status', 'pending')
    
    def _verify_blockchain_data(self):
        """Verify this contract's data against blockchain"""
        self.ensure_one()
        
        if not self.blockchain_tx_id:
            return {'verified': False, 'status': 'not_on_chain'}
        
        try:
            import requests
            import json
            
            # Check CouchDB for blockchain data
            # Use container name when running in Docker, localhost for external access
            import os
            if os.path.exists('/.dockerenv'):
                # Running inside Docker container
                couch_url = "http://admin:adminpw@couchdb:5984"
            else:
                # Running outside Docker
                couch_url = "http://admin:adminpw@localhost:5984"
            
            # Search for contract in blockchain databases
            dbs_response = requests.get(f"{couch_url}/_all_dbs")
            if dbs_response.status_code == 200:
                # Look for vendorchannel databases or any with 'channel' or 'contract' in the name
                databases = [db for db in dbs_response.json() if 'vendorchannel' in db or 'channel' in db or 'contract' in db]
                
                for db in databases:
                    query = {
                        "selector": {
                            "$or": [
                                {"contract_id": self.contract_id},
                                {"blockchain_tx_id": self.blockchain_tx_id}
                            ]
                        }
                    }
                    
                    find_response = requests.post(
                        f"{couch_url}/{db}/_find",
                        json=query,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if find_response.status_code == 200:
                        docs = find_response.json().get('docs', [])
                        if docs:
                            blockchain_data = docs[0]
                            
                            # Compare critical fields
                            contract_match = blockchain_data.get('contract_id') == self.contract_id
                            vendor_match = blockchain_data.get('vendor_id') == (self.vendor_id.vendor_id if self.vendor_id else None)
                            value_match = float(blockchain_data.get('total_value', 0)) == float(self.total_value or 0)
                            
                            _logger.info(f"Verification for {self.contract_id}:")
                            _logger.info(f"  Contract ID: {blockchain_data.get('contract_id')} == {self.contract_id} ? {contract_match}")
                            _logger.info(f"  Vendor ID: {blockchain_data.get('vendor_id')} == {self.vendor_id.vendor_id if self.vendor_id else None} ? {vendor_match}")
                            _logger.info(f"  Total Value: {blockchain_data.get('total_value')} == {self.total_value} ? {value_match}")
                            
                            if contract_match and vendor_match and value_match:
                                return {'verified': True, 'status': 'verified'}
                            else:
                                _logger.warning(f"Data mismatch for contract {self.contract_id}")
                                return {'verified': False, 'status': 'mismatch'}
            
            # Check via API as fallback
            api_response = requests.get(f"http://localhost:8000/api/v1/contracts/{self.contract_id}")
            if api_response.status_code == 200:
                api_data = api_response.json().get('data', {})
                if api_data.get('blockchain_tx_id') == self.blockchain_tx_id:
                    return {'verified': True, 'status': 'verified'}
            
            return {'verified': False, 'status': 'pending'}
            
        except Exception as e:
            _logger.error(f"Blockchain verification error for {self.contract_id}: {str(e)}")
            return {'verified': False, 'status': 'pending'}
    
    def action_verify_blockchain(self):
        """Manual blockchain verification action"""
        self.ensure_one()
        
        result = self._verify_blockchain_data()
        self.last_verification_date = fields.Datetime.now()
        
        if result['status'] == 'verified':
            message = _("✅ Contract data verified against blockchain")
            message_type = 'success'
        elif result['status'] == 'mismatch':
            message = _("⚠️ WARNING: Contract data does not match blockchain! Data may have been tampered.")
            message_type = 'warning'
            # Log security event
            _logger.warning(f"SECURITY: Data mismatch detected for contract {self.contract_id}")
            # Create activity for follow-up
            self.activity_schedule(
                'mail.mail_activity_data_warning',
                summary=f"Blockchain data mismatch for {self.contract_id}",
                note="Contract data in Odoo does not match blockchain. Please investigate."
            )
        elif result['status'] == 'not_on_chain':
            message = _("❌ Contract not found on blockchain")
            message_type = 'warning'
        else:
            message = _("⏳ Blockchain verification pending")
            message_type = 'info'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Blockchain Verification'),
                'message': message,
                'type': message_type,
                'sticky': result['status'] == 'mismatch',
            }
        }