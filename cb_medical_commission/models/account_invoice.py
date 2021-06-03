# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def recompute_lines_agents(self):
        # Commission on medical sale orders will not be managed by the
        # recompute function
        return super(
            AccountInvoice, self.filtered(lambda r: not r.is_medical)
        ).recompute_lines_agents()


class AccountInvoiceLineAgent(models.Model):
    _inherit = "account.invoice.line.agent"

    procedure_id = fields.Many2one("medical.procedure", readonly=True)
    laboratory_event_id = fields.Many2one(
        "medical.laboratory.event", string="Laboratory Event"
    )
    laboratory_request_id = fields.Many2one(
        "medical.laboratory.request", string="Laboratory Request"
    )

    @api.constrains("agent", "amount")
    def _check_settle_integrity(self):
        if self.env.context.get("check_original_integrity", False):
            return super()._check_settle_integrity()
        return

    @classmethod
    def _build_model_attributes(cls, pool):
        res = super()._build_model_attributes(pool)
        constraints = []
        for (key, definition, message) in cls._sql_constraints:
            if key in ["unique_agent"]:
                constraints.append(
                    (
                        key,
                        "UNIQUE(object_id, agent, parent_agent_line_id, "
                        "procedure_id, is_cancel, laboratory_request_id, "
                        "laboratory_event_id)",
                        message,
                    )
                )
            else:
                constraints.append((key, definition, message))
        cls._sql_constraints = constraints
        return res

    def get_commission_cancel_vals(self, agent=False):
        res = super().get_commission_cancel_vals(agent)
        res["procedure_id"] = self.procedure_id.id or False
        res["laboratory_event_id"] = self.laboratory_event_id.id or False
        res["laboratory_request_id"] = self.laboratory_request_id.id or False
        return res
