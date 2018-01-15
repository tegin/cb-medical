# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MedicalCareplan(models.Model):
    _inherit = 'medical.careplan'

    def get_sale_order_vals(self, partner, key, is_insurance):
        vals = super(MedicalCareplan, self).get_sale_order_vals(
            partner, key, is_insurance)
        if key:
            vals[
                'invoice_group_method_id'
            ] = key.invoice_group_method_id.id
        return vals
