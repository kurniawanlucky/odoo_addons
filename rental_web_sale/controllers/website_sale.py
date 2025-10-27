from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http, fields
from odoo.http import request


class WebsiteSaleRentalFix(WebsiteSale):

    @http.route('/shop/address/submit', type='http', methods=['POST'], auth='public', website=True, sitemap=False)
    def shop_address_submit(
            self, partner_id=None, address_type='billing', use_delivery_as_billing=None,
            callback=None, required_fields=None, **form_data
    ):
        # 1) Run the original flow (creates/updates address, may change pricelist/partner, etc.)
        resp = super().shop_address_submit(
            partner_id=partner_id,
            address_type=address_type,
            use_delivery_as_billing=use_delivery_as_billing,
            callback=callback,
            required_fields=required_fields,
            **form_data
        )

        order = request.website.sale_get_order()
        if not order:
            return resp

        for line in order.order_line.sudo().filtered(lambda l: l.product_id.type == 'rental' and l.rental_start_date and l.rental_end_date):
            # recompute price from stored dates
            start_dt = fields.Datetime.from_string(line.rental_start_date)
            end_dt = fields.Datetime.from_string(line.rental_end_date)
            if end_dt and start_dt and end_dt > start_dt:
                hours = (end_dt - start_dt).total_seconds() / 3600.0
                price_unit, breakdown = request.env['product.product']._compute_rental_price(line.product_id, hours)
                line.write({
                    'price_unit': price_unit,
                    'name': (line.name or line.product_id.display_name) + (f"\nRental: {breakdown}" if breakdown else ''),
                })
                line._compute_rental_duration()
                line._compute_rental_total_price()

        return resp