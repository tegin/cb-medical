# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    college_number = fields.Char()
    is_requester = fields.Boolean()
    requester_identifier = fields.Char(readonly=True)

    @api.model
    def _get_medical_identifiers(self):
        res = super(ResPartner, self)._get_medical_identifiers()
        res.append(
            (
                "is_medical",
                "is_requester",
                "requester_identifier",
                self._get_requester_identifier,
            )
        )
        res.append(
            (
                "is_medical",
                "is_practitioner",
                "requester_identifier",
                self._get_requester_identifier,
            )
        )
        res.append(
            (
                "is_medical",
                "is_practitioner",
                "is_requester",
                self._get_requester_practitioner,
            )
        )
        return res

    @api.model
    def _get_requester_practitioner(self, vals):
        return True

    @api.model
    def _get_requester_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("medical.requester") or "/"
