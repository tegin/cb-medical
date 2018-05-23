from odoo import api, fields, models


class MedicalEvent(models.AbstractModel):
    _name = 'medical.event'
    _inherit = ['medical.event', 'medical.cb.identifier']

    encounter_id = fields.Many2one(
        'medical.encounter', readonly=True,
    )

    @api.model
    def get_request_format(self):
        return 'EV%02d'
