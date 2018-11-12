from odoo import api, models


class MedicalLaboratoryRequest(models.Model):
    _inherit = 'medical.laboratory.request'

    @api.multi
    def generate_event(self, vals=False):
        res = super().generate_event(vals=vals)
        for r in res:
            r.compute_commission()
        return res
