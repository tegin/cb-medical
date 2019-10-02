# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    procedure_ids = fields.Many2many(
        "medical.procedure",
        relation="sale_order_line_medical_procedure",
        column1="sale_order_line_id",
        column2="procedure_id",
    )
    laboratory_event_ids = fields.Many2many(
        "medical.laboratory.event",
        relation="sale_order_line_commission_medical_laboratory_event",
        column1="sale_order_line_id",
        column2="laboratory_event_id",
    )
    laboratory_request_ids = fields.Many2many(
        "medical.laboratory.event",
        relation="sale_order_line_commission_medical_laboratory_request",
        column1="sale_order_line_id",
        column2="laboratory_request_id",
    )

    @api.multi
    def _prepare_invoice_line(self, qty):
        vals = super()._prepare_invoice_line(qty)
        if self.encounter_id:
            vals["agents"] = [
                (
                    0,
                    0,
                    {
                        "agent": x.agent.id,
                        "commission": x.commission.id,
                        "procedure_id": x.procedure_id.id or False,
                        "laboratory_request_id": x.laboratory_request_id.id
                        or False,
                        "laboratory_event_id": x.laboratory_event_id.id
                        or False,
                    },
                )
                for x in self.agents
            ]
        return vals


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    procedure_id = fields.Many2one("medical.procedure", string="Procedure")
    laboratory_event_id = fields.Many2one(
        "medical.laboratory.event", string="Laboratory Event"
    )
    laboratory_request_id = fields.Many2one(
        "medical.laboratory.request", string="Laboratory Event"
    )
    parent_agent_line_id = fields.Many2one(
        "sale.order.line.agent", readonly=True
    )
    child_agent_line_ids = fields.One2many(
        "sale.order.line.agent",
        inverse_name="parent_agent_line_id",
        readonly=True,
    )
    is_cancel = fields.Boolean(default=False, required=True, readonly=True)
    can_cancel = fields.Boolean(compute="_compute_can_cancel", store=True)
    agent_sale_line = fields.Many2many(
        comodel_name="sale.commission.settlement.line",
        relation="settlement_agent_sale_line_rel",
        column1="agent_sale_line_id",
        column2="settlement_id",
        copy=False,
    )
    settled = fields.Boolean(
        compute="_compute_settled", store=True, copy=False
    )
    invoice_group_method_id = fields.Many2one(
        "invoice.group.method",
        related="object_id.invoice_group_method_id",
        index=True,
        store=True,
        readonly=True,
    )
    date = fields.Datetime(
        string="Date",
        related="object_id.order_id.confirmation_date",
        store=True,
        readonly=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="object_id.order_id.company_id",
        store=True,
        readonly=True,
        copy=False,
    )

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
                        "is_cancel, procedure_id, laboratory_event_id, "
                        "laboratory_request_id)",
                        message,
                    )
                )
            else:
                constraints.append((key, definition, message))
        cls._sql_constraints = constraints
        return res

    @api.depends(
        "agent_sale_line",
        "agent_sale_line.settlement.state",
        "invoice_group_method_id",
        "object_id.order_id.state",
    )
    def _compute_settled(self):
        # Count lines of not open or paid invoices as settled for not
        # being included in settlements
        for line in self:
            line.settled = (
                line.object_id.order_id.third_party_order
                or not line.invoice_group_method_id.no_invoice
                or line.object_id.order_id.state not in ("sale", "done")
                or any(
                    x.settlement.state != "cancel"
                    for x in line.agent_sale_line
                )
            )

    @api.depends(
        "child_agent_line_ids", "is_cancel", "object_id.order_id.state"
    )
    def _compute_can_cancel(self):
        for rec in self:
            rec.can_cancel = (
                not rec.child_agent_line_ids
                and not rec.is_cancel
                and rec.object_id.order_id.state != "draft"
            )

    @api.constrains("parent_agent_line_id", "is_cancel")
    def _check_cancel(self):
        for record in self:
            if record.is_cancel and not record.parent_agent_line_id:
                raise ValidationError(_("Cancelled lines must have a parent."))

    @api.depends(
        "object_id.price_subtotal", "is_cancel", "parent_agent_line_id.amount"
    )
    def _compute_amount(self):
        res = super(
            SaleOrderLineAgent, self.filtered(lambda r: not r.is_cancel)
        )._compute_amount()
        for record in self.filtered(lambda r: r.is_cancel):
            record.amount = -(record.parent_agent_line_id.amount)
        return res

    def get_commission_cancel_vals(self, agent=False):
        return {
            "parent_agent_line_id": self.id,
            "object_id": self.object_id.id,
            "commission": self.commission.id,
            "agent_sale_line": False,
            "agent": agent.id if agent else self.agent.id,
            "procedure_id": self.procedure_id.id or False,
            "laboratory_event_id": self.laboratory_event_id.id or False,
            "laboratory_request_id": self.laboratory_request_id.id or False,
            "is_cancel": self.is_cancel if agent else not self.is_cancel,
        }

    def change_agent(self, agent):
        self.ensure_one()
        if agent == self.agent:
            return
        if not self.agent_sale_line:
            self.agent = agent
            return
        self.create(self.get_commission_cancel_vals())
        self.create(self.get_commission_cancel_vals(agent))
