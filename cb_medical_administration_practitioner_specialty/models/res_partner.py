# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    # FHIR Entity: PractitionerRole
    # (https://www.hl7.org/fhir/practitionerrole.html)
    _inherit = "res.partner"

    specialty_id = fields.Many2one(
        "medical.specialty",
        string="Specialty",
        compute="_compute_specialty",
        inverse="_inverse_specialty",
        search="_search_specialty",
    )
    practitioner_role_id = fields.Many2one(
        "medical.role",
        string="Role",
        compute="_compute_role",
        inverse="_inverse_role",
        search="_search_practitioner_role",
    )
    specialty_required = fields.Boolean(
        related="practitioner_role_id.specialty_required", readonly=True
    )

    def _search_specialty(self, operator, value):
        return [("specialty_ids", operator, value)]

    def _search_practitioner_role(self, operator, value):
        return [("practitioner_role_ids", operator, value)]

    @api.depends("practitioner_role_ids")
    def _compute_role(self):
        for record in self:
            record.practitioner_role_id = record.practitioner_role_ids[:1]

    @api.depends("specialty_ids")
    def _compute_specialty(self):
        for record in self:
            record.specialty_id = record.specialty_ids[:1]

    def _inverse_specialty(self):
        for record in self:
            record.specialty_ids = record.specialty_id

    def _inverse_role(self):
        for record in self:
            record.practitioner_role_ids = record.practitioner_role_id

    @api.constrains("practitioner_role_ids")
    def _check_practitioner_role(self):
        for record in self:
            if len(record.practitioner_role_ids) > 1:
                raise ValidationError(_("Only one role is allowed"))

    def _get_practitioner_specialty_identifier(
        self, practitioner_role_id=False, specialty_id=False
    ):
        role = (
            self.env["medical.role"].browse(practitioner_role_id)
            or self.practitioner_role_id
        )
        if role.specialty_required:
            specialty = (
                self.env["medical.specialty"].browse(specialty_id) or self.specialty_id
            )
            return specialty.sequence_id._next()
        return False

    @api.model_create_multi
    def create(self, mvals):
        for vals in mvals:
            self._fill_ref_field(vals)
        return super().create(mvals)

    def write(self, vals):
        result = super().write(vals)
        if vals.get("is_practitioner"):
            for record in self:
                if not record.ref:
                    record.ref = record._get_practitioner_specialty_identifier()
        return result

    def _fill_ref_field(self, vals):
        defaults = self.default_get(
            ["ref", "is_practitioner", "practitioner_role_id", "specialty_id"]
        )
        if vals.get("ref", defaults.get("ref", False)) != defaults.get(
            "ref", False
        ) or not vals.get("is_practitioner", defaults.get("is_practitioner")):
            return
        vals["ref"] = self._get_practitioner_specialty_identifier(
            vals.get("practitioner_role_id", defaults.get("practitioner_role_id")),
            vals.get("specialty_id", defaults.get("specialty_id")),
        )
