from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _compute_rental_price(self, product, hours):
        weekly_rate = getattr(product, 'rental_price_per_week', 0.0) or 0.0
        daily_rate = getattr(product, 'rental_price_per_day', 0.0) or 0.0
        hourly_rate = getattr(product, 'rental_price_per_hour', 0.0) or 0.0

        min_hours = getattr(product, 'rental_min_hours', 0.0) or 0.0
        min_days = getattr(product, 'rental_min_days', 0.0) or 0.0
        min_weeks = getattr(product, 'rental_min_weeks', 0.0) or 0.0

        weeks = int(hours // (24 * 7))
        remaining_hours = hours - weeks * 24 * 7
        days = int(remaining_hours // 24)
        hours_left = remaining_hours - days * 24

        if hours_left >= 8:
            days += 1
            hours_left = 0
        else:
            hours_left = round(hours_left)

        if days >= 7:
            extra_weeks = days // 7
            weeks += extra_weeks
            days = days % 7

        if weeks < min_weeks:
            weeks, days, hours_left = min_weeks, 0, 0
        elif weeks == 0 and days < min_days:
            days, hours_left = min_days, 0
        elif weeks == 0 and days == 0 and hours_left < min_hours:
            hours_left = min_hours

        price = (weeks * weekly_rate) + (days * daily_rate) + (hours_left * hourly_rate)
        breakdown = f"{weeks}w {days}d {int(hours_left)}h (rounded)"
        return price, breakdown
