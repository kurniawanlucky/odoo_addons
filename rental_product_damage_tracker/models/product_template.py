from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    open_damage_count = fields.Integer(
        string="Open Damages",
        compute="_compute_open_damage_count"
    )

    def _compute_open_damage_count(self):
        DamageLine = self.env["rental.damage.line"]
        for tmpl in self:
            if not tmpl.product_variant_ids:
                tmpl.open_damage_count = 0
                continue
            tmpl.open_damage_count = DamageLine.search_count([
                ("product_id", "in", tmpl.product_variant_ids.ids),
                ("state", "=", "open"),
            ])

    def action_view_open_damages(self):
        """Open rental.damage.line filtered to this template’s variants and OPEN only."""
        self.ensure_one()
        action = self.env.ref("rental_product_damage_tracker.action_rental_damage_line").read()[0]
        # Narrow to all variants of this template and only open findings
        variant_ids = self.product_variant_ids.ids
        action["domain"] = [("product_id", "in", variant_ids)]
        # Nice defaults in search view
        ctx = dict(self._context or {})
        ctx.update({
            "search_default_state_open": 1,
            "default_product_id": variant_ids[:1] if variant_ids else False,
        })
        action["context"] = ctx
        return action
