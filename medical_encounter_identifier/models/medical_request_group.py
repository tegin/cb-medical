from odoo import api, models


class MedicalRequestGroup(models.Model):
    _inherit = 'medical.request.group'

    @api.model
    def get_request_format(self):
        return 'G%02d'

    @api.model
    def _get_internal_identifier(self, vals):
        code = self._get_cb_internal_identifier(vals)
        if code:
            return code
        return super()._get_internal_identifier(vals)
