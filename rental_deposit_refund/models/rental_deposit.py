from odoo import models, fields, api


class RentalDeposit(models.Model):
    _name = 'rental.deposit'
    _description = 'Rental Deposit Tracking'
    _order = 'create_date desc'

    name = fields.Char(default=lambda self: self.env['ir.sequence'].next_by_code('rental.deposit'))
    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
    deposit_invoice_id = fields.Many2one('account.move', string='Deposit Invoice', domain=[('move_type', '=', 'out_invoice')])
    refund_invoice_id = fields.Many2one('account.move', string='Refund Invoice', domain=[('move_type', '=', 'out_refund')])
    sale_order_id = fields.Many2one('sale.order', string='Related Rental Order')
    amount_deposit = fields.Monetary(string='Deposit Amount', currency_field='currency_id')
    amount_refunded = fields.Monetary(string='Refunded Amount', currency_field='currency_id')
    balance = fields.Monetary(string='Balance', compute='_compute_balance', store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('invoiced', 'Invoiced'),
        ('refunded', 'Refunded'),
        ('closed', 'Closed')
    ], default='draft')

    @api.depends('amount_deposit', 'amount_refunded')
    def _compute_balance(self):
        for rec in self:
            rec.balance = rec.amount_deposit - rec.amount_refunded
