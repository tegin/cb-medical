# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, models
from odoo.exceptions import ValidationError


class RequestGroup(models.Model):
    _inherit = "medical.request.group"

    def get_third_party_partner(self):
        if self.third_party_bill:
            request = self.procedure_request_ids
            if not request:
                raise ValidationError(
                    _(
                        "Error trying to determine the Third Party Partner. "
                        "No Request was found for Request %s"
                        % request.internal_identifier
                    )
                )
            request.ensure_one()
            procedure = request.procedure_ids
            if not procedure:
                raise ValidationError(
                    _(
                        "Error trying to determine the Third Party Partner. "
                        "No Procedure was found for Request %s"
                        % request.internal_identifier
                    )
                )
            procedure.ensure_one()
            partner = procedure.performer_id
            if partner.delegated_agent_id:
                partner = partner.delegated_agent_id
            if partner.third_party_sequence_id:
                return partner
        return super().get_third_party_partner()
