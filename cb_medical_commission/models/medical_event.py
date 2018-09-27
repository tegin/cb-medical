# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalEvent(models.AbstractModel):
    _inherit = 'medical.event'

    commission_agent_id = fields.Many2one(
        string='Commission Agent',
        comodel_name='res.partner',
        domain="[('id', 'in', commission_agent_ids)]",
    )
    commission_agent_ids = fields.Many2many(
        comodel_name='res.partner',
        related='performer_id.commission_agent_ids',
    )
    sale_agent_ids = fields.One2many(
        'sale.order.line.agent',
        inverse_name='id',
        readonly=True,
    )
    invoice_agent_ids = fields.One2many(
        'account.invoice.line.agent',
        inverse_name='id',
        readonly=True,
    )

    @api.onchange('performer_id')
    def _onchange_performer_id(self):
        self.commission_agent_id = False
        valid_performer_ids = self.performer_id.commission_agent_ids
        if not valid_performer_ids:
            valid_performer_ids += self.performer_id
        if len(valid_performer_ids) == 1:
            self.commission_agent_id = valid_performer_ids[0]

    def check_agents(self, agent):
        pass

    def get_sale_order_lines(self):
        pass

    def _get_sale_order_line_agent_vals(self, line):
        return {
            'sale_line': line.id,
            'commission': self.commission_agent_id.commission.id,
            'agent': self.commission_agent_id.id,
        }

    def _get_invoice_line_agent_vals(self, inv_line):
        return {
            'invoice_line': inv_line.id,
            'commission': self.commission_agent_id.commission.id,
            'agent': self.commission_agent_id.id,
        }

    @api.multi
    def check_commission(self):
        # We First check that all the line have been created
        for line in self.get_sale_order_lines():
            if not line.agents.filtered(lambda r: self.check_agents(r)):
                self.env['sale.order.line.agent'].create(
                    self._get_sale_order_line_agent_vals(line)
                )
            for inv_line in line.invoice_lines:
                if not inv_line.agents.filtered(
                    lambda r: self.check_agents(r)
                ):
                    self.env['account.invoice.line.agent'].create(
                        self._get_invoice_line_agent_vals(inv_line)
                    )
        sale_agents = self.sale_agent_ids.filtered(
            lambda r: not r.child_agent_line_ids and not r.is_cancel)
        invoice_agents = self.invoice_agent_ids.filtered(
            lambda r: not r.child_agent_line_ids and not r.is_cancel)
        for sale_agent in sale_agents:
            if sale_agent.agent != self.commission_agent_id:
                sale_agent.change_agent(self.commission_agent_id)
        for inv_agent in invoice_agents:
            if inv_agent and inv_agent.agent != self.commission_agent_id:
                inv_agent.change_agent(self.commission_agent_id)
