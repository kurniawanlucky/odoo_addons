# -*- coding: utf-8 -*-
# Copyright 2025 Lucky Kurniawan <kurniawanluckyy@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Rental Deposit Refund',
    'summary': '',
    'version': '18.0.1.0.0',
    'author': 'Lucky Kurniawan',
    'website': 'https://github.com/kurniawanlucky/odoo_addons',
    'category': 'Rental Management',
    'depends': ['rental_menu_base', 'rental_deposit'],
    'data': [
        'security/ir.model.access.csv',
        'data/rental_deposit_sequence.xml',
        'views/rental_deposit_views.xml',
        'views/res_partner_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
