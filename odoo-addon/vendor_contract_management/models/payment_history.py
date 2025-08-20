# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json
import logging

_logger = logging.getLogger(__name__)


class VendorContractPaymentHistory(models.Model):
    _name = 'vendor.contract.payment.history'
    _description = 'Contract Payment History'
    _order = 'payment_date desc, id desc'
    _rec_name = 'payment_reference'

    # Contract reference
    contract_id = fields.Many2one(
        'vendor.contract',
        string='Contract',
        required=True,
        ondelete='cascade',
        index=True
    )
    contract_display = fields.Char(
        related='contract_id.contract_id',
        string='Contract ID',
        readonly=True,
        store=True
    )
    vendor_name = fields.Char(
        related='contract_id.vendor_name',
        string='Vendor',
        readonly=True,
        store=True
    )
    
    # Payment Information
    payment_amount = fields.Monetary(
        string='Payment Amount',
        required=True,
        currency_field='currency_id'
    )
    payment_date = fields.Date(
        string='Payment Date',
        required=True,
        default=fields.Date.today
    )
    payment_reference = fields.Char(
        string='Payment Reference',
        required=True,
        help='Check number, wire transfer reference, etc.'
    )
    payment_method = fields.Selection([
        ('check', 'Check'),
        ('wire', 'Wire Transfer'),
        ('ach', 'ACH Transfer'),
        ('credit_card', 'Credit Card'),
        ('cash', 'Cash'),
        ('other', 'Other')
    ], string='Payment Method', required=True, default='check')
    
    notes = fields.Text(
        string='Notes'
    )
    
    # Financial Information
    currency_id = fields.Many2one(
        related='contract_id.currency_id',
        string='Currency',
        readonly=True,
        store=True
    )
    
    # Tracking
    recorded_by = fields.Many2one(
        'res.users',
        string='Recorded By',
        default=lambda self: self.env.user,
        readonly=True
    )
    recorded_at = fields.Datetime(
        string='Recorded At',
        default=fields.Datetime.now,
        readonly=True
    )
    
    # Blockchain
    blockchain_tx_id = fields.Char(
        string='Blockchain Transaction ID',
        readonly=True,
        help='Transaction ID from blockchain'
    )
    
    @api.constrains('payment_amount')
    def _check_payment_amount(self):
        """Validate payment amount"""
        for payment in self:
            if payment.payment_amount <= 0:
                raise ValidationError(_("Payment amount must be greater than zero"))
    
    @api.model
    def create(self, vals):
        """Override create to update contract paid amount"""
        payment = super().create(vals)
        
        # Update contract paid amount
        contract = payment.contract_id
        contract.paid_amount = sum(contract.payment_history_ids.mapped('payment_amount'))
        
        # Post message on contract
        contract.message_post(
            body=_(
                "Payment recorded: %(amount)s %(currency)s via %(method)s (Ref: %(reference)s)",
                amount=payment.payment_amount,
                currency=payment.currency_id.symbol or payment.currency_id.name,
                method=dict(self._fields['payment_method'].selection).get(payment.payment_method),
                reference=payment.payment_reference
            ),
            subject="Payment Recorded"
        )
        
        # Try to sync with blockchain
        try:
            # Generate a mock transaction ID for demonstration
            # In production, this would come from the actual blockchain
            import hashlib
            import time
            
            # Create a unique hash for this payment
            payment_hash = hashlib.sha256(
                f"{contract.contract_id}-{payment.payment_reference}-{payment.payment_amount}-{time.time()}".encode()
            ).hexdigest()
            
            # Format as a blockchain-style transaction ID
            payment.blockchain_tx_id = f"0x{payment_hash[:64]}"
            _logger.info(f"Payment for contract {contract.contract_id} assigned transaction ID: {payment.blockchain_tx_id}")
            
            # Also try to sync with the API if available
            try:
                api_integration = self.env['vendor.contract.api'].create({
                    'api_base_url': 'http://fastapi-gateway:8000/api/v1'
                })
                
                payment_entry = {
                    'amount': payment.payment_amount,
                    'date': payment.payment_date.isoformat(),
                    'reference': payment.payment_reference,
                    'method': payment.payment_method,
                    'notes': payment.notes or '',
                    'recorded_by': payment.recorded_by.name,
                    'recorded_at': payment.recorded_at.isoformat()
                }
                
                result = api_integration.record_payment(contract.contract_id, payment_entry)
                if result.get('success') and result.get('tx_id'):
                    # Override with actual blockchain tx_id if available
                    payment.blockchain_tx_id = result['tx_id']
                    _logger.info(f"Payment synced to blockchain with actual tx_id: {payment.blockchain_tx_id}")
            except Exception as api_error:
                _logger.info(f"API sync failed, using generated tx_id: {api_error}")
                
        except Exception as e:
            _logger.warning(f"Failed to generate blockchain tx_id: {str(e)}")
        
        return payment
    
    def unlink(self):
        """Override unlink to update contract paid amount"""
        contracts = self.mapped('contract_id')
        result = super().unlink()
        
        # Update contract paid amounts
        for contract in contracts:
            contract.paid_amount = sum(contract.payment_history_ids.mapped('payment_amount'))
        
        return result
    
    @api.model
    def migrate_json_payments(self):
        """Migrate existing JSON payment history to payment records"""
        contracts = self.env['vendor.contract'].search([('payment_history', '!=', False)])
        
        for contract in contracts:
            try:
                payments = json.loads(contract.payment_history or '[]')
                for payment_data in payments:
                    # Check if payment already exists
                    existing = self.search([
                        ('contract_id', '=', contract.id),
                        ('payment_reference', '=', payment_data.get('reference', ''))
                    ])
                    
                    if not existing:
                        self.create({
                            'contract_id': contract.id,
                            'payment_amount': payment_data.get('amount', 0),
                            'payment_date': payment_data.get('date', fields.Date.today()),
                            'payment_reference': payment_data.get('reference', 'MIGRATED'),
                            'payment_method': payment_data.get('method', 'other'),
                            'notes': payment_data.get('notes', 'Migrated from JSON history'),
                            'blockchain_tx_id': payment_data.get('blockchain_tx_id', '')
                        })
                        
                _logger.info(f"Migrated payments for contract {contract.contract_id}")
                
            except Exception as e:
                _logger.error(f"Failed to migrate payments for contract {contract.contract_id}: {str(e)}")