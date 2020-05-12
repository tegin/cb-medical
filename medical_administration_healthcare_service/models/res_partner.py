# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.modules import get_module_resource


class ResPartner(models.Model):
    # FHIR Entity: HealthCare Service
    #  (https://www.hl7.org/fhir/healthcareservice.html)
    _inherit = "res.partner"

    is_healthcare_service = fields.Boolean(default=False)
    healthcare_service_identifier = fields.Char(
        readonly=True
    )  # FHIR Field: identifier

    @api.model
    def _get_medical_identifiers(self):
        res = super(ResPartner, self)._get_medical_identifiers()
        res.append(
            (
                "is_medical",
                "is_healthcare_service",
                "healthcare_service_identifier",
                self._get_healthcare_service_identifier,
            )
        )
        return res

    @api.model
    def _get_healthcare_service_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code("medical.healthcare.service")
            or "/"
        )

    @api.model
    def _get_default_image_path(self, vals):
        if vals.get("is_healthcare_service", False):
            return get_module_resource(
                "medical_administration_healtchare_service",
                "static/src/img",
                "healtchare-avatar.png",
            )
