# -*- coding: utf-8 -*-
# © 2017
#   @Lucky Kurniawan <kurniawanluckyy@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Purchase Filter Today, Week, Month, Year',
    'summary': 'Filter Purchase Orders by Today, This Week, This Month, and This Year',
    'description': '''
    Filter Purchase Orders quickly by date ranges.
    ----------------------------------------------------
    - Today
    - This Week
    - This Month
    - This Year
        ''',
    'version': '18.0.1.0.0',
    'author': 'Lucky Kurniawan ',
    'website': 'https://github.com/kurniawanlucky/odoo_addons',
    'category': 'Purchase',
    'depends': ['purchase'],
    'data': [
        'views/purchase_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
