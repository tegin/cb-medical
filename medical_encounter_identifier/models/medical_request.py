from odoo import api, models


class MedicalRequest(models.AbstractModel):
    _name = 'medical.request'
    _inherit = ['medical.request', 'medical.cb.identifier']

    @api.model
    def get_request_format(self):
        return 'RQ%02d'
