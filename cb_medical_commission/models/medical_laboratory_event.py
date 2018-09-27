# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalLaboratoryEvent(models.Model):
    _inherit = 'medical.laboratory.event'

    private_cost = fields.Float(required=True, default=0)
    coverage_cost = fields.Float(required=True, default=0)
    commission_sale_order_line_ids = fields.Many2many(
        'sale.order.line',
        relation='sale_order_line_commission_medical_laboratory_event',
        column1='laboratory_event_id',
        column2='sale_order_line_id',
    )
    sale_agent_ids = fields.One2many(
        inverse_name='laboratory_event_id',
    )
    invoice_agent_ids = fields.One2many(
        inverse_name='laboratory_event_id',
    )

    def check_agents(self, agent):
        return agent.laboratory_event_id == self

    def get_sale_order_lines(self):
        return self.commission_sale_order_line_ids

    def _get_sale_order_line_agent_vals(self, line):
        res = super()._get_sale_order_line_agent_vals(line)
        res['laboratory_event_id'] = self.id
        return res

    def _get_invoice_line_agent_vals(self, inv_line):
        res = super()._get_invoice_line_agent_vals(inv_line)
        res['laboratory_event_id'] = self.id
        return res

    def compute_commission(self, request=False):
        req = request or self
        if req.sale_order_line_ids:
            self.commission_sale_order_line_ids = req.sale_order_line_ids
            return self.check_commission()
        if not request:
            return self.compute_commission(self.laboratory_request_id)
        if request.parent_model and request.parent_id:
            self.compute_commission(
                self.env[request.parent_model].browse(request.parent_id))
