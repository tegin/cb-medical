from datetime import date, timedelta

from odoo import _, fields, models


class SaleCommissionMakeSettle(models.TransientModel):
    _name = "sale.commission.no.invoice.make.settle"
    _inherit = "sale.commission.make.settle"
    _description = "Sale commission no invoice make settle"

    def action_settle(self):
        self.ensure_one()
        agent_line_obj = self.env["sale.order.line.agent"]
        settlement_obj = self.env["sale.commission.settlement"]
        settlement_line_obj = self.env["sale.commission.settlement.line"]
        settlement_ids = []
        if not self.agent_ids:
            self.agent_ids = self.env["res.partner"].search([("agent", "=", True)])
        date_to = self.date_to
        for agent in self.agent_ids:
            date_to_agent = self._get_period_start(agent, date_to)
            # Get non settled invoices
            domain = [
                ("date", "<", date_to_agent),
                ("agent_id", "=", agent.id),
                ("settled", "=", False),
            ]
            agent_lines = agent_line_obj.search(domain)
            for company in agent_lines.mapped("company_id"):
                agent_lines_company = agent_line_obj.search(
                    domain + [("company_id", "=", company.id)], order="date"
                )
                if not agent_lines_company:
                    continue
                pos = 0
                sett_to = date(year=1900, month=1, day=1)
                while pos < len(agent_lines_company):
                    line = agent_lines_company[pos]
                    if line.date.date() > sett_to:
                        sett_from = self._get_period_start(agent, line.date)
                        sett_to = self._get_next_period_date(
                            agent, sett_from
                        ) - timedelta(days=1)
                        sett_from = fields.Date.to_string(sett_from)
                        settlement = self._get_settlement(
                            agent, company, sett_from, sett_to
                        )
                        if not settlement:
                            settlement = settlement_obj.create(
                                self._prepare_settlement_vals(
                                    agent, company, sett_from, sett_to
                                )
                            )
                        settlement_ids.append(settlement.id)
                    settlement_line_obj.create(
                        {
                            "settlement_id": settlement.id,
                            "agent_sale_line": [(6, 0, [line.id])],
                        }
                    )
                    pos += 1
        # go to results
        if len(settlement_ids):
            return {
                "name": _("Created Settlements"),
                "type": "ir.actions.act_window",
                "views": [[False, "list"], [False, "form"]],
                "res_model": "sale.commission.settlement",
                "domain": [["id", "in", settlement_ids]],
            }

        else:
            return {"type": "ir.actions.act_window_close"}
