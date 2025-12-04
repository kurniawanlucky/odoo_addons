# -*- coding: utf-8 -*-
# Copyright 2025 Lucky Kurniawan <kurniawanluckyy@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale Line Delivery Address',
    'summary': 'Split deliveries per sales order line intervention address.',
    'version': '18.0.1.0.0',
    'author': 'Lucky Kurniawan',
    'website': 'https://github.com/kurniawanlucky/odoo_addons',
    'category': 'Sales',
    'depends': ['sale_stock'],
    'images': ['static/description/banner.png'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
