from odoo import api, fields, models


class SettlementLine(models.Model):
    _inherit = "sale.commission.settlement.line"

    agent_sale_line = fields.Many2many(
        comodel_name='sale.order.line.agent',
        relation='settlement_agent_sale_line_rel', column1='settlement_id',
        column2='agent_sale_line_id', required=True)
    settled_amount = fields.Float(
        related=False, compute='_compute_settled_amount')

    @api.multi
    @api.depends('agent_line.amount', 'agent_sale_line.amount')
    def _compute_settled_amount(self):
        for record in self:
            record.settled_amount = sum(
                record.agent_line.mapped('amount') +
                record.agent_sale_line.mapped('amount')
            )
