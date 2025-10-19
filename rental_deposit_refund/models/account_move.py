from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    rental_deposit_id = fields.Many2one('rental.deposit', string="Rental Deposit")

    def action_post(self):
        res = super().action_post()
        deposit_product = self.env.ref('rental_deposit.product_product_rental_deposit')
        for move in self:
            deposit_invoice_lines = move.invoice_line_ids.filtered(lambda rec: rec.product_id.id == deposit_product.id)
            is_rental_deposit = True if deposit_invoice_lines else False
            if is_rental_deposit and not move.rental_deposit_id:
                source_orders = self.line_ids.sale_line_ids.order_id
                sale_order_id = source_orders.ids[0]
                amount_deposit = sum(deposit_invoice_lines.mapped('price_subtotal'))
                deposit = self.env['rental.deposit'].create({
                    'partner_id': move.partner_id.id,
                    'deposit_invoice_id': move.id,
                    'amount_deposit': amount_deposit,
                    'sale_order_id': sale_order_id,
                    'state': 'invoiced',
                })
                move.rental_deposit_id = deposit.id
            elif is_rental_deposit and move.rental_deposit_id and move.move_type == 'out_refund':
                rental_deposit = move.rental_deposit_id
                rental_deposit.write({
                    'refund_invoice_id': move.id,
                    'amount_refunded': move.amount_total
                })
        return res
