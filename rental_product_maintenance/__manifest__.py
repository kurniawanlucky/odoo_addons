# -*- coding: utf-8 -*-
# Copyright 2025 Lucky Kurniawan <kurniawanluckyy@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Product Rental Maintenance',
    'summary': '',
    'version': '18.0.1.0.0',
    'author': 'Lucky Kurniawan',
    'website': 'https://github.com/kurniawanlucky/odoo_addons',
    'category': 'Product Management',
    'depends': ['rental_product_base', 'maintenance'],
    'data': [
        'views/maintenance_request_views.xml',
        'views/product_template_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
