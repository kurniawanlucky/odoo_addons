from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_rental_order = fields.Boolean(
        string="Rental Order",
        compute="_compute_is_rental_order",
        store=True,
        index=True,
        readonly=True,
    )

    @api.depends('order_line.product_id.type', 'order_line.display_type')
    def _compute_is_rental_order(self):
        for order in self:
            order.is_rental_order = any(
                l.product_id
                and not l.display_type  # ignore section/note
                and l.product_id.type == 'rental'
                for l in order.order_line
            )
