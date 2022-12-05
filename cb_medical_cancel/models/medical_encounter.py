from odoo import _, fields, models
from odoo.exceptions import ValidationError


class MedicalEncounter(models.AbstractModel):
    _inherit = "medical.encounter"

    cancel_reason_id = fields.Many2one(
        "medical.cancel.reason",
        readonly=True,
        tracking=True,
        string="Cancel reason",
    )

    def cancel(self, cancel_reason_id, session, cancel_reason=False):
        self.ensure_one()
        models = [
            self.env[model]
            for model in self.env["medical.request"]._get_request_models()
        ]
        states = ["onleave", "completed", "entered-in-error", "cancelled"]
        if self.state in states:
            raise ValidationError(
                _("Encounter %s can't be cancelled" % self.display_name)
            )
        for model in models:
            childs = model.search(
                [
                    ("encounter_id", "=", self.id),
                    ("parent_id", "=", False),
                    ("parent_model", "=", False),
                    ("state", "!=", "cancelled"),
                ]
            )
            childs.with_context(
                {
                    "cancel_reason_id": cancel_reason_id.id,
                    "cancel_reason": cancel_reason,
                }
            ).cancel()
        self.with_context(
            pos_session_id=session.id,
            company_id=session.config_id.company_id.id,
            cancel_reason_id=cancel_reason_id.id,
        ).inprogress2onleave()

    def inprogress2onleave_values(self):
        res = super().inprogress2onleave_values()
        if self._context.get("cancel_reason_id", False):
            res["cancel_reason_id"] = self._context.get("cancel_reason_id", False)
        return res
