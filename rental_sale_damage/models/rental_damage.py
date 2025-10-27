from odoo import api, fields, models, _


class RentalDamage(models.Model):
    _inherit = "rental.damage"

    rental_order_id = fields.Many2one("sale.order")
