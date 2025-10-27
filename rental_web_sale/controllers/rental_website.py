# controllers/rental_website.py
from odoo import http, fields, _
from odoo.http import request
from datetime import datetime

DATETIME_FORMAT = "%Y-%m-%d %H:%M"


class RentalWebsiteController(http.Controller):

    @http.route(['/rental'], type='http', auth='public', website=True)
    def rental_search_page(self, **kw):
        return request.render('rental_web_sale.rental_search_page')

    @http.route(['/rental/results'], type='http', auth='public', website=True)
    def rental_results(self, **kw):
        start_date = kw.get('start_date')
        end_date = kw.get('end_date')
        start_time = kw.get('start_time', '09:00')
        end_time = kw.get('end_time', '09:00')
        if not (start_date and end_date):
            return request.redirect('/rental')

        start_dt = datetime.strptime(f"{start_date} {start_time}", DATETIME_FORMAT)
        end_dt = datetime.strptime(f"{end_date} {end_time}", DATETIME_FORMAT)
        if start_dt >= end_dt:
            return request.redirect('/rental')

        Product = request.env['product.product'].sudo()
        products = Product.search([('type', '=', 'rental')])

        # Filter by availability (no overlapping confirmed/done SOL)
        available_products = []
        SOL = request.env['sale.order.line'].sudo()
        for product in products:
            overlapping = SOL.search_count([
                ('product_id', '=', product.id),
                ('order_id.state', 'in', ['sale', 'done']),
                ('rental_start_date', '<=', end_dt),
                ('rental_end_date', '>=', start_dt),
            ])
            if not overlapping:
                available_products.append(product)

        return request.render('rental_web_sale.rental_search_results', {
            'products': available_products,
            'start_date': start_date,
            'end_date': end_date,
            'start_time': start_time,
            'end_time': end_time,
        })

    @http.route(['/rental/add/<int:product_id>'], type='http', auth='public', website=True, csrf=False)
    def rental_add_to_cart(self, product_id, **kw):
        """Add rental product with dates; override price; ensure availability just-in-time."""
        start_date = kw.get('start_date')
        end_date = kw.get('end_date')
        start_time = kw.get('start_time', '09:00')
        end_time = kw.get('end_time', '09:00')
        qty = float(kw.get('add_qty') or 1.0)

        if not (start_date and end_date):
            return request.redirect('/rental')
        try:
            start_dt = datetime.strptime(f"{start_date} {start_time}", DATETIME_FORMAT)
            end_dt = datetime.strptime(f"{end_date} {end_time}", DATETIME_FORMAT)
        except Exception:
            return request.redirect('/rental')
        if start_dt >= end_dt:
            return request.redirect('/rental')

        product = request.env['product.product'].sudo().browse(product_id).exists()
        if not product or product.type != 'rental':
            return request.redirect('/rental')

        # JIT availability check
        overlapping = request.env['sale.order.line'].sudo().search_count([
            ('product_id', '=', product.id),
            ('order_id.state', 'in', ['sale', 'done']),
            ('rental_start_date', '<=', end_dt),
            ('rental_end_date', '>=', start_dt),
        ])
        if overlapping:
            return request.redirect('/rental')

        # Get/Create cart
        order = request.website.sale_get_order(force_create=1)
        # Add the item
        result = order._cart_update(product_id=product_id, add_qty=qty)
        # Find the affected line
        line = order.order_line.browse(result.get('line_id')) if result.get('line_id') else \
               order.order_line.filtered(lambda l: l.product_id.id == product_id).sorted('id')[-1]

        # Compute price using your rounding/minimum rules
        hours = (end_dt - start_dt).total_seconds() / 3600.0
        price_unit, breakdown = request.env['product.product']._compute_rental_price(product, hours)

        # Write rental fields + override price; append breakdown to description
        line.sudo().write({
            'rental_start_date': fields.Datetime.to_string(start_dt),
            'rental_end_date': fields.Datetime.to_string(end_dt),
            'price_unit': price_unit,
            'name': (line.name or product.display_name) + (f"\nRental: {breakdown}" if breakdown else ''),
        })
        line.sudo()._compute_rental_duration()
        line.sudo()._compute_rental_total_price()

        return request.redirect('/shop/cart')
