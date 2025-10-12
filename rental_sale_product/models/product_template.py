from odoo import models, fields, api, _
from datetime import datetime


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    total_rental_qty = fields.Integer(string="Total Rental Units", default=1)
    rental_active_count = fields.Integer(string="Currently Rented", compute="_compute_rental_counts")
    rental_available_qty = fields.Integer(string="Available Units", compute="_compute_rental_counts")

    def _compute_rental_counts(self):
        now = fields.Datetime.now()
        for product in self:
            active_lines = self.env['sale.order.line'].search_count([
                ('product_id', 'in', product.product_variant_ids.ids),
                ('order_id.state', 'in', ['sale', 'done']),
                ('rental_start_date', '<=', now),
                ('rental_end_date', '>=', now),
            ])
            product.rental_active_count = active_lines
            product.rental_available_qty = max(product.total_rental_qty - active_lines, 0)

    def action_view_rental_orders(self):
        """Smart button → open related rental orders"""
        self.ensure_one()
        action = self.env.ref('sale.action_orders').read()[0]
        action['domain'] = [
            ('order_line.product_id', 'in', self.product_variant_ids.ids),
            ('order_line.product_id.type', '=', 'rental'),
        ]
        action['context'] = {'default_product_id': self.id}
        return action
