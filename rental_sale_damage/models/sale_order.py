# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    rental_damage_count = fields.Integer(
        string="Damage Reports",
        compute="_compute_rental_damage_count",
        store=False,
    )

    def _compute_rental_damage_count(self):
        Damage = self.env["rental.damage"]
        for order in self:
            order.rental_damage_count = Damage.search_count([
                ("rental_order_id", "=", order.id)
            ])

    def action_open_rental_damage(self):
        self.ensure_one()
        action = self.env.ref("rental_sale_damage.action_rental_damage_from_sale").read()[0]
        action["domain"] = [("rental_order_id", "=", self.id)]
        action["context"] = {
            **(self.env.context or {}),
            "default_rental_order_id": self.id,
            # optional auto-fill when only one rental product exists
            "default_product_id": self._default_damage_product_id(),
        }
        return action

    def _default_damage_product_id(self):
        """Prefill product if the order has exactly one rental item."""
        self.ensure_one()
        rental_lines = self.order_line.filtered(
            lambda l: getattr(l.product_id, "type", False) == "rental"
        )
        products = rental_lines.mapped("product_id")
        return products[0].id if len(products) == 1 else False

    def action_create_rental_damage(self):
        """Open a new damage form directly from Sale Order."""
        self.ensure_one()
        ctx = {
            **(self.env.context or {}),
            "default_rental_order_id": self.id,
            "default_product_id": self._default_damage_product_id(),
        }
        return {
            "type": "ir.actions.act_window",
            "name": _("New Damage Report"),
            "res_model": "rental.damage",
            "view_mode": "form",
            "target": "current",
            "context": ctx,
        }
