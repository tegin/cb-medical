# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def compute_procedure(self):
        return self.env['medical.procedure'].search([
            ('sale_order_line_ids', 'in', self.ids)
        ])

    @api.model
    def prepare_sale_order_line_agent(self, agent):
        return [{
            'agent': agent.id,
            'commission': agent.commission.id,
        }]


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    agent_sale_line = fields.Many2many(
        comodel_name='sale.commission.settlement.line',
        relation='settlement_agent_sale_line_rel',
        column1='agent_sale_line_id', column2='settlement_id',
        copy=False)
    settled = fields.Boolean(
        compute="_compute_settled",
        store=True, copy=False)
    invoice_group_method_id = fields.Many2one(
        'sale.invoice.group.method',
        related='sale_line.order_id.invoice_group_method_id',
        index=True,
        store=True,
        readonly=True,
    )
    date = fields.Datetime(
        string="Date",
        related="sale_line.order_id.confirmation_date",
        store=True, readonly=True
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        related="sale_line.order_id.company_id",
        store=True,
        readonly=True,
        copy=False
    )

    @api.depends('agent_sale_line', 'agent_sale_line.settlement.state',
                 'invoice_group_method_id', 'sale_line.order_id.state')
    def _compute_settled(self):
        # Count lines of not open or paid invoices as settled for not
        # being included in settlements
        no_invoice = self.env.ref(
            'cb_medical_sale_invoice_group_method.no_invoice')
        for line in self:
            line.settled = (
                line.invoice_group_method_id != no_invoice or
                line.sale_line.order_id.state not in ('sale', 'done') or
                any(x.settlement.state != 'cancel'
                    for x in line.agent_sale_line))
