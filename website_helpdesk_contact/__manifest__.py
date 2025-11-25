# -*- coding: utf-8 -*-
# Copyright 2025 Lucky Kurniawan <kurniawanluckyy@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Website Helpdesk Contact',
    'summary': 'Create helpdesk tickets from the public Contact Us form.',
    'version': '18.0.1.0.0',
    'author': 'Lucky Kurniawan',
    'website': 'https://github.com/kurniawanlucky/odoo_addons',
    'category': 'Website',
    'depends': ['website', 'helpdesk_mgmt'],
    'data': [
        'data/website_form_data.xml',
        'views/website_contact_template.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
}

