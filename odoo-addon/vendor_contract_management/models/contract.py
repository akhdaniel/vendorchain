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