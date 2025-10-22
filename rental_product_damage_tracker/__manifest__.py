# -*- coding: utf-8 -*-
# Copyright 2025 Lucky Kurniawan <kurniawanluckyy@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Rental Damage Tracker',
    'summary': 'Track per-vehicle damages and show open issues on website',
    'version': '18.0.1.0.0',
    'author': 'Lucky Kurniawan',
    'website': 'https://github.com/kurniawanlucky/odoo_addons',
    'category': 'Product Management',
    'depends': ['product', 'rental_menu_base'],
    'data': [
        'data/rental_damage_sequence.xml',
        'security/ir.model.access.csv',
        'views/rental_damage_views.xml',
        'views/rental_damage_line_views.xml',
        'views/rental_menu_views.xml',
        'views/product_template_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
