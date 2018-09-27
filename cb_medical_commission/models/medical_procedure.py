# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalProcedure(models.Model):
    _inherit = 'medical.procedure'

    variable_fee = fields.Float(
        string='Variable fee (%)',
        related='procedure_request_id.variable_fee'
    )
    fixed_fee = fields.Float(
        string='Fixed fee',
        related='procedure_request_id.fixed_fee'
    )
    service_id = fields.Many2one(
        related='procedure_request_id.service_id'
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
