from odoo import api, fields, models


class MedicalCommissionAction(models.AbstractModel):
    _name = "medical.commission.action"
    _description = "medical.commission.action"

    performer_id = fields.Many2one(
        string="Performer",
        comodel_name="res.partner",
        domain=[("is_practitioner", "=", True)],
    )
    commission_agent_id = fields.Many2one(
        string="Commission Agent",
        comodel_name="res.partner",
        domain="[('id', 'in', commission_agent_ids)]",
    )
    commission_agent_ids = fields.Many2many(
        comodel_name="res.partner",
        related="performer_id.commission_agent_ids",
        readonly=True,
    )
    sale_agent_ids = fields.One2many(
        "sale.order.line.agent", inverse_name="id", readonly=True
    )
    invoice_agent_ids = fields.One2many(
        "account.invoice.line.agent", inverse_name="id", readonly=True
    )

    @api.onchange("performer_id")
    def _onchange_performer_id(self):
        valid_performer_ids = self.performer_id.commission_agent_ids
        if not valid_performer_ids:
            self.commission_agent_id = self.performer_id
        elif len(valid_performer_ids) == 1:
            self.commission_agent_id = valid_performer_ids[0]
        else:
            self.commission_agent_id = False

    def check_agents(self, agent):
        pass

    def get_sale_order_lines(self):
        pass

    def _get_agent(self):
        performer_agent = False
        valid_agent_ids = self.performer_id.commission_agent_ids
        if not valid_agent_ids:
            valid_agent_ids += self.performer_id
        if len(valid_agent_ids) == 1:
            performer_agent = valid_agent_ids[0]
        agent = self.commission_agent_id or performer_agent
        return agent

    def _get_sale_order_line_agent_vals(self, line):
        agent = self._get_agent()
        res = {
            "object_id": line.id,
            "commission_id": agent.commission_id.id,
            "agent_id": agent.id,
        }
        return res

    def _get_invoice_line_agent_vals(self, inv_line):
        agent = self._get_agent()
        return {
            "object_id": inv_line.id,
            "commission": agent.commission.id,
            "agent_id": agent.id,
        }

    def check_commission(self):
        # We First check that all the line have been created
        agent = self._get_agent()
        for line in self.get_sale_order_lines():
            if (
                not line.agent_ids.filtered(lambda r: self.check_agents(r))
                and agent
                and agent.agent
            ):
                self.env["sale.order.line.agent"].create(
                    self._get_sale_order_line_agent_vals(line)
                )
            for inv_line in line.invoice_lines:
                if (
                    not inv_line.agent_ids.filtered(
                        lambda r: self.check_agents(r)
                    )
                    and agent
                    and agent.agent_id
                ):
                    self.env["account.invoice.line.agent"].create(
                        self._get_invoice_line_agent_vals(inv_line)
                    )
        sale_agents = self.sale_agent_ids.filtered(
            lambda r: not r.child_agent_line_ids and not r.is_cancel
        )
        invoice_agents = self.invoice_agent_ids.filtered(
            lambda r: not r.child_agent_line_ids and not r.is_cancel
        )
        for sale_agent in sale_agents:
            sale_agent._compute_amount()
            if sale_agent.agent_id != agent:
                sale_agent.change_agent(agent)
        for inv_agent in invoice_agents:
            inv_agent._compute_amount()
            if inv_agent and inv_agent.agent_id != agent:
                inv_agent.change_agent(agent)
