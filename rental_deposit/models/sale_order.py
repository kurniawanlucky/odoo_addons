from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('order_line')
    def _onchange_add_rental_deposit(self):
        for order in self:
            deposit_product = self.env.ref('rental_deposit.product_product_rental_deposit')
            rental_lines = order.order_line.filtered(lambda l: l.product_id.type == 'rental')
            deposit_line = order.order_line.filtered(lambda l: l.product_id.id == deposit_product.id)

            if not rental_lines:
                # Remove deposit line if no rental
                order.order_line -= deposit_line
                continue

            total_rental = sum(l.price_subtotal for l in rental_lines)
            deposit_amounts = []
            for l in rental_lines:
                prod = l.product_id
                if prod.rental_deposit_type == 'percent':
                    deposit_amounts.append(total_rental * (prod.rental_deposit_value / 100))
                else:
                    deposit_amounts.append(prod.rental_deposit_value)

            # Calculate total deposit
            calc_mode = rental_lines[0].product_id.rental_deposit_mode or 'sum'
            total_deposit = max(deposit_amounts) if calc_mode == 'max' else sum(deposit_amounts)

            if deposit_line:
                deposit_line.price_unit = total_deposit
            else:
                self.order_line += self.env['sale.order.line'].new({
                    'product_id': deposit_product.id,
                    'name': deposit_product.name,
                    'product_uom_qty': 1,
                    'price_unit': total_deposit
                })
