from odoo import api, fields, models


class MedicalLaboratoryRequest(models.Model):
    _name = 'medical.laboratory.request'
    _inherit = ['medical.laboratory.request', 'medical.commission.action']

    commission_sale_order_line_ids = fields.Many2many(
        'sale.order.line',
        relation='sale_order_line_commission_medical_laboratory_request',
        column1='laboratory_request_id',
        column2='sale_order_line_id',
    )

    def check_agents(self, agent):
        return agent.laboratory_request_id == self

    def get_sale_order_lines(self):
        return self.commission_sale_order_line_ids

    def _get_sale_order_line_agent_vals(self, line):
        res = super()._get_sale_order_line_agent_vals(line)
        res['laboratory_request_id'] = self.id
        return res

    def _get_invoice_line_agent_vals(self, inv_line):
        res = super()._get_invoice_line_agent_vals(inv_line)
        res['laboratory_request_id'] = self.id
        return res

    @api.multi
    def generate_event(self, vals=False):
        res = super().generate_event(vals=vals)
        for r in res:
            r.compute_commission()
        return res

    def compute_commission(self, request):
        if request.is_billable:
            self.commission_sale_order_line_ids = request.sale_order_line_ids
            return self.check_commission()
        if request.parent_model and request.parent_id:
            self.compute_commission(
                self.env[request.parent_model].browse(request.parent_id))
