from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.constrains('product_id', 'start_date', 'end_date')
    def _check_maintenance_conflict(self):
        for line in self:
            if line.product_id != 'rental' or (not line.product_id or not line.start_date or not line.end_date):
                continue

            maintenance = self.env['maintenance.request'].search([
                ('rental_product_id', '=', line.product_id.id),
                ('schedule_date', '<=', line.rental_end_date),
                ('maintenance_end_datetime', '>=', line.rental_start_date),
                ('stage_id.done', '=', False)
            ], limit=1)

            if maintenance:
                start_user_dt = fields.Datetime.context_timestamp(line, maintenance.schedule_date)
                end_user_dt = fields.Datetime.context_timestamp(line, maintenance.maintenance_end_datetime)
                raise ValidationError(
                    f"{line.product_id.display_name} is scheduled for maintenance from "
                    f"{start_user_dt.strftime('%Y-%m-%d %H:%M')} to "
                    f"{end_user_dt.strftime('%Y-%m-%d %H:%M')}. "
                    "It cannot be rented in this period."
                )
