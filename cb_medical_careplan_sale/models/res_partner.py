# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    # FHIR Entity: Payor
    # (https://www.hl7.org/fhir/coverage-definitions.html#Coverage.payor)
    _inherit = "res.partner"

    is_sub_payor = fields.Boolean(default=False)
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
    def default_medical_fields(self):
        result = super(ResPartner, self).default_medical_fields()
        result.append("is_sub_payor")
        return result

    def _check_medical(self, mode="write"):
        super()._check_medical(mode=mode)
        if (
            self.is_sub_payor
            and mode != "read"
            and not self.env.user.has_group("medical_base.group_medical_finance")
        ):
            _logger.info(
                "Access Denied by ACLs for operation: %s, uid: %s, model: %s",
                "write",
                self._uid,
                self._name,
            )
            raise AccessError(
                _(
                    "You are not allowed to %(mode)s medical Contacts (res.partner) records.",
                    mode=mode,
                )
            )
