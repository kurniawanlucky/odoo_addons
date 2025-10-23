from odoo import http
from odoo.http import request


class RentalDamageController(http.Controller):

    @http.route(['/rental/damage/<string:token>'], type='http', auth='public', website=True)
    def rental_damage_page(self, token, **kw):
        product = request.env['product.template'].sudo().search([('damage_token', '=', token)], limit=1)
        if not product:
            return request.not_found()

        damages = request.env['rental.damage'].sudo().search([
            ('product_id', '=', product.product_variant_id.id),
            ('state', '=', 'confirmed'), ('line_ids', '!=', False)
        ])

        return request.render('rental_web_product_damage.damage_page_template', {
            'product': product,
            'damages': damages,
        })
