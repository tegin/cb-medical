# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


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
    commission_agent_id = fields.Many2one(
        string='Commission Agent',
        comodel_name='res.partner',
    )
    sale_order_line_ids = fields.Many2many(
        string='Sale order lines',
        comodel_name='sale.order.line'
    )

    @api.onchange('performer_id')
    def _onchange_performer_id(self):
        self.commission_agent_id = False
        valid_performer_ids = self.performer_id.commission_agent_ids
        if not valid_performer_ids:
            valid_performer_ids += self.performer_id
        if len(valid_performer_ids) == 1:
            self.commission_agent_id = valid_performer_ids[0]
        else:
            return {
                'domain':
                    {'commission_agent_id':
                        [('id', 'in',
                          self.performer_id.commission_agent_ids.ids)]
                     }
            }

    def compute_commission(self, request):
        if request.is_billable:
            self.sale_order_line_ids = request.sale_order_line_ids
            return
        if request.parent_model and request.parent_id:
            self.compute_commission(
                self.env[request.parent_model].browse(request.parent_id))
