from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    rental_product_id = fields.Many2one(
        'product.product',
        string="Rental Product",
        domain="[('type','=','rental')]"
    )

    @api.depends('schedule_date', 'duration')
    def _compute_end_datetime(self):
        for rec in self:
            rec.maintenance_end_datetime = (
                rec.schedule_date + timedelta(hours=rec.duration)
                if rec.schedule_date and rec.duration
                else False
            )

    maintenance_end_datetime = fields.Datetime(
        string="End Time",
        compute="_compute_end_datetime",
        store=True
    )

    @api.depends('rental_product_id', 'equipment_id', 'schedule_date', 'duration')
    def _compute_display_name(self):
        for rental in self:
            name = "[{}] {} - {} > {}".format(
                rental.name,
                rental.rental_product_id.display_name if rental.rental_product_id else rental.equipment_id.name,
                rental.schedule_date,
                rental.maintenance_end_datetime,
            )
            rental.display_name = name

    @api.constrains('rental_product_id', 'schedule_date', 'duration')
    def _check_active_maintenance_conflict(self):
        """Prevent selecting a product already under maintenance during the same period."""
        for rec in self:
            if not rec.rental_product_id or not rec.schedule_date:
                continue

            # compute this request’s end time
            end_time = rec.schedule_date + timedelta(hours=rec.duration or 0)

            # find overlapping maintenance for same product
            conflict = self.search([
                ('id', '!=', rec.id),
                ('rental_product_id', '=', rec.rental_product_id.id),
                ('stage_id.done', '=', False),  # exclude completed ones
                ('schedule_date', '<=', end_time),
                ('maintenance_end_datetime', '>=', rec.schedule_date),
            ], limit=1)

            if conflict:
                raise ValidationError(
                    f"{rec.rental_product_id.display_name} is already scheduled for maintenance:\n"
                    f"- From: {conflict.schedule_date}\n"
                    f"- To: {conflict.maintenance_end_datetime}\n\n"
                    f"Please choose another time."
                )
