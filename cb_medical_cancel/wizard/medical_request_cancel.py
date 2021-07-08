from odoo import fields, models


class MedicalCareplanCancel(models.AbstractModel):
    _name = "medical.request.cancel"
    _description = "medical.request.cancel"

    request_id = fields.Many2one(
        "medical.request", required=True, readonly=True
    )
    cancel_reason_id = fields.Many2one("medical.cancel.reason", required=True)
    cancel_reason = fields.Text(string="Description")

    def run(self):
        self.ensure_one()
        self.request_id.with_context(
            cancel_reason_id=self.cancel_reason_id.id,
            cancel_reason=self.cancel_reason,
        ).cancel()
