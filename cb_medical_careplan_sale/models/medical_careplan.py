# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models

SO_OPEN = ['draft']


class MedicalCareplan(models.AbstractModel):
    _inherit = 'medical.careplan'

    sale_order_ids = fields.One2many(
        'sale.order',
        inverse_name='careplan_id',
        readonly=True,
    )

    def get_sale_order_line_vals(self, partner, is_insurance):
        return {
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
            'careplan_id': self.id,
            'pricelist_id': self.env.ref('product.list0').id,
        }

    def get_payor(self, is_insurance):
        if is_insurance:
            return self.coverage_id.coverage_template_id.payor_id
        return self.patient_id.partner_id

    def generate_sale_order(self, key, order_lines):
        is_insurance = bool(key)
        partner = self.get_payor(is_insurance)
        order = self.sale_order_ids.filtered(lambda r: (
            (key == r.coverage_agreement_id.id and is_insurance) or
            (not is_insurance and not self.coverage_agreement_id)))
        if not order:
            order_vals = self.get_sale_order_line_vals(partner, is_insurance)
            order_vals['coverage_agreement_id'] = key
            order = self.env['sale.order'].create(order_vals)
        for order_line in order_lines:
            order_line['order_id'] = order.id
            self.env['sale.order.line'].create(order_line)

    def create_sale_order(self):
        self.ensure_one()
        values = dict()
        for model in self._get_request_models():
            for request in self.env[model].search([
                (self._get_parent_field_name(), '=', self.id)
            ]):
                if request.is_sellable_insurance:
                    if not values.get(request.coverage_agreement_id.id, False):
                        values[request.coverage_agreement_id.id] = []
                    values[request.coverage_agreement_id.id].append(
                        request.get_sale_order_line_vals(True))
                if request.is_sellable_private:
                    if not values.get(0, False):
                        values[0] = []
                    values[0].append(
                        request.get_sale_order_line_vals(False))
        for key in values.keys():
            self.generate_sale_order(key if key > 0 else False, values[key])
        return self.action_view_sale_order()

    @api.multi
    def action_view_sale_order(self):
        self.ensure_one()
        action = self.env.ref(
            'sale.action_orders')
        result = action.read()[0]
        result['domain'] = "[('careplan_id', '=', " + str(self.id) + ")]"
        if len(self.sale_order_ids) == 1:
            result['views'] = [(False, 'form')]
            result['res_id'] = self.sale_order_ids.id
        return result
