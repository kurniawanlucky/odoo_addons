# -*- coding: utf-8 -*-
# Copyright 2025 Lucky Kurniawan <kurniawanluckyy@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Rental Sale Product Website',
    'summary': 'Add rental product type and rental pricing to sales orders',
    'version': '18.0.1.0.0',
    'author': 'Lucky Kurniawan',
    'website': 'https://github.com/kurniawanlucky/odoo_addons',
    'category': 'Product Management',
    'depends': ['website_sale', 'sale', 'rental_sale_product'],
    'data': [
        'views/rental_search_page.xml',
        'views/rental_search_results.xml',
        'views/website_product_rental_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'rental_web_sale/static/src/scss/rental_search.scss',
            'rental_web_sale/static/src/js/rental_datepicker.js',
            'rental_web_sale/static/src/js/rental_pdp.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
