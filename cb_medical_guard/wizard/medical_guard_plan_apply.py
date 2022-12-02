from datetime import timedelta

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class MedicalGuardPlanApply(models.TransientModel):
    _name = "medical.guard.plan.apply"
    _description = "medical.guard.plan.apply"

    start_date = fields.Date(required=True, default=fields.Date.today())
    end_date = fields.Date(required=True)

    def run(self):
        self.ensure_one()
        guards = self.env["medical.guard"].search(
            [("date", ">=", self.start_date), ("date", "<=", self.end_date)]
        )
        if guards:
            raise ValidationError(_("Guards already exists, plan cannot be applied"))
        plans = self.env["medical.guard.plan"].search([])
        start = fields.Date.from_string(self.start_date)
        end = fields.Date.from_string(self.end_date)
        for i in range(0, (end - start).days + 1):
            date = fields.Date.to_string(start + timedelta(days=i))
            for plan in plans.filtered(lambda r: r.check_date(date)):
                plan.apply_plan(date)
