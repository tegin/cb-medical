# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MedicalRequest(models.AbstractModel):
    _inherit = 'medical.request'

    def get_sale_order_line_vals(self, is_insurance):
        vals = super().get_sale_order_line_vals(is_insurance)
        if is_insurance:
            vals[
                'coverage_agreement_item_id'
            ] = self.coverage_agreement_item_id.id or False
        return vals

    def _change_authorization(self, vals, **kwargs):
        res = super()._change_authorization(vals, **kwargs)
        if self.mapped('sale_order_line_ids'):
            self.mapped('sale_order_line_ids').filtered(
                lambda r: not r.is_private
            ).write(vals)
        return res
