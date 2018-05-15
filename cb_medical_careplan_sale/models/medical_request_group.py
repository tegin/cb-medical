# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class RequestGroup(models.Model):
    _inherit = 'medical.request.group'

    def get_third_party_partner(self):
        if self.third_party_bill:
            request = self.procedure_request_ids
            request.ensure_one()
            procedure = request.procedure_ids
            procedure.ensure_one()
            if procedure.performer_id.third_party_sequence_id:
                return procedure.performer_id.id
        return super().get_third_party_partner()
