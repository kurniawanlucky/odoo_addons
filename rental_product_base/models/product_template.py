from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    type = fields.Selection(selection_add=[('rental', 'Rental')], ondelete={'rental': 'cascade'})
    rental_price_per_hour = fields.Float(string="Rental Price / Hour", default=1.0, digits='Product Price')
    rental_price_per_week = fields.Float(string="Rental Price / Week", default=1.0, digits='Product Price')
    rental_price_per_day = fields.Float(string="Rental Price / Day", default=1.0, digits='Product Price')

    rental_min_hours = fields.Float(string="Minimum Hours", default=0)
    rental_min_days = fields.Float(string="Minimum Days", default=0)
    rental_min_weeks = fields.Float(string="Minimum Weeks", default=0)

    deposit_amount = fields.Float(string="Deposit")
