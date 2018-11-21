# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MedicalCoverageAgreementItem(models.Model):
    _inherit = 'medical.coverage.agreement.item'

    def _check_authorization(self, method, **kwargs):
        vals = super()._check_authorization(method, **kwargs)
        if 'invoice_group_method_id' not in vals:
            vals['invoice_group_method_id'] = (
                method.invoice_group_method_id.id or
                self.coverage_agreement_id.invoice_group_method_id.id
            )
        return vals
