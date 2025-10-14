from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_view_maintenance(self):
        self.ensure_one()
        action = self.env.ref('maintenance.hr_equipment_request_action').read()[0]
        action['domain'] = [('rental_product_id', 'in', self.product_variant_ids.ids)]
        return action
