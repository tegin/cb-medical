from odoo import api, fields, models


class MedicalLaboratoryRequest(models.Model):
    _name = "medical.laboratory.request"
    _inherit = ["medical.laboratory.request", "medical.commission.action"]

    commission_sale_order_line_ids = fields.Many2many(
        "sale.order.line",
        relation="sale_order_line_commission_medical_laboratory_request",
        column1="laboratory_request_id",
        column2="sale_order_line_id",
    )
    variable_fee = fields.Float(string="Variable fee (%)", default="0.0")
    fixed_fee = fields.Float(string="Fixed fee", default="0.0")
    medical_commission = fields.Boolean(
        related="service_id.medical_commission", readonly=True
    )
    sale_agent_ids = fields.One2many(inverse_name="laboratory_request_id")
    invoice_agent_ids = fields.One2many(inverse_name="laboratory_request_id")

    def check_agents(self, agent):
        return agent.laboratory_request_id == self

    def get_sale_order_lines(self):
        return self.commission_sale_order_line_ids

    def _get_sale_order_line_agent_vals(self, line):
        res = super()._get_sale_order_line_agent_vals(line)
        res["laboratory_request_id"] = self.id
        return res

    def _get_invoice_line_agent_vals(self, inv_line):
        res = super()._get_invoice_line_agent_vals(inv_line)
        res["laboratory_request_id"] = self.id
        return res

    def _get_event_values(self, vals=False):
        res = super()._get_event_values(vals=vals)
        self.commission_agent_id = False
        valid_performer_ids = self.performer_id.commission_agent_ids
        if not valid_performer_ids:
            valid_performer_ids += self.performer_id
        if len(valid_performer_ids) == 1:
            self.commission_agent_id = valid_performer_ids[0]
        res.update(
            {
                "commission_agent_id": self.commission_agent_id
                and self.commission_agent_id.id,
                "service_id": self.service_id.id,
            }
        )
        conditions = self.performer_id.practitioner_condition_ids
        practitioner_condition_id = conditions.get_condition(
            self.request_group_id.service_id, self.service_id, self.center_id
        )
        if practitioner_condition_id:
            res.update(
                {"practitioner_condition_id": practitioner_condition_id.id}
            )
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
                self.env[request.parent_model].browse(request.parent_id)
            )
