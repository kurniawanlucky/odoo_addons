from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    rental_deposit_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percent', 'Percentage of Rental Price')
    ], string="Deposit Type", default='fixed')

    rental_deposit_value = fields.Float(string="Deposit Value", default=0.0)
    rental_deposit_mode = fields.Selection([
        ('sum', 'Sum All Deposits'),
        ('max', 'Take Maximum Deposit')
    ], string="Deposit Calculation Mode", default='sum')
