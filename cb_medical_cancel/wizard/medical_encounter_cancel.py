from odoo import api, fields, models


class MedicalEncounterCancel(models.TransientModel):
    _name = "medical.encounter.cancel"
    _description = "medical.encounter.cancel"

    encounter_id = fields.Many2one("medical.encounter")
    cancel_reason_id = fields.Many2one(
        "medical.cancel.reason", required=True, string="Cancel reason"
    )
    cancel_reason = fields.Text()
    pos_session_id = fields.Many2one("pos.session", required=True)

    @api.multi
    def run(self):
        self.ensure_one()
        return self.encounter_id.cancel(
            self.cancel_reason_id,
            session=self.pos_session_id,
            cancel_reason=self.cancel_reason,
        )
