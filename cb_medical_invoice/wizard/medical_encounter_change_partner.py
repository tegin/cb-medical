from odoo import api, fields, models


class MedicalEncounterChangePartner(models.TransientModel):
    _name = "medical.encounter.change.partner"

    partner_id = fields.Many2one("res.partner", required=True)
    encounter_id = fields.Many2one("medical.encounter", required=True)

    @api.multi
    def run(self):
        self.encounter_id._change_invoice_partner(self.partner_id)
        return True
