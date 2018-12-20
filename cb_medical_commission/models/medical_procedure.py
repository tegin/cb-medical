# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalProcedure(models.Model):
    _inherit = 'medical.procedure'

    variable_fee = fields.Float(
        string='Variable fee (%)',
        store=True,
        compute='_compute_fees',
    )
    fixed_fee = fields.Float(
        string='Fixed fee',
        store=True,
        compute='_compute_fees',
    )
    practitioner_condition_id = fields.Many2one(
        'medical.practitioner.condition',
        readonly=True,
    )
    service_id = fields.Many2one(
        related='procedure_request_id.request_group_id.service_id',
        store=True,
        readonly=True,
    )
    procedure_service_id = fields.Many2one(
        related='procedure_request_id.service_id',
        store=True,
        readonly=True,
    )
    medical_commission = fields.Boolean(
        related='service_id.medical_commission'
    )
    sale_order_line_ids = fields.Many2many(
        'sale.order.line',
        string='Sale order lines',
        relation='sale_order_line_medical_procedure',
        column1='procedure_id',
        column2='sale_order_line_id',
    )
    sale_agent_ids = fields.One2many(
        inverse_name='procedure_id',
    )
    invoice_agent_ids = fields.One2many(
        inverse_name='procedure_id',
    )

    @api.constrains(
        'commission_agent_id', 'practitioner_condition_id', 'variable_fee',
        'fixed_fee',
    )
    def _launch_recompute_commission(self):
        for rec in self:
            rec.compute_commission(rec.procedure_request_id)

    @api.onchange('performer_id', 'service_id',
                  'procedure_service_id')
    def _onchange_check_condition(self):
        for rec in self:
            conditions = rec.performer_id.practitioner_condition_ids
            rec.practitioner_condition_id = conditions.get_condition(
                rec.service_id,
                rec.procedure_service_id,
                rec.procedure_request_id.center_id
            )

    @api.depends('procedure_request_id.variable_fee',
                 'procedure_request_id.fixed_fee', 'practitioner_condition_id')
    def _compute_fees(self):
        for rec in self:
            if rec.practitioner_condition_id:
                rec.variable_fee = rec.practitioner_condition_id.variable_fee
                rec.fixed_fee = rec.practitioner_condition_id.fixed_fee
            else:
                rec.variable_fee = rec.procedure_request_id.variable_fee
                rec.fixed_fee = rec.procedure_request_id.fixed_fee

    def check_agents(self, agent):
        return agent.procedure_id == self

    def get_sale_order_lines(self):
        return self.sale_order_line_ids

    def _get_sale_order_line_agent_vals(self, line):
        res = super()._get_sale_order_line_agent_vals(line)
        res['procedure_id'] = self.id
        return res

    def _get_invoice_line_agent_vals(self, inv_line):
        res = super()._get_invoice_line_agent_vals(inv_line)
        res['procedure_id'] = self.id
        return res

    def compute_commission(self, request):
        if request.is_billable:
            self.sale_order_line_ids = request.sale_order_line_ids
            return self.check_commission()
        if request.parent_model and request.parent_id:
            self.compute_commission(
                self.env[request.parent_model].browse(request.parent_id))
