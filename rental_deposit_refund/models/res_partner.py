from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    deposit_count = fields.Integer(compute='_compute_deposit_count')
    total_deposit_balance = fields.Monetary(compute='_compute_total_deposit_balance', currency_field='currency_id')

    def _compute_deposit_count(self):
        for partner in self:
            partner.deposit_count = self.env['rental.deposit'].search_count([('partner_id', '=', partner.id)])

    def _compute_total_deposit_balance(self):
        for partner in self:
            deposits = self.env['rental.deposit'].search([('partner_id', '=', partner.id)])
            partner.total_deposit_balance = sum(d.balance for d in deposits)

    def action_view_rental_deposits(self):
        action = self.env['ir.actions.act_window']._for_xml_id('rental_deposit_refund.action_rental_deposit')
        action['domain'] = [('partner_id', '=', self.id)]
        return action
        return {
            'type': 'ir.actions.act_window',
            'name': 'Rental Deposits',
            'res_model': 'rental.deposit',
            'view_mode': 'tree,form',
            'view_id': self.env.ref("account.res_company_view_form_terms", False).id,
            'domain': [('partner_id', '=', self.id)],
        }
