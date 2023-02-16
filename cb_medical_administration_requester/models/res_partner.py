# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    college_number = fields.Char()
    is_requester = fields.Boolean()

    @api.model
    def default_medical_fields(self):
        result = super(ResPartner, self).default_medical_fields()
        result.append("is_requester")
        return result

    def _check_medical(self, mode="write"):
        super()._check_medical(mode=mode)
        if self.is_requester and mode != "read" and not self._check_medical_requester():
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

    def _check_medical_requester(self):
        return self._check_medical_practitioner()
