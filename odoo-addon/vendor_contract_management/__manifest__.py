# -*- coding: utf-8 -*-
{
    'name': 'Vendor Contract Management',
    'version': '1.0.0',
    'category': 'Purchases',
    'summary': 'Blockchain-based vendor contract management system',
    'description': """
Vendor Contract Management System
==================================

This module provides a comprehensive vendor contract management system with:
- Vendor registration and management
- Contract creation with three-stage workflow (Created → Verified → Submitted)
- Payment tracking and history
- Blockchain integration via Hyperledger Fabric
- Real-time synchronization with smart contracts
- Dashboard for contract analytics
- Expiration reminders and alerts

Key Features:
-------------
* Three-stage contract workflow
* Payment tracking with history
* Blockchain immutability
* API integration with FastAPI gateway
* Comprehensive reporting
    """,
    'author': 'VendorChain',
    'website': 'https://vendorchain.com',
    'depends': [
        'base',
        'mail',
        'web',
    ],
    'data': [
        # Security - Groups must be defined before access rules
        'security/vendor_contract_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/contract_data.xml',
        # 'data/cron_jobs.xml',  # Temporarily disabled
        
        # Wizard views
        'wizard/payment_wizard_view.xml',
        
        # Views - workflow_views must be first, then contract_views, then vendor_views due to action references
        'views/workflow_views.xml',
        'views/contract_views.xml',
        'views/payment_history_views.xml',
        'views/vendor_views.xml',
        'views/dashboard_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'assets': {},
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'images': ['static/description/banner.png'],
    'external_dependencies': {
        'python': ['requests'],
    },
}