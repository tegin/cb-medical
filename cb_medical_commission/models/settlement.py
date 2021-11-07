from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SettlementLine(models.Model):
    _inherit = "sale.commission.settlement.line"

    agent_sale_line = fields.Many2many(
        comodel_name="sale.order.line.agent",
        relation="settlement_agent_sale_line_rel",
        column1="settlement_id",
        column2="agent_sale_line_id",
        required=True,
    )
    settled_amount = fields.Float(
        related=False, compute="_compute_settled_amount", store=True,
    )

    @api.depends("agent_line.amount", "agent_sale_line.amount")
    def _compute_settled_amount(self):
        for record in self:
            record.settled_amount = sum(
                record.agent_line.mapped("amount")
                + record.agent_sale_line.mapped("amount")
            )

    @api.constrains("settlement_id", "agent_line", "agent_sale_line")
    def _check_company(self):
        super(
            SettlementLine, self.filtered(lambda r: r.agent_line)
        )._check_company()
        for rec in self.filtered(lambda r: r.agent_sale_line):
            if rec.agent_sale_line.company_id != rec.company_id:
                raise UserError(_("Company must be the same"))
