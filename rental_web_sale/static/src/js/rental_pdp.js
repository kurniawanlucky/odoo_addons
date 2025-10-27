odoo.define('rental_web_sale.rental_pdp', function (require) {
  'use strict';
  const publicWidget = require('web.public.widget');
  const rpc = require('web.rpc');

  publicWidget.registry.RentalPDP = publicWidget.Widget.extend({
    selector: '.o_add_to_cart',
    events: {
      'change input[name="rental_start_date"]': '_onDatesChange',
      'change input[name="rental_end_date"]': '_onDatesChange',
      'keyup input[name="rental_start_date"]': '_onDatesChange',
      'keyup input[name="rental_end_date"]': '_onDatesChange',
    },
    start() {
      this._onDatesChange();
      return this._super.apply(this, arguments);
    },
    _onDatesChange() {
      const $form = this.$el;
      const start = $form.find('input[name="rental_start_date"]').val();
      const end = $form.find('input[name="rental_end_date"]').val();
      const productId = parseInt($form.find('input[name="product_id"]').val());
      if (!start || !end || isNaN(productId)) {
        this._setPreview('');
        return;
      }
      rpc.query({
        route: '/rental/compute_price',
        params: { product_id: productId, start: start, end: end },
      }).then((res) => {
        if (res && res.price_unit) {
          this._setPreview(`Estimated unit price: ${res.price_unit} – ${res.breakdown}`);
        } else {
          this._setPreview('');
        }
      }).catch(() => this._setPreview(''));
    },
    _setPreview(text) {
      const el = document.getElementById('rental_price_preview');
      if (el) el.textContent = text || '';
    },
  });
});
