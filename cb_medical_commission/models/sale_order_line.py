# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    procedure_ids = fields.Many2many(
        'medical.procedure',
        relation='sale_order_line_medical_procedure',
        column1='sale_order_line_id',
        column2='procedure_id',
    )

    @api.multi
    def _prepare_invoice_line(self, qty):
        vals = super()._prepare_invoice_line(qty)
        if self.encounter_id:
            vals['agents'] = [
                (0, 0, {'agent': x.agent.id,
                        'commission': x.commission.id,
                        'procedure_id': x.procedure_id.id,
                        }) for x in self.agents]
        return vals


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    procedure_id = fields.Many2one(
        'medical.procedure',
        string='Procedure'
    )
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
    # TODO: Pending to add the change of no_invoice following the code
    # of sale_commission_cancel
    _sql_constraints = [
        ('unique_agent',
         'UNIQUE(sale_line, agent, procedure_id)',
         'You can only add one time each agent.')
    ]

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
