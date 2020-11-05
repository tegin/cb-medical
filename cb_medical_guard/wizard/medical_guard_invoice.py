from datetime import timedelta

from odoo import _, api, fields, models


class MedicalGuardPlanApply(models.TransientModel):
    _name = "medical.guard.invoice"
    _description = "medical.guard.invoice"

    date_from = fields.Date(required=True, default=fields.Date.today())
    date_to = fields.Date(required=True)
    practitioner_ids = fields.Many2many(
        "res.partner", domain=[("is_practitioner", "=", True)]
    )
    location_ids = fields.Many2many(
        "res.partner",
        domain=[("is_location", "=", True), ("guard_journal_id", "!=", False)],
    )

    def get_guard_domain(self):
        date_to = fields.Date.to_string(
            fields.Date.from_string(self.date_to) + timedelta(days=1)
        )
        domain = [
            ("date", ">=", self.date_from),
            ("date", "<", date_to),
            ("state", "=", "completed"),
        ]

        return domain

    @api.multi
    def run(self):
        self.ensure_one()
        guards = self.env["medical.guard"].search(self.get_guard_domain())
        for guard in guards:
            guard.make_invoice()
        invoices = guards.mapped("invoice_line_ids").mapped("invoice_id")
        if len(invoices):
            return {
                "name": _("Created Invoices"),
                "type": "ir.actions.act_window",
                "views": [[False, "list"], [False, "form"]],
                "res_model": "account.invoice",
                "domain": [["id", "in", invoices.ids]],
            }
        else:
            return {"type": "ir.actions.act_window_close"}
