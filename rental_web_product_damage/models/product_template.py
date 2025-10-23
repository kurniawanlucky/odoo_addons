from odoo import models, fields, api
import secrets


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    damage_token = fields.Char("Damage Token", copy=False, readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('type') == 'rental' and not vals.get("damage_token"):
            vals["damage_token"] = secrets.token_urlsafe(16)
        return super().create(vals)

    def refresh_damage_token(self):
        """Call this when rental finished"""
        for rec in self:
            rec.damage_token = secrets.token_urlsafe(16)

    def get_damage_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/rental/damage/{self.damage_token}"

    def action_open_damage_page(self):
        """Open the public rental damage page"""
        self.ensure_one()
        damage_url = self.get_damage_url()
        return {
            'type': 'ir.actions.act_url',
            'url': damage_url,
            'target': 'new',
        }
