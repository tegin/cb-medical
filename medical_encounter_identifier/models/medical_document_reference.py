# Copyright 2018 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class MedicalDocumentReference(models.Model):
    _inherit = 'medical.document.reference'

    @api.model
    def get_request_format(self):
        return 'DR%02d'

    @api.model
    def _get_internal_identifier(self, vals):
        code = self._get_cb_internal_identifier(vals)
        if code:
            return code
        return super()._get_internal_identifier(vals)
