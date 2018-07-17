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
