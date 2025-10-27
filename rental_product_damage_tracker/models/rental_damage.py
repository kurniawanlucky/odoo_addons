from odoo import api, fields, models, _
from odoo.exceptions import UserError


class RentalDamage(models.Model):
    _name = "rental.damage"
    _description = "Rental Damage Report"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "report_date desc, id desc"

    name = fields.Char(default="/", readonly=True, copy=False)
    type = fields.Selection([
        ("check_in","Check-in"), ("check_out","Check-out"), ("adhoc","Ad-hoc")
    ], required=True, default="adhoc", tracking=True)
    product_id = fields.Many2one("product.product", required=True, tracking=True, index=True,
                                 domain="[('type', '=', 'rental')]")
    report_date = fields.Datetime(default=lambda self: fields.Datetime.now(), required=True, index=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("confirmed", "Confirmed"),
        ("closed", "Closed"),
    ], default="draft", tracking=True)
    note = fields.Text()
    line_ids = fields.One2many("rental.damage.line", "damage_id", string="Findings")

    open_line_count = fields.Integer(compute="_compute_counts")
    fixed_line_count = fields.Integer(compute="_compute_counts")

    @api.depends("line_ids.state")
    def _compute_counts(self):
        for rec in self:
            rec.open_line_count = sum(l.state == "open" for l in rec.line_ids)
            rec.fixed_line_count = sum(l.state == "fixed" for l in rec.line_ids)

    def action_confirm(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("Add at least one finding before confirming."))
            rec.state = "confirmed"

    def _sync_state_from_lines(self):
        """Header auto-closes when all lines fixed; reopens if any line is open."""
        for rec in self:
            if not rec.line_ids:
                # No lines = keep as-is (or stay draft); choose your policy
                continue
            if all(l.state == "fixed" for l in rec.line_ids):
                if rec.state != "closed":
                    rec.state = "closed"
            else:
                if rec.state == "closed":
                    rec.state = "confirmed"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("rental.damage") or "/"
        return super().create(vals_list)
