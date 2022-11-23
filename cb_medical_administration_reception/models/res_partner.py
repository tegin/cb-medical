# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    # FHIR Entity: Location (https://www.hl7.org/fhir/location.html)
    _inherit = "res.partner"

    is_reception = fields.Boolean(default=False)
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
    def default_medical_fields(self):
        result = super(ResPartner, self).default_medical_fields()
        result.append("is_reception")
        return result

    def _check_medical(self, mode="write"):
        super()._check_medical(mode=mode)

        if (
            self.is_reception
            and mode != "read"
            and not self.env.user.has_group("medical_base.group_medical_configurator")
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
