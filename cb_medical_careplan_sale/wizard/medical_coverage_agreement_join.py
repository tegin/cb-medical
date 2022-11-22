# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError


class MedicalCoverageAgreementJoin(models.TransientModel):
    _inherit = "medical.coverage.agreement.join"

    def check_possible_join(self):
        super().check_possible_join()
        if len(self.agreement_ids.mapped("invoice_group_method_id")) > 1:
            raise ValidationError(_("Invoice group method must be the same"))
        if (
            self.agreement_ids.filtered(lambda r: not r.invoice_group_method_id)
            and len(self.agreement_ids.mapped("invoice_group_method_id")) == 1
        ):
            raise ValidationError(_("Invoice group method must be the same"))
