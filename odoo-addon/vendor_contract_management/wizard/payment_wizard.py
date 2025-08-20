# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
import json
import logging

_logger = logging.getLogger(__name__)


class VendorContractPaymentWizard(models.TransientModel):
    _name = 'vendor.contract.payment.wizard'
    _description = 'Record Contract Payment'

    contract_id = fields.Many2one(
        'vendor.contract',
        string='Contract',
        required=True,
        readonly=True
    )
    contract_display = fields.Char(
        related='contract_id.contract_id',
        string='Contract ID',
        readonly=True
    )
    vendor_name = fields.Char(
        related='contract_id.vendor_name',
        string='Vendor',
        readonly=True
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
        readonly=True
    )
    total_value = fields.Monetary(
        related='contract_id.total_value',
        string='Contract Value',
        readonly=True,
        currency_field='currency_id'
    )
    paid_amount = fields.Monetary(
        related='contract_id.paid_amount',
        string='Already Paid',
        readonly=True,
        currency_field='currency_id'
    )
    remaining_amount = fields.Monetary(
        string='Remaining After Payment',
        compute='_compute_remaining',
        currency_field='currency_id'
    )
    
    @api.depends('contract_id.remaining_amount', 'payment_amount')
    def _compute_remaining(self):
        """Compute remaining amount after this payment"""
        for wizard in self:
            if wizard.contract_id and wizard.payment_amount:
                wizard.remaining_amount = wizard.contract_id.remaining_amount - wizard.payment_amount
            else:
                wizard.remaining_amount = wizard.contract_id.remaining_amount if wizard.contract_id else 0
    
    @api.constrains('payment_amount')
    def _check_payment_amount(self):
        """Validate payment amount"""
        for wizard in self:
            if wizard.payment_amount <= 0:
                raise ValidationError(_("Payment amount must be greater than zero"))
            if wizard.payment_amount > wizard.contract_id.remaining_amount:
                raise ValidationError(_(
                    "Payment amount (%(amount)s) cannot exceed remaining amount (%(remaining)s)",
                    amount=wizard.payment_amount,
                    remaining=wizard.contract_id.remaining_amount
                ))
    
    def action_record_payment(self):
        """Record the payment"""
        self.ensure_one()
        
        # Create payment history record
        payment_history = self.env['vendor.contract.payment.history'].create({
            'contract_id': self.contract_id.id,
            'payment_amount': self.payment_amount,
            'payment_date': self.payment_date,
            'payment_reference': self.payment_reference,
            'payment_method': self.payment_method,
            'notes': self.notes,
        })
        
        # The payment history model's create method handles:
        # - Updating contract paid_amount
        # - Posting message on contract
        # - Syncing with blockchain
        
        # Return action to view the payment list
        return {
            'name': _('Payment History'),
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.contract.payment.history',
            'view_mode': 'list,form',
            'domain': [('contract_id', '=', self.contract_id.id)],
            'target': 'current',
            'context': {
                'default_contract_id': self.contract_id.id,
            }
        }