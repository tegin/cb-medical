# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    # FHIR Entity: Payor
    # (https://www.hl7.org/fhir/coverage-definitions.html#Coverage.payor)
    _inherit = "res.partner"

    @api.model
    def _default_edit_sub_payor(self):
        return (
            self.env["res.users"]
            .browse(self.env.uid)
            .has_group(
                "medical_financial_coverage." "group_medical_payor_manager"
            )
        )

    is_sub_payor = fields.Boolean(default=False)
    edit_sub_payor = fields.Boolean(
        default=_default_edit_sub_payor, compute="_compute_edit_sub_payor"
    )
    sub_payor_identifier = fields.Char(readonly=True)  # FHIR Field: identifier
    payor_id = fields.Many2one(
        "res.partner", string="Payor", domain=[("is_payor", "=", True)]
    )
    sub_payor_ids = fields.One2many("res.partner", inverse_name="payor_id")

    def _compute_edit_sub_payor(self):
        for record in self:
            record.edit_sub_payor = self._default_edit_sub_payor()

    @api.constrains("is_sub_payor", "payor_id")
    def _check_subpayor(self):
        for record in self:
            if record.is_sub_payor and not record.payor_id:
                raise ValidationError(_("Payor is required on subpayors"))

    @api.model
    def _get_medical_identifiers(self):
        res = super(ResPartner, self)._get_medical_identifiers()
        res.append(
            (
                "is_medical",
                "is_sub_payor",
                "sub_payor_identifier",
                self._get_sub_payor_identifier,
            )
        )
        return res

    @api.model
    def _get_sub_payor_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("medical.sub.payor") or "/"
