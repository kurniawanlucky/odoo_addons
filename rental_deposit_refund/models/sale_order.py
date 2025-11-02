from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    deposit_ids = fields.One2many('rental.deposit', 'sale_order_id', string='Deposits')
    deposit_balance_total = fields.Monetary(
        string='Total Deposit Balance', currency_field='currency_id',
        compute='_compute_deposit_balance_total', store=False)

    @api.depends('deposit_ids.balance', 'deposit_ids.state')
    def _compute_deposit_balance_total(self):
        for order in self:
            order.deposit_balance_total = sum(
                d.balance for d in order.deposit_ids if d.state in ('invoiced', 'refunded') and d.balance > 0
            )

    def _get_default_sales_journal(self):
        self.ensure_one()
        company = self.company_id
        journal = self.env['account.journal'].search(
            [('type', '=', 'sale'), ('company_id', '=', company.id)], limit=1
        )
        if not journal:
            raise UserError(_("No Sales journal found for company %s.") % company.name)
        return journal

    def action_create_deposit_refund(self):
        self.ensure_one()
        # find first refundable deposit (positive balance, still open)
        deposit = next((d for d in self.deposit_ids
                        if d.balance > 0 and d.state in ('invoiced', 'refunded')), None)
        if not deposit:
            raise UserError(_("No refundable deposit found on this order."))

        deposit_product = self.env.ref('rental_deposit.product_product_rental_deposit')
        if not deposit_product:
            raise UserError(_("Missing deposit product 'rental_deposit.product_product_rental_deposit'."))

        journal = self._get_default_sales_journal()
        partner = deposit.partner_id
        order = self

        # map taxes via fiscal position (if any)
        taxes = deposit_product.taxes_id.filtered(lambda t: t.company_id == order.company_id)
        fpos = order.fiscal_position_id
        if fpos:
            taxes = fpos.map_tax(taxes, product=deposit_product, partner=partner)

        # safety: amount must be > 0
        amount = float(deposit.balance)
        if amount <= 0:
            raise UserError(_("Deposit balance is zero."))

        move_vals = {
            'move_type': 'out_refund',
            'partner_id': partner.id,
            'invoice_origin': order.name or '',
            'invoice_date': fields.Date.context_today(self),
            'invoice_date_due': fields.Date.context_today(self),
            'journal_id': journal.id,
            'currency_id': order.currency_id.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': deposit_product.id,
                'name': _('Refund for Deposit %s (SO: %s)') % (deposit.name, order.name),
                'quantity': 1.0,
                'price_unit': amount,
                'tax_ids': [(6, 0, taxes.ids)],
            })],
            # link so your account.move.action_post updates the deposit automatically
            'rental_deposit_id': deposit.id,
        }

        move = self.env['account.move'].create(move_vals)

        # open the created credit note in form view
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': move.id,
        }
