from odoo import api, models


class MedicalProcedure(models.Model):
    _inherit = "medical.procedure"

    @api.multi
    def in_progress2completed(self):
        res = super().in_progress2completed()
        self.mapped("procedure_request_id").filtered(
            lambda r: r.state == "active"
        ).active2completed()
        return res
