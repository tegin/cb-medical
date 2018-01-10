# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, _
from odoo.exceptions import ValidationError


class RequestGroup(models.Model):
    # FHIR Rntity: Request Group (https://www.hl7.org/fhir/requestgroup.html)
    _inherit = 'medical.request.group'

    def breakdown_request_group(self):
        feasible_breakdown = False
        if self.is_breakdown:
            for request in self.procedure_request_ids or \
                    self.medication_request_ids:
                if request.coverage_agreement_item:
                    request.is_billable = True
                    feasible_breakdown = True
        if feasible_breakdown:
            self.is_breakdown = False
            self.is_billable = False
        else:
            raise ValidationError(
                _("To breakdown a Request Group at least one request "
                  "should be listed in an agreement item."))
