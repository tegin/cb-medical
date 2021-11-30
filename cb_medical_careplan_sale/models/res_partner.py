# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    # FHIR Entity: Payor
    # (https://www.hl7.org/fhir/coverage-definitions.html#Coverage.payor)
    _inherit = "res.partner"

    is_sub_payor = fields.Boolean(default=False)
    sub_payor_identifier = fields.Char(readonly=True)  # FHIR Field: identifier
    payor_id = fields.Many2one(
        "res.partner", string="Payor", domain=[("is_payor", "=", True)]
    )
    sub_payor_ids = fields.One2many("res.partner", inverse_name="payor_id")
    show_patient = fields.Boolean()
    show_subscriber = fields.Boolean()
    show_authorization = fields.Boolean()
    invoice_nomenclature_id = fields.Many2one(
        "product.nomenclature",
        "Nomenclature",
        help="Nomenclature for invoices",
    )

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

    @api.model
    def default_medical_fields(self):
        result = super(ResPartner, self).default_medical_fields()
        result.append("is_sub_payor")
        return result
