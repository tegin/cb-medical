# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models

SO_OPEN = ['draft']


class MedicalCareplan(models.Model):
    _inherit = 'medical.careplan'

    sale_order_ids = fields.One2many(
        'sale.order',
        inverse_name='careplan_id',
        readonly=True,
    )
    payor_id = fields.Many2one(
        'res.partner',
        related='coverage_id.coverage_template_id.payor_id',
    )
    sub_payor_id = fields.Many2one(
        'res.partner',
        domain="[('payor_id', '=', payor_id), ('is_sub_payor', '=', True)]"
    )

    @api.onchange('coverage_id')
    def _onchange_coverage_id(self):
        for record in self:
            record.sub_payor_id = False

    def get_sale_order_vals(self, partner, key, is_insurance):
        vals = {
            'partner_id': partner.id,
            'careplan_id': self.id,
            'patient_id': self.patient_id.id,
            'coverage_agreement_id': key.id,
            'pricelist_id': self.env.ref('product.list0').id,
        }
        if is_insurance:
            vals['company_id'] = key.company_id.id
        return vals

    def get_payor(self, is_insurance):
        if is_insurance:
            if self.sub_payor_id:
                return self.sub_payor_id
            return self.payor_id
        return self.patient_id.partner_id

    def generate_sale_order(self, key, order_lines):
        is_insurance = bool(key)
        agreement = self.env['medical.coverage.agreement']
        if is_insurance:
            agreement = agreement.browse(key)
        partner = self.get_payor(is_insurance)
        order = self.sale_order_ids.filtered(lambda r: (
            (agreement.id == r.coverage_agreement_id.id and is_insurance and
             not r.state == 'cancel') or
            (not is_insurance and not self.coverage_agreement_id and not
             r.state == 'cancel')))
        if not order:
            order_vals = self.get_sale_order_vals(
                partner, agreement, is_insurance)
            order = self.env['sale.order'].create(order_vals)
        for order_line in order_lines:
            order_line['order_id'] = order.id
            self.env['sale.order.line'].with_context(
                force_company=order.company_id.id
            ).create(order_line)
        return order

    def get_sale_order_lines(self):
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
        return values

    def create_sale_order(self):
        self.ensure_one()
        values = self.get_sale_order_lines()
        for key in values.keys():
            self.generate_sale_order(key, values[key])
        return self.action_view_sale_order()

    @api.multi
    def action_view_sale_order(self):
        self.ensure_one()
        action = self.env.ref('sale.action_orders')
        result = action.read()[0]
        result['domain'] = "[('careplan_id', '=', " + str(self.id) + ")]"
        if len(self.sale_order_ids) == 1:
            result['views'] = [(False, 'form')]
            result['res_id'] = self.sale_order_ids.id
        return result
