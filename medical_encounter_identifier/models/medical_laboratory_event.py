from odoo import api, models


class MedicalLaboratoryEvent(models.Model):
    _inherit = 'medical.laboratory.event'

    @api.model
    def get_request_format(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'medical.laboratory.event.identifier')

    @api.model
    def _get_internal_identifier(self, vals):
        code = self._get_cb_internal_identifier(vals)
        if code:
            return code
        return super()._get_internal_identifier(vals)
