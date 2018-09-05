from odoo import api, fields, models


class MedicalEncounter(models.Model):
    _inherit = 'medical.encounter'

    sale_order_ids = fields.One2many(
        'sale.order',
        inverse_name='encounter_id',
        readonly=True,
    )

    sale_order_count = fields.Integer(
        compute='_compute_sale_order_count'
    )

    @api.depends('sale_order_ids')
    def _compute_sale_order_count(self):
        for record in self:
            record.sale_order_count = len(record.sale_order_ids)

    def _get_sale_order_vals(
        self, partner, cov, agreement, third_party_partner, is_insurance
    ):
        vals = {
            'third_party_order': third_party_partner != 0,
            'third_party_partner_id':
                third_party_partner != 0 and third_party_partner,
            'partner_id': partner,
            'encounter_id': self.id,
            'coverage_id': cov,
            'patient_id': self.patient_id.id,
            'coverage_agreement_id': agreement.id,
            'pricelist_id': self.env.ref('product.list0').id,
        }
        if is_insurance:
            vals['company_id'] = agreement.company_id.id
        return vals

    @api.multi
    def _generate_sale_order(
            self, key, cov, partner, third_party_partner, order_lines
    ):
        is_insurance = bool(key)
        is_third_party = bool(third_party_partner)
        agreement = self.env['medical.coverage.agreement']
        if is_insurance:
            agreement = agreement.browse(key)
        order = self.sale_order_ids.filtered(
            lambda r: (
                (
                    agreement == r.coverage_agreement_id and is_insurance and
                    r.coverage_id.id == cov
                ) or (
                    not is_insurance and not r.coverage_agreement_id)
            ) and (
                (
                    is_third_party and r.third_party_order and
                    r.third_party_partner_id == third_party_partner
                ) or (not is_third_party and not r.third_party_order)
            ) and
            r.state == 'draft' and
            r.partner_id.id == partner
        )
        if not order:
            order = self.env['sale.order'].create(self._get_sale_order_vals(
                partner, cov, agreement, third_party_partner, is_insurance))
        order.ensure_one()
        for order_line in order_lines:
            order_line['order_id'] = order.id
            line = self.env['sale.order.line'].with_context(
                force_company=order.company_id.id
            ).create(order_line)
            line.change_company_id()
        return order

    def get_patient_partner(self):
        return self.patient_id.partner_id.id

    def get_sale_order_lines(self):
        values = dict()
        for model in self.env['medical.request']._get_request_models():
            for request in self.env[model].search([
                ('encounter_id', '=', self.id)
            ]):
                query = []
                if request.is_sellable_insurance:
                    query.append((
                        request.coverage_agreement_id.id,
                        request.careplan_id.get_payor(),
                        request.coverage_id.id,
                        True,
                        request.get_third_party_partner()
                        if request.third_party_bill else 0
                    ))
                if request.is_sellable_private:
                    query.append((
                        0, self.get_patient_partner(), False, False,
                        request.get_third_party_partner()
                        if request.third_party_bill else 0
                    ))
                for key, partner, cov, is_insurance, third_party in query:
                    if not values.get(key, False):
                        values[key] = {}
                    if not values[key].get(partner, False):
                        values[key][partner] = {}
                    if not values[key][partner].get(cov, False):
                        values[key][partner][cov] = {}
                    if not values[key][partner][cov].get(third_party, False):
                        values[key][partner][cov][third_party] = []
                    values[key][partner][cov][third_party].append(
                        request.get_sale_order_line_vals(is_insurance))
        return values

    @api.multi
    def create_sale_order(self):
        self.ensure_one()
        values = self.get_sale_order_lines()
        for key in values.keys():
            for partner in values[key]:
                for cov in values[key][partner]:
                    for third_party_partner in values[key][partner][cov]:
                        self._generate_sale_order(
                            key,
                            cov,
                            partner,
                            third_party_partner,
                            values[key][partner][cov][third_party_partner]
                        )
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
