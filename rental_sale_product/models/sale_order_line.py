from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_type = fields.Selection(relation='product.product_type', string='Product Type', readonly=True)
    rental_start_date = fields.Datetime(string="Rental Start")
    rental_end_date = fields.Datetime(string="Rental End")
    rental_duration_hours = fields.Float(string="Duration (Hours)", compute="_compute_rental_duration", store=True)
    rental_pricing_breakdown = fields.Char(string="Duration Breakdown", compute="_compute_rental_duration", store=True)
    rental_total_price = fields.Monetary(string="Total Rental Amount", compute="_compute_rental_total_price", store=True)

    @api.depends('rental_start_date', 'rental_end_date')
    def _compute_rental_duration(self):
        for line in self:
            line.rental_duration_hours = 0.0
            line.rental_pricing_breakdown = ''
            if line.rental_start_date and line.rental_end_date:
                delta = line.rental_end_date - line.rental_start_date
                hours = max(delta.total_seconds() / 3600.0, 0)
                line.rental_duration_hours = hours

                weeks = int(hours // (24 * 7))
                remaining_hours = hours - weeks * 24 * 7
                days = int(remaining_hours // 24)
                hours_left = round(remaining_hours - days * 24, 2)

                line.rental_pricing_breakdown = f"{weeks}w {days}d {hours_left}h"

    @api.onchange('product_id', 'rental_duration_hours')
    def _onchange_product_or_duration(self):
        for line in self:
            product = line.product_id
            if not product or product.type != 'rental' or line.rental_duration_hours <= 0:
                continue

            weekly_rate = product.rental_price_per_week or 0
            daily_rate = product.rental_price_per_day or 0
            hourly_rate = product.rental_price_per_hour or 0

            min_hours = product.rental_min_hours or 0
            min_days = product.rental_min_days or 0
            min_weeks = product.rental_min_weeks or 0

            hours = line.rental_duration_hours

            # Compute precise breakdown
            weeks = int(hours // (24 * 7))
            remaining_hours = hours - weeks * 24 * 7
            days = int(remaining_hours // 24)
            hours_left = remaining_hours - days * 24

            # --- Rounding rules ---
            # If hours_left > 0.1 (6 minutes tolerance), keep decimals
            # If hours_left >= 8 hours → round up to 1 extra day
            if hours_left >= 8:
                days += 1
                hours_left = 0
            else:
                hours_left = round(hours_left)

            # If days >= 7 → convert to extra week
            if days >= 7:
                extra_weeks = days // 7
                weeks += extra_weeks
                days = days % 7

            # Apply minimums
            if weeks < min_weeks:
                weeks = min_weeks
                days = 0
                hours_left = 0
            elif weeks == 0 and days < min_days:
                days = min_days
                hours_left = 0
            elif weeks == 0 and days == 0 and hours_left < min_hours:
                hours_left = min_hours

            total_price = (
                    (weeks * weekly_rate) +
                    (days * daily_rate) +
                    (hours_left * hourly_rate)
            )

            line.price_unit = total_price
            line.rental_pricing_breakdown = f"{weeks}w {days}d {hours_left}h (rounded)"

    @api.depends('price_unit', 'product_uom_qty')
    def _compute_rental_total_price(self):
        for line in self:
            line.rental_total_price = line.price_unit * line.product_uom_qty

    @api.onchange('rental_end_date')
    def _check_rental_availability(self):
        """Prevent double booking of the same rental product."""
        for line in self:
            product = line.product_id
            if not product or product.type != 'rental':
                continue
            if not line.rental_start_date or not line.rental_end_date:
                continue
            if line.rental_start_date >= line.rental_end_date:
                raise ValidationError(_("End date must be after start date."))

            overlapping = self.env['sale.order.line'].search_count([
                ('id', '!=', line.id),
                ('product_id', '=', product.id),
                ('order_id.state', 'in', ['sale', 'done']),  # confirmed or completed
                ('rental_start_date', '<=', line.rental_end_date),
                ('rental_end_date', '>=', line.rental_start_date),
            ])

            if overlapping:
                raise ValidationError(_(
                    "Product '%s' is already rented between %s and %s."
                ) % (
                  product.display_name,
                  line.rental_start_date.strftime('%Y-%m-%d %H:%M'),
                  line.rental_end_date.strftime('%Y-%m-%d %H:%M'),
                ))
