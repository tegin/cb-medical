from odoo import api, fields, models


class MedicalEncounter(models.Model):
    _inherit = 'medical.encounter'

    sale_order_ids = fields.One2many(
        'sale.order',
        inverse_name='encounter_id',
        readonly=True,
    )

    def get_sale_order_vals(self, partner, key, is_insurance):
        vals = {
            'partner_id': partner,
            'encounter_id': self.id,
            'patient_id': self.patient_id.id,
            'coverage_agreement_id': key.id,
            'pricelist_id': self.env.ref('product.list0').id,
        }
        if is_insurance:
            vals['company_id'] = key.company_id.id
        return vals

    def generate_sale_order(self, key, partner, order_lines):
        is_insurance = bool(key)
        agreement = self.env['medical.coverage.agreement']
        if is_insurance:
            agreement = agreement.browse(key)
        order = self.sale_order_ids.filtered(lambda r: (
            (agreement.id == r.coverage_agreement_id.id and is_insurance) or
            (not is_insurance and not r.coverage_agreement_id)
        ) and r.state == 'draft'and r.partner_id.id == partner)
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

    def get_patient_partner(self):
        return self.patient_id.partner_id.id

    def get_sale_order_lines(self):
        values = dict()
        for model in self.env['medical.request']._get_request_models():
            for request in self.env[model].search([
                ('encounter_id', '=', self.id)
            ]):
                if request.is_sellable_insurance:
                    partner = request.careplan_id.get_payor()
                    key = request.coverage_agreement_id.id
                    if not values.get(key, False):
                        values[key] = {}
                    if not values[key].get(partner, False):
                        values[key][partner] = []
                    values[key][partner].append(
                        request.get_sale_order_line_vals(True))
                if request.is_sellable_private:
                    partner = self.get_patient_partner()
                    if not values.get(0, False):
                        values[0] = {}
                    if not values[0].get(partner, False):
                        values[0][partner] = []
                    values[0][partner].append(
                        request.get_sale_order_line_vals(False))
        return values

    def create_sale_order(self):
        self.ensure_one()
        values = self.get_sale_order_lines()
        for key in values.keys():
            for partner in values[key]:
                self.generate_sale_order(key, partner, values[key][partner])
        return self.action_view_sale_order()

    @api.multi
    def action_view_sale_order(self):
        self.ensure_one()
        action = self.env.ref('sale.action_orders')
        result = action.read()[0]
        result['domain'] = "[('encounter_id', '=', " + str(self.id) + ")]"
        if len(self.sale_order_ids) == 1:
            result['views'] = [(False, 'form')]
            result['res_id'] = self.sale_order_ids.id
        return result
