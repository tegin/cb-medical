# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalEncounter(models.Model):
    _inherit = 'medical.encounter'

    pos_session_id = fields.Many2one(
        comodel_name='pos.session',
        string='PoS Session',
        readonly=1,
        track_visibility=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        readonly=1,
        track_visibility=True,
    )

    def _get_sale_order_vals(
            self, partner, agreement, third_party_partner, is_insurance
    ):
        vals = super()._get_sale_order_vals(
            partner, agreement, third_party_partner, is_insurance)
        if self.pos_session_id:
            vals['pos_session_id'] = self.pos_session_id.id
        if not is_insurance:
            if not self.pos_session_id:
                raise ValidationError(_(
                    'Session is required in order to create patient invoice'))
            if not self.company_id:
                self.company_id = self.pos_session_id.config_id.company_id
            vals['company_id'] = self.company_id.id
        return vals

    @api.multi
    def onleave2finished(self):
        self.create_sale_order()
        return super().onleave2finished()

    def down_payment_inverse_vals(self, order, line):
        return {
            'order_id': order.id,
            'product_id': line.product_id.id,
            'name': line.name,
            'product_uom_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'price_unit': - line.price_unit,
        }

    def get_sale_order_lines(self):
        values = super().get_sale_order_lines()
        down_payments = self.sale_order_ids.filtered(
            lambda r: r.is_down_payment and r.coverage_agreement_id is False
        )
        if down_payments:
            if 0 not in values:
                values[0] = {}
            if self.get_patient_partner() not in values[0]:
                values[0][self.get_patient_partner()] = {}
            if 0 not in values[0][self.get_patient_partner()]:
                values[0][self.get_patient_partner()][0] = []
        return values

    def _generate_sale_order(
            self, key, partner, third_party_partner, order_lines
    ):
        order = super()._generate_sale_order(
            key, partner, third_party_partner, order_lines
        )
        if key == 0:
            orders = self.sale_order_ids.filtered(
                lambda r: (
                    r.is_down_payment and r.coverage_agreement_id is False
                )
            )
            for pay in orders:
                for line in pay.order_line:
                    self.env['sale.order.line'].create(
                        self.down_payment_inverse_vals(order, line)
                    )
        return order
