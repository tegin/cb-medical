# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class MedicalMedicationAdministration(models.Model):
    _inherit = "medical.medication.administration"

    @api.model
    def get_request_format(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("medical.medical.administration.ident")
        )

    @api.model
    def _get_internal_identifier(self, vals):
        code = self._get_cb_internal_identifier(vals)
        if code:
            return code
        return super()._get_internal_identifier(vals)
