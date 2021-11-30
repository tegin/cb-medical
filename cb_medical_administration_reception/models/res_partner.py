# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    # FHIR Entity: Location (https://www.hl7.org/fhir/location.html)
    _inherit = "res.partner"

    is_reception = fields.Boolean(default=False)
    reception_identifier = fields.Char(readonly=True)  # FHIR Field: identifier
    reception_count = fields.Integer(compute="_compute_reception_count")

    @api.depends("location_ids")
    def _compute_reception_count(self):
        for record in self:
            record.reception_count = len(
                record.location_ids.filtered(lambda r: r.is_reception)
            )

    @api.depends("location_ids")
    def _compute_location_count(self):
        for record in self:
            record.location_count = len(
                record.location_ids.filtered(lambda r: r.is_location)
            )

    @api.constrains("is_reception", "center_id")
    def check_reception_center(self):
        if self.is_reception and not self.center_id:
            raise ValidationError(_("Center must be fullfilled on receptions"))

    @api.model
    def _get_medical_identifiers(self):
        res = super(ResPartner, self)._get_medical_identifiers()
        res.append(
            (
                "is_medical",
                "is_reception",
                "reception_identifier",
                self._get_reception_identifier,
            )
        )
        return res

    @api.model
    def _get_reception_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("medical.reception") or "/"

    @api.model
    def default_medical_fields(self):
        result = super(ResPartner, self).default_medical_fields()
        result.append("is_reception")
        return result
