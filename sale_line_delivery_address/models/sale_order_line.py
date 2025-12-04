# -*- coding: utf-8 -*-
# Copyright 2025 Lucky Kurniawan <kurniawanluckyy@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    intervention_address_id = fields.Many2one(
        "res.partner",
        string="Intervention Address",
        domain="[('id', 'child_of', order_partner_id)]",
        help="Alternate delivery address for this line. Must be a child contact of the order customer.",
    )
    intervention_procurement_group_id = fields.Many2one(
        "procurement.group",
        string="Intervention Procurement Group",
        copy=False,
        help="Procurement group used when splitting deliveries per intervention address.",
    )

    def _get_delivery_partner(self):
        self.ensure_one()
        return (
            self.intervention_address_id
            or self.order_id.partner_shipping_id
            or self.order_partner_id
        )

    def _get_location_final(self):
        self.ensure_one()
        partner = self._get_delivery_partner()
        return partner.property_stock_customer

    def _prepare_procurement_group_vals(self):
        vals = super()._prepare_procurement_group_vals()
        partner = self._get_delivery_partner()
        vals["partner_id"] = partner.id
        return vals

    def _prepare_procurement_values(self, group_id=False):
        values = super()._prepare_procurement_values(group_id)
        partner = self._get_delivery_partner()
        values.update(
            {
                "partner_id": partner.id,
                "location_final_id": partner.property_stock_customer,
            }
        )
        return values

    def _prepare_procurement_group_update_vals(self, group):
        self.ensure_one()
        partner = self._get_delivery_partner()
        updated_vals = {}
        if group.partner_id != partner:
            updated_vals["partner_id"] = partner.id
        if group.move_type != self.order_id.picking_policy:
            updated_vals["move_type"] = self.order_id.picking_policy
        if not group.sale_id:
            updated_vals["sale_id"] = self.order_id.id
        return updated_vals

    def _get_intervention_procurement_group(self):
        self.ensure_one()
        if not self.intervention_address_id:
            return self.order_id.procurement_group_id
        group = self.intervention_procurement_group_id
        if not group:
            group = self.env["procurement.group"].search(
                [
                    ("sale_id", "=", self.order_id.id),
                    ("partner_id", "=", self.intervention_address_id.id),
                ],
                limit=1,
            )
            if group:
                self.intervention_procurement_group_id = group
        return group

    def _create_intervention_procurement_group(self):
        self.ensure_one()
        return self.env["procurement.group"].create(self._prepare_procurement_group_vals())

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        if self._context.get("skip_procurement"):
            return True

        intervention_lines = self.filtered("intervention_address_id")
        regular_lines = self - intervention_lines
        if regular_lines:
            super(SaleOrderLine, regular_lines)._action_launch_stock_rule(
                previous_product_uom_qty=previous_product_uom_qty
            )
        if not intervention_lines:
            return True

        precision = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        procurements = []
        for line in intervention_lines:
            line = line.with_company(line.company_id)
            if line.state != "sale" or line.order_id.locked or line.product_id.type != "consu":
                continue

            qty = line._get_qty_procurement(previous_product_uom_qty)
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) == 0:
                continue

            group_id = line._get_intervention_procurement_group()
            if not group_id:
                group_id = line._create_intervention_procurement_group()
                line.intervention_procurement_group_id = group_id

            updated_vals = line._prepare_procurement_group_update_vals(group_id)
            if updated_vals:
                group_id.write(updated_vals)

            values = line._prepare_procurement_values(group_id=group_id)
            product_qty = line.product_uom_qty - qty

            line_uom = line.product_uom
            quant_uom = line.product_id.uom_id
            origin = (
                f"{line.order_id.name} - {line.order_id.client_order_ref}"
                if line.order_id.client_order_ref
                else line.order_id.name
            )
            product_qty, procurement_uom = line_uom._adjust_uom_quantities(product_qty, quant_uom)
            procurements += line._create_procurements(product_qty, procurement_uom, origin, values)

        if procurements:
            self.env["procurement.group"].run(procurements)

        orders = intervention_lines.mapped("order_id")
        for order in orders:
            pickings_to_confirm = order.picking_ids.filtered(lambda p: p.state not in ["cancel", "done"])
            if pickings_to_confirm:
                pickings_to_confirm.action_confirm()
        return True
