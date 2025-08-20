# -*- coding: utf-8 -*-

from odoo import models, fields, api


class VendorContractWorkflowLog(models.Model):
    _name = 'vendor.contract.workflow.log'
    _description = 'Contract Workflow Log'
    _order = 'performed_at desc'
    _rec_name = 'action'

    contract_id = fields.Many2one(
        'vendor.contract',
        string='Contract',
        required=True,
        ondelete='cascade'
    )
    action = fields.Char(
        string='Action',
        required=True
    )
    from_state = fields.Selection([
        ('draft', 'Draft'),
        ('created', 'Created'),
        ('verified', 'Verified'),
        ('submitted', 'Submitted'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
    ], string='From State')
    
    to_state = fields.Selection([
        ('draft', 'Draft'),
        ('created', 'Created'),
        ('verified', 'Verified'),
        ('submitted', 'Submitted'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
    ], string='To State', required=True)
    
    performed_by = fields.Many2one(
        'res.users',
        string='Performed By',
        required=True
    )
    performed_at = fields.Datetime(
        string='Performed At',
        required=True,
        default=fields.Datetime.now
    )
    notes = fields.Text(
        string='Notes'
    )
    blockchain_tx_id = fields.Char(
        string='Blockchain Transaction ID',
        readonly=True
    )
    
    def name_get(self):
        """Custom name display"""
        result = []
        for log in self:
            name = f"{log.action} - {log.performed_at}"
            result.append((log.id, name))
        return result