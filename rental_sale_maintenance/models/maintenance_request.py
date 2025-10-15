from odoo import models, fields, api
from odoo.exceptions import ValidationError
import pytz
from datetime import datetime


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    @api.constrains('rental_product_id', 'schedule_date', 'duration')
    def _check_active_rental_conflict(self):
        for rec in self:
            if not rec.rental_product_id or not rec.schedule_date:
                continue

            # end_time = rec.schedule_date + timedelta(hours=rec.duration or 0)

            # Check if product is rented during this period
            sale_line = self.env['sale.order.line'].search([
                ('product_id', '=', rec.rental_product_id.id),
                ('order_id.state', 'in', ['sale', 'done']),
                ('rental_start_date', '<=', rec.maintenance_end_datetime),
                ('rental_end_date', '>=', rec.schedule_date),
            ], limit=1)

            if sale_line:
                start_user_dt = fields.Datetime.context_timestamp(rec, sale_line.rental_start_date)
                end_user_dt = fields.Datetime.context_timestamp(rec, sale_line.rental_end_date)
                raise ValidationError(
                    f"{rec.rental_product_id.display_name} is currently rented "
                    f"from {start_user_dt.strftime('%Y-%m-%d %H:%M')} to "
                    f"{end_user_dt.strftime('%Y-%m-%d %H:%M')}. Maintenance cannot be scheduled in this period."
                )
