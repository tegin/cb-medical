# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class MedicalMedicationRequest(models.Model):
    _inherit = "medical.medication.request"

    def _get_event_values(self):
        res = super()._get_event_values()
        if self.encounter_id:
            res["encounter_id"] = self.encounter_id.id
        return res

    @api.model
    def get_request_format(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("medical.medication.request.identifier")
        )

    @api.model
    def _get_internal_identifier(self, vals):
        code = self._get_cb_internal_identifier(vals)
        if code:
            return code
        return super()._get_internal_identifier(vals)
