# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalRequestGroupCheckAuthorization(models.TransientModel):
    _inherit = "medical.request.group.check.authorization"

    @api.model
    def _default_authorization(self):
        return self._default_request().authorization_checked

    authorization_checked = fields.Boolean(default=_default_authorization)

    def _get_kwargs(self):
        res = super()._get_kwargs()
        res["authorization_checked"] = self.authorization_checked
        return res
