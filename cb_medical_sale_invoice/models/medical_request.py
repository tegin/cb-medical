# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MedicalRequest(models.AbstractModel):
    _inherit = 'medical.request'

    def get_sale_order_line_vals(self, is_insurance):
        vals = super().get_sale_order_line_vals(is_insurance)
        if is_insurance:
            vals['patient_name'] = self.patient_id.display_name
            vals['authorization_number'] = self.authorization_number
            vals['subscriber_id'] = self.coverage_id.subscriber_id
        return vals
