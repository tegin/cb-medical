# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalRequest(models.AbstractModel):
    _inherit = 'medical.request'

    sale_order_line_ids = fields.One2many(
        string='Sale order lines',
        comodel_name='sale.order.line',
        compute='_compute_sale_order_line_ids',
    )
    is_sellable_insurance = fields.Boolean(
        compute='_compute_is_sellable'
    )
    is_sellable_private = fields.Boolean(
        compute='_compute_is_sellable'
    )

    def _compute_sale_order_line_ids(self):
        inverse_field_name = self._get_parent_field_name()
        for rec in self:
            sale_order_line_ids = self.env['sale.order.line'].search(
                [(inverse_field_name, '=', rec.id)])
            rec.sale_order_line_ids = sale_order_line_ids

    @api.depends('is_billable', 'sale_order_line_ids',
                 'coverage_agreement_item_id')
    def _compute_is_sellable(self):
        for rec in self:
            ca = rec.coverage_agreement_id
            rec.is_sellable_private = bool(
                rec.is_billable and
                len(rec.sale_order_line_ids.filtered(
                    lambda r: (
                        r.state != 'cancel' and
                        not r.order_id.coverage_agreement_id)
                )) == 0 and
                rec.coverage_agreement_item_id.private_price > 0
            )
            rec.is_sellable_insurance = bool(
                rec.is_billable and
                len(rec.sale_order_line_ids.filtered(
                    lambda r: (
                        r.state != 'cancel' and
                        r.order_id.coverage_agreement_id.id == ca.id)
                )) == 0 and
                rec.coverage_agreement_item_id.coverage_price > 0
            )

    def compute_price(self, is_insurance):
        cai = self.coverage_agreement_item_id
        return cai.coverage_price if is_insurance else cai.private_price

    def get_sale_order_line_vals(self, is_insurance):
        return {
            'product_id': self.service_id.id,
            'name': self.name,
            self._get_parent_field_name(): self.id,
            'product_uom_qty': 1,
            'product_uom': self.service_id.uom_id.id,
            'price_unit': self.compute_price(is_insurance),
        }
