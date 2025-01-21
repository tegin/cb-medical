from odoo import api, fields, models


class CommissionSettlement(models.Model):
    _inherit = "commission.settlement"

    settlement_type = fields.Selection(
        selection_add=[("sale_no_invoice", "Sales With No Invoices")],
        ondelete={"sale_no_invoice": "set default"},
    )


class CommissionSettlementLine(models.Model):
    _inherit = "commission.settlement.line"

    sale_agent_line_id = fields.Many2one(
        comodel_name="sale.order.line.agent",
        index=True,
    )
    settled_amount = fields.Float(
        related=False,
        compute="_compute_settled_amount",
        store=True,
    )

    @api.depends("invoice_agent_line_id.amount", "sale_agent_line_id.amount")
    def _compute_settled_amount(self):
        for record in self:
            record.settled_amount = (
                record.invoice_agent_line_id.amount + record.sale_agent_line_id.amount
            )
