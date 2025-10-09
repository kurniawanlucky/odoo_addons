# -*- coding: utf-8 -*-
# © 2025
#   @Lucky Kurniawan <kurniawanluckyy@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Invoice Filter by Date',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Filter Invoices by Today, This Week, This Month, and This Year',
    'description': """
Easily filter and analyze your customer invoices by specific date ranges.
----------------------------------------------------
- Today
- This Week
- This Month
- This Year
    """,
    'author': 'Lucky Kurniawan',
    'website': 'https://github.com/kurniawanlucky/odoo_addons',
    'depends': ['account'],
    'images': ['static/description/banner.png'],
    'data': [
        'views/account_move_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
