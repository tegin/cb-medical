# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models, fields
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
    )
    practitioner_role_id = fields.Many2one(
        "medical.role",
        string="Role",
        compute="_compute_role",
        inverse="_inverse_role",
    )
    specialty_required = fields.Boolean(
        related="practitioner_role_id.specialty_required", readonly=True
    )

    @api.multi
    @api.depends("practitioner_role_ids")
    def _compute_role(self):
        for record in self:
            if record.practitioner_role_ids:
                record.practitioner_role_id = record.practitioner_role_ids[0]

    @api.multi
    @api.depends("specialty_ids")
    def _compute_specialty(self):
        for record in self:
            if record.specialty_ids:
                record.specialty_id = record.specialty_ids[0]

    @api.multi
    def _inverse_specialty(self):
        for record in self:
            record.specialty_ids = record.specialty_id

    @api.multi
    def _inverse_role(self):
        for record in self:
            record.practitioner_role_ids = record.practitioner_role_id

    @api.constrains("practitioner_role_ids")
    def _check_practitioner_role(self):
        for record in self:
            if len(record.practitioner_role_ids) > 1:
                raise ValidationError(_("Only one role is allowed"))

    @api.model
    def _get_practitioner_identifier(self, vals):
        if vals.get("practitioner_role_id", False):
            role = self.env["medical.role"].browse(
                vals["practitioner_role_id"]
            )
            if role.specialty_required:
                specialty = self.env["medical.specialty"].browse(
                    vals["specialty_id"]
                )
                if specialty.sequence_id:
                    return specialty.sequence_id._next()
        return super(ResPartner, self)._get_practitioner_identifier(vals)
