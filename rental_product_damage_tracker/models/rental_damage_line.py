from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RentalDamageLine(models.Model):
    _name = "rental.damage.line"
    _description = "Rental Damage Line"
    _inherit = ["mail.thread"]
    _order = "state asc, id desc"

    damage_id = fields.Many2one("rental.damage", required=True, ondelete="cascade")
    product_id = fields.Many2one(related="damage_id.product_id", store=True)
    name = fields.Char(required=True, tracking=True)
    description = fields.Text()
    area = fields.Selection([
        ("front_bumper", "Front bumper"),
        ("rear_bumper", "Rear bumper"),
        ("left_front", "Left front"),
        ("right_front", "Right front"),
        ("left_rear", "Left rear"),
        ("right_rear", "Right rear"),
        ("hood", "Hood"),
        ("roof", "Roof"),
        ("trunk", "Trunk"),
        ("interior", "Interior"),
        ("other", "Other"),
    ], tracking=True)
    severity = fields.Selection([("minor","Minor"),("moderate","Moderate"),("major","Major")],
                                default="minor", required=True, tracking=True)
    state = fields.Selection([("open", "Open"), ("fixed", "Fixed")], default="open", tracking=True)
    report_date = fields.Datetime(related='damage_id.report_date')
    fixed_date = fields.Datetime()
    cover_image = fields.Image(max_width=1920, max_height=1920, store=True)
    images = fields.Many2many("ir.attachment", string="Photos")

    def action_mark_fixed(self):
        for rec in self:
            rec.write({
                "state": "fixed",
                "fixed_date": fields.Datetime.now(),
            })
            rec.damage_id._sync_state_from_lines()

    def action_reopen(self):
        for rec in self:
            rec.write({
                "state": "open",
                "fixed_date": False,
            })
            rec.damage_id._sync_state_from_lines()
