from odoo import api, models


class MedicalProcedureRequest(models.Model):
    _inherit = 'medical.procedure.request'

    @api.multi
    def generate_event(self):
        res = super().generate_event()
        if res:
            self.filtered(lambda r: r.state == 'draft').draft2active()
        return res
